"""`D-093`'s prohibitions, written BEFORE the clinical association layer exists.

⚠⚠ **THESE PROHIBIT; THEY DO NOT IMPLEMENT.** No table is created, no row is written, no schema is
final. `D-093` is a pre-registration and is **void if code precedes it**, so the only code that may
land ahead of `D-093 amendment 2` is code that constrains the layer rather than builds it.

⚠ **Measured 2026-08-19 at `b7ecc2a`, before a line of this file existed:** the five assertions
`D-093` lists under *"Consequences / test surface — written before any code"* returned **ZERO** hits
across `tests/`, `core/`, `app/` and `worker/` for `burden`, `Cancer prognostics`,
`burden_supplier_unlicensed` and `therapeutic_precedent`. **The test surface the entry describes did
not exist.** That is not a defect in `D-093` — nothing it governs has been built — but *a listed
assertion nobody wrote is indistinguishable from one nobody needed*, so it is recorded here.

⚠⚠ **THE VACUITY PROBLEM, NAMED RATHER THAN DISCOVERED.** A test asserting *"no burden field"* over
a codebase with no burden concept passes for the wrong reason — Principle 9's second form, and the
same shape as a snapshot check that passes on an empty file list. **Every assertion below is
therefore paired with a fixture that makes it FAIL**, and the failures were observed. Where an
assertion cannot yet be made discriminating, it is **left unwritten and reported**, not written
vacuously.

⚠ **`burden_supplier_unlicensed` renders as a named category** — `D-093` amendment 1 clause 2
excludes every `Cancer prognostics — … (TCGA)` column, so the schema mandates a field nothing
licensed can populate. **That assertion is NOT written here**: the surface it would test does not
exist, and a rendering test with no renderer is the vacuity above wearing a ticket number.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pytest

from _tracked_sources import tracked_files

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.features import EXTENDED_FEATURE_NAMES, FEATURE_NAMES  # noqa: E402
from core.scorer import FEATURE_SETS  # noqa: E402

#: ⚠ The vocabulary is data, not a regex buried in a loop, so a reader can see exactly what is
#: barred. `burden` covers the statistic itself; the rest are the tuple fields `D-093` decision 4
#: makes mandatory, which are what a burden field looks like when it arrives without its name.
BURDEN_TOKENS = ("burden", "survival", "mortality", "incidence", "five_year", "5_year",
                 "stage_or_extent", "data_era")

#: `D-093` amendment 1 clause 2. ⚠ COLUMN-SCOPED: the column's PRESENCE is the violation, not its
#: use, because a column present in a stored table is ingested whether or not anything reads it.
#:
#: ⚠⚠ **THE RULE AS WRITTEN NAMED A COLUMN THAT DOES NOT EXIST.** Amendment 1 clause 2 excludes
#: every ``Cancer prognostics — … (TCGA)`` column. Measured 2026-08-19 against HPA v22:
#:
#:   `Cancer prognostics` as a column prefix : 0 in pathology.tsv, 0 in proteinatlas.tsv
#:   columns whose name contains `TCGA`      : 0 in either file
#:   what is ACTUALLY there                  : `prognostic - favorable`,
#:                                             `unprognostic - favorable`,
#:                                             `prognostic - unfavorable`,
#:                                             `unprognostic - unfavorable`   (4, pathology.tsv)
#:                                             `Pathology prognostics - <cancer>` (17, summary)
#:
#: **A guard matching a string that never occurs passes forever while the thing it means to
#: exclude flows through under its real name** — KEEL-1 V9 Principle 6 clause (c), and the same
#: shape as the `## P-004` grep that manufactures a false absence. So the match is on the TOKEN,
#: not the prefix, and the prefix is kept only to document what was originally ruled.
EXCLUDED_COLUMN_PREFIX_AS_RULED = "Cancer prognostics"
EXCLUDED_COLUMN_TOKEN = "prognos"

CODE_DIRS = ("core", "app", "worker")

#: ⚠⚠ THE TWO DISEASE-LEVEL MODULES, NAMED ONE BY ONE — `D-149`. NOT a pattern, NOT a directory,
#: NOT a `burden` glob: two literal paths, so a third file cannot join the exemption by being
#: named plausibly.
#:
#: **WHY AN EXEMPTION IS CORRECT HERE AND WOULD BE WRONG ANYWHERE ELSE.** `D-093` decision 1 says
#: burden is a property of the **DISEASE** and *"may never be a protein-level column"*. The rule is
#: about the PROTEIN path. `core/cancer_burden.py` and `app/cancer_burden_read.py` are the disease
#: surface `D-149` shipped: they define a `mortality` / `incidence` vocabulary over **SEER cancer
#: sites**, and they carry no accession, no gene, no protein and no score. The tokens that trip the
#: scan there are two module-level constants naming the two statistics — exactly the vocabulary a
#: disease-level surface must have in order to exist at all.
#:
#: ⚠⚠ **THE EXEMPTION IS EARNED, NOT GRANTED, AND THREE TESTS DO THE EARNING.** Directly below:
#: (1) the exemption is exactly these two paths and no more; (2) neither exempt module carries a
#: protein identifier of any kind; (3) no module on the protein path imports either of them. A bare
#: skip-list with nothing compensating would be a hole in the shape of a rule.
DISEASE_LEVEL_BURDEN_MODULES = frozenset({
    "core/cancer_burden.py",
    "app/cancer_burden_read.py",
})

#: ⚠ What an exempt module must NOT contain. `D-093` decision 1's rule stated from the other side:
#: a burden module may name diseases and may not name proteins.
PROTEIN_PATH_TOKENS = ("accession", "uniprot", "gene", "plddt", "structural_score",
                       "span_aa", "analysis_id", "protein_analyses", "ranking_run")


def _python_sources() -> list[Path]:
    out: list[Path] = []
    for d in CODE_DIRS:
        # ⚠ TRACKED ONLY — see tests/_tracked_sources.py. Another team's untracked script
        # is not this repository's code, and a prohibition scan must not blame it.
        out += tracked_files(REPO, [d])
    return out


# ─────────────────────────────────────────────────── 1-3: no burden on the protein path ──

def test_the_source_scan_reaches_real_files():
    """⚠ A-017 (a): a scan that matches nothing passes everything. Pin the corpus."""
    srcs = _python_sources()
    assert len(srcs) >= 20, f"only {len(srcs)} sources found — the scan is not reaching the tree"
    assert any(p.name == "features.py" for p in srcs)
    assert any(p.name == "scorer.py" for p in srcs)


def test_no_protein_level_model_or_payload_carries_a_burden_field():
    """`D-093` decision 1: clinical burden is a property of the DISEASE. It attaches by traversal
    and **may never be a protein-level column** — not in the scorer, not in the census filter, not
    in any protein payload.

    ⚠ Proven able to fail: adding `burden_five_year_survival` to any scanned module reds this.
    Observed 2026-08-19 by inserting it into `core/features.py` and watching it red at this
    assertion, then removing it. ⚠ Re-proven 2026-09-09 for `D-149` — see
    `test_the_burden_scan_still_fires_on_a_protein_path_module`, which inserts a probe into a real
    protein-path module rather than a temporary file.

    ⚠⚠ **`D-149` EXEMPTS TWO NAMED DISEASE-LEVEL MODULES AND NOTHING ELSE.** See
    `DISEASE_LEVEL_BURDEN_MODULES` for why that is the rule applied rather than the rule weakened,
    and for the three tests that make the exemption earned rather than granted.
    """
    offenders: list[str] = []
    for path in _python_sources():
        if str(path.relative_to(REPO)).replace("\\", "/") in DISEASE_LEVEL_BURDEN_MODULES:
            continue
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            # ⚠ Only DEFINITIONS, not prose: a comment naming the prohibition is the prohibition
            # working, and matching it would make the guard fire on its own documentation.
            if stripped.startswith("#") or stripped.startswith('"'):
                continue
            for tok in BURDEN_TOKENS:
                if re.search(rf"\b\w*{tok}\w*\s*[:=]", stripped, re.I):
                    offenders.append(f"{path.relative_to(REPO)}:{i}: {stripped[:80]}")
    assert not offenders, (
        "a burden-shaped field is defined on the protein path — D-093 decision 1 bars it:\n  "
        + "\n  ".join(offenders))


# ───────────────── D-149: the disease-level exemption, and the three tests that earn it ──


def test_the_burden_exemption_is_exactly_two_named_files_that_exist():
    """⚠⚠ (1) THE EXEMPTION CANNOT GROW BY ACCIDENT. It is two literal paths; a third file joining
    it reddens here. And each must EXIST — an exemption naming a deleted file is a skip-list entry
    that protects nothing while looking like a decision (`F-039`'s shape)."""
    assert len(DISEASE_LEVEL_BURDEN_MODULES) == 2, (
        f"the disease-level burden exemption has grown to {sorted(DISEASE_LEVEL_BURDEN_MODULES)}. "
        f"D-093 decision 1 exempts the DISEASE surface, not any file that mentions burden — a new "
        f"member needs its own ruling")
    for rel in sorted(DISEASE_LEVEL_BURDEN_MODULES):
        assert (REPO / rel).is_file(), f"{rel} is exempted but does not exist"
    # ⚠ and each exempt file must be inside the scanned corpus, or the exemption is a no-op that
    # reads as a decision. A-017: the fixture must reach the code under test.
    scanned = {str(p.relative_to(REPO)).replace("\\", "/") for p in _python_sources()}
    assert DISEASE_LEVEL_BURDEN_MODULES <= scanned, (
        f"exempted but never scanned in the first place: "
        f"{sorted(DISEASE_LEVEL_BURDEN_MODULES - scanned)}")


@pytest.mark.parametrize("rel", sorted(DISEASE_LEVEL_BURDEN_MODULES))
def test_an_exempt_burden_module_names_diseases_and_never_proteins(rel):
    """⚠⚠ (2) THE EXEMPTION IS EARNED. `D-093` decision 1 from the other side: a burden module may
    name a disease and may **not** name a protein. If `core/cancer_burden.py` ever grew an
    `accession` or a `structural_score`, the burden statistic would have become a protein-level
    field by the back door — through the one file the scan no longer reads."""
    text = (REPO / rel).read_text(encoding="utf-8")
    offenders: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # ⚠ definitions only, not prose — a comment explaining the prohibition is the prohibition
        # working, and matching it would make the guard fire on its own documentation.
        if stripped.startswith("#") or stripped.startswith('"') or stripped.startswith("'"):
            continue
        for tok in PROTEIN_PATH_TOKENS:
            if re.search(rf"\b\w*{tok}\w*\s*[:=]", stripped, re.I):
                offenders.append(f"{rel}:{i}: {stripped[:80]}")
    assert not offenders, (
        "a protein identifier is defined in a DISEASE-level burden module. That is D-093 decision "
        "1 violated through the file the burden scan exempts:\n  " + "\n  ".join(offenders))
    # ⚠ an accession-shaped literal, which no token list would catch
    assert not re.search(r"['\"][OPQ][0-9][A-Z0-9]{3}[0-9]['\"]", text), (
        f"{rel} contains an accession-shaped literal")


def test_no_protein_path_module_imports_the_disease_level_burden_surface():
    """⚠⚠ (3) THE WALL, AT FILE GRANULARITY. `D-079` amendment 1 ruling 5's separation applied to
    this layer: the modules that serve proteins must not be able to reach the burden vocabulary at
    all, so a burden figure cannot arrive on a protein payload however the code is later edited.

    ⚠ The check is the IMPORT, not the field, and that is stronger: the field guard catches a name
    someone chose, and this catches the reachability that would let any name through.
    """
    burden_modules = ("core.cancer_burden", "core/cancer_burden",
                      "app.cancer_burden_read", "app/cancer_burden_read")
    offenders: list[str] = []
    for path in _python_sources():
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        if rel in DISEASE_LEVEL_BURDEN_MODULES:
            continue
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            if any(m in stripped for m in burden_modules):
                offenders.append(f"{rel}:{i}: {stripped[:90]}")
    # ⚠ `app/read_routes.py` is the ONE permitted importer: it is the router, its import is inside
    # the route function body (not module scope), and a router that could not reach a supplier could
    # not serve it. It is named, not pattern-matched.
    allowed_prefix = "app/read_routes.py:"
    unexpected = [o for o in offenders if not o.startswith(allowed_prefix)]
    assert not unexpected, (
        "a protein-path module imports the disease-level burden surface. D-093 decision 1 keeps "
        "burden off the protein path; an import is how it would get there:\n  "
        + "\n  ".join(unexpected))
    # ⚠⚠ AND THE ROUTER'S IMPORT MUST BE FUNCTION-LOCAL, never module scope — the same posture
    # `app/read_routes.py` already uses for `app.census_structural_read`. A module-scope import
    # would put the burden vocabulary in the namespace every route body can see.
    routes = (REPO / "app" / "read_routes.py").read_text(encoding="utf-8")
    for line in routes.splitlines():
        if "cancer_burden_read" in line and (line.startswith("import ")
                                             or line.startswith("from ")):
            raise AssertionError(
                "app/read_routes.py imports the burden supplier at MODULE scope; it must be "
                f"function-local so no other route body can see it: {line.strip()!r}")


def test_the_burden_scan_still_fires_on_a_protein_path_module(tmp_path, monkeypatch):
    """⚠⚠ `A-016` — any red proves the assertion bites, and after an exemption is added that
    proof has to be re-taken. A skip-list is exactly the change that can turn a live guard vacuous,
    and *"the exemption was small"* is not a safety property.

    The probe goes into a copy of a REAL protein-path module (`core/features.py`), and the scan is
    pointed at the copy — so this exercises the same code path with the same corpus shape, rather
    than a synthetic file the real scan would never see.
    """
    real = REPO / "core" / "features.py"
    assert real.is_file()
    probe_dir = tmp_path / "core"
    probe_dir.mkdir()
    probe = probe_dir / "features.py"
    probe.write_text(
        real.read_text(encoding="utf-8") + "\n\nburden_five_year_survival: float = 0.0\n",
        encoding="utf-8")

    monkeypatch.setattr(sys.modules[__name__], "_python_sources", lambda: [probe])
    monkeypatch.setattr(sys.modules[__name__], "REPO", tmp_path)
    with pytest.raises(AssertionError, match="burden-shaped field is defined on the protein path"):
        test_no_protein_level_model_or_payload_carries_a_burden_field()


#: ⚠⚠ EVERY CLINICAL-LAYER FIELD, not just `therapeutic_precedent` (`EE-0`, step-4 order §6).
#:
#: **`P-001` asks whether a STRUCTURE-derived ranking reorders an EXPRESSION-based one.** If any
#: clinical-layer field reaches the scorer's feature path, **that question stops being answerable**
#: — the structural axis would be validated against a ranking that already contains expression.
#: ⚠⚠ **This is worse than the `therapeutic_precedent` circularity, because it would not be visible
#: in the output.** The ranking would look fine. It would simply be measuring the wrong thing.
CLINICAL_LAYER_TOKENS = (
    # the evidence label and its neighbours
    "therapeutic", "precedent", "adc_reference", "approved", "clinical", "indication",
    # the tumour axis
    "tumour", "tumor", "cancer", "pathology", "prognos",
    # the expression axis — counts, levels, and the derived score
    "expression", "ihc", "hpa", "atlas", "qh_score", "quasi_h", "h_score",
    "not_detected", "detected", "panel",
    # the normal-tissue axis
    "tissue", "cell_type", "normal_level", "reliability",
    # the evidence enum itself
    "evidence_type", "differential",
)


def test_the_scorers_feature_path_is_closed_to_every_clinical_layer_field():
    """⚠⚠ `CE2` widened by `EE-0`, and this is the most important assertion in the clinical arc.

    *"Has been developed as an ADC target"* used to RANK ADC targets is circular — the identical
    argument that bars GPI status, and the one `P-004` item 1 makes against Kathad's own validation
    step. **But `therapeutic_precedent` was only the visible case.**

    ⚠⚠ **An EXPRESSION field reaching the feature vector is the invisible one.** `P-001`'s question
    is whether structure reorders expression; if expression is *inside* the structural ranking, the
    comparison is against itself and **nothing in the output would show it.**

    ⚠ The closure is structural, not aspirational: `FEATURE_NAMES` is the pre-registered six and
    `FEATURE_SETS` indexes into it, so a clinical feature cannot be reached by the scorer without
    changing one of these two objects — and changing either reds this test.
    """
    assert len(FEATURE_NAMES) == 6, "D-027's six is the pre-registration"
    assert len(EXTENDED_FEATURE_NAMES) == 7, "six plus D-075's feature 7, and nothing else"

    barred = BURDEN_TOKENS + CLINICAL_LAYER_TOKENS
    for name in EXTENDED_FEATURE_NAMES:
        for tok in barred:
            assert tok not in name.lower(), (
                f"feature {name!r} carries the barred token {tok!r} — a clinical-layer attribute "
                f"has reached the scorer's feature vector. D-093 decision 1 bars it, and P-001's "
                f"question stops being answerable the moment it is true")

    # ⚠ every declared feature SET must index inside the pre-registered six
    for set_name, idx in FEATURE_SETS.items():
        assert all(0 <= i < len(EXTENDED_FEATURE_NAMES) for i in idx), set_name

    # ⚠⚠ and the six themselves are pinned BY NAME, so a rename cannot smuggle one past the token
    # scan. A feature called `mean_expression_ecd` would pass the loop above only if `expression`
    # were dropped from the barred list; pinning the exact six makes that a second red, not a
    # silent widening.
    assert FEATURE_NAMES == (
        "ecd_length", "radius_of_gyration", "mean_plddt_ecd",
        "membrane_proximal_plddt", "sasa_normalized", "largest_patch_fraction"), (
        "the pre-registered six changed — D-027 is the pre-registration and this is not a "
        "refactor-safe list")


# ────────────────────────────────────────── 4: the column-scoped exclusion, by PRESENCE ──

def _delimited_files() -> list[Path]:
    out: list[Path] = []
    for pat in ("*.csv", "*.tsv"):
        out += [p for p in (REPO / "data").rglob(pat)]
    return out


def test_the_delimited_file_scan_reaches_real_files():
    """⚠ A-017 (a) again, and it matters more here: `data/` is gitignored in places, so a scan
    that found nothing would look identical to a tree with no violations."""
    files = _delimited_files()
    assert len(files) >= 10, f"only {len(files)} delimited files under data/ — scan not reaching"


def test_no_cancer_prognostics_column_is_present_in_any_committed_or_cached_table():
    """`D-093` amendment 1 clause 2, made structural.

    ⚠⚠ **The column's PRESENCE is the violation, not its use.** HPA redistributes TCGA-derived
    prognostic columns under bespoke User terms nobody here has read, so the safe form is that no
    stored table carries them at all — not that no code selects them.

    ⚠ Proven able to fail: a temp CSV carrying `Cancer prognostics - x (TCGA)` under `data/` reds
    this. Observed 2026-08-19.
    """
    offenders: list[str] = []
    for path in _delimited_files():
        try:
            with path.open(encoding="utf-8", errors="replace", newline="") as fh:
                head = fh.readline()
        except OSError:
            continue
        delim = "\t" if path.suffix == ".tsv" else ","
        for col in next(csv.reader([head], delimiter=delim), []):
            if EXCLUDED_COLUMN_TOKEN in col.strip().lower():
                offenders.append(f"{path.relative_to(REPO)}: {col.strip()!r}")
    assert not offenders, (
        "a `Cancer prognostics` column is PRESENT in a stored table — presence is the violation "
        "(D-093 amendment 1 clause 2):\n  " + "\n  ".join(offenders))


# ─────────────────────────────────────────────────────── the discriminating fixtures ──

def test_the_burden_scan_would_catch_a_real_field(tmp_path):
    """⚠ The fixture that makes the prohibition falsifiable, rather than trusting the scan."""
    probe = "    burden_five_year_survival: float = 0.0"
    assert any(re.search(rf"\b\w*{tok}\w*\s*[:=]", probe, re.I) for tok in BURDEN_TOKENS)
    innocent = "    mean_plddt_ecd: float = 0.0"
    assert not any(re.search(rf"\b\w*{tok}\w*\s*[:=]", innocent, re.I) for tok in BURDEN_TOKENS)


def test_the_column_scan_would_catch_a_real_column(tmp_path):
    """⚠⚠ THE REAL COLUMN NAMES, not the one the rule was written against.

    Each name below exists in HPA v22 today, and **the as-ruled prefix misses every one of them.**
    That miss is asserted rather than described, so if `D-093` amendment 2 ever restates the rule
    in terms the data actually uses, this test reds and is re-derived deliberately.
    """
    real = ["prognostic - favorable", "unprognostic - favorable",
            "prognostic - unfavorable", "unprognostic - unfavorable",
            "Pathology prognostics - Breast cancer"]
    for name in real:
        cols = next(csv.reader([f"Gene,Gene name,{name}"]))
        assert any(EXCLUDED_COLUMN_TOKEN in c.strip().lower() for c in cols), name
        assert not any(c.strip().startswith(EXCLUDED_COLUMN_PREFIX_AS_RULED) for c in cols), (
            f"{name!r} now matches the as-ruled prefix — the finding has changed, re-derive it")

    clean = "Gene,Gene name,Tissue,Cell type,Level,Reliability"
    assert not any(EXCLUDED_COLUMN_TOKEN in c.strip().lower()
                   for c in next(csv.reader([clean])))


@pytest.mark.parametrize("name", ["therapeutic_precedent", "burden_five_year_survival",
                                  "ihc_high_count", "normal_tissue_level", "qh_score_breast",
                                  "evidence_type_ordinal", "reliability_grade"])
def test_a_barred_name_would_be_rejected_if_it_reached_the_feature_vector(name):
    """⚠⚠ The prohibition's own negative control. If this ever passes for a name that IS in
    `EXTENDED_FEATURE_NAMES`, the guard above is matching nothing."""
    barred = BURDEN_TOKENS + CLINICAL_LAYER_TOKENS
    assert any(tok in name.lower() for tok in barred)
    assert name not in EXTENDED_FEATURE_NAMES
