### D-069 — Every surface is self-sufficient: what a reader needs to understand what they are looking at is on the surface they are looking at

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Type:** A principle. **It names a pattern the project has already been following inconsistently**
  and makes it enforceable rather than remembered.
- **Relates:** D-024 (the denominator travels with the claim), D-055 + its amendment (terms decodable
  in situ, not on another page), D-062 (caveat (b) renders with the result), D-068 (a score never
  renders without its distribution context), D-050 (derived, never hardcoded).

---

**Context.** Three separate decisions have independently ruled the same thing: a number needs its
denominator beside it, a term needs its definition beside it, a result needs its caveat beside it.
**Each was ruled as a local fix. They are one rule**, and stating it once prevents the fourth
instance from being argued from scratch.

The immediate case: F-005's finding — that the ordering is carried by the model's confidence rather
than by geometry, and that this is ambiguous — is currently stated on the Scorer surface. **But a
reader forms their impression of it on the target page**, seeing the same pattern target after
target. **The explanation must be where the impression is formed.**

---

#### Decision (1) — the rule

**A reader must be able to understand what they are looking at without leaving the surface they are
on.** Every rendered number carries its denominator and its scale; every rendered claim carries its
boundary; every term of art is decodable in place.

**A surface that requires navigation to be understood is incomplete**, regardless of whether the
missing piece exists elsewhere in the app.

#### Decision (2) — ⚠ self-sufficiency is implemented as SHARED COMPONENTS, never duplicated prose

**This is the trap, and it is the one this project has been bitten by repeatedly.**

If F-005's ambiguity note is written once on Scorer and again on TargetView, **there are now two
copies of one claim, and they will drift.** That is *two paths to one quantity* — seven instances
recorded — **applied to prose instead of data**, and prose drift is harder to detect because no test
naturally compares two sentences.

**Ruled: a claim that appears on more than one surface is a component, not a string.** One source,
rendered in many places, changed in one. **A claim boundary duplicated as literal text in two
components is a defect** — the same class as a hardcoded denominator (D-050).

#### Decision (3) — self-sufficiency is LAYERED, so it does not fight readability

**The obvious objection: if everything must be on-surface, copy grows without bound and D-056's
readability ceiling breaks.** Story is already at FK 12.12 against a 12.5 ceiling.

**Resolved by layering, not by volume:**

- **Body copy carries the claim and its boundary, short.**
- **Tooltips carry the depth** — definitions, derivations, the F-005 ambiguity in full.

**Self-sufficiency means the reader never has to navigate away. It does not mean every word is in
the body.** The D-055 amendment already established the mechanism; this entry states why it is
required rather than merely preferred.

#### Decision (4) — what this promotes from deferred to required

- **⚠ The glossary copy sweep across the unscanned surfaces (11 prose-bearing, ~9 effective) is no
  longer optional.** A surface carrying undefined terms is not self-sufficient by definition.
  **Still post-freeze, but no longer discretionary** — it now has a principle behind it rather than
  a preference.
- **⚠ The `.term-def` overflow fix becomes load-bearing.** A definition that opens off the right
  edge of a narrow viewport **is not decodable in place**, which means the surface is not
  self-sufficient for that reader. **This upgrades the fix from cosmetic to principle-critical.**
- **Every surface rendering a cohort or result number must render its denominator** — D-024
  generalised beyond the coverage line.

#### Decision (5) — what this does NOT license

- **Not more claims.** Self-sufficiency is about making existing claims understandable, **not about
  saying more.** Every claim boundary in D-028, D-041 and D-062 stands unchanged.
- **Not duplicated numbers.** Numbers stay derived (D-050). A denominator rendered on two surfaces
  is computed twice from one endpoint, never typed twice.
- **Not a freeze-day sweep.** Applied **incrementally, per surface, as each is touched.** Attempting
  it everywhere at once would be exactly the scope creep the freeze exists to prevent.

---

- **Deep-learning justification.** The project's central claim is that the system is **visible about
  what it cannot do.** Visibility that requires navigation is not visibility — a reader who does not
  click does not see the bound, and forms an impression the system knows to be unsupported. **This
  entry is what makes the honesty claim operational rather than aspirational**, and it applies most
  sharply to F-005, whose finding is ambiguous in a way a casual reader will not infer unaided.

- **Consequences / test surface:**
  - **A claim rendered on two surfaces is a shared component** — asserted by absence of the
    duplicate literal in the second component.
  - **Every surface rendering a score, percentile or cohort count renders its denominator or scale**
    — asserted per surface as each is touched.
  - **Readability measured per surface after each application**, against D-056's ceiling. **If a
    surface breaches, depth moves to tooltips — the claim boundary is never the thing shortened.**
  - **Applied incrementally.** This entry does not itself change any surface; it governs the ones
    that follow, beginning with D-068.
