"""`GC2` — the `D-100` acceptance bar, expressed so it can run INSIDE the ingest transaction.

⚠⚠ **THE BAR IS NOT A POST-HOC CHECK. IT IS A PRECONDITION OF COMMITTING.** The ingest loads, then
reproduces Kathad's grid **against the rows it just wrote**, and if any figure differs the
transaction **rolls back**. A wrong ingest cannot land — not *we notice and repair it*, but *the
database refuses to keep data that fails the grid.* **Honesty made structural rather than
documentary.**

⚠ **Nothing is reimplemented.** `qh_score`, `is_kept` and `normalise_cancer` are IMPORTED from
`scripts/kathad_reproduction`, which is what `D-100` was established with. A second copy of the
convention would be two paths to one quantity in the one place the whole bar exists to prevent it.

⚠ **This module is pure.** It takes rows and returns a verdict; it opens no connection and knows no
SQL. The transaction that calls it decides what to do with the verdict — which is what lets the bar
be tested against fixtures, and proven to REJECT, without a database.

**Why the bar is free:** `D-100` already established the numbers, so the ingest checks something
already known rather than inventing an acceptance criterion for itself.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
from dataclasses import dataclass, field

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.kathad_reproduction import is_kept, normalise_cancer, qh_score  # noqa: E402
# ⚠ MOVED, not copied (see core/source_pin.py): these are provenance helpers, not clinical
# ones, and living here coupled every ingest to `scripts.kathad_reproduction`. Re-exported so
# existing callers and tests are unchanged.
from core.source_pin import (  # noqa: E402,F401
    IngestRefused,
    is_noop_rerun,
    sha256_of,
    verify_source,
)

#: The figures `D-100` established. ⚠ Named constants, not literals buried in an assertion, so a
#: change to any of them is a diff a reviewer sees.
D100_KEPT = 337
D100_EXCLUDED = 1303
D100_ROWS = 1640

COUNT_FIELDS = ("high", "medium", "low", "not_detected")



@dataclass
class GridVerdict:
    """The reproduction's result, reported as a composition rather than a single verdict."""
    rows: int = 0
    kept: int = 0
    excluded: int = 0
    no_score: int = 0
    mismatches: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (not self.mismatches
                and self.rows == D100_ROWS
                and self.kept == D100_KEPT
                and self.excluded == D100_EXCLUDED)

    def report(self) -> str:
        lines = [
            f"  rows        {self.rows:>6,d}  expected {D100_ROWS:,}",
            f"  kept        {self.kept:>6,d}  expected {D100_KEPT:,}",
            f"  excluded    {self.excluded:>6,d}  expected {D100_EXCLUDED:,}",
            f"  no score    {self.no_score:>6,d}  (empty panel — a category, never a zero)",
        ]
        if self.mismatches:
            lines.append(f"  ⚠ per-row mismatches: {len(self.mismatches)}")
            lines += [f"      {m}" for m in self.mismatches[:10]]
        return "\n".join(lines)


def reproduce_d100(ingested_rows, s3_rows) -> GridVerdict:
    """Reproduce `D-100` from INGESTED rows against the published S3 grid.

    ⚠ `ingested_rows` are dicts as they came back out of the database — **not the parsed TSV.**
    Reading the file again would compare the file to itself; the whole point is that the comparison
    crosses the write.

    ⚠⚠ Every one of the four count columns is compared, not just the derived score. Two panels can
    give the same `qh` from different counts, so a score-only check would pass a corrupted ingest.
    """
    by_key = {}
    for r in ingested_rows:
        by_key[(str(r["gene_name"]).strip(), normalise_cancer(r["cancer"]))] = r

    v = GridVerdict()
    for s3 in s3_rows:
        key = (str(s3["Gene name"]).strip(), normalise_cancer(s3["Cancer"]))
        got = by_key.get(key)
        if got is None:
            v.mismatches.append(f"{key}: absent from the ingested rows")
            continue
        v.rows += 1
        for col, field_name in (("High", "high"), ("Medium", "medium"),
                                ("Low", "low"), ("Not detected", "not_detected")):
            if int(got[field_name]) != int(s3[col]):
                v.mismatches.append(
                    f"{key}: {field_name} ingested {got[field_name]} != S3 {s3[col]}")
        total = sum(int(got[f]) for f in COUNT_FIELDS)
        score = qh_score(high=int(got["high"]), medium=int(got["medium"]),
                         low=int(got["low"]), total=total)
        if score is None:
            v.no_score += 1
        elif is_kept(score):
            v.kept += 1
        else:
            v.excluded += 1
    return v


def assert_grid_or_refuse(ingested_rows, s3_rows) -> GridVerdict:
    """⚠⚠ THE GATE. Call inside the transaction; on `IngestRefused`, ROLL BACK."""
    v = reproduce_d100(ingested_rows, s3_rows)
    if not v.ok:
        raise IngestRefused(
            "the ingested rows do not reproduce D-100's grid, so this transaction may not "
            "commit:\n" + v.report())
    return v


# ── GC4 / GC5 — the source pin, and what happens when it does not match ──────────────────────


