"""Entry name -> accession mapping (scale-readiness order §2).

⚠ WHY THIS IS A HARD PREREQUISITE AND NOT A CLEANUP PASS. `surfaceome_ids.txt`
holds 2,886 UniProt **entry names** (`1A01_HUMAN`). **0 of 2,886 are
accession-shaped** — the overlap with this project's join key is ZERO by
construction, not merely small. So a "try the accession, else map it" fallback
would succeed on nothing, silently. Until this mapping runs the census has 2,886
identifiers and 0 joinable rows.

⚠ AND THE PRECEDENT THAT SETS THE BAR: a **ten-line** seed file once carried
**two** wrong accessions (2026-07-22). At 2,886 rows an unverified mapping is not
a risk, it is a certainty. Entry names are explicitly not stable identifiers;
accessions are.

The failure modes are first-class outputs here, not exceptions. Every one of them
is a way of not knowing, and each is a different way, so they are kept apart.

Pure. No network — the UniProt client is injected. No GPU, no database.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from scripts.accession_map import (
    MULTI,
    OBSOLETE,
    RESOLVED,
    UNRESOLVED,
    bucket_counts,
    map_entry_names,
)


class FakeClient:
    """Stands in for the UniProt ID-mapping endpoint. Records its calls so the
    cache test can prove a second run does not re-query."""

    def __init__(self, table):
        self.table = table
        self.calls = []

    def __call__(self, entry_name):
        self.calls.append(entry_name)
        return self.table.get(entry_name, [])


# ── §2 required tests ────────────────────────────────────────────────────────

def test_every_input_id_lands_in_exactly_one_bucket():
    """resolved ∪ obsolete ∪ multi ∪ unresolved partitions the input, and the
    counts SUM TO THE INPUT COUNT. Dropping a bucket reddens this."""
    client = FakeClient({
        "A_HUMAN": [{"accession": "P11111", "active": True}],
        "B_HUMAN": [{"accession": "P22222", "active": False}],
        "C_HUMAN": [{"accession": "P33333", "active": True},
                    {"accession": "P44444", "active": True}],
        "D_HUMAN": [],
    })
    rows = map_entry_names(["A_HUMAN", "B_HUMAN", "C_HUMAN", "D_HUMAN"], client)
    counts = bucket_counts(rows)

    assert len(rows) == 4
    assert sum(counts.values()) == 4, "buckets must partition the input exactly"
    assert counts[RESOLVED] == 1 and counts[OBSOLETE] == 1
    assert counts[MULTI] == 1 and counts[UNRESOLVED] == 1


def test_unresolved_is_a_bucket_not_a_silent_drop():
    """An unmappable id appears in the output WITH ITS REASON. Filtering reddens."""
    client = FakeClient({"GONE_HUMAN": []})
    rows = map_entry_names(["GONE_HUMAN"], client)

    assert len(rows) == 1
    assert rows[0]["entry_name"] == "GONE_HUMAN"
    assert rows[0]["status"] == UNRESOLVED
    assert rows[0]["accession"] == ""
    assert rows[0].get("reason"), "an unresolved row must carry why"


def test_one_to_many_is_not_silently_collapsed():
    """An entry name resolving to >1 accession lands in `multi`, NEVER first-wins.
    Taking `[0]` reddens this.

    Owner-reserved: how a `multi` row is resolved is an identity judgement, not a
    mechanical one. The mapper reports the list and does not pick.
    """
    client = FakeClient({"AMB_HUMAN": [{"accession": "P11111", "active": True},
                                       {"accession": "P22222", "active": True}]})
    rows = map_entry_names(["AMB_HUMAN"], client)

    assert rows[0]["status"] == MULTI
    assert rows[0]["accession"] == "", "multi must not adopt one of the candidates"
    assert "P11111" in rows[0]["candidates"] and "P22222" in rows[0]["candidates"]


def test_mapping_is_cached_and_rerun_is_byte_identical(tmp_path):
    """Second run reads the cache and produces identical output. Re-querying reddens.

    2,886 entry names is thousands of requests; a re-run that re-queried would be
    slow, rude to UniProt, and — worse — could return something different, making
    the artifact non-reproducible.
    """
    client = FakeClient({"A_HUMAN": [{"accession": "P11111", "active": True}]})
    cache = tmp_path / "idcache"

    first = map_entry_names(["A_HUMAN"], client, cache_dir=str(cache))
    calls_after_first = len(client.calls)
    second = map_entry_names(["A_HUMAN"], client, cache_dir=str(cache))

    assert calls_after_first == 1
    assert len(client.calls) == 1, "second run must not re-query"
    assert first == second, "a cached re-run must be byte-identical"


def test_no_accession_is_synthesized():
    """No code path constructs an accession from a string pattern. Adding a regex
    derivation reddens this.

    The failure this prevents: turning `1A01_HUMAN` into a plausible-looking
    accession by rule. It would be well-formed, joinable, and wrong — the worst
    combination, because nothing downstream would notice.
    """
    source = (Path(__file__).resolve().parent.parent / "scripts" / "accession_map.py").read_text(
        encoding="utf-8"
    )
    body = re.sub(r'""".*?"""', "", source, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))

    # no accession-shaped regex literal, and no string-building onto an accession field
    assert "[OPQ][0-9]" not in body, "an accession-shaped regex suggests derivation, not lookup"
    for pat in ("_HUMAN'", '_HUMAN"'):
        assert f".replace({pat}" not in body, "accession must not be derived from the entry name"

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "synth" in node.name.lower():
            pytest.fail(f"synthesis helper present: {node.name}")


def test_an_empty_bucket_is_asserted_empty_not_missing():
    """⚠ `unresolved: 0` is a finding; a MISSING `unresolved` key is an unanswered
    question wearing the same clothes."""
    client = FakeClient({"A_HUMAN": [{"accession": "P11111", "active": True}]})
    counts = bucket_counts(map_entry_names(["A_HUMAN"], client))

    for bucket in (RESOLVED, OBSOLETE, MULTI, UNRESOLVED):
        assert bucket in counts, f"bucket {bucket!r} missing from the summary"
    assert counts[UNRESOLVED] == 0 and counts[MULTI] == 0 and counts[OBSOLETE] == 0


# ── the obsolete ruling (CORRECTION-RULINGS §2) ─────────────────────────────

def test_obsolete_keeps_its_provenance_even_when_a_replacement_exists():
    """⚠ CORRECTION-RULINGS §2, extended: if an obsolete entry resolves to a
    replacement accession, the row KEEPS its `obsolete` provenance alongside the
    replacement. It does not become `resolved` as though nothing happened.

    The census must be able to answer "how many of these came through a
    retirement?" later, and that answer is destroyed the moment the status is
    overwritten. Same principle as D-071's three-valued provenance strength.
    """
    client = FakeClient({"OLD_HUMAN": [{"accession": "P99999", "active": False,
                                        "replaced_by": "P12345"}]})
    rows = map_entry_names(["OLD_HUMAN"], client)

    assert rows[0]["status"] == OBSOLETE, "a retirement must not be erased by a replacement"
    assert rows[0]["accession"] == "P12345", "the replacement is still recorded"
    assert rows[0]["obsolete_accession"] == "P99999"


def test_resolved_on_is_recorded_for_every_row():
    """A mapping is a measurement with a date. Without it, a stale cache is
    indistinguishable from a fresh query."""
    client = FakeClient({"A_HUMAN": [{"accession": "P11111", "active": True}]})
    rows = map_entry_names(["A_HUMAN"], client, resolved_on="2026-08-04")
    assert rows[0]["resolved_on"] == "2026-08-04"


def test_order_is_preserved_so_output_is_diffable():
    """Row order follows input order, so two runs diff cleanly and a reviewer can
    find a specific entry without sorting."""
    names = [f"{c}_HUMAN" for c in "ABCDEFGH"]
    client = FakeClient({n: [{"accession": f"P{i:05d}", "active": True}]
                         for i, n in enumerate(names)})
    rows = map_entry_names(names, client)
    assert [r["entry_name"] for r in rows] == names


def test_a_client_error_is_unresolved_not_a_crash_and_not_a_guess():
    """A transient failure must not abort 2,886 rows, and must not be recorded as
    a successful mapping to nothing."""
    class Boom:
        def __call__(self, entry_name):
            raise RuntimeError("503 upstream")

    rows = map_entry_names(["A_HUMAN"], Boom())
    assert rows[0]["status"] == UNRESOLVED
    assert "503" in rows[0]["reason"]
