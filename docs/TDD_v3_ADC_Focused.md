# Technical Design Document v3: PharmFoldMDK

**Project Name**: PharmFoldMDK – ADC Target Exploration Platform  
**Focus**: Antibody-Drug Conjugate (ADC) Target Analysis for Cancer  
**Date**: July 16, 2026  
**Hosting**: Fly.io (Postgres + pgvector + Volumes)  
**Security (MVP)**: Username / Password

---

## 1. Executive Summary

**PharmFoldMDK** is an interactive web application focused on **Antibody-Drug Conjugate (ADC) target exploration**. Users input cancer types or overexpressed proteins and receive AI-powered structural analysis to evaluate their potential as ADC targets.

The tool predicts or retrieves 3D protein structures, identifies druggable pockets, assesses ADC suitability, analyzes mutation impacts, and generates pharma-relevant reports. It is designed as both a practical research aid and an educational platform, with an engaging “Mission Briefing” onboarding experience.

**Primary Value**: Accelerate early-stage ADC target evaluation by combining protein structure prediction with pharmaceutical reasoning.

---

## 2. Project Overview & Objectives

### Background
Antibody-Drug Conjugates represent one of the most promising advancements in targeted cancer therapy. Success depends heavily on choosing the right target protein — one that is overexpressed on cancer cells, accessible on the cell surface, and has suitable binding sites.

Traditional target evaluation is slow and requires deep expertise. PharmFoldMDK aims to lower the barrier by providing rapid structural insights.

### Objectives
- Deliver a focused tool for exploring overexpressed proteins as potential ADC targets.
- Provide high-value outputs: protein structure, druggable pockets, ADC suitability assessment, and actionable reports.
- Include strong educational components (ADC Mission Briefing) to teach users about ADC design.
- Build on a maintainable architecture (Postgres + pgvector) suitable for long-term evolution.
- Align with the user’s broader agentic and Second Brain ecosystem goals.

---

## 3. System Value Proposition

### Frontend Inputs
- Cancer type or specific overexpressed protein
- Optional: Known mutations or variants
- User preferences for analysis depth

### Valuable Backend Outputs (Ranked)

| Rank | Output                              | Description                                                                 | ADC Relevance                          |
|------|-------------------------------------|-----------------------------------------------------------------------------|----------------------------------------|
| 1    | Predicted 3D Structure             | High-confidence structure of the target protein (especially extracellular domains) | Foundation for all further analysis   |
| 2    | Druggable Pocket Identification    | Ranked surface pockets suitable for antibody or small-molecule binding     | Critical for epitope selection        |
| 3    | ADC Target Suitability Assessment  | Evaluation of surface accessibility, size, and druggability for ADC design | Directly supports ADC decision-making |
| 4    | Mutation Impact Analysis           | How cancer-associated mutations affect structure or binding sites          | Important for patient stratification  |
| 5    | Comparison to Known ADC Targets    | Similarity scoring to successful targets (HER2, Trop-2, etc.)              | Helps prioritize new targets          |
| 6    | Therapeutic Hypothesis Report      | Structured summary with confidence caveats and next-step recommendations   | Actionable output for researchers     |

---

## 4. ADC-Focused Development Iterations

### Iteration 1: MVP – Core ADC Target Analysis
**Goal**: Deliver structure + pocket analysis with educational onboarding.

**Features**:
- ADC Mission Briefing tab (explains Antibody, Linker, Payload + tool mission)
- Cancer/overexpressed protein input (with suggested database of targets)
- Structure retrieval/prediction of target protein
- Basic 3D visualization
- Druggable pocket identification
- Simple ADC suitability summary
- Per-user history

### Iteration 2: Deeper ADC Analysis
**Goal**: Add mutation and comparison capabilities.

**Features**:
- Mutation impact analysis on structure and pockets
- Comparison to known successful ADC targets
- Enhanced pocket analysis with ADC-specific scoring
- Improved visualization (pocket highlighting, surface accessibility)

### Iteration 3: Reports & Intelligence Layer
**Goal**: Deliver synthesized, decision-support outputs.

**Features**:
- Automated ADC Target Report generation
- Semantic search over user’s analyzed targets
- Stronger therapeutic hypothesis generation
- Exportable reports and data bundles

### Iteration 4 (Stretch): Advanced ADC Capabilities
**Goal**: Move toward design support and agentic features.

**Features**:
- Epitope suggestion / antibody binding region analysis
- Basic ADC complex modeling (antibody + target)
- Agentic workflows (e.g., “Find similar targets to Trop-2”)
- Integration hooks for external ADC databases

---

## 5. Architecture & Technology Stack (Summary)

**Core Architecture** remains consistent with previous versions:
- Streamlit frontend + FastAPI backend
- Fly.io Postgres + pgvector (primary database)
- Fly Volumes for large structure files (PDB/CIF)
- Python ecosystem (Hugging Face, BioPython, py3Dmol/stmol, etc.)

**Key Addition**: Strong emphasis on ADC-specific outputs and the educational Mission Briefing experience.

---

## 6. Database Considerations (Postgres + pgvector)

The database schema from Database Plan v2 remains appropriate, with minor extensions possible for:
- ADC-specific metadata fields on `protein_analyses` (e.g., `adc_suitability_score`, `surface_accessibility_notes`)
- Enhanced support for cancer target database entries

Large structure files continue to be stored on Fly Volumes.

---

## 7. Risks & Mitigations

- **Overly broad scope**: Mitigated by strict ADC focus in Iterations 1–3.
- **Data quality for cancer targets**: Start with well-known, high-quality targets; allow user-added proteins later.
- **Educational vs. research balance**: The Mission Briefing tab serves both new learners and experienced users.
- **GPU deprecation on Fly.io**: Handled by preferring pre-computed structures and lightweight models.

---

## 8. Next Steps

With this TDD v3 approved, the following documents are aligned:
- **Database Plan v2** (Postgres + pgvector)
- **UI Plan** (includes ADC Mission Briefing tab)
- **Test Plan** (updated for ADC-focused functional and user testing)

---

**End of Technical Design Document v3 – ADC Focused**