"""The extracellular SEGMENT topology behind a census span, as a joinable fact — `D-147`.

⚠⚠ **WHAT THIS MODULE EXISTS TO SAY: `span_aa` IS THE LARGEST EXTRACELLULAR SEGMENT, NOT THE
EXTRACELLULAR CONTENT** (`F-037`). `core/span_extract.extract()` keeps the longest accepted
topological domain and discards every other one. For a single-pass receptor that is the whole
ectodomain and the two are the same number. **For a multi-pass protein it is one loop out of
several**, and 1,649 of the 3,467 census proteins are in that second case.

⚠⚠ **AND WHY IT EXISTS SEPARATELY FROM `core/census_structural.py`, WHICH IS THE INTERESTING
PART.** That module's `formula_version()` is a **sha256 of its own source bytes** (`D-027`'s
pattern): *"a run persisted under a formula that has since changed is then detectable rather than
silent."* Putting a display category in there would have moved `formula_version` from
**`c859da97f73d`** — the value the **live** `census_structural_runs` id=1 recorded on
2026-09-09 — for a change that alters no arithmetic. **A detector that fires on a comment is a
detector its readers learn to ignore**, which is the failure `core/derived_freshness.py` records
against `mtime` one layer down. So the formula file does not move, and *that* is checkable: the
`D-145` / `D-146` sha256 pins on `core/census_structural.py` stay **green** through this entry.

⚠ **A SEPARATE SUPPLIER, THE `census_profile_read.py` / `census_cost_read.py` SHAPE.** The formula
imports nothing from here, and the only thing imported from it is `CENSUS_MANIFEST` — **a path, so
that the freshness check and the rank are stamped against one population rather than two spellings
of it.** No score, factor, flag or constant of the formula's is read. `structural_score()` never
sees a topology, so there is exactly **one** code path that can emit `ecd_intermittent` and nothing
for a second one to drift against.

═══════════════════════════════════════════════════════════════════════════════
THE THREE WORDS, AND WHY THEY ARE THREE AND NOT TWO
═══════════════════════════════════════════════════════════════════════════════

    contiguous            one accepted extracellular segment; the span IS the ectodomain
    intermittent          more than one; the span is the LARGEST of them
    no_accepted_segment   none — GPI-anchored and similar architectures

⚠⚠ **`no_accepted_segment` IS NOT A DEGENERATE `intermittent` AND POOLING THEM WOULD BE A FALSE
CLAIM ABOUT 125 PROTEINS.** UniProt records **no topological domains for GPI-anchored proteins by
design** (`F-025`, per `D-133 am. 1`'s correction of the standing `D-081` citation): the whole
mature chain is outward-facing, held on by a lipid anchor rather than by crossing the membrane. In
the Census legend's own words the absence is *"not missing data, and not an intermittent surface."*
They take their own word and earn **no flag**.

═══════════════════════════════════════════════════════════════════════════════
IT IS A CATEGORY, NOT A FACTOR — AND NOT A TRAFFICKING CLAIM
═══════════════════════════════════════════════════════════════════════════════

⚠⚠ **`ecd_intermittent` ENTERS NO SCORE.** `score_ecd` is `min(1.0, span_aa / 200)` before and
after this module exists, and no row's `structural_score` or `rank` moves because it is flagged.
The disclosure is the deliverable; a penalty would be a suitability judgement nobody ruled.

⚠⚠ **AND IT IS NOT INTERNALIZATION.** A multi-loop extracellular topology says nothing about
whether an antibody bound to the protein would be taken into the cell.
`core.census_structural.EXCLUDED_FACTORS` already records `internalization` as *"never measured by
this project for any protein"*, and that stays exactly true. The two sentences ride in the same
payload deliberately, because *multi-loop surface* is the phrase a reader is most likely to hear
as a trafficking statement.
"""

from __future__ import annotations

import csv
import functools
import pathlib
from dataclasses import dataclass
from typing import Any, Optional

#: The population the derivation must be stamped against. ⚠ Imported rather than retyped — one
#: path, one population. It is the **only** thing this module takes from the formula, and it is a
#: path rather than any part of the arithmetic.
from core.census_structural import CENSUS_MANIFEST

_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: The derived artifact, and it is the **same one** `/api/census` and `/api/census/{id}` have read
#: since `F-037` — joined, never copied. A second derivation of *"is this span one loop of
#: several"* would be a second answer waiting to disagree with the census card.
SPAN_SEGMENTS = _ROOT / "data" / "census" / "span_segments.csv"

#: ⚠ The freshness stamp beside it. `scripts/span_segments.py` writes the **manifest's content
#: hash** here, so a manifest revision cannot leave the topology quietly describing a population
#: that is no longer on disk.
SPAN_SEGMENTS_PROVENANCE = _ROOT / "data" / "census" / "span_segments.provenance.json"

#: The three topology words `scripts/span_segments.py` writes. ⚠ Named here so the producer and
#: the consumer cannot come to spell one category two ways (`F-027`).
TOPOLOGY_CONTIGUOUS = "contiguous"
TOPOLOGY_INTERMITTENT = "intermittent"
TOPOLOGY_NO_ACCEPTED_SEGMENT = "no_accepted_segment"
TOPOLOGIES = (TOPOLOGY_CONTIGUOUS, TOPOLOGY_INTERMITTENT, TOPOLOGY_NO_ACCEPTED_SEGMENT)

#: What a row's `topology` reads when the derivation is FRESH and holds no entry for it.
#: ⚠ Distinct from a freshness verdict: *nobody derived this* and *it was derived against another
#: manifest* have different causes and different fixes.
TOPOLOGY_UNKNOWN = "unknown"

#: The flag. ⚠ Deliberately NOT declared in `core/census_structural.py`: its
#: `test_every_flag_is_a_stated_category_with_a_meaning` pairs that module's `FLAG_*` names against
#: its own `FLAG_MEANING`, and a flag this module owns belongs in this module's mapping. The served
#: `formula.flag_meaning` is the UNION of the two, and a test asserts every flag that can reach a
#: row has an entry there.
FLAG_ECD_INTERMITTENT = "ecd_intermittent"

FLAG_MEANING = {
    FLAG_ECD_INTERMITTENT: (
        "the extracellular part of this protein arrives in MORE THAN ONE segment (a multi-loop "
        "ECD), and span_aa is the LARGEST of those segments — not the extracellular total "
        "(F-037). segment_count, extracellular_total_aa and discarded_aa on this row say how many "
        "segments there are and how much extracellular material is outside the structure we hold. "
        "⚠⚠ IT DOES NOT ENTER structural_score: score_ecd is min(1.0, span_aa / 200) before and "
        "after this flag existed, and no row's score or rank moves because it is flagged (D-147). "
        "⚠⚠ IT IS NOT INTERNALIZATION and implies nothing about trafficking — internalization is "
        "named in formula.excluded_factors as never measured by this project for any protein, and "
        "a multi-loop surface is a statement about TOPOLOGY only. ⚠ It is also not "
        "no_accepted_segment: a GPI-anchored protein has no topological domains BY DESIGN and is a "
        "different architecture, not a degenerate case of this one."
    ),
}

#: ⚠ The Census table's own sentence (`ui/src/components/CensusTable.jsx` `TOPOLOGY_LEGEND`),
#: reused rather than reworded. The GO asked for the Census language; two surfaces defining one
#: word differently is the drift `D-133 am. 1` extracted `topologyBadgeKey` to prevent.
CENSUS_LEGEND_SENTENCE = (
    "the outward-facing part arrives in n separate segments. Only the LARGEST of them was folded; "
    "the others were left out, and the row says how many amino acids that was."
)


@dataclass(frozen=True)
class SegmentFacts:
    """One protein's extracellular segment structure, as `scripts/span_segments.py` derived it.

    ⚠ Every count is `Optional[int]` and **`0` is a measurement, not an absence**:
    `segment_count = 0` is what `no_accepted_segment` means, and `discarded_aa = 0` is what
    `contiguous` means. Coercing either to `None` would report a derived fact as a missing one.
    """

    topology: str
    segment_count: Optional[int]
    extracellular_total_aa: Optional[int]
    discarded_aa: Optional[int]
    segments: Optional[str]


@dataclass(frozen=True)
class SegmentJoin:
    """The join, plus **the freshness verdict it was read under**.

    ⚠⚠ THE VERDICT TRAVELS WITH THE DATA RATHER THAN BESIDE IT. `core/derived_freshness.py` exists
    because a derived artifact whose source moved does not fail, warn or change — it goes on
    answering about a manifest that is no longer there, and **a wrong topology is worse than a
    missing one, because a missing one is visible.** A stale derivation is therefore DROPPED here,
    the verdict is what a surface reports, and no flag is emitted from data this module could not
    trust.
    """

    verdict: str
    note: str
    facts: dict[str, SegmentFacts]

    def topology_for(self, accession: str) -> str:
        """The word for one accession — or the honest absence, which is **two** absences.

        ⚠ `unknown` means *the derivation is current and holds no row for this protein*; anything
        else is the freshness verdict itself. This is `app.reads.census_projection`'s rule over
        the same artifact, read rather than reinvented.
        """
        found = self.facts.get(accession)
        if found is not None:
            return found.topology
        from core.derived_freshness import FRESH

        return TOPOLOGY_UNKNOWN if self.verdict == FRESH else self.verdict

    def flags_for(self, accession: str) -> tuple[str, ...]:
        """`(FLAG_ECD_INTERMITTENT,)` for a multi-segment ECD, `()` for everything else.

        ⚠⚠ `intermittent` AND NOTHING ELSE. `contiguous` earns no flag because there is nothing to
        disclose, and `no_accepted_segment` earns none because it is a **different architecture** —
        pooling those 125 rows in would inflate the count by exactly 125 and assert a multi-loop
        surface for proteins UniProt records no topological domains for by design. ⚠ An absent or
        stale derivation flags nothing: this module does not guess a topology it could not read.
        """
        found = self.facts.get(accession)
        if found is None or found.topology != TOPOLOGY_INTERMITTENT:
            return ()
        return (FLAG_ECD_INTERMITTENT,)


@functools.lru_cache(maxsize=1)
def segment_join(path: Any = None, manifest: Any = None) -> SegmentJoin:
    """Read `span_segments.csv`, **freshness-checked against the manifest**, into one join.

    ⚠ An absent CSV, a missing or unreadable provenance stamp, and a stale derivation all yield an
    **empty** `facts` map carrying the verdict — never partial data, and never the old values. A
    consumer then serves the verdict and no flag, which is a stated category rather than a silent
    `contiguous`.

    ⚠ Cached, because the caller is a read route over 3,467 rows and a per-request CSV parse would
    make the join's cost a function of the population on every fetch.
    """
    from core.derived_freshness import FRESH, check

    segments_path = pathlib.Path(path or SPAN_SEGMENTS)
    manifest_path = pathlib.Path(manifest or CENSUS_MANIFEST)
    # ⚠ The stamp is derived FROM the CSV's own path when one is passed, so a fixture cannot be
    # checked against the committed artifact's provenance and read as fresh.
    provenance = (SPAN_SEGMENTS_PROVENANCE if path is None
                  else segments_path.parent / f"{segments_path.stem}.provenance.json")
    verdict, note = check(provenance, manifest_path)

    facts: dict[str, SegmentFacts] = {}
    if verdict == FRESH and segments_path.is_file():
        with segments_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                acc = (row.get("census_accession") or "").strip().upper()
                topology = (row.get("topology") or "").strip()
                # ⚠ A row with no accession or no topology word is SKIPPED, not defaulted: the
                # absence of a category is not the `contiguous` category.
                if not acc or not topology:
                    continue
                facts[acc] = SegmentFacts(
                    topology=topology,
                    segment_count=whole_number(row.get("segment_count")),
                    extracellular_total_aa=whole_number(row.get("extracellular_total_aa")),
                    discarded_aa=whole_number(row.get("discarded_aa")),
                    segments=(row.get("segments") or "").strip() or None,
                )
    return SegmentJoin(verdict=verdict, note=note, facts=facts)


def whole_number(value: Any) -> Optional[int]:
    """A NON-NEGATIVE whole number, or `None`.

    ⚠⚠ `core.census_structural._whole_residues`' sibling, and **the difference is why it exists**:
    that one refuses `0` because a 0 aa *span* measures nothing. These are **counts**, and `0` is a
    derived fact — `segment_count = 0` for a GPI row, `discarded_aa = 0` for a contiguous one.
    Coercing them to `None` would make a measured zero indistinguishable from a blank cell.

    ⚠ `bool` is refused explicitly: `isinstance(True, int)` is `True` in Python, so a truthiness
    flag reaching this field would otherwise count as one segment.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        return int(value) if value >= 0 and value.is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        return int(text) if text.isdigit() else None
    return None
