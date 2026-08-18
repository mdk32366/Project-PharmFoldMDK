<!-- DERIVED FILE — do not hand-edit. -->
<!-- source: KEEL-4-The-Assumption-Register-V9.docx -->
<!-- source sha256: 5c5912958dd3ba3bbce882b8d728e9d77ce4bba1269dd5995709a25c491c367f -->
<!-- derived by: scripts/docx_to_markdown.py -->

> ⚠ **Derived from `KEEL-4-The-Assumption-Register-V9.docx`**, sha256 `5c5912958dd3ba3bbce882b8d728e9d77ce4bba1269dd5995709a25c491c367f`.
> **The `.docx` is the owner's authored master; this Markdown is the repository record.**
> ⚠⚠ Only the Markdown is committed — two formats of one document is two paths to one
> artifact (KEEL-2 V9 Step 20). Re-derive with
> `python scripts/docx_to_markdown.py <source>.docx <this file>` and compare.

---

**KEEL — The Assumption Register**

**Version 9**

*The fifth named document — what you are relying on without having decided to.*

This was proposed against v5, re-proposed against v6, and ruled for the first time in V9. It is adopted as a document and a field on the decision log — deliberately not as a principle, for the reason in section 3.

**PAID FOR IN BLOOD:**  *While it sat unruled, three assumption numbers were assigned locally by a project that needed them and had never received this page. They are cited in shipped code and in test docstrings, and they resolve to nothing. A document that exists only as a proposal is a document whose numbering has already started without it.*

## 1. The gap this fills, stated precisely

The other four documents route the assumptions somebody thought to examine. A decision tests one, a finding records the result, the survivors become the premises your technical designs get built on. That pipeline is sound and it works.

It has no home for the assumption nobody thought about. Every stage of that flow is triggered by an act of authorship — someone decides, someone measures, someone writes a guard. An assumption is by definition the thing that felt too obvious to state, so it enters no stage and appears in no file. It is not a decision, because nobody chose it. Not a finding, because nobody measured it. Not a rejected option, because it was never on the table.

It becomes visible only when it breaks, and the post-mortem sentence is always the same: "that was correct only while…"

## 2. Why a fifth named document

Principle 7 asks why four, and why those four — because they answer four different questions, and a reader arrives with one. The fifth is a fifth question:

| **Document** | **The question it answers** |
|---|---|
| **architecture.md** | **"What am I looking at?"** |
| **decisions.md** | **"Why is it like this?"** |
| **findings.md** | **"How do we know?"** |
| **testplan.md** | **"What would catch it if it broke?"** |
| **assumptions.md** | **"What are we taking for granted?"** |

None of the other four answers it. architecture.md names what is deliberately absent — the absences you chose. testplan.md names what you deliberately do not cover — again, chosen. Neither has a place for what you are relying on without having decided to.

And Principle 7’s other half applies unchanged: an empty assumptions.md is legible; a missing assumptions section is invisible. A gap you can see is the entire reason for naming files after what they hold.

## 3. Why it is NOT a principle — the ruling, and the reasoning

The earlier proposal asked for this to become a numbered principle. V9 declines, and takes the eleventh principle for something else: past the point a human will look, correctness stops being observable.

The reason is the register’s own strongest argument, turned around. It survives because it is a by-product of a ritual that already exists — you write a decision, you name what it relies on, and the register fills itself. That is a mechanism, and mechanisms belong in the field manual, not in the list of things you believe. A principle it would have to be remembered; a field on a template gets filled in because the template has a field.

The distinction matters in practice: a register kept by conviction lasts about three weeks. A register kept by a form lasts as long as the form does.

## 4. The entry, and the two bars

### A-NNN — <the assumption, as a falsifiable proposition>

- Registered: YYYY-MM-DD        - Status: ASSUMED | HELD | BROKE | GUARDED | RETIRED
- Relied on by: <the D-/F- entries, files, surfaces that depend on it>    <- blast radius
- What breaks if false: <a number, a route, a claim — concretely>
- The test: <what falsifies it, and what it costs>
- Guard: <the assertion that makes it structural, or "none — hand-checked">

Two bars, both strict, and both exist to stop this becoming a register of vague unease.

If you cannot state the test that would falsify it, it does not go in. An unfalsifiable belief is a claim, and claims already have a home in findings.md, where they carry their n. A register of unease accumulates faster than anyone reads it and dilutes the real entries.

If nothing breaks when it is false, it is a detail. "Relied on by" coming back empty is a rejection, not a blank field.

Cite an entry by number AND name — A-007 (every feature row carries six features), never a bare A-007. Numbers get reused and reassigned; the name makes a wrong citation wrong on sight, and this namespace has already been renumbered once.

## 5. How it stays alive — fed by rituals you already have

The four documents rot by omission, and a fifth needing its own ceremony would be kept for three weeks and then quietly stop. A stale register is worse than none, because it looks like coverage. So it is fed by what already happens:

**1.**  Every decision entry carries an "Assumptions relied on" field. Naming an assumption becomes part of writing a decision — the act that already occurs. Anything named there without a number gets one. The register is a by-product of the decision log.

**2.**  Every finding that records a break asks: which assumption was this? Register it retroactively and mark it BROKE.

**3.**  The post-flight question extends by one word — "which of the FIVE documents changed today?" Assumption registered or resolved, it goes here. "None" stays a fine answer; not asking is not.

**4.**  Never reviewed on a schedule. Read at exactly two moments: when writing a decision that might rely on something, and when something breaks. A cadence would be the rot.

## 6. The score, and how to read it honestly

The register keeps a running tally of assumptions that broke when finally tested. That is a calibration instrument for your own confidence — what "carry the n" does for claims, applied to premises.

One project’s seed: seventeen registered, twelve tested, twelve broke.

That is survivorship and must be labelled as such wherever it appears. An assumption that holds quietly is never written down, so every retroactive row is drawn from the ones that failed. The denominator is unknown and unknowable backwards. The score becomes calibration only forward, once assumptions are registered before they are tested — which is why a register starts rather than being reconstructed.

What twelve-of-twelve does establish, with no denominator: when that project finally tested a load-bearing assumption, it broke. Twelve times. Enough to justify the instrument, and not enough to justify a percentage.

**PAID FOR IN BLOOD:**  *A refit was correct only while every feature row carried exactly six features — an invariant nothing asserted, and nothing would have said otherwise until the numbers came out wrong. Nine more were catalogued in one project: a field named analysis_id that held one only on success; a metric assumed to lead that turned out to be anti-correlated with the thing it predicted; a duplication documented in a code comment and left live for weeks, because writing it down felt like handling it. Every one was found late, by accident, or by someone going looking. None was found by a test — because the thing you never stated is the thing you never wrote a guard for.*

## 7. Starting one on a project already underway

You cannot reconstruct the register backwards, and you should not try. What you can do is seed it from the breaks you already know about, marked BROKE, with the survivorship caveat attached — then register forward from today.

The first entries will feel too obvious to write. That is the correct feeling and it is the whole point: the assumption that feels worth registering has usually already been examined by something else.
