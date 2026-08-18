<!-- DERIVED FILE — do not hand-edit. -->
<!-- source: KEEL-3-Quick-Reference-Card-V9.docx -->
<!-- source sha256: ade6bd7339603622fc9d3de3d5b971c5b96282dbd5be20da05bbcef59b36e1ea -->
<!-- derived by: scripts/docx_to_markdown.py -->

> ⚠ **Derived from `KEEL-3-Quick-Reference-Card-V9.docx`**, sha256 `ade6bd7339603622fc9d3de3d5b971c5b96282dbd5be20da05bbcef59b36e1ea`.
> **The `.docx` is the owner's authored master; this Markdown is the repository record.**
> ⚠⚠ Only the Markdown is committed — two formats of one document is two paths to one
> artifact (KEEL-2 V9 Step 20). Re-derive with
> `python scripts/docx_to_markdown.py <source>.docx <this file>` and compare.

---

**KEEL — Quick Card**

**Version 9**

*Lay the Keel before you build.  "All good rules were written in blood."  ·  Top to bottom. ✓ = proof — if it doesn’t happen, STOP and fix it.*

**THREE PLAYERS, and the third one is you.**

| **Player** | **Does** | **Fails by** |
|---|---|---|
| **PLANNER** | **Browser chat, sealed room. Sees only what you hand it + a PUBLIC repo you connect. Thinking.** | **Reasoning — from a stale copy, a title it never opened, a premise nobody re-derived. Fluent summaries.** |
| **BUILDER** | **Laptop tool, works as you. Sees everything. Doing.** | **Doing — mistakes are executed before anyone reads them.** |
| **YOU** | **Rulings · credentials · destructive ops · the two rituals · the decision to stop.** | **Omission. Nothing goes red.** |

Plan with one, build with the other — and you carry the seams. Build PUBLIC so the Planner can see; go private when it goes real.

**PART A — Workshop**

**1  Project + name**

**☐**  Create a Project in your AI chat. Name it. That name is THE name, everywhere.

**PROOF:**  *named Project appears, you can click in.*

**2  Repository**

**☐**  github.com → New → same name → set PUBLIC (you must choose it) → add README → Create.

**PROOF:**  *GitHub page shows your name, the word Public, + README.*

**3  Connect repo to Project**

**☐**  In the chat Project, add the GitHub repo as a source. This is why it’s public.

**PROOF:**  *ask "what files do you see?" → it lists your README back.*

**4  Local workshop**

**☐**  VS Code terminal: make Projects folder (Win: mkdir C:\Projects / Mac: mkdir -p ~/Projects). Keep OUT of OneDrive/iCloud.

**☐**  Command Palette → Git: Clone → paste repo address → pick Projects → Open.

**PROOF:**  *VS Code shows your project folder + README. THIS IS YOUR WORKSHOP.*

**5  Builder**

**☐**  Open your laptop build tool; connect it to the repo.

**PROOF:**  *Builder open, logged in, sees the repo.*

**6  Planning brain**

**☐**  Pick the mid/upper all-rounder model — not cheapest, not top specialist.

**PROOF:**  *chosen model shows as active.*

**7  Project instructions**

**☐**  Fill the Project description. Cloud = planning; repo = permanent.

**PROOF:**  *description filled; you know it’s cloud-only until saved to repo.*

**PART B — Lay the Keel**

**8  The five documents**

**☐**  Make docs/ and five named files. Name the file after the thing it holds — a README is a greeting, not a container.

| **File** | **Holds** | **Answers** |
|---|---|---|
| **architecture.md** | **Pieces, boundaries, data flow, what is deliberately absent.** | **"What am I looking at?"** |
| **decisions.md** | **D-001, D-002… in order, with the options rejected.** | **"Why is it like this?"** |
| **findings.md** | **What was measured, when, n, where the raw record is.** | **"How do we know?"** |
| **testplan.md** | **Covered · not covered & why · how each guard was proven able to fail.** | **"What would catch it if it broke?"** |
| **assumptions.md** | **A-001, A-002… what you rely on without having decided to.** | **"What are we taking for granted?"** |

**☐**  Write architecture.md’s first paragraph now, before any code.

**PROOF:**  *all five exist; you can say in one sentence what belongs in each.*

*Why named files? A reader arrives with ONE of those questions. And absence becomes visible — an empty findings.md is legible; a missing findings section is invisible.*

*assumptions.md is the fifth because the other four hold what somebody decided to write. An assumption is the thing too obvious to state. Two bars: no falsifying test, no entry; nothing breaks if false, it’s a detail. Read it when writing a decision and when something breaks — never on a schedule.*

**9  Decision log**

**☐**  One decision per entry, numbered D-001, D-002… Seven fields: decision · context · options rejected · evidence · supersedes · assumptions relied on · amended by.

**☐**  Cite by number AND name — "D-023 (the tiling design)", never a bare D-023. A checker proves a number exists; nothing proves it still means what your sentence assumed.

**PROOF:**  *write up last week’s decision → you can name what you rejected and what evidence backed it.*

*Keep it one file until it hurts — one file is one search, forty is forty. Size isn’t the problem; addressability is.*

**10  How you know → findings.md**

**☐**  Every claim names its source artefact AND its sample size. Ask for the breakdown, not the total; what’s available, not what’s on.

**☐**  Carry the n. "13 seconds" and "13 seconds, 5 of 9" are different claims.

**☐**  Two people reading one output are ONE observation. Corroboration measures agreement, not truth.

**☐**  Record the method, not just the number. Where you chose a threshold, report several — one setting is a dial wearing the costume of a measurement.

**PROOF:**  *pick a claim at random → reach the raw evidence in under a minute, and reproduce the number from what is written.*

**11  Secrets out**

**☐**  .gitignore lists .env BEFORE first commit; all keys in the platform, by name only. Wire a secret-scanner into the gate.

**☐**  After setting a secret, confirm it is APPLIED, not merely saved.

**PROOF:**  *search project → zero real keys.*

**12  Self-contained tests + testplan.md**

**☐**  Tests run isolated — no internet, no services. Add one trivial test.

**☐**  testplan.md gets two headings: Covered · Deliberately not covered, and why.

**☐**  The suite REFUSES a database whose data is not expendable — hard error, never a skip.

**PROOF:**  *tests pass in seconds with internet OFF; pointing the suite at something real stops it.*

**13  The gate**

**☐**  Auto-deploy only if tests pass; ship by MERGING. Deploy token scoped + named exactly right.

**PROOF:**  *(proven in step 14 — don’t trust yet).*

**14  PROVE the gate (never skip)**

**☐**  Push a FAILING test → watch deploy get blocked → fix → watch it ship. Record it in testplan.md.

**PROOF:**  *you SAW it block bad, allow good.*

*Every guard, not just the gate — and the proof rule has THREE clauses. A revert proof is valid only if (a) the fixture reaches the code under test, (b) each asserted property has its own test, and (c) the fixture contains a case where correct and incorrect differ. Break it with a value no correct version could produce. Then look at WHERE the red fired: an error-red is not a failure-red.*

*Check which way the guard points. What does it do when its input is missing or malformed? If it stands aside, it is not a guard. Hard error, never a skip. Override = a sentence someone must mean, not a flag they flick.*

**15  Make it BINDING**

**☐**  Branch protection on: require PR, require the check, no bypass — not even for you. Push straight to main and watch it get REFUSED.

**PROOF:**  *a failing PR reads BLOCKED, not just "red X."*

**16  Hand-deploy dies**

**☐**  Merging is the only way to ship. Manual = emergencies only.

**PROOF:**  *a merge reaches prod with no command from you.*

**GO PRIVATE — at the first of these**

**☐**  first real credential  ·  first real user data  ·  first live deploy

*Flipping to Private costs the Planner’s direct view — pre-flight reverts to handing it the close-out + a snapshot: git archive --format=tar.gz -o ‹name›-$(date +%Y%m%d).tar.gz HEAD. From then on it reasons about a copy that goes stale mid-session. Tell it when a numbered entry lands.*

**DAILY RITUALS — every session. YOUR job; nothing enforces them.**

**Post-flight (close of session)**

**☐**  AI writes a session close-out → commit it to docs/. That’s tomorrow’s baton. Uncommitted = invisible to the Planner and absent from any recovery.

**☐**  Ask: "which of the five documents changed today?" "None" is a fine answer; not asking is not. These files rot by omission.

*Never keep one chat open for days. A long session sheds its OLDEST context first — it keeps this morning’s trivia and forgets your foundational decisions, then answers fluently anyway.*

**Pre-flight (start of session)**

**☐**  New chat, not yesterday’s. Connected repo → upload nothing. Private → hand over close-out + snapshot.

**☐**  Ask for a REPORTED grounding block, not a summary: highest entry number in each log quoted from the header · open items read as output · live repo or snapshot, and what each can prove · everything changed since the last close-out, derived not listed.

**PROOF:**  *it reports those specifics before planning anything. A summary is not verification — a Planner can produce a confident, wrong one, and will.*

**PART C — When it gets big**

*Trigger: the first time an output grows past what you actually read row by row. Past that point correctness stops being observable and must become structural. Full steps 17–23 are in the Day-One Checklist; the short form:*

**☐**  Say when you crossed the line, and write down what shape "wrong" would take.

**☐**  Every absence is a category with a cause — never a zero, never a blank. Never-fetched and came-back-empty must differ.

**☐**  Reconcile BOTH directions. A one-directional check cannot see orphans.

**☐**  Two paths to one number: compare once, on purpose, record it, then collapse. Compare the numbers, not summaries of them.

**☐**  Accept an artefact by REPRODUCTION, not by label. A version string is a claim.

**☐**  Never assert absence from a stale copy. Name the artefact and its revision, or ask.

**☐**  Before you destroy anything, say what you lose: a COMPLETED backup exists · its age as exposure · what it does not cover. At the operation, never at session start.

Doctrine is compression. Keep a travelogue too — one document per project, indexed — because a one-line scar cannot tell you which part to change when the world moves.
