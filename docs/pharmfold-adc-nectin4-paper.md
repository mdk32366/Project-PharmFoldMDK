# How a Poison-Carrying Antibody Sticks to the Outside of Nectin-4

*An eighth-grade paper. Written 2026-09-03 for Matt Kelly. Updated the same day with a second part: can Padcev's antibody also hit other proteins, and how to rank folded proteins as next ADC targets. Facts are from the sources at the end. If a source did not say it, this paper does not say it.*

Source Drive: https://docs.google.com/document/d/1dnXYjWOI34gcsMdGfrrEBVqXSKUjVnCSI--DhEfzQSc/edit

## UI placement (Emma 2026-09-05)
- Expand existing SPA route `/about` → `ui/src/components/AdcContext.jsx` (nav: "About ADCs").
- Do not invent a second competing explainer page.
- Phase 2 add-on / follow-on after P0 honesty; do not block Phase 1.
- Keep Track A red-without-wet-bind and Track B ranking algorithm visible.

## Part 1 — The original question

### The question

Some cancer drugs are built like a delivery truck. The truck is an antibody. The cargo is a poison. Together they are called an antibody-drug conjugate, or ADC.

One real ADC is enfortumab vedotin (brand name Padcev). It is aimed at a protein called Nectin-4 that sits on the outside of some cancer cells.

The question is: what specifically lets that antibody, while it is carrying poison, connect in a lasting way to the **outside** piece of an antigen like Nectin-4?

The short answer has two parts, and they are easy to mix up:

1. The antibody **holds onto Nectin-4** with a tight, lock-and-key fit. That hold is not a chemical glue. It is a very sticky handshake.
2. The poison is **chemically glued to the antibody**, not to Nectin-4. After the cell swallows the pair, the glue is cut and the poison works inside.

### Two different "connects"

Think of a key on a keychain with a heavy charm.

- The key fits one lock (Nectin-4). That is the antibody-to-antigen hold.
- The charm is welded to the keyring. That is the poison-to-antibody hold.

The charm does not have to fit the lock. Padcev's poison (MMAE) is not described as binding Nectin-4. The antibody does that job. Then the cell takes the whole thing in, and enzymes cut the linker so MMAE can break the cell's microtubules.

### What the "outside piece" of Nectin-4 looks like

Nectin-4 (NECTIN4 / PVRL4) is a type I membrane protein: outside ECD, one transmembrane helix, cytoplasmic tail. UniProt Q96NY8: signal 1–31; outside 32–349; TM 350–370; inside 371–510. Three Ig-like domains: V-type 32–144 (far tip), C2-type 148–237, C2-type 248–331. The Padcev family antibody grabs the **V tip**.

### What holds the antibody on that tip

CDR loops on the Fab arms stick with **non-covalent** forces: hydrogen bonds, electrostatics/salt bridges, van der Waals. Challita-Eid 2016: epitope on membrane-distant V domain; blocks Nectin-4–Nectin-1 adhesion in vitro; apparent KD ~0.01 nM on T-47D (later ADC versions ~0.057–0.060 nM). Exact atomic contacting residues for enfortumab itself: not in sources used here (PDB 9KKJ is a different ADC).

### Durable without permanent glue

Affinity (one arm) + avidity (two arms when antigen density allows). Design goal is internalization, not camping forever on the surface.

### Where the poison is connected

AGS-22C3 IgG1κ; ~3.8–4 MMAE per antibody via vc linker on interchain cysteines. Covalent to antibody, not to Nectin-4. FDA MOA: bind → internalize → cleave → microtubule disruption.

## Part 2 — Can EV also target other extracellular segments?

### Short answer

1. **Same EV antibody, other proteins:** Do not assume yes. A V domain is a common fold shape, not the same lock. Taiwan FDA assessment: EV/AGS-22M6E bound Nectin-4 but **not** Nectin-1, -2, or -3. Broader IgV cross-binding = **unknown** without lab tests.
2. **Next targets after building EV:** Realistic path is usually a **new antibody** against a **new membrane protein**, reusing ADC learnings.
3. **Bond types:** H-bonds, electrostatics, van der Waals are how antibodies in general stick — not a special third Padcev-only bond.

### V surface ≠ EV keyhole

"V-type" = immunoglobulin-variable-like fold. Other proteins can share the brick without sharing the lock. PDB 4JJH = Nectin-4 D1 structure for shape searches, not EV-binding proof.

### Suggested algorithm

**Track A — Reuse EV antibody:** List membrane IgV / nectin-like ECDs — feasible. Wet binding assays — required. No bind → stop. Do not rank docking guesses as hits. Track A is mostly off-target risk mapping unless wet binding is shown.

**Track B — New Ab, new antigen, reuse ADC learnings** (realistic next-target path): topology; cancer vs normal; internalization; antigen density; fold confidence (pLDDT); epitope exposure; ADC suitability; do **not** require IgV/4JJH similarity; rank by (cancer × membrane × internalization × density) / normal risk.

### Bottom line

Padcev's durable connection to Nectin-4's outside is a high-affinity, often two-armed, non-covalent CDR fit on the membrane-distant V domain, while MMAE is covalently attached to the antibody and released after internalization.

That same antibody is not a universal V-domain key. For next targets after EV, rank folded membrane proteins by ADC biology, then make a **new** antibody — unless wet assays prove the existing EV antibody truly binds something else.
