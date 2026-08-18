<!-- DERIVED FILE — do not hand-edit. -->
<!-- source: KEEL-1-The-Build-First-Pattern-V9.docx -->
<!-- source sha256: 84304888123d311b9f7921e3f80b25dec9570a6466ddc5d5917e5625cbad79c6 -->
<!-- derived by: scripts/docx_to_markdown.py -->

> ⚠ **Derived from `KEEL-1-The-Build-First-Pattern-V9.docx`**, sha256 `84304888123d311b9f7921e3f80b25dec9570a6466ddc5d5917e5625cbad79c6`.
> **The `.docx` is the owner's authored master; this Markdown is the repository record.**
> ⚠⚠ Only the Markdown is committed — two formats of one document is two paths to one
> artifact (KEEL-2 V9 Step 20). Re-derive with
> `python scripts/docx_to_markdown.py <source>.docx <this file>` and compare.

---

**The Build-First Pattern**

**KEEL — Version 9**

*"All good rules were written in blood."*

Lay the KEEL before you sail. The foundation discipline for building with AI — for people who have judgment and intend to use it.

The tools now let one person build what used to take a team. That is the opportunity and the trap. The speed is intoxicating, and intoxicated builders skip foundations — then discover, weeks in, that the only copy of their work can vanish, that nothing was ever tested, or that a decision made in a chat window is gone. The people who will thrive in this era are not the fastest typists. They are the ones with the discipline to insist on solid ground before they build on it. That discipline is the asset a long career gives you. We call the foundation the KEEL — the first timber laid, the spine that keeps a boat upright when the weather turns. A project without one doesn’t sail badly; it capsizes. This page is how to apply it.

**Every principle below was paid for. The line beneath each is what it cost us — not a hypothetical. A scar.**

**What changed in V9, and why it is V9 and not V7**

Two upgrade sets were written and never issued. A v7 proposal was assembled on 2026-08-05 from a single session in which eleven planning defects were caught before execution. A v8 amendment on destructive operations was written on 2026-08-17, the day a production database was destroyed and recovered. Neither reached these pages, and in the meantime half of v8 shipped as code against a doctrine that did not contain v7.

So this set is issued once, as V9, carrying both — and the fact that v7 and v8 never existed as documents is recorded here rather than back-filled. Every document in the set is stamped V9, including the two that needed no changes: an unchanged page left at V6 beside a V9 set is ambiguous between reviewed and forgotten, and that ambiguity is exactly what the rest of this doctrine exists to remove.

The substantive changes: one new principle (11) · a second clause on Principle 1 · a rewritten proof rule in Principle 6 · a fifth named document and back-references in Principle 7 · four new clauses in Principle 8 · and a closing section on specification speed. The scars behind them are dated in place.

## The one rule, if you remember nothing else

Lay the KEEL — version control, automated testing, automated deployment — BEFORE you plan a single feature, and before you start dreaming with an AI. Not after the prototype works. Not once it "gets serious." First. The foundation is a thirty-second setup on day one and a painful, error-prone retrofit on day ninety. You will never regret having it; you will always regret not having it.

## The eleven principles (each learned the hard way)

**1.**  **One canonical copy. Exactly one — and a backup you have verified.**

Every project is a version-controlled repository with an offsite copy, from the first day. No "working folder plus backup folder," no pile of dated snapshots. The place you edit is the one true place.

And the copy has to be real. Before any operation whose undo is "restore from backup" — a migration, any schema change, a bulk write or delete, creating or destroying a database, rotating a credential that could orphan access — say three things out loud, in your own words:

One: a backup exists and its status is completed. Not queued, not running. A queued backup is not a backup. Two: how old it is, phrased as exposure — "the newest completed backup is four hours old, so up to four hours of work is at risk." Three: what it does not cover. That third one is a judgement about your system, not a field in a response, which is why this is a sentence you say and not a script you run. A pre-flight tool would return "ok" and answer none of it.

Say it at the moment of the operation, never at the start of the session. A check that runs when nothing is at risk passes, and trains you to skip it. This one runs at the only moment the answer changes what you do.

**PAID FOR IN BLOOD:**  *Fourteen nearly-identical snapshot folders, no clear "real" copy — and we nearly edited a dead one. Worse: a whole working feature existed ONLY on the running server, committed nowhere. One power-cycle from gone. Years later a test suite was run with production credentials loaded and truncated the live database — 2,771 rows to 1 — and we recovered it from a backup nobody had ever verified existed. It worked. That is luck standing in for process, and luck is not a principle.*

**2.**  **Tests guard deployment. Always. From the first change.**

A broken build must be physically unable to reach production. Automatic, not a habit you rely on remembering. It costs nothing on day one and is miserable to add later.

**PAID FOR IN BLOOD:**  *For weeks, anything we pushed could reach production whether it worked or not — nothing stood in the way. One bad afternoon from shipping a broken build to the system we depend on daily.*

**3.**  **Deployment is automated, never by hand.**

Merging your approved work is what ships it — not you running a command and hoping you did it right. Manual deploy is break-glass only. A step that depends on you remembering it will eventually be forgotten.

**PAID FOR IN BLOOD:**  *We deployed by hand for weeks while the automatic deploy we thought we had sat silently broken the entire time. Nobody knew, because nothing told us.*

**4.**  **Secrets live in the platform, never in the code.**

Passwords, keys, and tokens are held by the hosting platform and referenced by name. Never in a file, never committed, never pasted into a chat. A leaked secret is a bad day; a committed one is a bad year.

**PAID FOR IN BLOOD:**  *The automatic deploy was dead for one stupid reason — a single secret saved under the wrong NAME. One typo, and the whole safety system sat there looking perfectly fine. An afternoon gone. Later, a secret updated but left Staged rather than Deployed meant the application kept its old connection string and answered every query with zero rows instead of an error — the most misleading possible response.*

**5.**  **Tests must be self-contained — no live services, no network.**

The suite brings its own isolated world and pretends every outside service is present. That is what makes testing instant, free, and trustworthy. If a test needs the real world, it is a different kind of check that runs elsewhere.

And a test suite is entitled to assume its database is disposable — because that is what makes it free to truncate, reset and rebuild. So the suite must refuse to run against a database whose data is not expendable. Those two facts must never meet.

**PAID FOR IN BLOOD:**  *Cost us nothing, for a long time — because our tests need no passwords and no internet, the whole safety system was trivial to build and runs in seconds, free, every time. Then one evening the environment file was loaded in the same shell as the test command, and a fixture that begins every test by emptying three tables did exactly that, to production.*

**6.**  **Prove the safety net works — by tripping it, once. Then prove each guard the same way.**

On day one, deliberately break something and watch the system refuse to deploy it. Then fix it and watch it ship. A safety net you have never seen catch anything is a hope, not a guarantee.

The same move applies to every individual guard you write afterwards, not just the gate: break the thing the test is watching and confirm the test goes red. A test that passes whether or not the system works is worse than no test, because it is a passing test. Where that proof lives is Principle 7 — testplan.md.

**NEW IN V9 —** The proof rule has three clauses, not one. A revert proof is valid only if (a) the fixture reaches the code under test, (b) each asserted property has its own test, and (c) the fixture contains a case on which a correct and an incorrect implementation actually differ. Break it with a value no correct version could produce — and confirm the code you are testing actually ran. Watch where the red fires, not just that it fired: an error-red and a failure-red are different objects, and only a failure-red proves the assertion executed at all.

**NEW IN V9 —** A guard has a direction, and it can point the wrong way. Ask what the guard does when its input is missing, malformed, or unexpected — because that is the case it will meet. If the answer is "it stands aside," it is not a guard. Make it a hard error, never a skip; a skip is how a dangerous thing comes to look harmless. If it has an override, make the override a sentence someone has to mean, not a flag someone can flick by habit. And write inside the guard what it does not cover, because the next person will assume it covers everything.

**PAID FOR IN BLOOD:**  *We had "tests that guard deploys" on paper before we ever watched one actually block a bad build. Later the same lesson arrived one layer down: a guard we trusted turned out to pass no matter what we broke, because the value we broke it with happened to be the answer it expected. Then five more in a single day — a revert that reddened because the module failed to import, so the assertion never ran; a fixture with no positive cases, so the code returned before reaching the function under test and the test would have passed with the guard placed anywhere; and a compound test that proved only its first failing assertion. And the guard that was supposed to stop a destructive test suite skipped unless a database was reachable — so supplying production credentials armed it. Its safety property was "you probably do not have a database," which is not a safety property.*

**7.**  **Write it down where someone would look for it — five named documents, not one README.**

A design agreed in conversation and never recorded does not exist. But recording it is only half the job: a record nobody can find is a record that doesn’t exist either. Discoverability is a property of the filename, and a README is a greeting, not a container. So the project carries named documents, and each one’s name is the whole explanation of what is inside it.

| **File** | **Holds** | **Answers** |
|---|---|---|
| **architecture.md** | **Pieces, boundaries, data flow, what is deliberately absent.** | **"What am I looking at?"** |
| **decisions.md** | **D-001, D-002… appended in order, with the options rejected.** | **"Why is it like this?"** |
| **findings.md** | **What was measured, when, n, and where the raw record is.** | **"How do we know?"** |
| **testplan.md** | **Covered · deliberately not covered & why · how each guard was proven able to fail.** | **"What would catch it if it broke?"** |
| **assumptions.md** | **A-001, A-002… what you are relying on without having decided to.** | **"What are we taking for granted?"** |

Why these, and why named? Because a reader arrives with one of those questions. Mixing them means every reader reads everything to find their part. And the emptiness is the point as much as the content: an empty findings.md is legible; a missing findings section inside a README is invisible. Named files make a gap something you can see.

The decision log is the one that earns its keep first. Give each decision a number, in the order you resolved them, and include the alternative you rejected and what forced the call — a decision without its discarded options is a fact, not a decision, and facts don’t teach anyone anything. Cite the evidence too: the experiment, the measurement, the source. A decision backed by supposition is a guess with a document number.

Version control lets you go back to the last good commit. A numbered decision log lets you go back to the last good decision. Do this for a whole project and you end up holding something you never set out to build: the complete design story, in sequence, reasoning intact. That artifact has a market value the code doesn’t. It is what you show when someone asks how you think.

**NEW IN V9 —** The fifth document, and how it stays alive. assumptions.md holds the thing that felt too obvious to state — not a decision, because nobody chose it; not a finding, because nobody measured it. It becomes visible only when it breaks, and the post-mortem sentence is always "that was correct only while…". Two strict bars keep it from becoming a register of vague unease: if you cannot state the test that would falsify it, it does not go in; and if nothing breaks when it is false, it is a detail, not an assumption. It is fed by a ritual you already have — every decision entry gains one field, "Assumptions relied on," and anything named there without a number gets one. Never review it on a schedule. Read it at exactly two moments: when writing a decision that might rely on something, and when something breaks. A cadence would be the rot.

**NEW IN V9 —** An entry points at what changed it. Every numbered entry carries an "Amended by:" line, updated when the amendment merges. Without it, a reader finds a confident entry and has no way to know that four later rulings narrowed it — and the numbers they are reading may already be withdrawn.

**NEW IN V9 —** A citation carries a name, not just a number. Write D-023 (the tiling design), never a bare D-023. A checker can prove that a cited number exists; nothing can prove it still means what the citing sentence assumed. A missing entry announces itself the moment anyone follows the reference. A number that has been reused hands the reader a real, well-formed, confident entry and lets them read it as authority for a claim it never made — and nothing objects, ever. The name makes that wrong on sight. Apply it forward; do not retrofit, because a bulk rewrite touches every citation while verifying none.

**NEW IN V9 —** Size is not the problem; addressability is. A long log is fine if you can reach any part of it without reading the rest. The failure mode is not "too big to read," it is "cannot find the thing without reading all of it." Those are different problems and only one is solved by writing less. The fix is naming, numbering, indexing and back-references. Keep the log in one file until it genuinely hurts — a single file is one search; a folder of forty is forty.

**PAID FOR IN BLOOD:**  *A decision made in a chat and never written down came back a day later as a confident, WRONG note — and sent us chasing a bug already fixed. So we started writing them down, into docs/README.md, because that is where we happened to open. It worked, for us, because we invented the convention. Nobody arriving at that repository would ever have found them. We had rebuilt the exact failure the principle was written to prevent, one directory up. And we then left it there for a further four months while the file grew to 835 KB — the scar stayed open the whole time this principle was being taught from it. Name the file after the thing it holds, and rename it the day you notice you didn’t.*

**8.**  **Every claim carries how you know it — and a summary is not knowing.**

A written record fixes a claim in place; it does not make it true. Before a number or a status goes into findings.md, name the artefact it came from — the log line, the query output, the run link. If you cannot name it, you are recording a belief. And prefer the question whose answer could disqualify you: ask what is available, not just what is on; ask for the breakdown, not the total.

Carry the sample size with the claim. "It answers in thirteen seconds" and "it answered in thirteen seconds five times out of nine" are different sentences, and only one of them survives being quoted back at you six weeks later.

**NEW IN V9 —** Independence of source is not independence of inference. Two people reading the same output and writing down the same conclusion separately are one observation, however separately they wrote it. Corroboration measures agreement, not truth — and it is most convincing exactly when it is least informative. What actually protects you is writing the expectation down before the numbers exist, so it can be falsified.

**NEW IN V9 —** A number whose method cannot be reconstructed from the record is not a measurement. If the prose says one thing and the arithmetic did another, you have published something nobody can reproduce, including you. And where a choice was made — a threshold, a tolerance, a filter, a rule for perturbing something — report the answer at several settings rather than one. A single setting is a dial wearing the costume of a measurement.

**NEW IN V9 —** You cannot assert absence from a stale copy. A snapshot is a positive record: it can support "this existed at that revision" and can never support "this does not exist." Presence is stable; absence decays the instant anyone commits. So any claim that something is unwritten, missing or not yet done either goes in as a question, or names the artefact and its timestamp — "absent as of that revision; confirm against live." Phrased that way it refutes itself when it goes stale. A bare assertion does not.

**NEW IN V9 —** Accept an artefact by reproduction, not by label. A version string, a filename and a file date are all claims. Where a known-good subset of the thing exists — a published extract, a prior result, a figure someone else computed — acceptance is reproducing that subset exactly. And be most suspicious of the well-formed answer: an empty result from a mismatched key, a zero from a stale connection, a 405 read as a 404. In every one of those the wrong answer arrives correctly formatted, and nothing objects.

**PAID FOR IN BLOOD:**  *Three claims reversed in one afternoon — every one already written down, every one true as stated and wrong in what it implied. "All parameters on the GPU" was true, and missed that the model had spilled past physical memory. "217 hardware errors" was true, and missed that only four were fatal. Later, two people independently pre-registered the same wrong expectation from one line of shared output and called it corroboration. Later still, a published flip rate could not be reproduced under any of five candidate rules — including the one its own prose appeared to describe — by the person who had, the same day, twice required someone else to fix exactly that.*

**9.**  **A failing check nobody is forced to obey is decoration.**

The gate stops the deploy. Only branch protection stops the human. Require the check, require a pull request, and allow no bypass — not even for you, the owner. Without that, a red X is a suggestion.

The same shape has a second form worth watching for: a check placed where its answer cannot change what you do. It fires downstream of the decision it was meant to inform, passes, and teaches everyone to scroll past it. A check nobody reads is a decoration that costs attention.

**PAID FOR IN BLOOD:**  *Our first deliberately-broken pull request showed a red X and sat there perfectly mergeable. The gate had worked exactly as designed and blocked nothing, because nothing obliged anyone to care. We turned on protection and watched the same PR flip to BLOCKED. Two different mechanisms. You need both.*

**10.**  **Build in the open. Go private when it goes real.**

Your Builder logs in as you and reads a private repository fine. Your Planner cannot — it can only connect directly to a repository that is PUBLIC. So the repository is public while you build, connected to your Planner, and it goes private once the project is production-stable. The concrete tripwires, whichever comes first: the first real credential, the first real user data, or the first live deploy. The price of public is that nothing secret ever goes in a file — which is Principle 4, now structurally enforced instead of merely intended.

And know what you give up when you flip it. Once the Planner works from a hand-carried snapshot, it is reasoning about a copy that stops being true the moment anyone commits — including during the session it is reading. Tell it when a numbered entry lands. One line costs nothing; the alternative is a planner confidently describing a document that was written two hours ago.

**PAID FOR IN BLOOD:**  *We spent weeks hand-carrying dated archives of our own code into the planning chat every morning, because we’d assumed private was simply the responsible default and never asked what it cost. It cost us our Planner’s eyes. Going public deleted the ritual and an entire class of "the AI is working from a stale copy" bugs — in one setting change. After we went private again, that class came straight back: the Planner asserted four times in one session that a design document was unwritten. It had been written that morning, by the Builder, and the Builder had said so twice.*

**11.**  **Past the point a human will look, correctness stops being observable.**

At eighty rows you can read the output and see whether it is right. At three thousand nobody ever will, and from that point on the question is no longer "is this right?" but "what shape would wrong take, and would anything go red?"

This is the principle that governs everything you build at scale, and it is the hardest one to feel, because nothing announces it. The defects that survive are not the ones that crash. They are the ones that produce an artefact with the right shape, the right provenance, the right date, and a plausible number in it. Plausibility, not error, is the failure mode.

So a count that cannot be checked by looking must be checked by a guard that fails. Reconcile totals in both directions rather than one. Make every absence a category with a cause, never a zero and never a blank — an unfetched row and a row with nothing in it must not carry the same value. Where the same quantity is computed in two places, compare them once, on purpose, and record the comparison; two paths to one number that are never compared is the most reliable defect there is.

**PAID FOR IN BLOOD:**  *Eleven defects caught in a single day of planning, every one of which would have produced a dated, hashed, provenanced, confidently wrong artifact: a coverage report reading "no topology" for 2,807 proteins, a table silently doubled in two generations, one family weighted 83-fold in every statistic, and a pre-registered result firing its expected outcome for the wrong reason because a null had been coerced to zero. Every one was visible at eighty rows and invisible at three thousand. And a year’s worth of a model’s own confidence output was discarded for a month by a path that only ran on rented hardware — nothing errored, nothing warned, no number was wrong, and we found it only because a different question happened to need the data.*

## Three players, and the part only you can do

There are three of you on this project, not two, and the third one is you. Each fails in a different way, and knowing which failure you are looking at is most of knowing what to do about it.

The Builder fails by doing. It acts on what it is handed, quickly, and its mistakes are executed before anyone reads them. The Planner fails by reasoning — from a copy that went stale an hour ago, from a title it never opened, from a premise it inherited three messages back and nobody re-derived. Its mistakes arrive as fluent summaries, which is what makes them hard to catch: a wrong plan and a right plan look identical until someone checks a number.

You fail by omission. Not doing something, and nothing goes red. There is no gate for it, no test, no red X — which is why the two rituals in the field manual are the only part of this whole discipline enforced by nothing but you.

That is not an accident of tooling; it is structural. Neither AI can close a session, because neither has a clock and neither knows the day ended. Neither can rule on a judgement call, because the call is yours to be wrong about. Neither can rotate a credential, destroy a cluster, or decide that a result is good enough to stop. Continuity lives in the gap between sessions, and the gap is the one place both of them cannot reach.

So the balance is: they carry the work, and you carry the seams. When you are short of time, the seams are what you drop, because dropping them costs nothing today.

**PAID FOR IN BLOOD:**  *One session was allowed to run for a week rather than closed each day, when circumstances made the time hard to find. Nothing visibly broke — and then we went and looked. Nine documents dated the sixth and seventh of the month landed in the repository on the sixteenth, including the ruled vocabulary that decides which proteins the entire project is about. For nine days the single most load-bearing rule in the system existed only in a chat window and on one laptop, invisible to the planner and to any recovery. Nothing was lost. So either that was luck, or something is sitting in the application undetected — and from the inside those two look exactly alike. A conversation that long also sheds its oldest context first: the foundational decisions go, this morning’s trivia stays, and what it produces afterwards is fluent, confident, and quietly unmoored from what it has forgotten. "No damage" is not a finding here; it is the absence of one. The day you are too busy to close the session properly is precisely the day the close-out was worth writing.*

## The move that makes it stick with AI

The temptation to skip the Keel is strongest at exactly the instant you start planning with an AI — planning is the fun part, and the foundation feels like a detour between you and it. Willpower loses that fight, so do not rely on it. Move the enforcement earlier than the temptation.

Make starting correctly take thirty seconds — a template or script that lays the whole Keel in one step, including the five empty documents with their headings already in place, so beginning the right way is easier than beginning the wrong way. And give the AI a standing instruction: before we design anything, confirm the foundation exists — and if it doesn’t, stop and build it first. You turn the very thing that tempts you to skip the foundation into the thing that guards it.

## Speed belongs in execution, not specification

The tools make writing a specification almost free, and that is a trap with no warning attached. Planning documents produced faster than the code they describe do not get compared to anything. They accumulate, they cross-reference each other, and the defects hide in the seams between them.

Two rules, both cheap. Where a specification names a producer and a consumer, it names the contract test between them in the same document, or it specifies neither — proximity is not comparison, and two halves of an interface described on one page have still never been checked against each other. And where it names a stopping point, it names the mechanism that stops: "stop when the guard passes" is a sentence, not an instruction, and after the fix that same command is the thing being stopped.

This one indicts the planner rather than the builder, which is why it belongs in the doctrine and not in a project log. The rest of these pages govern the person doing the work thoroughly and the person directing it barely at all.

**PAID FOR IN BLOOD:**  *Twenty specification documents in a day against a typical three or four — and the defect rate tracked the volume of specification written ahead of the code, not the diligence of the review. An output schema and its consumer were specified in the same document and never compared. A stopping instruction, followed faithfully, would have run the exact thing the day was sequenced to protect.*

## Keep the travelogue as well as the doctrine

These pages are compression, and compression discards the evidence. Each blood line is one sentence — the surviving residue of an episode that took days. That compression is what makes the principles usable, and it is also what makes them impossible to re-derive. When a principle stops matching the world, a one-line scar cannot tell you which part to change. The full episode can.

So keep a running account of what actually happened, one document per project, indexed — not a single growing file, which is this doctrine’s own Principle 7 failure at a larger scale. It preserves three things the doctrine has no room for: which principles keep getting paid for, the near-misses where nothing was written and here is the artifact that would have been, and the scars that turned out to be local and never generalised.

Doctrine is only as good as the vividness of its scars, and scars fade. Someone reading "prove the safety net by tripping it" five years from now has a rule. Someone reading the episode where a guard passed against every value it was broken with has the reason, and can re-derive the rule when the tooling changes underneath it.

## Why this is ours to teach

None of this is about being a programmer. It is about refusing to build on sand, insisting on ground truth before action, and writing down your reasoning so it outlives the moment — judgment, in other words. A long working life is where judgment comes from, and the tools have finally caught up to the people who have it. Lay the Keel first. Then go build the thing you have been waiting your whole career to build.
