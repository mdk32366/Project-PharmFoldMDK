# Database Plan v2: PharmFoldMDK (Postgres + pgvector)

**Project**: PharmFoldMDK – AI-Powered Protein Structure Prediction & Pharmaceutical Analysis Platform  
**Date**: July 16, 2026  
**Primary Recommendation**: Fly.io Postgres + pgvector  

---

## 1. Recommendation: Postgres + pgvector (Primary Choice)

After reviewing your long-term goals — maintaining this as a **living example** of AI application in pharma, with semantic search, potential agentic access (LangGraph), and growth beyond a pure class project — the recommended database is **Fly.io Postgres addon with the pgvector extension**.

### Why Postgres + pgvector over SQLite

- **Concurrency & multi-user/agent readiness**: Postgres handles simultaneous connections far better than SQLite. This matters for future agentic use (LangGraph tools calling the API), potential shared access, or scaling.
- **Native vector support (pgvector)**: Mature HNSW and IVFFlat indexes for semantic search over analyses and embeddings. Excellent integration with SQL and LangChain/LangGraph.
- **JSONB flexibility (document store)**: Ideal for metadata, confidence maps (pLDDT/PAE), pocket lists, and evolving pharma-relevant fields without constant schema migrations.
- **Long-term maintainability**: Better tooling for migrations (Alembic), backups, monitoring, point-in-time recovery, and scaling. Aligns with your intent to keep and evolve this project.
- **Hybrid workloads**: Single system for relational data + document/JSONB + vectors — no need for a separate vector database for most use cases.

**Note on large files**: PDB/mmCIF structure files, large PAE JSONs, generated reports, and user uploads should be stored on the **Fly Volume filesystem** (organized under `/data/analyses/{id}/`). The database stores only paths + metadata. This is best practice regardless of DB engine.

Fly.io makes Postgres easy via their managed addon. pgvector can be enabled with a simple `CREATE EXTENSION vector;` command.

---

## 2. Core Entity Schema

The schema is intentionally simple and normalized while leveraging JSONB for flexibility. It directly supports the value outputs in the TDD.

### 2.1 users

| Column            | Type                  | Notes                          |
|-------------------|-----------------------|--------------------------------|
| id                | SERIAL PRIMARY KEY    | Auto-increment                 |
| username          | VARCHAR(50) UNIQUE    | Login identifier               |
| hashed_password   | VARCHAR(128)          | bcrypt or passlib hash         |
| created_at        | TIMESTAMPTZ           | Default now()                  |
| preferences       | JSONB                 | Default organism, report style, etc. |

### 2.2 protein_analyses (core entity)

| Column            | Type                                      | Notes                                      |
|-------------------|-------------------------------------------|--------------------------------------------|
| id                | SERIAL PRIMARY KEY                        | -                                          |
| user_id           | INTEGER REFERENCES users(id)              | -                                          |
| input_type        | VARCHAR(20)                               | 'uniprot' \| 'fasta' \| 'pdb_upload'       |
| input_value       | TEXT                                      | Sequence, ID, or filename                  |
| structure_source  | VARCHAR(30)                               | 'alphafold_db' \| 'esmfod_local' \| 'user_upload' |
| pdb_path          | TEXT                                      | Path on Fly Volume                         |
| mean_plddt        | REAL                                      | Average confidence (0-100)                 |
| pae_json_path     | TEXT                                      | Optional PAE matrix path                   |
| metadata          | JSONB                                     | Length, organism, gene, UniProt data, etc. |
| created_at        | TIMESTAMPTZ                               | -                                          |
| notes             | TEXT                                      | User free-text notes                       |

### 2.3 mutations

| Column            | Type                                      | Notes                                      |
|-------------------|-------------------------------------------|--------------------------------------------|
| id                | SERIAL PRIMARY KEY                        | -                                          |
| analysis_id       | INTEGER REFERENCES protein_analyses(id)   | -                                          |
| position          | INTEGER                                   | 1-based residue position                   |
| original_aa       | CHAR(1)                                   | -                                          |
| new_aa            | CHAR(1)                                   | -                                          |
| impact_score      | REAL                                      | Optional stability/pocket delta (Iter 2+)  |
| impact_notes      | TEXT                                      | Qualitative assessment                     |
| created_at        | TIMESTAMPTZ                               | -                                          |

### 2.4 reports

| Column            | Type                                      | Notes                                      |
|-------------------|-------------------------------------------|--------------------------------------------|
| id                | SERIAL PRIMARY KEY                        | -                                          |
| analysis_id       | INTEGER REFERENCES protein_analyses(id)   | -                                          |
| report_type       | VARCHAR(30)                               | 'structure_summary' \| 'mutation_impact' \| 'pharma_context' |
| content_path      | TEXT                                      | Path to PDF/Markdown on Volume             |
| generated_at      | TIMESTAMPTZ                               | -                                          |

### 2.5 embeddings / vector search (pgvector)

For semantic search (Iteration 3+):

```sql
CREATE TABLE analysis_embeddings (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES protein_analyses(id),
    embedding vector(384)
);

CREATE INDEX ON analysis_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

This enables efficient cosine similarity search. pgvector supports HNSW (recommended) and hybrid/filtered queries directly in SQL.

---

## 3. Relationships, Indexing & pgvector Strategy

- `users` 1:N `protein_analyses`
- `protein_analyses` 1:N `mutations` & `reports`

**Key indexes**:
- `users(username)`
- `protein_analyses(user_id, created_at)`
- `protein_analyses(structure_source)`
- `mutations(analysis_id)`
- `reports(analysis_id)`
- Vector: HNSW index on embedding column (cosine or L2)

pgvector allows powerful hybrid queries (e.g., filter by `user_id` + semantic similarity).

---

## 4. Storage Architecture on Fly.io

- **Structured + vector data**: Fly.io Postgres addon (with pgvector enabled)
- **Large files & artifacts**: Fly Volume mounted at `/data` (PDB/CIF files, PAE JSONs, generated reports, uploads). Organized by analysis ID.
- **Backups**: Fly Postgres automated backups + volume snapshots. Simple export scripts for extra safety.
- **Migrations**: Alembic with versioned scripts.

---

## 5. Migration Path from SQLite (Optional)

If you want to move very quickly in early development, you can start with SQLite on a Volume using the same schema. SQLModel makes switching to Postgres straightforward later — just change the connection string and run migrations. The vector table can be added when you reach Iteration 3.

---

**End of Database Plan v2**