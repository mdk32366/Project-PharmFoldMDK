#!/usr/bin/env bash
# Seed climb cache on the RunPod — cache-only; no UniProt fetch.
# Expected stdout: SEED_OK accession=Q04721 len=2471
set -euo pipefail
cd /workspace/Project-PharmFoldMDK
python3 data/census/seed_Q04721_climb_cache.py
ls -la data/census/spancache/Q04721.json