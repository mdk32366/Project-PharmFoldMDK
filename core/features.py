"""D-027 six-feature extractor + D-058 in-repo Shrake–Rupley SASA.

**ZERO third-party imports** (D-058 decision 1). `numpy`/`scipy` are in neither
`requirements.lock` nor `requirements-dev.lock`, and this module ships in the serving
tier (`core/` is copied into the image — DEP-001), so a module-scope third-party import
here would be a landmine `test_image_contents.py` cannot catch: the module present, its
dependency absent. Everything below is standard library.

**Pure given `(structure.pdb, plddt, manifest_row)`** (D-027): no network, no GPU, no
database. `extract_features` never raises on bad input — a feature that cannot be computed
records **`null` with a reason** (D-027's null-with-a-reason; *imputing a mean would be the
worst available option*). This is the function the offline driver
(`scripts/extract_features.py`) calls once per fold.

The six features (D-027, count FIXED at six — a seventh invalidates the pre-registration):

  1. ECD length — residues folded
  2. Radius of gyration, length-normalised — CA coordinates
  3. Mean pLDDT over the folded ECD
  4. Membrane-proximal pLDDT — mean over the C-terminal 25% of the ECD (derived from the
     folded-span LENGTH, never a fixed residue count; `boundary_method` travels with the row
     so a `whole` target's value is not silently compared to a `sliced_ecd` one — D-021/D-027)
  5. Solvent-accessible surface area, length-normalised — Shrake–Rupley over all atoms
  6. Largest contiguous accessible surface patch, as a fraction of total SASA — the fragile
     one (D-027); its two parameters are fixed by external convention in D-058 decision 2 and
     pinned by a test, NOT tuned against any fit.

SASA is Shrake–Rupley with parameters fixed by convention BEFORE any fit exists (D-058):
92 golden-spiral sample points per atom, 1.4 Å water probe, a committed van-der-Waals radii
table (not read from a library). Neighbour search is a spatial grid so the kernel stays under
the D-058 §1.2 timing gate; a naive O(n²) pass over ~5,000 atoms is what would trip it.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── pinned constants — changing any of these must redden the gate (D-058 test surface) ──
SASA_PROBE_RADIUS = 1.4          # Å, water probe (Shrake & Rupley / D-058 decision 1)
SASA_SAMPLE_POINTS = 92          # Shrake & Rupley's published value (D-058 decision 1)
REL_SASA_ACCESSIBLE = 0.25       # relative-SASA exposed/buried cutoff (D-058 decision 2)
CONTIGUITY_CA_ANGSTROM = 8.0     # CA–CA residue-contact distance for patch contiguity (D-058 dec 2)
MEMBRANE_PROXIMAL_FRACTION = 0.25   # feature 4: C-terminal 25% of the ECD (D-027)
PLDDT_FLOOR = 50.0               # D-041 §5, D-039 bands

# The six D-027 features, in order. The COUNT is the pre-registration (D-027) — a seventh name
# here is a decision that needs its own log entry, and the gate asserts len == 6.
FEATURE_NAMES = (
    "ecd_length",
    "radius_of_gyration",
    "mean_plddt_ecd",
    "membrane_proximal_plddt",
    "sasa_normalized",
    "largest_patch_fraction",
)

# van-der-Waals radii (Å), Bondi 1964 — a committed table, NOT read from a library at runtime
# (D-058 decision 1). Keyed by element symbol (upper-case). Unknown elements fall back to carbon.
VDW_RADII: dict[str, float] = {
    "H": 1.20, "C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80,
    "SE": 1.90, "F": 1.47, "CL": 1.75, "BR": 1.85, "I": 1.98,
    "NA": 2.27, "MG": 1.73, "K": 2.75, "CA": 2.31, "ZN": 1.39, "FE": 2.00,
}
DEFAULT_VDW = 1.70   # carbon — the dominant protein atom

# Theoretical maximum solvent-accessible surface area per residue (Å²), Tien et al. 2013
# ("Maximum Allowed Solvent Accessibilities of Residues in Proteins", PLOS ONE) — the
# denominator of relative SASA (feature 6). A committed reference table, not our measurement.
MAX_ASA: dict[str, float] = {
    "ALA": 129.0, "ARG": 274.0, "ASN": 195.0, "ASP": 193.0, "CYS": 167.0,
    "GLU": 223.0, "GLN": 225.0, "GLY": 104.0, "HIS": 224.0, "ILE": 197.0,
    "LEU": 201.0, "LYS": 236.0, "MET": 224.0, "PHE": 240.0, "PRO": 159.0,
    "SER": 155.0, "THR": 172.0, "TRP": 285.0, "TYR": 263.0, "VAL": 174.0,
}


# ── golden-spiral unit sphere (deterministic; no RNG — determinism is a D-027 requirement) ──
def _unit_sphere(n: int) -> list[tuple[float, float, float]]:
    """`n` roughly-equidistant points on the unit sphere via the golden-spiral construction.
    Deterministic — no random sampling — so features are byte-identical across runs (D-027)."""
    points: list[tuple[float, float, float]] = []
    golden = math.pi * (3.0 - math.sqrt(5.0))   # ~2.399963 rad
    for k in range(n):
        y = 1.0 - 2.0 * (k + 0.5) / n            # from +1 down to -1
        r = math.sqrt(max(0.0, 1.0 - y * y))
        phi = k * golden
        points.append((math.cos(phi) * r, y, math.sin(phi) * r))
    return points


_SPHERE = _unit_sphere(SASA_SAMPLE_POINTS)


# ── PDB parsing (stdlib only) ────────────────────────────────────────────────
@dataclass(frozen=True)
class Atom:
    name: str          # atom name, e.g. "CA", "CB", "OG1"
    element: str       # element symbol, upper-case
    res_seq: int       # residue sequence number
    res_name: str      # 3-letter residue name, e.g. "ALA"
    chain: str
    x: float
    y: float
    z: float

    @property
    def is_ca(self) -> bool:
        return self.name == "CA"

    @property
    def radius(self) -> float:
        return VDW_RADII.get(self.element, DEFAULT_VDW)


def parse_pdb(text: str) -> list[Atom]:
    """Parse ATOM/HETATM records into `Atom`s. Fixed-column PDB format. A line too short or
    with unparseable coordinates is skipped (a malformed structure yields few/no atoms, which
    the caller turns into a null-with-reason — never a crash)."""
    atoms: list[Atom] = []
    for line in text.splitlines():
        if not (line.startswith("ATOM") or line.startswith("HETATM")):
            continue
        if len(line) < 54:
            continue
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
        except ValueError:
            continue
        name = line[12:16].strip()
        res_name = line[17:20].strip()
        chain = line[21:22].strip()
        try:
            res_seq = int(line[22:26])
        except ValueError:
            continue
        element = line[76:78].strip().upper() if len(line) >= 78 else ""
        if not element:
            # Infer from the atom name: the leading alphabetic characters, minus any leading digit.
            stripped = name.lstrip("0123456789")
            element = (stripped[:1] or "C").upper()
        atoms.append(Atom(name=name, element=element, res_seq=res_seq, res_name=res_name,
                          chain=chain, x=x, y=y, z=z))
    return atoms


# ── Shrake–Rupley SASA (spatial grid; D-058 decision 1 / §1.2) ───────────────
def shrake_rupley(
    atoms: list[Atom],
    *,
    probe_radius: float = SASA_PROBE_RADIUS,
    n_points: int = SASA_SAMPLE_POINTS,
) -> list[float]:
    """Per-atom solvent-accessible surface area (Å²), Shrake–Rupley.

    Each atom's expanded sphere (vdW radius + probe) is sampled at `n_points` golden-spiral
    points; a point is accessible iff it lies outside every *other* atom's expanded sphere.
    SASA_i = (accessible fraction) · 4π(r_i + probe)².

    Neighbour search is a **uniform spatial grid** with cell size equal to the largest possible
    interaction distance, so each atom only tests atoms in its own and adjacent cells — O(n) at
    protein density, where the naive O(n²) pass is what trips the D-058 §1.2 timing gate.

    An isolated atom returns exactly `4π(r + probe)²` (every point accessible); this closed-form
    value is the D-058 anchor the test asserts against — not another implementation's output.
    """
    n = len(atoms)
    if n == 0:
        return []

    expanded = [a.radius + probe_radius for a in atoms]          # r_i + probe
    max_expanded = max(expanded)
    cell = 2.0 * max_expanded                                    # ≥ any (r_i+probe)+(r_j+probe) cutoff
    if cell <= 0.0:
        return [0.0] * n

    # Bin atom indices into grid cells.
    grid: dict[tuple[int, int, int], list[int]] = defaultdict(list)

    def cell_of(a: Atom) -> tuple[int, int, int]:
        return (int(math.floor(a.x / cell)), int(math.floor(a.y / cell)), int(math.floor(a.z / cell)))

    cells = [cell_of(a) for a in atoms]
    for i, c in enumerate(cells):
        grid[c].append(i)

    sphere = _unit_sphere(n_points) if n_points != SASA_SAMPLE_POINTS else _SPHERE
    sasa: list[float] = [0.0] * n
    neighbour_offsets = [
        (dx, dy, dz)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
    ]

    for i, a in enumerate(atoms):
        ri = expanded[i]
        cx, cy, cz = cells[i]
        # Collect candidate neighbours whose expanded spheres could bury a point on atom i's sphere.
        neighbours: list[int] = []
        for dx, dy, dz in neighbour_offsets:
            for j in grid.get((cx + dx, cy + dy, cz + dz), ()):  # noqa: B905
                if j == i:
                    continue
                rj = expanded[j]
                cutoff = ri + rj
                ddx = atoms[j].x - a.x
                ddy = atoms[j].y - a.y
                ddz = atoms[j].z - a.z
                if ddx * ddx + ddy * ddy + ddz * ddz < cutoff * cutoff:
                    neighbours.append(j)

        if not neighbours:
            sasa[i] = 4.0 * math.pi * ri * ri                    # closed-form: fully accessible
            continue

        accessible = 0
        for px, py, pz in sphere:
            # A sample point on atom i's expanded sphere, in absolute coordinates.
            sx = a.x + ri * px
            sy = a.y + ri * py
            sz = a.z + ri * pz
            buried = False
            for j in neighbours:
                rj = expanded[j]
                ddx = sx - atoms[j].x
                ddy = sy - atoms[j].y
                ddz = sz - atoms[j].z
                if ddx * ddx + ddy * ddy + ddz * ddz < rj * rj:
                    buried = True
                    break
            if not buried:
                accessible += 1

        sasa[i] = (accessible / len(sphere)) * 4.0 * math.pi * ri * ri
    return sasa


# ── the six features ─────────────────────────────────────────────────────────
@dataclass
class FeatureRow:
    """The extractor's output for one target: the six D-027 features (any of which may be
    `None`), the reasons any are `None`, the stored D-041 §5 floor decision, and the source-hash
    `feature_version`. `null_reasons` is non-empty **iff** some feature is `None`."""

    ecd_length: Optional[float] = None
    radius_of_gyration: Optional[float] = None
    mean_plddt_ecd: Optional[float] = None
    membrane_proximal_plddt: Optional[float] = None
    sasa_normalized: Optional[float] = None
    largest_patch_fraction: Optional[float] = None
    null_reasons: dict[str, str] = field(default_factory=dict)
    mean_plddt: Optional[float] = None
    below_plddt_floor: Optional[bool] = None
    boundary_method: Optional[str] = None
    feature_version: str = ""

    def as_feature_dict(self) -> dict[str, Optional[float]]:
        """The six features by name — exactly six keys, the enforced pre-registration (D-027)."""
        return {name: getattr(self, name) for name in FEATURE_NAMES}


def _radius_of_gyration(ca_coords: list[tuple[float, float, float]]) -> float:
    """Raw radius of gyration over CA coordinates: sqrt(mean |r_i − r_com|²)."""
    n = len(ca_coords)
    cx = sum(c[0] for c in ca_coords) / n
    cy = sum(c[1] for c in ca_coords) / n
    cz = sum(c[2] for c in ca_coords) / n
    msd = sum((c[0] - cx) ** 2 + (c[1] - cy) ** 2 + (c[2] - cz) ** 2 for c in ca_coords) / n
    return math.sqrt(msd)


def _largest_patch_fraction(atoms: list[Atom], per_atom_sasa: list[float]) -> Optional[float]:
    """Feature 6: summed SASA of the largest contiguous accessible patch / total SASA.

    A residue is *accessible* if its relative SASA (its summed atom SASA over Tien's theoretical
    maximum for its type) ≥ 0.25; two accessible residues are *contiguous* if their CA atoms are
    within 8 Å. The patch is the largest connected component under that relation. Both thresholds
    are external conventions fixed in D-058 decision 2 — not tuned against any fit.
    """
    # Aggregate SASA and locate the CA atom per residue key (chain, res_seq).
    res_sasa: dict[tuple[str, int], float] = defaultdict(float)
    res_name: dict[tuple[str, int], str] = {}
    res_ca: dict[tuple[str, int], tuple[float, float, float]] = {}
    for a, s in zip(atoms, per_atom_sasa):  # noqa: B905
        key = (a.chain, a.res_seq)
        res_sasa[key] += s
        res_name.setdefault(key, a.res_name)
        if a.is_ca:
            res_ca[key] = (a.x, a.y, a.z)

    total_sasa = sum(res_sasa.values())
    if total_sasa <= 0.0:
        return None

    # Accessible residues: relative SASA ≥ 0.25, and we need a CA to place them for contiguity.
    accessible: list[tuple[str, int]] = []
    for key, s in res_sasa.items():
        max_asa = MAX_ASA.get(res_name.get(key, ""), None)
        if max_asa is None or key not in res_ca:
            continue
        if s / max_asa >= REL_SASA_ACCESSIBLE:
            accessible.append(key)
    if not accessible:
        return 0.0

    # Connected components under CA–CA ≤ 8 Å (union–find over the accessible residues).
    parent = {k: k for k in accessible}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a_key, b_key):
        ra, rb = find(a_key), find(b_key)
        if ra != rb:
            parent[ra] = rb

    cutoff_sq = CONTIGUITY_CA_ANGSTROM * CONTIGUITY_CA_ANGSTROM
    for i in range(len(accessible)):
        ax, ay, az = res_ca[accessible[i]]
        for j in range(i + 1, len(accessible)):
            bx, by, bz = res_ca[accessible[j]]
            if (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2 <= cutoff_sq:
                union(accessible[i], accessible[j])

    component_sasa: dict[tuple[str, int], float] = defaultdict(float)
    for key in accessible:
        component_sasa[find(key)] += res_sasa[key]

    return max(component_sasa.values()) / total_sasa


def extract_features(
    pdb_text: Optional[str],
    plddt: Optional[list[float]],
    *,
    boundary_method: Optional[str] = None,
    mean_plddt: Optional[float] = None,
) -> FeatureRow:
    """Compute the six D-027 features for one fold. **Never raises** — a feature that cannot be
    computed is `None` with an entry in `null_reasons` (D-027; never an imputed mean).

    `pdb_text` may be `None`/empty (a failed fold with an analysis row but no structure, e.g.
    IGF2R — D-058 Addendum 2 §1); the structural features are then null-with-reason and the
    pLDDT features follow whatever `plddt` provides. `boundary_method` travels onto the row so
    feature 4's cross-method incomparability (D-021/D-027) is legible downstream. `mean_plddt`
    is the fold's stored value (D-041 §5 floor); when omitted it is derived from `plddt`.
    """
    row = FeatureRow(boundary_method=boundary_method, feature_version=feature_version())

    # ── pLDDT-derived features (3, 4) and the stored floor decision ──
    if plddt:
        n_res = len(plddt)
        row.ecd_length = float(n_res)                                    # feature 1
        row.mean_plddt_ecd = sum(plddt) / n_res                          # feature 3
        k = max(1, math.ceil(MEMBRANE_PROXIMAL_FRACTION * n_res))        # C-terminal 25% of the span
        row.membrane_proximal_plddt = sum(plddt[-k:]) / k                # feature 4
        row.mean_plddt = mean_plddt if mean_plddt is not None else row.mean_plddt_ecd
    else:
        for name in ("ecd_length", "mean_plddt_ecd", "membrane_proximal_plddt"):
            row.null_reasons[name] = "no per-residue pLDDT (fold produced no plddt.json)"
        row.mean_plddt = mean_plddt

    row.below_plddt_floor = (row.mean_plddt < PLDDT_FLOOR) if row.mean_plddt is not None else None

    # ── structure-derived features (2, 5, 6) ──
    atoms = parse_pdb(pdb_text) if pdb_text else []
    if not atoms:
        reason = "no structure (fold failed - no PDB)" if not pdb_text \
            else "malformed structure (no atoms parsed from PDB)"
        for name in ("radius_of_gyration", "sasa_normalized", "largest_patch_fraction"):
            row.null_reasons[name] = reason
        return row

    ca_coords = [(a.x, a.y, a.z) for a in atoms if a.is_ca]
    n_res_struct = len(ca_coords)

    # feature 2 — radius of gyration, length-normalised
    if n_res_struct >= 2:
        row.radius_of_gyration = _radius_of_gyration(ca_coords) / n_res_struct
    else:
        row.null_reasons["radius_of_gyration"] = "fewer than two CA atoms (no gyration to compute)"

    # features 5, 6 — SASA
    per_atom_sasa = shrake_rupley(atoms)
    total_sasa = sum(per_atom_sasa)
    length_for_norm = n_res_struct if n_res_struct > 0 else len(atoms)
    if total_sasa > 0.0 and length_for_norm > 0:
        row.sasa_normalized = total_sasa / length_for_norm               # feature 5
    else:
        row.null_reasons["sasa_normalized"] = "zero total SASA (degenerate structure)"

    patch = _largest_patch_fraction(atoms, per_atom_sasa)                 # feature 6
    if patch is None:
        row.null_reasons["largest_patch_fraction"] = "zero total residue SASA (degenerate structure)"
    else:
        row.largest_patch_fraction = patch

    return row


# ── feature_version: source-hash pin (D-027) ─────────────────────────────────
_FEATURE_VERSION: Optional[str] = None


def feature_version() -> str:
    """A short hash of THIS module's source (D-027): a refit against changed feature code is then
    detectable rather than silent. Derived from the source, never a hand-typed constant — so a
    literal `"v1"` in place of this derivation reddens the source-hash pin test (D-009 red-on-change)."""
    global _FEATURE_VERSION
    if _FEATURE_VERSION is None:
        source = Path(__file__).read_bytes()
        _FEATURE_VERSION = hashlib.sha256(source).hexdigest()[:12]
    return _FEATURE_VERSION
