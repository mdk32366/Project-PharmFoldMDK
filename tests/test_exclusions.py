"""D-085 — a named exclusion must say whether it can be folded, and under what conditions.

⚠ The owner's ruling: *"It appears all of those exclusions cannot be folded. If that is NOT the
case and it can be folded, then stating the conditions under which that is possible is required."*

⚠⚠ **The premise did not hold, which is exactly why these tests exist.** `MUC16` and `FAT2` are in
the census manifest at **tranche 5, tier=rental — scheduled to fold.** An exclusion registry read
as *"cannot be folded"* would have abandoned two queued rows.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from core.manifest import EXCLUSIONS, NAMED_EXCLUSIONS, Exclusion

REPO = Path(__file__).resolve().parent.parent


def test_every_foldable_exclusion_states_its_conditions():
    """⚠ The ruling made structural. Prose decays; a constructor does not."""
    for acc, e in EXCLUSIONS.items():
        if e.foldable != "no":
            assert e.conditions.strip(), (
                f"{acc} is foldable ({e.foldable!r}) but states no conditions — "
                f"it would read as impossible and the work would be silently abandoned")


def test_the_conditions_rule_is_enforced_at_construction_not_by_review():
    """⚠ Prove it bites: an entry added in a hurry must be REFUSED, not merely reviewed."""
    with pytest.raises(ValueError, match="conditions"):
        Exclusion(symbol="X", scope="cohort", reason="r", foldable="yes, on rental", conditions="")
    # ⚠ And the escape hatch still works, or the rule would be unusable and get deleted.
    Exclusion(symbol="X", scope="cohort", reason="r", foldable="no", conditions="")


def test_named_exclusions_is_cohort_scoped_and_excludes_the_census_only_entry():
    """⚠⚠ THE SCOPE IS LOAD-BEARING. `NAMED_EXCLUSIONS` drives the COHORT manifest and the roster
    reconciliation. `P55073` is a census accession and is NOT in the 82 — putting it there would
    be inert where it matters and wrong where it lands."""
    assert "P55073" in EXCLUSIONS
    assert "P55073" not in NAMED_EXCLUSIONS
    assert set(NAMED_EXCLUSIONS) == {"Q8WXI7", "Q9NYQ8"}


def test_the_cohort_exclusions_are_actually_queued_in_the_census():
    """⚠⚠ The fact that refuted the premise, asserted against the DATA rather than restated.

    If a future edit routes `MUC16`/`FAT2` away from tranche 5, this fails — and it should, because
    their `foldable` text promises a queued rental fold."""
    manifest = REPO / "data" / "census" / "census_manifest.v7.csv"
    if not manifest.is_file():
        pytest.skip("census manifest absent")
    rows = {r["census_accession"]: r for r in csv.DictReader(manifest.open(encoding="utf-8"))}
    for acc in ("Q8WXI7", "Q9NYQ8"):
        assert acc in rows, f"{acc} is not in the census manifest — its stated conditions are false"
        assert rows[acc]["tier"] == "rental"
        assert EXCLUSIONS[acc].foldable.startswith("yes")


def test_the_untokenisable_residue_set_matches_what_the_vocabulary_actually_accepts():
    """⚠ `X` is IN the ESM vocabulary and `U` is not — measured (F-033), not assumed.

    Asserted here so a future edit that 'tidies' `X` out of `TOKENISABLE` would fail: it would
    silently exclude every span carrying an unknown residue."""
    import sys
    sys.path.insert(0, str(REPO))
    from scripts.census_ingest import TOKENISABLE, untokenisable_residues

    assert "X" in TOKENISABLE, "X tokenises — excluding it would drop foldable spans"
    assert "U" not in TOKENISABLE
    assert untokenisable_residues("ACDEFGHIKLMNPQRSTVWYX") == []
    assert untokenisable_residues("MKTAYIAKQRUQISFVK") == ["U"]
    # ⚠ Returns them ALL, so the reason can name every offender rather than only the first.
    assert untokenisable_residues("MKTUOAYI") == ["O", "U"]


def test_the_selenocysteine_row_is_the_one_that_actually_failed():
    """⚠ The exclusion must point at the real span, not a plausible one. P55073's span is what the
    worker choked on; an exclusion naming a different range would guard nothing."""
    e = EXCLUSIONS["P55073"]
    assert "68" in e.symbol and "304" in e.symbol
    assert "selenocysteine" in e.reason
    # ⚠ It must NOT claim to be unfoldable — it is foldable, by folding a different sequence.
    assert e.foldable != "no"
    assert "DIFFERENT SEQUENCE" in e.foldable
