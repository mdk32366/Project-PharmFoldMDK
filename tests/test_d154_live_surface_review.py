"""D-154 — the live-surface review ship. All of these must go red if their fix is reverted.

⚠⚠ **THE DEFECT THIS FILE EXISTS FOR IS ONE A FIXTURE CANNOT SEE, AND THAT IS THE WHOLE POINT.**
`D-152` decision 5 states that `/coverage` and `/scorer` search *"aliases included"*, and
`ui/src/components/SurfaceLayout.d152.test.jsx:71` proves it by hand-writing ``aliases: ['CA-125']``
onto a coverage fixture row. **On the live site `CA-125` returned 0 rows and `HER2` returned 0
ranking rows**, because `coverage_payload` and `ranking_payload` never put an `aliases` key on the
wire at all. The fixture asserted a field the server does not send — `D-146`'s recorded shape (*the
gate pins the WORDS and never the WORLD*) and `F-054`'s (*green tests certifying a feature absent
from production*), in the suite that shipped the promise.

⚠ **So the alias guards below run the REAL builders over the REAL pinned alias cache** — never a
row literal with the key already on it. `core/protein_aliases.py` reads a committed cache, so this
is hermetic: no network, no Fly, no ops, no GPU, no artifact read.

⚠ **`D-152` is NOT amended by any of this.** Every word of its decision 5 is true of what that PR
wired on the client; the missing half was on the server, and this entry supplies it.

⚠ The three copy guards (burden geography, the never-folded length verdict, the unnamed Tranche
cell) are **source-level** here and **behavioural** in `ui/src/components/*.d154.test.jsx` — the
Python side pins that the fix exists in the tree, the vitest side pins what a reader sees.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.reads import (
    COHORT_TRANCHE,
    attach_aliases,
    coverage_payload,
    list_analyses,
    ranking_payload,
)
from core.cancer_burden import US_ONLY_DISCLAIMER
from core.protein_aliases import aliases_by_accession
from db.models import (
    Base,
    ProteinAnalysis,
    RankingResult,
    RankingRun,
    TargetScore,
)

ROOT = Path(__file__).resolve().parents[1]
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
FLY = (ROOT / "fly.toml").read_text(encoding="utf-8")
UI = ROOT / "ui" / "src"
BURDEN_VIEW = (UI / "components" / "CancerBurdenView.jsx").read_text(encoding="utf-8")
CENSUS_PROTEIN = (UI / "components" / "CensusProteinView.jsx").read_text(encoding="utf-8")
CENSUS_TABLE = (UI / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
# ⚠ D-155: `/coverage`'s table is `/targets`' table now, and its search box went with it.
COVERAGE_VIEW = (UI / "components" / "TargetList.jsx").read_text(encoding="utf-8")
SCORER_VIEW = (UI / "components" / "ScorerView.jsx").read_text(encoding="utf-8")

#: MUC16 / CA-125 — the query `/coverage`'s own placeholder advertises, and the row it must reach.
#: ⚠ A `D-022` oversize exclusion, so it is NOT in `/api/analyses` at all: it reaches `/targets`
#: and `/coverage` from the manifest, which is exactly why the cohort list's aliases never covered it.
MUC16 = "Q8WXI7"
#: ERBB2 / HER2 — the query `/scorer`'s placeholder advertises. Ranked, folded, rank 7 on the live run.
ERBB2 = "P04626"


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _seed_ranking(engine, accession: str) -> None:
    """One valid run with one scored row, keyed on a REAL accession so the alias join is exercised
    rather than mocked. ⚠ The score and rank are fixture values and no live number is implied."""
    with Session(engine) as s:
        run = RankingRun(target_list_version="v", scorer_version="d154-fixture")
        s.add(run)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=run.id, n_fit_positives=3, n_ranking_set=7,
            structural_percentiles=[0.5], lambda_per_fold=[{"symbol": "SEED", "converged": True}],
            excluded=[], loo_status="complete", fulldata_status="converged",
            status_detail="fixture",
        ))
        a = ProteinAnalysis(input_type="uniprot", input_value=accession,
                            cohort_tranche=COHORT_TRANCHE, meta={"gene": "SEED"})
        s.add(a)
        s.flush()
        s.add(TargetScore(ranking_run_id=run.id, analysis_id=a.id, score=0.5,
                          attributions=[0.1] * 6, rank=1))
        s.commit()


# ───────────────────────────── the promise each box prints ─────────────────────────────


def test_the_coverage_row_carries_the_alias_its_own_placeholder_advertises(engine):
    """⚠⚠ THE HEADLINE DEFECT, AS THE SURFACE STATED IT. `/coverage`'s box reads *"gene, accession,
    or a name like CA-125"* and `CA-125` matched nothing, because `MUC16`'s row had no alias on it.
    ⚠ The assertion is the ALIAS ON THE ROW, not the count of rows a matcher returns: the matcher is
    `ui/src/searchRows.js` and is tested there. What was missing is the field it reads."""
    row = next(r for r in coverage_payload(engine)["rows"] if r["accession"] == MUC16)
    assert "aliases" in row, "the coverage row carries no aliases key at all — the D-152 defect"
    assert row["aliases"], "MUC16's aliases are empty; the pinned cache has four for it"
    assert "CA-125" in row["aliases"], (
        "the exact string the placeholder advertises is not on the row it must reach")


def test_the_ranking_row_carries_the_alias_its_own_placeholder_advertises(engine):
    """⚠ Same defect, the other surface: `/scorer` prints *"a name like HER2"* and `HER2` returned
    zero ranking rows while `ERBB2` returned rank 7."""
    _seed_ranking(engine, ERBB2)
    row = ranking_payload(engine)["rows"][0]
    assert row["accession"] == ERBB2
    assert "aliases" in row and row["aliases"], "the ranking row carries no aliases"
    assert "HER2" in row["aliases"]


def test_the_two_placeholders_still_name_the_aliases_the_payloads_now_carry():
    """⚠⚠ THE PROMISE AND THE PAYLOAD ARE PINNED TOGETHER, because the defect was the GAP between
    them. If a later edit changes either placeholder to advertise a different name, this reddens and
    sends the writer to the payload rather than letting the surface promise something again."""
    # ⚠ D-155: one surface, one box. The merged page advertises `HER2`, and `CA-125` remains
    # the alias that must resolve — asserted on the payload above and on the matcher's own
    # suite, so the promise and the data stay pinned together even though the two boxes became
    # one. The literal is kept in this file so a reader can still find the string that failed.
    assert "HER2" in COVERAGE_VIEW, (
        "the merged cohort surface stopped advertising an alias; the payload guard above is "
        "now aimed at nothing")
    assert "HER2" in SCORER_VIEW, "/scorer stopped advertising HER2; the guard above is now aimed at nothing"


def test_every_row_of_both_payloads_answers_the_alias_question_one_way_or_the_other(engine):
    """⚠ `None` is an answer and an absent key is not. A row with no known alias must still carry
    the key, so a consumer can tell *"this protein has no other names on file"* from *"this surface
    does not serve them"* — the same absence discipline the rest of the tree applies to a cell."""
    _seed_ranking(engine, ERBB2)
    for payload, label in ((coverage_payload(engine), "coverage"), (ranking_payload(engine), "ranking")):
        for row in payload["rows"]:
            assert "aliases" in row, f"a {label} row is missing the aliases key entirely"


def test_the_cohort_list_did_not_lose_its_aliases_when_the_block_was_extracted(engine):
    """⚠ The regression the extraction could have caused. `list_analyses` had this behaviour since
    `D-101`'s follow-through and must still have it."""
    with Session(engine) as s:
        s.add(ProteinAnalysis(input_type="uniprot", input_value=ERBB2,
                              cohort_tranche=COHORT_TRANCHE, meta={"gene": "ERBB2"}))
        s.commit()
    row = next(r for r in list_analyses(engine) if r["accession"] == ERBB2)
    assert row["aliases"] and "HER2" in row["aliases"]


def test_attach_aliases_is_one_function_and_not_a_fourth_copy():
    """⚠⚠ `F-052` IS THE REASON THIS IS A TEST. The block was pasted into one caller, and the entry
    that reasoned about two more never received it. A fourth copy would look identical the day it
    was written and drift on the first tweak, so the assignment must exist exactly ONCE in the file
    and the callers must call the function."""
    assert READS.count('row["aliases"] = alias_map.get') == 1, (
        "the alias assignment appears more than once — that is the copy, not the fix")
    assert "def attach_aliases(" in READS
    for caller in ("coverage_payload", "ranking_payload"):
        body = READS.split(f"def {caller}(", 1)[1].split("\ndef ", 1)[0]
        assert "attach_aliases(" in body, f"{caller} does not attach aliases"


def test_attach_aliases_costs_the_aliases_and_nothing_else_when_the_cache_is_gone(monkeypatch):
    """⚠⚠ `F-054`'s rule: a guard must not be wider than the optional thing it guards. If the alias
    cache cannot be read, the rows still come back — search degrades to gene / accession, and a
    coverage denominator is never lost to a naming convenience."""
    import core.protein_aliases as pa
    monkeypatch.setattr(pa, "aliases_by_accession", lambda: (_ for _ in ()).throw(OSError("cache gone")))
    rows = attach_aliases([{"accession": MUC16, "gene": "MUC16"}])
    assert rows[0]["gene"] == "MUC16", "the row did not survive an unreadable cache"
    assert rows[0]["aliases"] is None, "an unreadable cache must read as no aliases, never as a raise"


def test_the_pinned_cache_really_holds_the_two_names_these_guards_assert():
    """⚠ The guards above would pass vacuously if the cache lost these entries and the assertions
    were written against the empty case. Named here so the instrument is checked, not assumed."""
    cache = aliases_by_accession()
    assert "CA-125" in (cache.get(MUC16) or [])
    assert "HER2" in (cache.get(ERBB2) or [])


# ───────────────────────────── the three copy fixes ─────────────────────────────


def test_the_served_geography_sentence_is_the_reason_the_page_said_it_twice():
    """⚠ The instrument for the next two assertions: the payload's own text BEGINS with the sentence
    the page used to bold ahead of it. That is the whole mechanism, and it is a property of the
    served constant rather than of the component."""
    assert US_ONLY_DISCLAIMER.startswith("United States only.")


def test_the_burden_page_never_prefixes_the_served_sentence_with_a_copy_of_itself():
    """⚠⚠ **"United States only. United States only. These are US figures…"** — measured on the live
    site 2026-09-10. Both call sites bolded a hardcoded lead-in and then printed `meta.us_only`.
    ⚠ The served string is NOT edited: `ServedQualifier` emphasises the payload's own first sentence,
    so `D-149`'s bold geography survives with one copy of the words."""
    assert "def ServedQualifier" in BURDEN_VIEW or "function ServedQualifier" in BURDEN_VIEW
    assert "export function leadSentence" in BURDEN_VIEW
    assert BURDEN_VIEW.count("<ServedQualifier") == 2, (
        "both the banner and the limits bullet must render through the one helper")
    assert "<strong>United States only.</strong>{' '}\n        {meta?.us_only" not in BURDEN_VIEW
    assert "<li><strong>United States only.</strong> {meta.us_only}</li>" not in BURDEN_VIEW


def test_the_never_folded_card_keys_its_length_claim_on_the_recorded_reason():
    """⚠⚠ `P55073`/`DIO3` IS 237 aa AND WAS TOLD IT WAS TOO LONG TO FOLD LOCALLY, one line under its
    own copy saying it *"was assigned to the local tier and should have folded"*. The unconditional
    clause is gone; the claim now rides on the reason `core/census_unfolded.py` recorded, which keeps
    `above_local_ceiling` apart from `ceiling_unmeasured` and `reason_unrecorded` on purpose."""
    assert "long by the standards of what this" not in CENSUS_PROTEIN, (
        "the unconditional length verdict is back")
    assert "not_folded_reason === 'above_local_ceiling'" in CENSUS_PROTEIN, (
        "the length clause is not keyed on the recorded reason")


def test_the_census_tranche_cell_names_its_absence_like_every_neighbour():
    """⚠ One row of 3,467 has no tranche and drew a blank cell — the only absence on that table a
    reader cannot tell from a rendering failure. ⚠ `??` and never `||`: tranche `0` is the cohort."""
    assert "<td className=\"num\">{r.tranche}</td>" not in CENSUS_TABLE, "the bare cell is back"
    assert "r.tranche ?? " in CENSUS_TABLE
    assert "r.tranche || " not in CENSUS_TABLE, (
        "`||` would print the absence copy over tranche 0, which is the cohort")


# ───────────────────────────── the machine the review killed ─────────────────────────────


def test_the_serving_machine_carries_the_headroom_the_oom_made_the_case_for():
    """⚠⚠ MEASURED KILL, PREDICTED MECHANISM, and the config says which is which. The event is
    `exit_code=137, oom_killed=true` at 2026-09-10T15:37:17Z with a reboot and a 502 on a public
    surface; what allocated the memory was never measured, and the comment must keep saying so —
    otherwise the next reader takes the bump as a diagnosis."""
    assert re.search(r'^\s*memory = "1024mb"', FLY, re.M), "the serving tier is back at 512mb"
    assert "oom_killed=true" in FLY, "the config does not name the event that moved it"
    assert "PREDICTED, NOT MEASURED" in FLY, (
        "the comment stopped distinguishing the measured kill from the unmeasured cause")


# ───────────────────────────── the living-documentation ritual ─────────────────────────────


def test_the_log_entry_exists_and_leads_with_the_defect_rather_than_the_fix():
    assert re.search(r"^### D-154 — Every UI surface walked on the live site", LOG, re.M)
    assert len(re.findall(r"^### D-154 —", LOG, re.M)) == 1, "exactly one D-154 entry"
    assert LOG.index("### D-154 —") < LOG.index("### D-152 —"), "newest first"
    entry = LOG.split("### D-154 —", 1)[1].split("\n### D-152 —", 1)[0]
    assert "0 rows" in entry, "the entry does not carry the measurement that names the defect"
    assert "oom_killed=true" in entry, "the entry does not carry the OOM event"
    assert "UNMEASURED" in entry, "the narrow-viewport residual is not stated"
    assert "predicted, not measured" in entry.lower(), (
        "the OOM mechanism must be labelled predicted — D-016 / the method note")
    assert "Deep-learning justification" in entry


def test_the_next_free_integer_is_named_and_barred_and_148_is_still_a_held_hole():
    """⚠⚠ **Bar OR name, never neither.** ``### D-154`` is claimed by name here; ``### D-148`` is a
    ``RESERVED.md`` HOLD for the trafficking Spec and stays BARRED; ``### D-155`` takes the next-free
    bar. ⚠ Nothing is relaxed to a ``>=``: a ``>=`` here would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as *data* in
    order to check the others; a newline-less match would find a "bar" in the file whose job is to
    look for one. That is D-145's recorded mistake, not rediscovered here."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 154 in ids, "this entry did not claim its own integer"
    assert 152 in ids and 153 in ids, "the entries this one builds on must still be named"
    assert 155 in ids, "D-155 spent 155 in the surface-merge ship"
    # D-156 spent 156 when it split the log into five documents: ADDED by name,
    # and `### D-157` takes the bar. Never relaxed to a `>=`.
    assert 156 in ids, "D-156 claimed this integer"
    assert 148 not in ids and 157 not in ids
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until that Spec "
        "claims it by name — never admitted by a `>=`")
    # ⚠⚠ D-155 SPENT the integer this guard barred (the surface-merge ship), so it is NAMED
    # here rather than barred and `### D-157` takes the next-free bar. A name is ADDED and
    # nothing becomes a `>=` — the widening D-145 fixed the shape of.
    assert "\n### D-155 — One population had two tables" in LOG, (
        "D-155 was spent by the surface-merge ship, so it must be NAMED here rather than barred")
    assert "\n### D-157" not in LOG, (
        "D-157 is the next free integer and must stay unspent until an entry claims it by name — "
        "never admitted by a `>=`")


def test_the_reserved_map_retires_154_marker_safe_and_the_pointer_moves_here():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: eight suites locate the
    154 row with ``re.search(r"^\\| \\*\\*D-154\\*\\*", …)``, so striking it to ``~~**D-154**~~``
    would break those guards instead of satisfying them. The D-142 / D-145 / D-150 / D-151 / D-152
    rows each record the same trap of themselves."""
    assert re.search(r"^\| \*\*D-154\*\*", RESERVED, re.M), (
        "D-154 lost its row; the citation invariant then has a hole indistinguishable from D-062's")
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-154**"))
    assert "WRITTEN" in row, "the 154 row does not record that the integer was spent"
    assert "Original reservation text" in row, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    assert re.search(r"^\| \*\*D-155\*\*", RESERVED, re.M), (
        "the bar moved to 155, so 155 must be a RESERVED row or the citation invariant has a hole")
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), "the trafficking hold lost its row"
    assert not re.search(r"^\| ~~\*\*D-15[45]\*\*~~", RESERVED, re.M), (
        "a marker is struck through; that breaks a sibling suite's lookup instead of satisfying it")
    assert "Next free `D-` integer: **`D-157`**" in RESERVED
    for spent in ("D-148", "D-149", "D-150", "D-151", "D-152", "D-153", "D-154", "D-155"):
        assert f"Next free `D-` integer: **`{spent}`**" not in RESERVED, (
            f"the pointer still names {spent}, which would hand a spent or held integer to the "
            f"next writer")


def test_the_inherited_guards_were_widened_by_adding_a_name_and_never_by_relaxing():
    """⚠⚠ The enumerated successor lists are what actually catch a collision, and they are checked
    here as *data*: each must NAME `D-154` and must bar 155 instead. A relaxation would be invisible
    in a diff that also adds a legitimate name."""
    for rel in ("tests/test_d129_phase5_named_refuse_spec.py",
                "tests/test_d130_residual_rmsd_spec.py",
                "tests/test_d152_surface_navigation.py",
                "tests/test_d153_bake_burden_loader.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "D-154 — Every UI surface walked on the live site" in text, (
            f"{rel} does not NAME the entry that spent 154")
        assert r'\n### D-157" not in' in text, f"{rel} does not bar the next free integer"
    # ⚠⚠ THE `>=` CHECK IS SCOPED TO THE TWO SPEC SUITES, AND THE SCOPE IS THE POINT.
    # `tests/test_d153_bake_burden_loader.py` performs this very check on those two files, so it
    # HOLDS the relaxation pattern as *data* — asserting the string's absence there would redden on
    # the file whose job is to look for it. That is D-145's recorded trap, obeyed rather than
    # rediscovered, and it is why this loop is not the loop above.
    for rel in ("tests/test_d129_phase5_named_refuse_spec.py",
                "tests/test_d130_residual_rmsd_spec.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "if i > 129] >=" not in text and "if i > 130] >=" not in text, (
            f"{rel} relaxed its enumeration to a `>=` — the widening must ADD a name")


def test_architecture_records_the_alias_contract_rather_than_only_the_log():
    """⚠ `ARCHITECTURE.md` is the source of truth for system shape (CLAUDE.md rule 2), and *which
    list payloads carry aliases* is a payload contract three surfaces depend on — not an entry-only
    fact. A row that names it is what stops the fourth caller from being written without it."""
    assert "attach_aliases" in ARCH, (
        "ARCHITECTURE.md does not name the alias contract the read payloads now share")
    assert "D-154" in ARCH
