# BRIEFING COPY — "About ADCs" surface

> **This file is the single source of the briefing copy.** The UI renders it; it is not
> re-typed into components. Changing a claim here is a copy change with the same review
> weight as a code change, because **D-028 lives in the wording**.
>
> **Governing constraints, all of which shaped the text below:**
> - **D-028** — the system describes the model, never the target. The briefing must not
>   *supply* a biological claim the Scorer surface would then appear to confirm.
> - **UI_Plan_v2 §7.1** — keep the guided-munition metaphor; it is mechanism, not decoration.
> - **UI_Plan_v2 §7.2** — bound the outcome claims.
> - **F-005** (confidence confound), **F-012** (single-chain / oligomer), plus the glycan and
>   threshold limitations — disclosed in §7, owned in full by the Limitations page.
> - **Owner ruling, 2026-08-17** — one merged glossary, hyperlinked, with tooltips, dual-audience.
>   Every **bolded term** below is a glossary link. Glossary data: `glossary.json`.
>
> **Reading level: 8th grade, by owner request.** Every domain term is defined on first use
> *and* carries a glossary tooltip. Long words are not avoided — they are explained.
>
> **⚠ Open question for the owner:** does this file need its own `D-` entry, or is it execution
> of UI_Plan_v2 §7 plus the standing glossary ruling? The Planner's read is the latter, but §6
> and §7 contain copywriting rulings, and a ruling that lives only in a content file is a ruling
> nobody will find in the log.

---

## Operation: Precision Strike

### 1. The problem

Chemotherapy works, and it works bluntly.

Most chemo drugs go after cells that divide quickly. Cancer cells divide quickly — but so do the
cells lining your stomach, the cells in your bone marrow, and the cells at the roots of your hair.
The drug cannot tell them apart. That is why chemotherapy causes nausea, weakened immunity, and hair
loss: **the treatment's reach does not match the disease's shape.**

Think of it as an area weapon. It covers the target, and it covers everything around the target.

### 2. The idea

An **antibody-drug conjugate**, or **ADC**, is built on a different plan: carry a poison so strong
you could never inject it on its own, but attach it to something that only lets go at the right
address.

An ADC has three parts.

| Part | What it does | The analogy |
|---|---|---|
| **Antibody** | Finds and grips one specific protein | Guidance |
| **Linker** | Holds the poison on tight in the bloodstream, releases it inside the cell | Fuse |
| **Payload** | Kills the cell | Warhead |

A guided munition instead of an area weapon. That is a real change in how the drug is delivered, and
the analogy is accurate about it.

**But be careful what the analogy promises.** It describes *delivery*. It does not promise a cure,
and it does not promise the treatment is gentle. Approved ADCs have real side effects, including
serious ones. Better aim is not the same as no damage — and some of the hardest problems in the
field come from the aim being imperfect in ways nobody can see in advance.

### 3. What the antibody actually grabs

Here is the part that most explanations skip, and it is the part this whole tool exists because of.

An antibody is shaped like the letter **Y**. The two tips at the top are its hands. Both hands are
identical, and both grab the same one thing. The formal name for one arm is the **Fab**; the stem at
the bottom is the **Fc**, which is a handle for other parts of your immune system, not a grabber.

Each hand is built from two pieces pressed together — one called **VH**, one called **VL**. Think
thumb and fingers: two separate parts that only grip well as a pair. Across the very tips of those
two pieces sit six small loops. Those loops are the actual points of contact. They are called
**CDR** loops, or **hypervariable** loops, and the word *variable* is the important one: most of an
antibody is mass-produced and identical from one to the next, but these six loops differ wildly.
That variation is how your body makes billions of different antibodies for billions of different
targets.

All six loops together form one gripping surface, called the **paratope**.

Now the thing being grabbed. A protein is a long chain of small parts called **residues**, strung
together like beads on a necklace. But the necklace does not stay stretched out. It folds into a
specific crumpled shape and holds it.

**Try this.** Take a long strip of paper and write the letters A through Z along it, spread out.
Now crumple the strip into a tight ball. Look at the outside of the ball: the letter C might be
sitting right next to Q, which is sitting right next to W. On the flat strip those letters were
nowhere near each other. Crumpled, they touch.

That small cluster on the outside of the ball is what the antibody's hand grabs. It is called the
**epitope** — the patch on the target that the paratope grips. Paratope and epitope are a pair: one
is the hand, one is the handhold.

Roughly **nine out of ten** real epitopes work this way. They are built from residues that are far
apart on the flat strip and only come together once it folds. These are called **conformational
epitopes**. The other kind, **linear epitopes**, are made of residues already side by side in the
sequence.

**This is why structure matters at all.** If antibodies gripped stretches of the flat strip, you
could read the sequence and be done. They don't. You have to know how it crumples.

Two more things about the grip:

It is **not** a key going into a lock. There is no hole. It is closer to two hands pressing palms
together — two bumpy surfaces whose bumps happen to match. Wide, fairly flat, no deep pocket.

It is **small**. Somewhere around 15 to 25 residues out of a chain that might be a thousand residues
long.

### 4. Grabbing is not the whole job

This is where ADCs get genuinely difficult, and it is worth slowing down for.

For an ADC to kill a cancer cell, **four** things have to happen in order:

1. **Bind.** The antibody grips its target on the outside of the cell.
2. **Get swallowed.** The cell pulls the whole thing inside — a process called
   **internalization**, or **endocytosis**. The cell membrane dimples inward around whatever is
   stuck to it, pinches off, and forms a bubble inside the cell.
3. **Reach the stomach.** That bubble has to travel to the **lysosome**, the cell's acid-and-enzyme
   chamber for breaking things down.
4. **Let go.** The acid and enzymes cut the linker, and the payload is finally released — inside the
   cancer cell.

**A perfect grip that never gets swallowed does nothing.** An antibody that binds beautifully to a
protein the cell never pulls inside is a failed ADC. This is why picking the right target protein —
and the right patch on it — is not a detail. It is most of the problem.

### 5. Why the target is the hard part

There are thousands of proteins sitting on the surface of human cells. Only a small number are
serious ADC candidates, and figuring out which ones is genuinely unsolved.

The usual approach is to look for proteins that appear in far greater amounts on cancer cells than
on healthy ones. That is a sensible place to start and it is not enough, for two reasons:

**It misses things.** Several proteins that are now the basis of approved, working ADC drugs would
not have passed a straightforward amount-based filter. They were found other ways.

**Amount is not the only question.** A protein can be abundant and still be a poor target — if the
cell never swallows it, if the useful part is hidden, or if it also appears on your heart or your
lungs, where you very much do not want the payload delivered.

**That gap is what this project is about.** It asks a different question: does the *shape* of a
target protein tell you something that the *amount* of it does not?

### 6. What this tool does — and what it does not claim

Being precise here matters more than sounding impressive.

**What it does.** It uses **ESMFold**, a neural network, to predict the folded shape of a protein's
**ECD** — the extracellular domain, meaning the part that sticks out of the cell into open space.
That is the only part an antibody can reach, so it is the only part worth folding. From that
predicted shape it measures a small, fixed set of geometric quantities. One of them measures how
much of the surface forms a single large connected region that water could reach — a quantity called
**SASA**, or solvent-accessible surface area. The logic is simple: if water can get to it, other
things probably can too.

**What it does not claim.** It does not find binding sites. It does not identify epitopes. It does
not predict whether an antibody would work.

**Read that as the actual design, not as modesty.** When this tool highlights a region of a
structure, the honest description is:

> *These residues, in a shape predicted by a neural network from sequence alone, are calculated to
> be solvent-accessible and adjacent to one another.*

Whether that has anything to do with where an antibody would really bind is **the open question this
project is testing**. It is not an assumption the tool is built on. A version of this tool that
labelled those regions "possible binding sites" would be answering the question before asking it.

So when a surface here says something like *"this measurement accounts for most of this target's
structural rank,"* that is a statement about **the model**. It is not a statement about the protein,
and it should not be written down as one.

### 7. What this tool cannot see

Four limitations. None of them are small, and the last one is the one to remember.

**The prediction has a confidence score, and confidence is not accuracy.** ESMFold reports a number
called **pLDDT** for every residue, from 0 to 100. High means the model is fairly sure that residue
is where it put it. Low means it is guessing. A measurement taken over low-confidence residues is
not a measurement of the protein — it is a measurement of a guess. Everywhere a number is shown
here, its confidence is shown with it.

**The cutoffs are chosen, not discovered.** To decide whether a residue counts as "reachable," the
tool uses a threshold. To decide whether two reachable residues count as "next to each other," it
uses a distance. Both numbers come from published convention. They are reasonable and they are also
**arbitrary** — nudge them and the answer moves. A hard-edged coloured region on a screen makes a
chosen number look like an anatomical fact.

**The sugar is missing.** Real cells coat their surface proteins in bushy sugar structures called
**glycans**. A glycan sitting over a patch can block it completely. **ESMFold does not model glycans
at all.** A region that looks wide open in this tool may be under a bush in real life.

**The tool folds one chain at a time, and many of these proteins do not work alone.** Plenty of
surface proteins only function stuck together with copies of themselves or with partner proteins.
The face where two copies join is permanently covered up in a living cell. But fold **one** copy on
a computer and that face looks wide open and inviting — and because it evolved to be a big flat
sticking surface, it is often the *largest* open face in the whole structure.

**So the most "accessible" region this tool finds could be exactly the one surface an antibody can
never reach.** That is not an occasional error. It runs in one direction, which makes it worse than
random noise — and the tool currently has no way to tell you when it is happening. This is recorded
in full on the Limitations page, and it is why regions shown on a structure here always arrive with
this warning attached.

### 8. Why say all of this

A tool that reported only its results would look more confident and be worth less.

Every limitation above was found by measuring something, not by guessing, and each one narrows what
the results are allowed to mean. **A result you can trust is one that arrives with an honest account
of where it breaks.** That account is not a disclaimer bolted on at the end. It is the finding.

---

## Test surface for this copy

Content has a test surface, and this one is assertable.

- Every **bolded term** in this file resolves to exactly one entry in `glossary.json`. A bolded term
  with no entry fails the gate; an entry defined twice fails the gate.
- Every glossary term appearing in **any** UI string — this surface, the Scorer, the coverage line,
  the topology glossary — renders as a link with a tooltip.
- **No UI string asserts that a region is a binding site, an epitope, antibody-accessible, or
  reachable.** A banned-phrase list is checked against all rendered copy. This is D-028 enforced by
  the gate rather than by memory.
- §7's four limitations each link to their owning Limitations entry; a broken or missing link fails.
- The single-chain warning (§7, fourth item) is a **precondition for structure-region rendering** —
  if patch rendering ships on the 3Dmol viewer, it cannot mount without the warning component
  present. **Proven by revert** (A-017): remove the component, watch the gate redden.
- No number appears in this copy that is derived from project data. The two numbers present — *nine
  out of ten* conformational epitopes and *15 to 25* residues — are **external literature values,
  not project measurements**, and are marked as such in the glossary. ⚠ **Verify both against
  primary sources before publication; the Planner cannot check citations.**
