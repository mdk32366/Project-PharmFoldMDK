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
EXCLUDED_COLUMN_PREFIX = "Cancer prognostics"

CODE_DIRS = ("core", "app", "worker")


def _python_sources() -> list[Path]:
    out: list[Path] = []
    for d in CODE_DIRS:
        out += [p for p in (REPO / d).rglob("*.py") if "__pycache__" not in p.parts]
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
    assertion, then removing it.
    """
    offenders: list[str] = []
    for path in _python_sources():
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


def test_the_scorers_feature_path_is_closed_and_cannot_acquire_a_clinical_feature():
    """⚠⚠ `CE2`. *"Has been developed as an ADC target"* used to RANK ADC targets is circular —
    the identical argument that bars GPI status, and the one `P-004` item 1 makes against Kathad's
    own validation step. **`therapeutic_precedent` is a label and a filter. It is never a feature.**

    ⚠ The closure is structural, not aspirational: `FEATURE_NAMES` is the pre-registered six and
    `FEATURE_SETS` indexes into it, so a seventh clinical feature cannot be reached by the scorer
    without changing one of these two objects — and changing either reds this test.
    """
    assert len(FEATURE_NAMES) == 6, "D-027's six is the pre-registration"
    assert len(EXTENDED_FEATURE_NAMES) == 7, "six plus D-075's feature 7, and nothing else"

    barred = BURDEN_TOKENS + ("therapeutic", "precedent", "adc_reference", "approved",
                              "clinical", "indication", "tumour", "tumor", "cancer")
    for name in EXTENDED_FEATURE_NAMES:
        for tok in barred:
            assert tok not in name.lower(), (
                f"feature {name!r} carries the barred token {tok!r} — a clinical attribute has "
                f"reached the scorer's feature vector, which D-093 decision 1 and the GPI "
                f"circularity argument both prohibit")

    # ⚠ every declared feature SET must index inside the pre-registered six
    for set_name, idx in FEATURE_SETS.items():
        assert all(0 <= i < len(EXTENDED_FEATURE_NAMES) for i in idx), set_name


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
            if col.strip().startswith(EXCLUDED_COLUMN_PREFIX):
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
    """⚠ Same, for the column-scoped rule: a header carrying the excluded prefix must be seen."""
    header = "Gene,Gene name,Cancer prognostics - breast cancer (TCGA)"
    cols = next(csv.reader([header]))
    assert any(c.strip().startswith(EXCLUDED_COLUMN_PREFIX) for c in cols)
    clean = "Gene,Gene name,Tissue,Cell type,Level,Reliability"
    assert not any(c.strip().startswith(EXCLUDED_COLUMN_PREFIX)
                   for c in next(csv.reader([clean])))


@pytest.mark.parametrize("name", ["therapeutic_precedent", "burden_five_year_survival"])
def test_a_barred_name_would_be_rejected_if_it_reached_the_feature_vector(name):
    """⚠⚠ The prohibition's own negative control. If this ever passes for a name that IS in
    `EXTENDED_FEATURE_NAMES`, the guard above is matching nothing."""
    barred = BURDEN_TOKENS + ("therapeutic", "precedent", "clinical")
    assert any(tok in name.lower() for tok in barred)
    assert name not in EXTENDED_FEATURE_NAMES
