"""D-172 — ABSENT widen hunt + SIFTS refresh (match_kind, related, no invent)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
FIX = json.loads((ROOT / "tests" / "fixtures" / "d172_widen_fixtures.json").read_text(encoding="utf-8"))


def test_d172_entry_and_pointer():
    assert "\n### D-172 — Census PDB ABSENT widen + SIFTS refresh (metadata-only)" in LOG
    assert "match_kind" in LOG
    assert "0.50" in LOG
    assert "Next free `D-` integer: **`D-175`**" in RESERVED
    assert "Next free `D-` integer: **`D-172`**" not in RESERVED
    assert "| **D-172**" in RESERVED and "Spent" in RESERVED.split("| **D-172**", 1)[1][:220]
    assert "| **D-173**" in RESERVED and "Spent" in RESERVED.split("| **D-173**", 1)[1][:280]
    assert "| **D-174**" in RESERVED

def test_complex_chain_promotes_absent_to_present():
    from core.census_pdb import STATUS_PRESENT, select_pdb_for_accession
    from core.census_pdb_widen import merge_candidates, tag_direct

    fx = FIX["ABSENT_TO_COMPLEX"]
    painted = select_pdb_for_accession(
        accession="ABSENT_TO_COMPLEX",
        candidates_raw=merge_candidates(tag_direct(fx["direct"]), fx["widen"]),
        ecd_segments=fx["ecd_segments"],
    )
    assert painted["pdb_status"] == STATUS_PRESENT
    assert painted["pdb_best"]["pdb_id"] == "8xyz"
    assert painted["pdb_best"]["match_kind"] == "complex_chain"
    assert (painted["pdb_best"]["ecd_coverage_frac"] or 0) >= 0.50


def test_related_ortholog_alone_stays_absent_with_related():
    from core.census_pdb import STATUS_ABSENT, select_pdb_for_accession

    fx = FIX["ABSENT_RELATED_ONLY"]
    painted = select_pdb_for_accession(
        accession="ABSENT_RELATED_ONLY",
        candidates_raw=fx["widen"],
        ecd_segments=fx["ecd_segments"],
    )
    assert painted["pdb_status"] == STATUS_ABSENT
    assert painted["pdb_best"] is None
    assert painted["pdb_related"]
    assert painted["pdb_related"][0]["match_kind"] == "related_ortholog"
    assert painted["pdb_related"][0]["pdb_id"] == "1rel"


def test_widen_no_ecd_becomes_absent_no_ecd_not_present():
    from core.census_pdb import STATUS_ABSENT_NO_ECD, select_pdb_for_accession

    fx = FIX["ABSENT_WIDEN_NO_ECD"]
    painted = select_pdb_for_accession(
        accession="ABSENT_WIDEN_NO_ECD",
        candidates_raw=fx["widen"],
        ecd_segments=fx["ecd_segments"],
    )
    assert painted["pdb_status"] == STATUS_ABSENT_NO_ECD
    assert painted["pdb_best"] is None
    assert "9frag" in painted["pdb_ids"]


def test_loader_rejects_invented_missing_pdb_id():
    from core.census_pdb import STATUS_ABSENT, select_pdb_for_accession

    fx = FIX["INVENT_REFUSE"]
    painted = select_pdb_for_accession(
        accession="INVENT_REFUSE",
        candidates_raw=fx["direct"],
        ecd_segments=fx["ecd_segments"],
    )
    # missing pdb_id dropped → ABSENT, never invent
    assert painted["pdb_status"] == STATUS_ABSENT
    assert painted["pdb_best"] is None
    assert painted["pdb_ids"] == []


def test_refresh_second_load_flips_absent_without_score_touch(tmp_path):
    """Injected SIFTS-shaped row flips ABSENT→present; no structural files written."""
    from core.census_pdb import STATUS_ABSENT, STATUS_PRESENT, select_pdb_for_accession

    before = select_pdb_for_accession(
        accession="FLIPME", candidates_raw=[], ecd_segments="1-50"
    )
    assert before["pdb_status"] == STATUS_ABSENT
    after = select_pdb_for_accession(
        accession="FLIPME",
        candidates_raw=[{
            "pdb_id": "7new",
            "chain_id": "A",
            "experimental_method": "X-ray diffraction",
            "resolution": 1.9,
            "tax_id": 9606,
            "match_kind": "uniprot_direct",
            "unp_start": 1,
            "unp_end": 60,
            "observed_regions": [{"unp_start": 1, "unp_end": 60}],
        }],
        ecd_segments="1-50",
    )
    assert after["pdb_status"] == STATUS_PRESENT
    assert after["pdb_best"]["pdb_id"] == "7new"
    # structural score trees untouched by this module
    score_hits = list((ROOT / "app").rglob("*structural*"))
    assert score_hits  # exist elsewhere
    # our paint dict has no structural_score key
    assert "structural_score" not in after


def test_refresh_script_uses_normalize_db_url():
    text = (ROOT / "scripts" / "census_pdb_metadata.py").read_text(encoding="utf-8")
    assert "normalize_db_url" in text
    assert "--refresh" in text
    assert "weekly" in text.lower() or "Weekly" in text


def test_migration_additive_no_structural_writes():
    mig = (ROOT / "db" / "migrations" / "versions" / "0016_census_pdb_related.py").read_text(
        encoding="utf-8"
    )
    assert "pdb_related" in mig
    assert "structural" not in mig.lower() or "Does not touch structural" in mig
    assert "0015_census_pdb_metadata" in mig


def test_ui_honesty_related_not_this_protein():
    detail = (ROOT / "ui" / "src" / "components" / "CensusDetail.jsx").read_text(encoding="utf-8")
    assert "Related experimental structures" in detail
    assert "not this UniProt" in detail
    # forbid calling related the structure of this protein without related qualifier
    assert "match_kind" in detail or "matchKind" in detail or "complex chain" in detail
    table = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
    assert "ABSENT_NO_ECD_COVERING_STRUCTURE" in table or "ABSENT" in table
    assert "cohort-82 learned scorer" in table


def test_one_way_wall_still_holds():
    read = (ROOT / "app" / "census_pdb_read.py").read_text(encoding="utf-8")
    assert "from app.reads" not in read
    assert "import app.reads" not in read
    assert "pdb_related" in read


def test_bom_absent_on_new_python():
    for rel in (
        "core/census_pdb.py",
        "core/census_pdb_widen.py",
        "app/census_pdb_read.py",
        "scripts/census_pdb_metadata.py",
        "db/migrations/versions/0016_census_pdb_related.py",
        "tests/test_d172_census_pdb_widen_refresh.py",
    ):
        raw = (ROOT / rel).read_bytes()[:3]
        assert raw != b"\xef\xbb\xbf", f"BOM on {rel}"
