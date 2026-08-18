<!-- DERIVED FILE — do not hand-edit. -->
<!-- source: KEEL-2-The-Day-One-Checklist-V9.docx -->
<!-- source sha256: 3488d44ac569f14da2571874886e4470f25079e28e3e4e37a74700bed7ea0f1b -->
<!-- derived by: scripts/docx_to_markdown.py -->

> ⚠ **Derived from `KEEL-2-The-Day-One-Checklist-V9.docx`**, sha256 `3488d44ac569f14da2571874886e4470f25079e28e3e4e37a74700bed7ea0f1b`.
> **The `.docx` is the owner's authored master; this Markdown is the repository record.**
> ⚠⚠ Only the Markdown is committed — two formats of one document is two paths to one
> artifact (KEEL-2 V9 Step 20). Re-derive with
> `python scripts/docx_to_markdown.py <source>.docx <this file>` and compare.

---

**KEEL — The Day-One Checklist**

**Version 9**

*"All good rules were written in blood."*

How to lay the Keel on a new project — the field manual for The Build-First Pattern.

This is how you lay the Keel. The companion page, The Build-First Pattern, is the why. The Keel is your foundation — version control, tests, automated deploy, and the five documents that hold your reasoning — laid before you build anything on top. Do these in order, push the buttons, check each proof before moving on.

## How to run this

•  Do the steps in order, top to bottom. Don’t jump ahead. Don’t skip.

•  Every step ends with PROOF — how you know it worked. If the proof doesn’t happen, STOP on that step and fix it before going on. A skipped foundation step is invisible until it hurts, and by then it’s expensive.

•  Wherever you see ‹Project Name›, use the exact same name, same spelling, every single time.

•  You don’t have to understand every word. Your AI Builder can run any command — paste the step, say "do this," check the proof.

•  Parts A and B are day one. Part C is not — it is the section you come back to when the project outgrows what you can check by eye. Its trigger is written at the top of it.

## First, understand this — there are THREE of you

You will work with two different AIs, and they see your project through completely different windows. Confusing them is the #1 beginner mistake. But there are three players on this project, not two, and the third one is you — with a job neither AI can do.

| **Player** | **What it does** | **How it fails** |
|---|---|---|
| **The Planner** | **Browser chat. Sealed room — sees only what you hand it, plus a public repository you connect. Architecture, plans, catching the mistake you are about to make.** | **By reasoning. From a stale copy, a title it never opened, a premise nobody re-derived. Its mistakes arrive as fluent summaries.** |
| **The Builder** | **Laptop tool. Works as you — sees your files, your repository, your live system. Writes code, runs tests, ships.** | **By doing. It acts on what it is handed, fast, and its mistakes are executed before anyone reads them.** |
| **You** | **Rulings, credentials, destructive operations, the two daily rituals, and the decision to stop.** | **By omission. Not doing something — and nothing goes red.** |

The whole discipline in one line: you PLAN with the Planner (distance, can’t build), then hand the plan to the Builder (can build, shouldn’t plan). Thinking happens in the sealed room where nobody types too soon. Building happens in the trenches. Neither can do the other’s job — that’s the point.

And neither can do yours, which is structural rather than a gap in the tooling. Neither AI can close a session, because neither has a clock and neither knows the day ended. Neither can rule on a judgement call, because the call is yours to be wrong about. Neither can rotate a credential, destroy a database, or decide a result is good enough to stop. Continuity lives in the gap between sessions, and the gap is the one place both of them cannot reach.

They carry the work. You carry the seams. When you are short of time, the seams are what you drop — because dropping them costs nothing today.

***Burn this in — the visibility rule.***  *Your BUILDER reads a private repository fine; it logs in as you. Your PLANNER cannot. The Planner can only connect directly to a repository that is PUBLIC. So you build in the open — public repository, connected to your Project — and you go private once the project is production-stable. Public while you build. Private when it goes real. The tripwires, whichever comes first: the first real credential, the first real user data, or the first live deploy. The price of public is that nothing secret ever goes in a file, from the very first commit.*

## PART A — Set up the workshop

**Step 1 — Start the Project and name it**

**☐**  Go to your AI chat website and create a new Project (not just a chat — a Project).

**☐**  Name it. This name is now THE name. Write it on paper. Every ‹Project Name› below means this.

**PROOF:**  *your named Project appears in the list, and you can click into it.*

**Step 2 — Create the online home (the repository)**

**☐**  Go to github.com and sign in (free account if needed).

**☐**  Click the green New button to make a new repository.

**☐**  Repository name: your ‹Project Name› — exact same name, same spelling as Step 1.

**☐**  Set it to PUBLIC. You have to choose this — Private is the default. Your Planner can only connect to a public repository, and that connection is what makes every day after this one cheap.

**☐**  Check "Add a README file." Click Create repository.

**PROOF:**  *you’re looking at a GitHub page showing your ‹Project Name›, the word Public beside it, and a README file.*

***Public feels wrong. Read this once.***  *Public does not mean careless — it means the discipline is now enforced by the world instead of by your memory. There is nothing to protect yet: no credentials, no user data, no live system. You go private the moment any of those three appears. And the alternative is not "safer" — it is a Planner that cannot see your code, which you then compensate for by hand, every single morning, forever.*

**Step 3 — Connect the repository to your Project**

**☐**  In your chat Project, find the option to add a GitHub repository (it may sit under "project knowledge," "sources," or "connect").

**☐**  Connect the ‹Project Name› repository you just made.

**PROOF:**  *ask the Planner "what files do you see in my repository?" and it lists your README back to you. It is now looking at your real code, not your description of it.*

**PAID FOR IN BLOOD:**  *We spent weeks packaging our own code into a dated archive and uploading it by hand every morning — because we assumed private was the responsible default and never asked what it cost. It cost us the Planner’s eyes, plus a folder of near-identical archives and a steady drip of "the AI is working from a stale copy" bugs. One setting deleted all of it.*

**Step 4 — Build your local workshop**

**☐**  Open VS Code, then Terminal → New Terminal.

**☐**  Make your Projects folder — Windows: mkdir C:\Projects   ·   Mac: mkdir -p ~/Projects

**☐**  Keep projects OUT of any cloud-synced folder (OneDrive, iCloud Desktop/Documents). Cloud sync fights git and hides files.

**☐**  Command Palette (Ctrl/Cmd+Shift+P) → Git: Clone → paste your repository address → choose your Projects folder → Open. The clone makes the ‹Project Name› folder; don’t pre-make it yourself.

**PROOF:**  *VS Code shows your ‹Project Name› folder with README.md inside Projects, connected to your online repository. THIS IS YOUR WORKSHOP.*

**Step 5 — Open your Builder**

**☐**  Open your AI building tool and connect it to your GitHub account and the ‹Project Name› repository.

**PROOF:**  *the Builder is open, logged in, and can see your repository.*

**Step 6 — Choose your planning brain**

**☐**  Pick a strong all-rounder — mid-to-upper tier. Every provider offers a ladder: fast-cheap at the bottom, heavyweight specialist at the top, all-rounder in the middle. Pick the middle.

**PROOF:**  *the tool shows your chosen model as active.*

**Step 7 — Fill in the Project instructions**

**☐**  Write a few plain sentences on what this project is.

**☐**  Burn this in: everything typed there — instructions AND any documents the AI creates in the Project — lives ONLY in the cloud. Cloud Project = planning space. Repository = permanent record. Anything that must survive gets saved into one of the five documents in Step 8.

**PROOF:**  *your Project has a description, and you understand it’s cloud-only until saved into the repo.*

## PART B — Lay the Keel (before you build a single feature)

**Step 8 — Create the five documents (the reasoning half of the foundation)**

Tests and deploy protect your code. These five protect your thinking — and they are the half people skip, because nothing goes red when they’re missing.

**☐**  In your repository, create a folder called docs/.

**☐**  Inside it create five files, each with its headings already in place, even though they’re empty:

| **File** | **Holds** | **Answers** |
|---|---|---|
| **architecture.md** | **Pieces, boundaries, data flow, what is deliberately absent.** | **"What am I looking at?"** |
| **decisions.md** | **D-001, D-002… in order, each with the options rejected.** | **"Why is it like this?"** |
| **findings.md** | **What was measured, when, n, and where the raw record is.** | **"How do we know?"** |
| **testplan.md** | **Covered · deliberately not covered & why · how each guard was proven able to fail.** | **"What would catch it if it broke?"** |
| **assumptions.md** | **A-001, A-002… what you are relying on without having decided to.** | **"What are we taking for granted?"** |

**☐**  Write the first paragraph of architecture.md now, before any code exists. It will be wrong within a week. Updating it is the job.

**PROOF:**  *all five files exist in docs/, each with a heading, and you can say in one sentence what belongs in each. If two of them could hold the same note, reread the table.*

***Why named files instead of one README with sections?***  *Because a reader arrives with one of those questions, and sections inside a general-purpose file mean reading everything to find your part. And because absence becomes visible: an empty findings.md is legible; a missing findings section is invisible. Named files turn a gap into something you can see without already knowing to look for it.*

***Why assumptions.md is the fifth.***  *The other four hold things somebody decided to write. An assumption is by definition the thing that felt too obvious to state — not a decision, because nobody chose it; not a finding, because nobody measured it. It becomes visible only when it breaks, and the sentence is always "that was correct only while…". Two strict bars keep it from becoming a register of vague unease: if you cannot state the test that would falsify it, it does not go in; and if nothing breaks when it is false, it is a detail. Never review it on a schedule — read it when writing a decision that might rely on something, and when something breaks. A cadence would be the rot.*

**PAID FOR IN BLOOD:**  *We wrote our decisions down faithfully — into docs/README.md, because that’s the file that was already there. It worked, for us, because we invented the convention and we remembered it. Nobody else could have found them. A record nobody can find is a record that doesn’t exist — the exact failure we’d written the principle to prevent, rebuilt one directory up. And we then left it there for four more months while the file grew past 800 KB. Name the file after the thing it holds, and rename it the day you notice you didn’t.*

**Step 9 — Set up the decision log properly**

**☐**  One decision per entry, numbered in the order you resolve them: D-001, D-002, D-003.

**☐**  Have your Builder put a template at the top of decisions.md, so every entry carries:

•  The decision — what you chose, in one sentence.

•  The context — what question forced it, and what you knew at the time.

•  The options rejected — the real alternatives, not strawmen. This is the field that makes the log recoverable.

•  The evidence — the experiment, measurement, or source. A decision backed by supposition is a guess with a document number.

•  Supersedes — the earlier D-number this overturns, if any.

•  Assumptions relied on — anything the decision takes for granted. Whatever you name here without a number gets one in assumptions.md. That is how the register stays alive: it is a by-product of writing decisions, not a ritual of its own.

•  Amended by — added later, when something changes this entry. Without it, a reader finds a confident entry and no way to know four later rulings narrowed it.

**☐**  Cite entries by number AND name — "D-023 (the tiling design)", never a bare D-023. A checker can prove a number exists; nothing can prove it still means what your sentence assumed.

**PROOF:**  *pick a decision you made last week and write it up. You can name what you rejected, why, and what evidence backed it. If you can only name what you chose, you recorded an outcome, not a decision.*

***Keep it one file until it hurts.***  *Your Planner takes decisions.md in a single pass; a folder of forty files is worse for exactly the reader you built it for — and one file is one search, where forty is forty. Split into docs/decisions/ only when the one file genuinely becomes unwieldy, and then decisions.md becomes the index. Size is not the problem; addressability is. The failure mode is not "too big to read," it is "cannot find the thing without reading all of it," and the fix for that is naming, numbering and back-references, not brevity.*

**Step 10 — Write down HOW you know, not just what you concluded**

**☐**  At the top of findings.md, state the rule: every claim records the artefact it came from — the log line, the query, the run link — and its sample size.

**☐**  Carry the n. "It answers in 13 seconds" and "13 seconds, 5 times out of 9" are different claims.

**☐**  Prefer the question that could disqualify you. Ask what is available, not just what is on. Ask for the breakdown, not the total.

**☐**  When your AI reports a result, ask "what would I have to look at to see that myself?" If it can’t point at something, the result is a guess wearing a number.

**☐**  Two people agreeing is not two observations if they read the same output. Independence of source is not independence of inference — and corroboration is most convincing exactly when it is least informative. What protects you is writing the expectation down before the numbers exist.

**☐**  Record the method, not just the number. If nobody can reconstruct how a figure was produced from what you wrote, it is not a measurement. Where you chose a threshold or a tolerance, report the answer at several settings — a single setting is a dial wearing the costume of a measurement.

**PROOF:**  *pick any claim in findings.md at random. You can reach the raw evidence in under a minute, say how many observations it rests on, and reproduce the number from what is written. If you can’t, it was never a finding.*

**PAID FOR IN BLOOD:**  *We reversed three confidently-written claims in a single afternoon. Not one was a lie — each was a true summary that hid the thing that mattered. The counts were right and the severity was missing. The parameters were on the GPU and the memory had already overflowed. A summary is where the disqualifying detail goes to die. Years later, a published rate could not be reproduced under any of five candidate rules — including the one its own prose appeared to describe.*

**Step 11 — Lock secrets out of the code**

**☐**  Create .gitignore BEFORE your first real commit. Make sure it lists .env and any file holding secrets.

**☐**  Put every password, key, and token in your hosting platform’s secrets area. In documents, refer to a secret by NAME only, never by value.

**☐**  Add an automatic secret-scanner to your gate so a commit carrying a key is refused the same way a failing test is.

**☐**  After you set or change a secret, confirm it is actually applied, not merely saved. A staged-but-not-deployed secret leaves the old value live.

**PROOF:**  *search your whole project for a real password or key. You find NONE.*

**PAID FOR IN BLOOD:**  *One secret saved under the wrong NAME silently broke our entire deployment for an afternoon. Everything looked fine. It wasn’t. Later, a secret updated but left staged rather than deployed meant the application kept its old connection string and answered every query with zero rows instead of an error — the most misleading possible response.*

**Step 12 — Self-contained tests, and the plan that says what they cover**

**☐**  Set up the test framework so tests run in their own isolated world — no internet, no real services, no passwords required.

**☐**  Write one tiny throwaway test so the machinery exists and runs.

**☐**  Open testplan.md and write two headings you will keep filling in forever: Covered, and Deliberately not covered, and why. The second is what makes it a plan.

**☐**  Make the suite REFUSE to run against a database whose data is not expendable — a hard error, not a skip. A test suite is entitled to assume it can empty its own tables; that is what makes it free. So it must never be pointed at anything real.

**PROOF:**  *tests pass in seconds with your internet OFF; testplan.md names one thing you chose not to test, with the reason; and pointing the suite at a real database stops it with an error rather than a skip.*

**PAID FOR IN BLOOD:**  *The one we got RIGHT early: because our tests need nothing from the outside world, the whole safety system was trivial to build and runs free, in seconds. Then one evening the environment file was loaded in the same shell as the test command, and a fixture that begins every test by emptying three tables did exactly that — to production. 2,771 rows to 1.*

**Step 13 — Build the gate**

**☐**  Set up automatic deployment with a hard rule: work ships only if tests pass first, and shipping happens by merging — not by running a command.

**☐**  Create the deploy credential scoped to deploy only. Save it under the EXACT name the config expects — a mismatched name is the #1 silent failure.

**PROOF:**  *comes in Step 14. Do not trust the gate yet. Prove it.*

**Step 14 — PROVE the gate works (never skip this)**

**☐**  Deliberately write a test that FAILS. Push it on a branch.

**☐**  Watch the system REFUSE to deploy it. (If it ships anyway, your gate is fake — go back to Step 13.)

**☐**  Fix the test so it passes. Merge it. Watch it deploy.

**☐**  Record it in testplan.md: what you broke, and that you watched the gate catch it.

**PROOF:**  *you have watched, with your own eyes, the gate BLOCK a bad build and ALLOW a good one — and testplan.md says so.*

***Do this for every guard, not just the gate — and the proof rule has three clauses.***  *Break the thing the test watches and confirm it goes red. A revert proof is valid only if (a) the fixture actually reaches the code under test, (b) each asserted property has its own test, and (c) the fixture contains a case on which a correct and an incorrect implementation differ. Break it with a value no correct version could produce. Then look at WHERE the red fired: an error-red and a failure-red are different objects, and only a failure-red proves the assertion ran at all.*

***And check which way your guard points.***  *Ask what the guard does when its input is missing, malformed, or unexpected — because that is the case it will meet. If the answer is "it stands aside," it is not a guard. Hard error, never a skip. If it has an override, make it a sentence someone has to mean, not a flag someone flicks by habit. And write inside the guard what it does not cover.*

**PAID FOR IN BLOOD:**  *We had "tests that guard deploys" on paper before we ever watched one stop a bad build. Later a guard we trusted turned out to pass no matter what we broke, because the value we broke it with happened to be the answer it expected. Then five more in one day — including a fixture with no positive cases, so the code returned before reaching the function under test and the test would have passed with the guard placed anywhere.*

**Step 15 — Make the check BINDING**

**☐**  Turn on branch protection for main: require a pull request, require the test check, allow no bypass — including for you, the owner.

**☐**  Try to push directly to main. Watch it get REFUSED.

**☐**  Look at a pull request with a failing check. It must read BLOCKED, not merely "has a red X."

**PROOF:**  *you tried to push straight to main and the system said no — to you, the owner, with full permissions.*

**PAID FOR IN BLOOD:**  *We proved our gate by breaking a test on purpose, and it worked — the deploy was skipped. Then we looked closer: the pull request still showed as perfectly mergeable. A red X and a green Merge button, side by side. One tired evening from clicking straight through our own safety system.*

**Step 16 — Stop deploying by hand, forever**

**☐**  Kill any habit or note that says "run the deploy command after changes."

**☐**  From now on: merging approved work is the only way things ship. Manual deploy is break-glass only.

**PROOF:**  *you make a real change, merge it, and it reaches production WITHOUT you running any deploy command.*

**PAID FOR IN BLOOD:**  *We typed the deploy command by hand for WEEKS while the automatic one sat silently broken. Nobody knew, because nothing told us.*

## The Keel is laid

**☐**  Every PROOF above happened. If any didn’t, go back to that step — never sail on a cracked keel.

**☐**  All five documents exist and at least two have real content already.

**☐**  Only now do you start planning your first real feature.

## WHEN TO GO PRIVATE

You built in the open so your Planner could see your work. That trade stops paying the moment the project becomes real. Flip to Private at the first of these, whichever comes first:

**☐**  The first real credential — any key, token, or password touching a real account.

**☐**  The first real user data — anyone’s information but your own test rows.

**☐**  The first live deploy — the moment something you’d be upset to lose is running for real.

What changes: your Planner loses direct sight of the repository, and the Opening Ritual reverts to handing it your close-out and a snapshot by hand. Know what that costs. From then on the Planner reasons about a copy that stops being true the moment anyone commits — including during the session it is reading. So tell it when a numbered entry lands, in one line. The alternative is a Planner confidently describing a document that was written two hours ago.

**PROOF:**  *the repo reads Private, and your next planning session starts by handing the Planner the close-out yourself.*

## THE DAILY RITUALS — and they are YOUR job

The most worthwhile projects take days or weeks. The hardest part isn’t any single day — it’s picking the work back up without losing the thread. These two rituals are how. Run them like pre-flight and post-flight checks.

And they are the part of this whole discipline that nothing enforces. There is no gate for them, no test, no red X. Neither AI can run them — neither has a clock, neither knows the day ended. If they happen, it is because you did them.

**Why you do NOT keep one chat open for days**

The tempting mistake: you did good work in a chat, the AI "knows" your project now, and starting fresh tomorrow feels like throwing that away. So you keep the same session alive, afraid to close it.

That fear is backwards. Every AI has limited memory for a single conversation. A session running for days doesn’t preserve context — it quietly sheds the oldest parts first, forgetting your foundational decisions while keeping this morning’s trivia. It gets slower and dumber as it bloats. And your entire project history is trapped in one chat log you’re afraid to close.

The truth that sets you free: your continuity does not live in the conversation. It lives in the repository. The chat is a disposable scratchpad. The five documents, the code, and your close-out notes are permanent. Because the durable state is in the repo, you can close every chat with zero fear and start fresh every day.

**PAID FOR IN BLOOD:**  *One session was allowed to run for a week rather than closed each day, when circumstances made the time hard to find. Nothing visibly broke — and then we went and looked. Nine documents dated the sixth and seventh of the month landed in the repository on the sixteenth, including the ruled vocabulary that decides which proteins the entire project is about. For nine days the single most load-bearing rule in the system existed only in a chat window and on one laptop, invisible to the Planner and to any recovery. Nothing was lost. So either that was luck, or something is sitting in the application undetected — and from the inside those two look exactly alike. "No damage" is not a finding; it is the absence of one.*

**The Closing Ritual — end of every work session (post-flight)**

**☐**  Ask your AI to write a session close-out: what got done today, what’s still open, what’s next.

**☐**  Then ask: "which of the five documents changed today?" Decision → decisions.md. Measured → findings.md. Shape changed → architecture.md. Guard added or proven → testplan.md. Assumption registered or broken → assumptions.md. "None" is a fine answer; not asking is not.

**☐**  Commit all of it.

**PROOF:**  *the close-out is in the repo, and you can name which documents changed today or say plainly that none did. This is the baton you hand to tomorrow.*

***This ritual is load-bearing.***  *Anything you have NOT committed is invisible to the Planner and absent from any recovery. Uncommitted work might as well not exist. Commit the close-out, or tomorrow starts blind.*

**The Opening Ritual — start of every work session (pre-flight)**

**☐**  Start a brand-new chat. Do NOT reopen yesterday’s.

**☐**  If your repository is connected: upload nothing. If it is private: hand over the close-out and a fresh snapshot.

**☐**  Ask the Planner for a grounding block it must REPORT, not a summary it can narrate: the highest entry number in each log, quoted from the header itself · the open-items list, read as output · whether it is working from a live repository or a hand-carried snapshot, and what each can and cannot prove · and everything that changed since the last close-out, derived rather than listed.

**PROOF:**  *the AI reports those specifics back before it plans anything — not a fluent paragraph about where you are, but the actual numbers it will be reasoning from. A summary is not verification. A Planner can produce a confident, wrong summary, and it will.*

## PART C — When the project gets big

***When to run this, and it is not day one.***  *Come back here the first time an output grows past what you will actually read row by row. That threshold is not about the size of the codebase — it is about the size of the thing you are checking. Eighty rows you inspect. Three thousand nobody ever will, and from that moment correctness stops being observable and has to become structural. Every step below exists because a defect survived that transition looking exactly like a correct result.*

**Step 17 — Know that you crossed the line, and say so**

**☐**  Name the artefact you have stopped reading row by row. Write it in architecture.md with the date.

**☐**  For that artefact, stop asking "is this right?" and start asking "what shape would wrong take, and would anything go red?" Write the answer down.

**PROOF:**  *you can name the artefact, the date you crossed the line, and at least one specific way it could be wrong that nothing currently catches.*

**PAID FOR IN BLOOD:**  *Eleven defects caught in a single day of planning, every one of which would have produced a dated, hashed, provenanced, confidently wrong artifact. Every one was visible at eighty rows and invisible at three thousand. Plausibility, not error, is the failure mode at scale.*

**Step 18 — Every absence is a category with a cause**

**☐**  Never write a zero or a blank where you mean "we don’t have this." Give it a named category and a reason.

**☐**  Make sure a row that was never fetched and a row that was fetched and came back empty carry DIFFERENT values. They are different facts and they need different fixes.

**☐**  Check that no default quietly asserts the safe answer. A branch that labels anything unrecognised as the benign case is how a system states something nobody measured.

**PROOF:**  *pick any empty-looking cell in your data. It tells you WHY it is empty, and you can name a different empty cell with a different reason.*

**PAID FOR IN BLOOD:**  *A band called "no topology" turned out to mean five different things, only one of which was "this has no topology." And a badge’s final branch labelled everything unrecognised as the benign case, so four distinct failure states all rendered as fine.*

**Step 19 — Reconcile both directions**

**☐**  Whenever two sets should match, count the misses BOTH ways: things in A missing from B, and things in B missing from A.

**☐**  Report both numbers even when one is zero. A one-directional check cannot see orphans.

**PROOF:**  *you can state both miss-counts for your main data set, and the two together account for every row.*

**PAID FOR IN BLOOD:**  *"79 pointers resolve" and "79 files exist" are the same number and different claims. Only counting both directions turned it into a bijection with no orphans — and only then was it worth writing down.*

**Step 20 — Two paths to one number, compared once, on purpose**

**☐**  Find every quantity your system computes or writes down in more than one place. There will be more than you expect.

**☐**  For each, compare the two paths once, deliberately, and record the comparison. Then collapse to one path — in a separate commit, so the removal is visible in review.

**☐**  Compare the actual numbers, not summaries of them. Two percentages rounding to the same value is not agreement.

**PROOF:**  *you can point at a recorded comparison for at least one duplicated quantity, and say which path survived.*

**PAID FOR IN BLOOD:**  *A deck stated "79 of 82 folded" on two slides and "80 folded" on a third. Both were true — of different quantities. Two hand-typed numbers for one thing, in one artifact, disagreeing. Having two paths is not the defect; having two and never comparing them is.*

**Step 21 — Accept an artefact by reproduction, not by label**

**☐**  When you take in a file or a dataset, do not accept it on its filename, its version string, or its date. Those are claims.

**☐**  Find a known-good subset — a published extract, a prior result, a number someone else computed — and reproduce it exactly. That is the acceptance test.

**☐**  Be most suspicious of the well-formed wrong answer: an empty result from a mismatched key, a zero from a stale connection, a "method not allowed" read as "not found." Nothing objects to any of them.

**PROOF:**  *for your most important incoming data, you can name the subset you reproduced and the exact count that matched.*

**PAID FOR IN BLOOD:**  *Five wrong files arrived in one day, every one real, well-formed, correctly-schema’d data from the right organisation. Row counts and column names caught them. What finally settled it was reproducing a published extract to the row — a version label is a claim; a reproduction is a measurement.*

**Step 22 — Never assert absence from a stale copy**

**☐**  If your Planner works from a snapshot, treat it as a positive record only. It can support "this existed at that revision." It can never support "this does not exist."

**☐**  Phrase every absence claim so it refutes itself when stale: "absent as of ‹revision›; confirm against live." A bare assertion does not.

**☐**  Have the Builder report the number and title of any numbered entry it lands, in the message where it lands it. Drift accumulates during the session, not only before it.

**PROOF:**  *search your last planning session for the words "there is no" or "hasn’t been written." Every one either names an artefact and a revision, or is a question.*

**PAID FOR IN BLOOD:**  *A Planner asserted four times in one session that a design document was unwritten, including in the closing recommendations. It had been written that morning by the Builder — who had said so twice, and been read as making a numbering error, because the claim conflicted with a premise nobody was examining.*

**Step 23 — Before you destroy anything, say what you lose**

**☐**  Before a migration, any schema change, a bulk write or delete, creating or destroying a database, or rotating a credential that could orphan access — say three things out loud, in your own words.

•  A backup exists and its status is completed. Not queued, not running. A queued backup is not a backup.

•  How old it is, phrased as exposure: "the newest completed backup is four hours old, so up to four hours of work is at risk."

•  What it does not cover. This one is a judgement about your system, not a field in a response — which is why you say it and do not script it.

**☐**  Say it at the moment of the operation, never at the start of the session. A check that runs when nothing is at risk passes, and trains you to skip it.

**PROOF:**  *the last destructive thing you did has those three sentences written next to it, before the fact.*

**PAID FOR IN BLOOD:**  *A production database was destroyed and recovered from a backup nobody had ever verified existed. It worked. That is luck standing in for process, and this step converts one half of it. It does not make the luck retrospective.*

Keep this manual. Lay the Keel once per project (Parts A and B). Run the Daily Rituals every session, forever. Come back to Part C when the project outgrows your eyes. It never costs more than the time it saves.
