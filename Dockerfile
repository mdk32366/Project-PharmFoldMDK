# The Fly serving-tier image — two-stage since DEP-006 (was single-stage DEP-001).
#
# Stage 1 (Node, BUILD-TIME ONLY — DEP-006) builds the React bundle to static assets. Node
# never enters the runtime image; the built assets are plain files. Stage 2 is the runtime
# tier, UNCHANGED from DEP-001: the hash-locked runtime lock, app/ + core/ + db/ + data/, and
# no worker/ / torch. The image-contents test (tests/test_image_contents.py) asserts both
# halves — the runtime stage's shape, and that no npm/node instruction appears after the
# runtime FROM (DEP-006).

# ── Stage 1: build the UI bundle (D-037: npm ci against the committed lock) ────
FROM node:20-slim AS ui-build
WORKDIR /ui
# Lockfile first so the (slow) install layer caches on dependency changes, not source edits.
COPY ui/package.json ui/package-lock.json ./
# `npm ci` (never `npm install`) installs EXACTLY the lockfile and fails if package.json and the
# lock disagree (D-037). The JS toolchain is build-time only and outside D-013's hash guarantee.
RUN npm ci
COPY ui/ ./
RUN npm run build            # → /ui/dist (index.html + hashed assets/)

# ── Stage 2: the runtime serving tier (DEP-001, unchanged) ────────────────────
FROM python:3.11-slim
WORKDIR /srv

# Runtime lock ONLY — hash-verified, the same file and flag the gate installs (D-013). NOT
# requirements-dev.lock, NOT worker/requirements.txt. Copied alone first so the (slow) install
# layer caches on dependency changes rather than on every source edit.
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock

# The serving tier, and only it (DEP-001): app/ (FastAPI) + core/ (queue/manifest primitives,
# incl. the relocated FoldSpec contract) + db/ (ORM models) + data/ (the cohort CSVs the D-038
# coverage route computes from). worker/ and its torch==2.11.0+cu128 world (D-004/D-018) are
# deliberately absent from the always-on, no-GPU serving tier.
COPY app/ ./app/
COPY core/ ./core/
COPY db/ ./db/
COPY data/ ./data/

# The built React bundle from stage 1 — static files only, no Node (DEP-006). app_from_env
# serves it under / with /api and /jobs matched FIRST (route ordering).
COPY --from=ui-build /ui/dist ./ui_dist

EXPOSE 8080
# app_from_env builds the engine + settings from the environment (D-031) and mounts ui_dist;
# --factory because it is a callable that returns the app, not a module-level instance.
CMD ["uvicorn", "app.main:app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8080"]
