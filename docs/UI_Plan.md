# UI Plan: PharmFoldMDK

**Project**: PharmFoldMDK – AI-Powered Protein Structure Prediction & Pharmaceutical Analysis Platform  
**Date**: July 16, 2026  
**Primary Technology**: Streamlit (with FastAPI backend support)

---

## 1. Overall Approach

**Scope Focus**: PharmFoldMDK is now scoped primarily around **Antibody-Drug Conjugate (ADC) target exploration**. The tool helps users analyze overexpressed proteins in cancer as potential targets for ADCs by predicting structures, identifying druggable regions, and generating pharma-relevant insights.

The user interface will be built primarily with **Streamlit** for rapid development of interactive ML dashboards. It can be paired with a FastAPI backend for heavier inference endpoints if needed. The design prioritizes clarity around the high-value outputs defined in the TDD, with a strong emphasis on ADC applicability:

- High-confidence 3D structures + confidence metrics of cancer-associated proteins
- Druggable pocket identification on target proteins
- Assessment of ADC targeting potential
- Pharma-contextualized reports and therapeutic hypotheses
- Clean history/library with semantic search (Iteration 3+)

**Key Principles**:
- Educational onboarding through an engaging “Mission Briefing” style introduction
- Progressive disclosure (core structure first, advanced features on demand)
- Clear communication of model confidence
- Strong pharma/ADC-relevant framing
- Strong 3D visualization experience
- Clean history/library with semantic search (Iteration 3+)

---

## 2. High-Level Page Structure

### Sidebar Navigation (persistent)
- Home / Dashboard
- New Analysis
- My Library / History
- Reports
- Settings / Account

### Main Content Area

#### Page 1: Dashboard / Home
- Welcome message + quick stats (number of analyses, recent activity)
- Prominent “Start New Analysis” CTA button
- Recent analyses cards (mini confidence preview + quick actions)
- Quick links to documentation or example targets (e.g., common drug targets)

#### Page 2: New Analysis (Core Flow – Highest Value Output)
**Goal**: Deliver reliable structure + confidence visualization quickly.

**Input Options** (clear tabs or radio buttons):
- UniProt ID lookup (with autocomplete/search)
- Paste FASTA sequence
- Upload PDB or sequence file

**Advanced Options** (collapsible):
- Confidence threshold filter
- Preferred organism / database source hint
- Analysis notes

**Action**:
- Big “Run Analysis” button with clear loading state / progress indicator

**Immediate Output** (after processing):
- Prominent display of mean pLDDT score with color coding
- Interactive 3D viewer (py3Dmol or stmol)
- Quick actions: Export PDB, Save to Library, Generate Report, Simulate Mutation

#### Page 3: Analysis Detail / Visualize (Iterations 1–2)
**Goal**: Enable deep exploration of structure, mutations, and pockets.

**Main Panel**:
- Interactive 3D viewer with controls:
  - Rotate, zoom, center
  - Residue selection / highlighting
  - Toggle confidence coloring
  - Pocket surface highlighting (Iteration 2)
  - Mutation overlay (Iteration 2)

**Side / Bottom Panels**:
- pLDDT per-residue plot (interactive)
- PAE summary or heatmap toggle
- Mutation simulator controls (position + new amino acid dropdowns)
- Pocket / binding site list with druggability scores (Iteration 2)
- Wild-type vs. mutant comparison view (Iteration 2)

**Actions**:
- Save mutation experiment
- Generate report
- Export bundle (PDB + metadata + plots)

#### Page 4: My Library / History
**Goal**: Make past work searchable and reusable.

**Features**:
- Searchable and filterable table or card grid of past analyses
- Semantic search bar (Iteration 3+ using pgvector)
- Quick actions per item: Re-analyze, View Report, Compare, Delete
- Tags or folders for organization (future)

#### Page 5: Reports
**Goal**: Deliver synthesized, pharma-actionable outputs.

**Features**:
- List of generated reports with type and date
- Inline preview or modal viewer for Markdown/PDF
- Download options (PDF, Markdown, or full bundle)
- Report types tied to iterations:
  - Structure Summary (Iteration 1+)
  - Mutation Impact (Iteration 2+)
  - Pharma Context (Iteration 3+)

#### Page 6: Settings / Account (Light)
- Profile / password management
- Preferences (default organism, report style, notification settings)
- Data export / delete my analyses
- API key section (for future agentic use)

---

## 3. 3D Visualization Approach

**Primary Tool**: `py3Dmol` or `stmol` embedded in Streamlit.

**Capabilities**:
- Load PDB directly from volume path or string
- Residue highlighting and selection
- Surface / cartoon / stick representations
- Color by confidence (pLDDT)
- Pocket surface rendering (simple geometric or pre-computed)
- Mutation highlighting

**Fallbacks**:
- Static image export for reports
- Text-based residue tables when 3D is not available

---

## 4. Iteration Mapping

| Iteration | Key UI Features Added |
|-----------|-----------------------|
| **1 (MVP)** | Input flow, structure retrieval + confidence display, basic 3D viewer, history saving |
| **2** | Mutation simulator + comparison views, pLDDT plots, basic pocket highlighting |
| **3** | Report generation & viewing, semantic library search, improved organization |
| **4 (Stretch)** | Agentic query interface, batch processing UI, advanced visualizations |

---

## 5. New: ADC Mission Briefing / Educational Onboarding Tab

**Goal**: Make the tool immediately understandable and exciting, especially for users who may not be deep experts in ADCs. This acts as both an educational hub and a “video game mission briefing” style introduction.

### Recommended Implementation
- Add a prominent sidebar item called **“ADC Mission Briefing”** (or “How ADCs Work”).
- It can also appear as a one-time modal on first login or be permanently accessible.
- Tone: Professional but engaging — think high-quality scientific tool with light gamification (like a mission briefing in a strategy game). Static, clean design with good visuals and short paragraphs. No animations required.

### Content Structure (Mission Briefing Style)

**Header / Title**
- “Operation: Precision Strike – Antibody-Drug Conjugates”

**Section 1: The Problem**
- Brief, impactful statement: “Cancer cells are masters of disguise. Traditional chemotherapy often damages healthy cells along with the bad ones.”
- Simple explanation of why targeted therapies matter.

**Section 2: The Solution – Antibody-Drug Conjugates (ADCs)**
Explain the three core components clearly with simple analogies:

| Component     | What It Is                          | Simple Analogy                     | Role in the Mission                  |
|---------------|-------------------------------------|------------------------------------|--------------------------------------|
| **Antibody**  | A protein that acts like a smart missile guidance system | A heat-seeking missile that only locks onto one specific type of enemy | Finds and binds to the cancer cell   |
| **Linker**    | The connector between antibody and payload | The fuse or detonator on the warhead | Keeps the payload attached until it reaches the target, then releases it |
| **Payload**   | A powerful chemotherapy drug        | The explosive warhead              | Kills the cancer cell from the inside |

**Section 3: PharmFoldMDK’s Mission**
Clear statement of purpose:

> **Our Mission**: Help researchers and students rapidly explore overexpressed proteins in cancer as potential ADC targets. By predicting protein structures and identifying druggable regions, we aim to accelerate the discovery and design of next-generation targeted cancer therapies.

Make this feel inspiring and purposeful.

**Section 4: Cancer Target Database (Interactive)**
- Curated or selectable list of high-priority cancers and their overexpressed proteins.
- Suggested fields to include:
  - Cancer Type
  - Aggressiveness / Severity
  - Key Overexpressed Protein (e.g., HER2, Trop-2, EGFR, Nectin-4)
  - Accessibility Challenges (e.g., Blood-Brain Barrier for glioblastoma)
  - Current ADC Status (Approved, In Trials, Exploratory)
- Users can click a target to **pre-fill the New Analysis** screen with the relevant protein.

This turns the tool into both an explorer and an educational resource.

**Section 5: Call to Action**
- Big button: “Begin Mission – Analyze a Cancer Target”
- This takes the user directly to the New Analysis page.

### Design Notes
- Use clean cards or a dashboard-style layout for the three ADC components.
- Include simple diagrams (can be static images or even hand-drawn style illustrations).
- Keep text concise — aim for scannable sections rather than walls of text.
- This page should feel welcoming and reduce the learning curve for new users.

---

## 6. UX & Accessibility Notes

- Clear loading states and progress indicators (especially important for any on-demand inference)
- Helpful tooltips and inline documentation for confidence metrics and pharma terms
- Consistent color scheme (greens/blues for confidence, clear mutation highlighting)
- Responsive enough for desktop primary use (class + personal tool)
- Basic accessibility (labels, contrast, keyboard navigation where feasible)

---

**End of UI Plan**