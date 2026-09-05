# Project-PharmFoldMDK

PharmFoldMDK explores **antibody-drug conjugate (ADC) targets** by their 3-D structure. It
folds each target's extracellular domain with **ESMFold** (a deep-learning protein model —
the graded core of this project), measures the shape, and asks whether a **structure-derived**
ranking reorders an expression-based one. The live app is at **https://pharmfoldmdk.fly.dev**
(public `GET /api/*` reads).

---

## ▶ Try it yourself: the miniature demo notebook

The fastest way to see what this project does is **[`notebooks/miniature_NECTIN4.ipynb`](notebooks/miniature_NECTIN4.ipynb)** —
a plain-language walkthrough of the **entire pipeline in miniature, on one real target
(NECTIN4), folded live in front of you**. It imports the real `core/` and `worker/` code and
runs it; nothing is mocked. In six short steps it: states the question, **folds NECTIN4 live**
(~1 minute), renders the structure coloured by confidence, extracts the six shape features,
places NECTIN4 in the deployed ranking, and lays out the honest limits.

### What you need

- An **NVIDIA GPU with ~6 GB+ of VRAM** (the fold runs on the graphics card).
- **Python 3.11**.
- **~10 GB of disk** for the ESMFold weights — downloaded automatically the first time you run
  it (subsequent runs reuse the cache).

> The committed notebook already has its outputs and the structure figure saved in, so you can
> **read it on GitHub without running anything**. Run it only if you want to fold NECTIN4 yourself.

### Set up the demo-only environment

The notebook uses a **separate, demo-only** dependency world (`requirements-notebook.txt`) —
deliberately kept apart from the deployed app, which has no GPU and never ships this stack.

```bash
# from the repo root, on a GPU box:
python -m venv .venv-notebook
.venv-notebook\Scripts\activate            # Windows  (Linux/Mac: source .venv-notebook/bin/activate)
pip install torch==2.11.0+cu128 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements-notebook.txt
python -m ipykernel install --user --name pharmfold-notebook
```

### Run it

**Interactively** (recommended — you get to watch the fold, the render, and the ranking appear):

```bash
python -m jupyter lab notebooks/miniature_NECTIN4.ipynb
```

Pick the **pharmfold-notebook** kernel, then *Run All*. The fold cell is the slow one
(~1 minute) — a long wait there means it's *working*, not stuck.

**Headless** (run every cell top-to-bottom and save the outputs back into the file):

```bash
python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebooks/miniature_NECTIN4.ipynb
```

> Run these **from the repo root**, not from inside `notebooks/` — the path is relative to the
> repo root. On a first, cold start Python can take 15-30 s just to load before the notebook
> begins; let it run.

---

## Repository map

| Path | What it is |
| --- | --- |
| `notebooks/miniature_NECTIN4.ipynb` | The live-fold demo above (D-072) |
| `core/` | The pure logic: feature extractor, scorer, routing manifest, queue |
| `worker/` | The GPU tier: the ESMFold fold-runner and job-pull loop (never deployed) |
| `app/` | The Fly serving tier (FastAPI): the read API and worker routes |
| `data/adcs/` | ADC-A v1 FDA-approved catalog (`adcs.v1.json`, D-119). ADC-B pages (`/adcs`, D-122) consume it via `GET /api/adcs`. ADC-C-A (D-124) adds sibling `adcs.pipeline.v1.json` + `access.v1.json` (not merged into v1). Weekly Drugs@FDA watch is Emma's ops lane — see that folder's README. |
| `db/` | ORM models + Alembic migrations |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The living source-of-truth architecture |
| [`docs/README.md`](docs/README.md) | The design-decision log (every decision, newest first) |

## Developing

The serving/runtime tier is hash-locked; run the test suite with the project venv:

```bash
python -m pytest -q
```

CI must pass (`test` + `postgres`) before anything merges to `main`. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) and [`docs/README.md`](docs/README.md) for the full
picture and the reasoning behind every decision.
