"""The CSV and the workbook must never disagree (RULINGS-2026-08-04-F016 §4 + parent/child ruling).

⚠ WHY THESE TESTS EXIST AND WHAT THEY ARE GUARDING. The CSV and the xlsx hold the
same 7,903 rows. Two paths to one quantity is this project's signature defect
class — it is how F-002's denominators, F-008's precisions, and F-012's chunk
recipes each went wrong. Nothing compared these two artifacts, so they would have
drifted silently the first time either was regenerated.

The workbook is now DERIVED from the CSV by `scripts/build_membraneome_xlsx.py`.
These tests redden if that derivation is skipped, stale, or edited by hand.

⟡ They also pin the three class counts. A test that only compared the two files to
each other would stay green while both drifted together — which is the failure
mode of comparing a thing to its own copy.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")

ROOT = Path(__file__).resolve().parent.parent
STEM = "membraneome-reconstructed-2026-08-04"
CSV_PATH = ROOT / "data" / "census" / f"{STEM}.csv"
XLSX_PATH = ROOT / "data" / "census" / f"{STEM}.xlsx"

DERIVED_COLUMNS = [
    "surfy_class",
    "uniprot_status",
    "uniprot_current_accession",
    "uniprot_current_entry_name",
    "uniprot_primary_gene",
    "gene_symbol_changed",
    "foldable",
    "class_conflict",
]

# Read off the file 2026-08-04 and corroborated against wollscheidlab.org/SURFY,
# which publishes 2,886 surfaceome and 2,216 nonsurfaceome. 2,801 is published
# nowhere and is counted here.
EXPECTED_CLASS_COUNTS = {"surface": 2886, "non_surface": 2216, "unclassified": 2801}
EXPECTED_ROWS = 7903
EXPECTED_SURFACE_DENOMINATOR = 2807  # distinct accessions, NOT identifiers


pytestmark = pytest.mark.skipif(
    not CSV_PATH.exists(),
    reason=f"{CSV_PATH.name} not present; census artifacts are not built in this checkout",
)


def _csv_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        return next(rd), [r for r in rd]


def _xlsx_rows():
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb["membraneome"]
    rows = [["" if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
    wb.close()
    return rows[0], rows[1:]


def test_workbook_exists_alongside_its_parent():
    assert XLSX_PATH.exists(), (
        f"{XLSX_PATH.name} is missing. It is DERIVED from {CSV_PATH.name} - rebuild it with "
        f"scripts/build_membraneome_xlsx.py rather than authoring it."
    )


def test_row_counts_agree():
    _, csv_body = _csv_rows()
    _, xlsx_body = _xlsx_rows()
    assert len(csv_body) == EXPECTED_ROWS
    assert len(xlsx_body) == len(csv_body), (
        f"row-count drift: CSV has {len(csv_body)}, workbook has {len(xlsx_body)}. "
        f"The workbook is stale - rebuild it from the CSV."
    )


def test_headers_agree_and_carry_every_derived_column():
    csv_header, _ = _csv_rows()
    xlsx_header, _ = _xlsx_rows()
    assert csv_header == xlsx_header, "header drift between CSV and workbook"
    for col in DERIVED_COLUMNS:
        assert col in csv_header, f"derived column {col!r} missing from the source of record"


def test_derived_columns_agree_row_for_row():
    """The added columns are the ones a stale rebuild would silently change."""
    csv_header, csv_body = _csv_rows()
    xlsx_header, xlsx_body = _xlsx_rows()
    ci = {c: csv_header.index(c) for c in DERIVED_COLUMNS}
    xi = {c: xlsx_header.index(c) for c in DERIVED_COLUMNS}

    mismatches = []
    for n, (c_row, x_row) in enumerate(zip(csv_body, xlsx_body), start=2):
        for col in DERIVED_COLUMNS:
            if c_row[ci[col]] != x_row[xi[col]]:
                mismatches.append(f"row {n} col {col}: csv={c_row[ci[col]]!r} xlsx={x_row[xi[col]]!r}")
                if len(mismatches) >= 10:
                    break
        if len(mismatches) >= 10:
            break
    assert not mismatches, "derived-column drift:\n  " + "\n  ".join(mismatches)


def test_class_counts_are_the_counted_ones():
    """Guards against both files drifting together - comparing a thing to its own copy."""
    csv_header, csv_body = _csv_rows()
    idx = csv_header.index("surfy_class")
    counts = {}
    for r in csv_body:
        counts[r[idx]] = counts.get(r[idx], 0) + 1
    assert counts == EXPECTED_CLASS_COUNTS, (
        f"class counts changed: {counts} != {EXPECTED_CLASS_COUNTS}. "
        f"If this is intentional it is a NEW dated artifact, not a new version of this one."
    )


def test_surface_denominator_is_distinct_accessions_not_identifiers():
    """The F-016 correction, pinned: 2,886 identifiers are 2,807 proteins."""
    csv_header, csv_body = _csv_rows()
    cls = csv_header.index("surfy_class")
    cur = csv_header.index("uniprot_current_accession")
    surface = [r for r in csv_body if r[cls] == "surface"]
    assert len(surface) == EXPECTED_CLASS_COUNTS["surface"]
    assert len({r[cur] for r in surface}) == EXPECTED_SURFACE_DENOMINATOR, (
        "the surface denominator is distinct accessions, not identifiers"
    )


def test_inactive_rows_are_retained_and_flagged_not_foldable():
    """Rulings §5: present, flagged, dropped from nothing."""
    csv_header, csv_body = _csv_rows()
    st = csv_header.index("uniprot_status")
    fold = csv_header.index("foldable")
    inactive = [r for r in csv_body if r[st] == "inactive"]
    assert inactive, "inactive rows have gone missing - they must be retained, never dropped"
    assert all(r[fold] == "no" for r in inactive), "an inactive row has no current sequence to fold"
