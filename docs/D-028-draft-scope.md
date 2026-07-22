### D-028 — The system detects and classifies disagreement; it does not explain it
- **Date:** 2026-07-22
- **Status:** **Proposed**
- **Numbering note:** drafted as D-027, renumbered to D-028 when the Builder claimed D-026 for
  the enqueue step and the feature-set entry moved to D-027.
- **Context:** D-015 §1 asks *which disagreements are checkable against outcomes the world has
  already decided, and which are hypotheses.* D-015 §1a requires disagreement classes to be
  visually distinct. D-024 makes coverage a first-class surface.

  **None of them says what the system may claim about WHY two rankings disagree** — and the
  gap is not neutral. A comparative ranking view showing baseline rank, structural rank, and
  delta invites exactly one question from any reader, grader included: *why?* Left unruled,
  that question gets answered by whatever the UI happens to render next to the delta, and
  the most natural thing to render is the feature that moved most. **That would be a causal
  claim the system cannot support.**

  D-027's six features are *interpretable* — a disagreement can be attributed to a feature.
  **Attribution is not explanation, and the gap between them is one sentence wide in a UI.**
  *"Feature 6 accounts for most of this target's structural rank"* is a statement about the
  model, and true. *"This target ranks higher because its epitope is more accessible"* is a
  statement about biology, and the system has no standing to make it. The second is what a
  reader will write in their notes after reading the first, unless the interface is explicit
  about which one it is asserting.

- **Decision:** The system's claim is bounded at **detection and classification**.

  **In scope:**
  - **Detect** disagreement between the structural ranking and the comparator's evidence
    score — the delta, the movers, the direction.
  - **Classify** it per D-015 §1a: **class-1** (checkable against decided outcomes) or
    **class-2** (hypothesis on an axis never measured), rendered visually distinct.
  - **Attribute** it to features — which of the six moved this target, and by how much. A
    statement about the model, labelled as such.

  **Explicitly OUT of scope, as a named non-goal:**
  - Any claim about the **biological cause** of a disagreement.
  - Any ranking, scoring, or ordering of disagreements by "interestingness" or "promise" —
    which is an explanation wearing a number.
  - Any generated prose that narrates a disagreement into a mechanism.

  **A non-goal is a commitment, not an omission.** It is recorded here so that a later
  iteration adding explanation does so as a ruled change with its own entry, rather than as a
  feature that arrived because the UI had space for it.

  **This is a scope ruling, not a modesty clause.** The system is *more* defensible for
  stopping here, not less ambitious: a detected, classified, feature-attributed disagreement is
  a claim that can be checked. An explained one cannot be, at this cohort size, on this
  evidence. The boundary is drawn where the artefact's support ends — which is the same
  discipline D-016 applies to documents, applied to the product's output.

- **The quality of each disagreement class travels with the result.** Per owner's ruling, and
  in the same discipline as D-024's coverage line: the honest reading is rendered *with* the
  finding, not on a separate page a reader may not reach. Every disagreement class carries an
  inline explanation of **what that class can and cannot support**:

  | Class | What it supports | What it does not |
  |---|---|---|
  | **Class-1 — checkable** | The comparator's ranking can be tested against an outcome already decided (e.g. an approved ADC target the baseline filtered out). A disagreement here is **evidence about the comparator**. | It is a *single instance*, not a demonstrated pattern (D-015 §2's own caveat about Trop-2). |
  | **Class-2 — hypothesis** | The structural axis orders this target differently. That is a **generated hypothesis**, on an axis no one has measured against outcome. | Nothing about whether the structural ordering is *right*. There is no outcome to check it against. |

  Rendered as inline tooltips or equivalent, not as a footnote or a separate methods page.

- **A third quality note is required, and it is the one most likely to be omitted: structure
  and sequence disagree for well-understood reasons that have nothing to do with this
  project's question.** Convergent folds, divergent sequences within a family, domain
  shuffling — all produce structure/annotation divergence, and all predate this work by
  decades. A disagreement explicable by known homology relationships is **class-2 with a
  known confound**, and the UI must say so where the disagreement is shown.

  **Why this note specifically:** the headline *"structure and sequence disagree"* invites the
  response *"yes, and?"* — because that is the premise of structural biology, not a result of
  this project. The finding this project can support is narrower and therefore stronger:
  *these particular targets are ordered differently on a structural axis, here is the class of
  that difference, and here is what the class supports.* Without the confound note, the
  system's most eye-catching output is a rediscovery presented as a finding, and a reader who
  knows the field will notice — the same failure mode D-022 avoided by making MUC16's absence
  visible rather than silent.

- **Deep-learning justification:** This entry is about the boundary of the model's claim,
  which is part of understanding the model. D-015 §3 pre-registered two negative results
  precisely so the project could report a null honestly; D-027 does the same work one level
  up, by preventing the *presentation layer* from upgrading a detected difference into an
  explained one. A system that says "these disagree, here is the class, here is what the
  class supports" is making a defensible claim. One that says "these disagree because…" is
  making an indefensible one with the same data.

- **Consequences / follow-ups:**
  - **The UI Plan needs this**, alongside D-024's coverage surface. Both are Iteration-1
    scope; neither is in `docs/UI_Plan.md`, which predates both.
  - **A future "analyse disagreement" affordance is anticipated and deliberately deferred.**
    The owner's framing: an LLM with domain grounding could *suggest* why a disagreement
    exists and what axes of investigation it opens. **That is a different system making a
    different kind of claim**, and it needs: its own entry, a clear visual separation from
    the structural result, and explicit labelling as generated suggestion rather than
    finding. Recorded now so that when it is built it is built as a ruled addition — and so
    that its absence in this version is a **decision**, not an oversight.
  - **This entry constrains D-027's attribution output.** Feature attribution is in scope and
    must be rendered as a statement about the model ("feature 6 accounts for most of this
    target's structural rank"), never as a statement about the target ("this target has a
    more accessible epitope").
