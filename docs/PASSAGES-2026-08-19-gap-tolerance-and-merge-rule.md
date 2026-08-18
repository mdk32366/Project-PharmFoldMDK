# PASSAGES — 2026-08-19 — the gap-tolerance clause and the merge-rule counterfactual

> **Why this file exists.** Two passages were transmitted three times through the chat channel and
> corrupted three times, always in the same place. ⚠⚠ **The third transmission carried a `sha256` to
> make corruption detectable — and the checksum itself was truncated from 64 hex characters to 58,
> so it certified nothing.** The declared byte count caught what the hash could not.
>
> ⚠ **A declared length is a cheaper integrity check than a hash when the channel eats the hash.**
> That is worth carrying forward on its own; it is the same family as `F-047`.
>
> **The repository has never dropped a byte, so the content lives here.** It arrives with the next
> snapshot rather than through the lossy channel. `D-095 amendment 1` may quote it from this file.

---

## Passage 3 — the gap-tolerance clause (item 6's third leg)

Gap tolerance is zero uncovered residues (`start <= prev_end + 1`: adjacent joins, one uncovered
residue splits). State the number, not the expression.

### The same rule restated in fresh short lines, because the sentence above has died three times

**The shipped merge rule joins two domain intervals when they overlap OR when they abut.**

**Abut means no residue lies between them.** `100-200` and `201-300` become one run of 201 aa.

**One uncovered residue is enough to split.** `100-200` and `202-300` stay two runs, because
residue 201 belongs to no domain.

**So the gap tolerance is ZERO uncovered residues.**

⚠ **Record the number `0`, not the expression `start <= prev_end + 1`.** The `+ 1` is an artifact of
inclusive coordinates and reads as a tolerance of one residue. It is not one. **A reader who copies
the expression into a different coordinate convention gets a different rule.**

⚠⚠ **This is measured, not asserted:** `tests/test_tranche6_straddle_rules.py::test_merge_rules_disagree_on_abutment`
pins both halves — the abutting pair joins, and the pair with one uncovered residue does not.

---

## Passage 2 — the merge-rule counterfactual

`merge_rule` manufactures the problem the document exists to solve. It needs its own numbered
decision with the counterfactual stated, or the amendment's headline — *135 tile at gaps, 6 need one
cut* — is a construction presented as an observation, which is the `275`-residue shape one level up.

### The counterfactual it must carry, from the 2×3 on the 141

| merge rule | rows needing a cut | FAT1 runs |
|---|---|---|
| abutting OR overlapping (**shipped**) | **6** | 9 |
| overlapping ONLY | **0** | 39 |

⚠ **Zero under all three straddle rules.** The six rows needing a cut, the `run_interior` value,
and `tile_max_aa` as a spend decision all exist *because abutment is joined*.

⚠ **The shipped rule is still the right one** — the abutment IS the phenomenon, and a rule that does
not join abutting intervals cannot see a cadherin stack at all. **But it is a CHOICE, and the design
document must say so rather than inherit it.**

⚠ **And overlapping-ONLY does not remove the cut, it relabels it.** The 141 are past context *by
span*, so tiles are required under every merge rule. Under overlapping-ONLY FAT1's cuts land at
abutting boundaries — `35-149 | 150-257`, a gap of zero residues — and get filed as `gap` or
`domain_boundary` rather than `run_interior`. **The molecule is severed identically and the artifact
stops saying so.** Under `D-094` the `run_interior` disclosure is a mount precondition, so
overlapping-ONLY would extinguish the precondition while leaving the hazard where it was.
