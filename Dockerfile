# The Fly serving-tier image (DEP-001). RUNTIME TIER ONLY — no GPU, no worker/.
#
# What goes in is ruled, not left to whoever writes the COPY lines: DEP-001 (contents),
# D-013 (hash-locked install, exactly as the CI gate does it), D-004 + D-018 (the worker and
# its CUDA stack are a separate dependency world that is never deployed). The image-contents
# test (tests/test_image_contents.py) asserts this file's shape, so an edit that reaches back
# into worker/ and grows a `COPY worker` or a torch install to satisfy it reddens the gate.
FROM python:3.11-slim

WORKDIR /srv

# Runtime lock ONLY — hash-verified, the same file and flag the gate installs (D-013). NOT
# requirements-dev.lock, NOT worker/requirements.txt. Copied alone first so the (slow) install
# layer caches on dependency changes rather than on every source edit.
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock

# The serving tier, and only it:
#   app/  — the FastAPI transport (D-031's four routes)
#   core/ — the queue/manifest primitives the routes call, incl. the relocated FoldSpec
#           contract (DEP-001 Builder note) that lets app/ avoid importing worker/
#   db/   — the SQLAlchemy ORM models the upload route writes
# worker/ is deliberately absent: it runs on the GPU box (D-004) and its torch==2.11.0+cu128
# world (D-018) never ships to the always-on, no-GPU serving tier.
COPY app/ ./app/
COPY core/ ./core/
COPY db/ ./db/

EXPOSE 8080
# app_from_env builds the engine + settings from the environment (D-031); --factory because
# it is a callable that returns the app, not a module-level instance.
CMD ["uvicorn", "app.main:app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8080"]
