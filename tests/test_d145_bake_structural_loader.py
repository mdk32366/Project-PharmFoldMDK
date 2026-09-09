"""D-145 — the D-144 loader is baked into the serving image. All of these must go red.

⚠⚠ **The scar this suite exists for was invisible to every guard that already existed.** After
`D-144` merged, the structural-rank loader was hand-placed on `/srv/scripts/` with `sftp` so the
load could be run. **A rebuilt image would have dropped it** — `git show 2170bd8:Dockerfile`
carries exactly one `COPY scripts/...` line, the ingest's, so `/srv/scripts/` in any rebuild
holds exactly one file. Nothing in the gate objected, because nothing in the gate was looking
for an *absence*.

⚠ **That is the direction this suite adds.** `tests/test_serving_image_contents.py` holds the
UPPER bound — the scripts in the image are a subset of the permitted ones — and **a subset test
is satisfied perfectly by an empty set**. Deleting the `COPY` line keeps it green. So the
property the GO asks for (*"must go red if the COPY line is removed"*) needed a **positive**
assertion, and it is here and in `tests/test_image_contents.py`.

⚠ **What this suite CANNOT establish, said plainly rather than implied away.** No docker daemon
runs in the gate, so nothing here proves the *built image* contains the file. These are
assertions about the **declaration** — the `Dockerfile` names it, the build context admits it,
the file exists so the `COPY` is not a typo. The build is the other half of the proof, and it is
a loud half: a `COPY` of a path `.dockerignore` excludes fails the build rather than shipping
nothing.

Tree properties throughout, never a `git diff` against `origin/main` — the gate checks out a
merge ref at depth 1, so a diff-based check would pass by erroring (D-139's precedent).
"""

from __future__ import annotations

import hashlib
import pathlib
import re

import pytest

from _d144_surface import (
    D144_OWN_FILES,
    D144_REGION_MIN_LINES,
    D144_SHARED_REGIONS,
    extract_region,
    region_digest,
    whole_file_digest,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")
DOCKERIGNORE = (ROOT / ".dockerignore").read_text(encoding="utf-8")
FLY_TOML = (ROOT / "fly.toml").read_text(encoding="utf-8")
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")

LOADER = "scripts/census_structural_rank.py"
INGEST = "scripts/census_ingest_features.py"

#: The scripts the serving image is permitted to hold, in the order they are copied.
BAKED = (INGEST, LOADER)


def _instructions(text: str) -> list[str]:
    """Dockerfile INSTRUCTION lines only. A comment is a line whose first non-whitespace
    character is `#`; inline `#` is not a comment in Dockerfile syntax. ⚠ Stripping comments is
    not tidiness — every comment in this file *discusses* the things the assertions forbid, so a
    grep over the raw text is satisfied by the prose that warns against them (F-044)."""
    return [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def _runtime_instructions() -> list[str]:
    """Instructions from the LAST ``FROM`` onward — the runtime stage. Stage 1 is the Node
    builder, and DEP-001's rules are about what *runs*."""
    lines = _instructions(DOCKERFILE)
    last_from = max(i for i, ln in enumerate(lines) if ln.upper().startswith("FROM "))
    return lines[last_from:]


def _copy_sources(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if not line.upper().startswith("COPY "):
            continue
        parts = [p for p in line.split()[1:] if not p.startswith("--")]
        out.extend(parts[:-1])
    return out


# ─────────────── T-1252 — the COPY is present, named, and one file at a time


@pytest.mark.parametrize("rel", BAKED)
def test_the_runtime_stage_names_each_baked_script_as_its_own_copy(rel):
    """⚠ The GO's exact shape: *one explicit COPY, not `COPY scripts/`.* Asserted per file, so
    the failure message says WHICH one went missing rather than that a set changed size."""
    expected = f"COPY {rel} ./scripts/"
    assert expected in _runtime_instructions(), (
        f"D-145: the runtime stage must carry `{expected}` verbatim — and an absent COPY is "
        f"invisible to every subset guard in tests/test_serving_image_contents.py"
    )


def test_the_loader_is_baked_in_and_this_is_the_assertion_the_scar_needed():
    """⚠⚠ THE ONE THE OPS SCAR ASKS FOR. Delete the loader's `COPY` line and this reddens;
    `test_only_the_allowed_scripts_are_copied` stays green, because `{ingest} ⊆ {ingest, loader}`
    is true. **A set bound cannot see an absence**, and the absence is what happened."""
    assert f"COPY {LOADER} ./scripts/" in _runtime_instructions()
    assert (ROOT / LOADER).is_file(), (
        f"{LOADER} is copied into the image but does not exist — that fails the BUILD during a "
        f"deploy, not here, so it is caught here instead"
    )


def test_the_scripts_directory_is_never_copied_and_the_fitter_never_ships():
    """⚠ The bar the growing file list must not become. `D-079` dec 1 bars a refit outright and
    `scripts/fit_scorer.py` IS the fitter — `COPY scripts/` would leave a barred operation one
    `fly ssh` away behind no guard at all.

    ⚠⚠ **Measured under revert, and it is the DIRECTORY bar that protects the fitter — not the
    by-name check that reads as though it did.** With the copy broadened to `COPY scripts/`,
    `test_no_writing_script_reaches_the_image` and `test_the_fitter_is_named_and_absent` **both
    stay green**: a Dockerfile COPY yields its *source token*, which for a directory is
    `scripts/` and never `scripts/fit_scorer.py`, so the intersection against `WRITERS` is empty.
    A guard that names the fitter cannot see the copy that ships it. Both halves are asserted
    here — the directory bar first, because it is the one that bites.
    """
    sources = _copy_sources(_instructions(DOCKERFILE))
    bad = [s for s in sources if s.rstrip("/.") == "scripts" or s.startswith("scripts/*")]
    assert not bad, f"D-145: a scripts DIRECTORY is copied ({bad}) — never the directory"
    assert set(s for s in sources if s.startswith("scripts/")) == set(BAKED), (
        f"the scripts entering the image must be exactly {list(BAKED)}; "
        f"found {sorted(s for s in sources if s.startswith('scripts/'))}"
    )
    assert "fit_scorer" not in "\n".join(_instructions(DOCKERFILE)), (
        "D-079 dec 1: the fitter must never reach the production host"
    )


def test_the_build_context_re_includes_exactly_the_two_named_files():
    """⚠⚠ The half of the shape that reads as optional and is not. `scripts/` is excluded from
    the build CONTEXT, so a `COPY` with no matching `!` line names a path docker cannot see and
    **fails the build** — during a deploy, because no daemon runs in the gate. `b2196e9` shipped
    the ingest's `Dockerfile` line, its `.dockerignore` negation and its test in ONE commit for
    exactly this reason, and this test is why that stays true of the second file."""
    lines = [ln.strip() for ln in DOCKERIGNORE.splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    assert "scripts/" in lines, "`scripts/` must stay excluded from the build context"
    negations = {ln[1:] for ln in lines if ln.startswith("!")}
    assert {n for n in negations if n.startswith("scripts/")} == set(BAKED), (
        f"the context must re-include exactly {list(BAKED)} — never a pattern, never the "
        f"directory; found {sorted(n for n in negations if n.startswith('scripts/'))}"
    )


# ─────────────── the CSVs are not re-copied, and the paths resolve on the machine


def test_no_csv_is_re_copied_for_the_loader():
    """⚠ Hard stop from the GO. `COPY data/ ./data/` already ships them; a second, narrower copy
    aimed at `data/census/` would be two paths to one artefact — `F-014`'s class, which this log
    has now recorded ten times."""
    data_copies = [s for s in _copy_sources(_instructions(DOCKERFILE))
                   if s.split("/")[0] == "data"]
    assert data_copies == ["data/"], (
        f"data/ must be copied exactly once and as the whole directory; found {data_copies}"
    )


def test_the_loader_and_its_population_resolve_under_srv_without_a_path_constant_moving():
    """⚠ A loader that cannot find its inputs is worse than one that is absent, so the path is
    derived here rather than asserted as a string in a comment.

    `WORKDIR /srv` + the loader's own two-parents rule puts it at
    `/srv/scripts/census_structural_rank.py`; the formula module's two-parents rule puts its
    population at `/srv/data/census/census_manifest.v7.csv`. **Both are the repo's own relative
    shape**, which is precisely why baking the file in changes no constant.
    """
    assert "WORKDIR /srv" in _runtime_instructions()

    loader_src = (ROOT / LOADER).read_text(encoding="utf-8")
    assert "pathlib.Path(__file__).resolve().parent.parent" in loader_src, (
        "the loader's repo root is the file's grandparent — if that rule changes, /srv/scripts/ "
        "stops resolving to /srv and the population path moves with it"
    )

    formula_src = (ROOT / "core" / "census_structural.py").read_text(encoding="utf-8")
    assert '_ROOT / "data" / "census" / "census_manifest.v7.csv"' in formula_src

    for rel in ("data/census/census_manifest.v7.csv", "data/adc_reference_mapping.csv"):
        assert (ROOT / rel).is_file(), f"{rel} must exist under data/ — COPY data/ is what ships it"


def test_the_fly_volume_is_not_the_images_data_directory():
    """⚠⚠ `/srv/data` and `/data` are one path segment apart in a way that reads as a typo. The
    Volume holds fold artifacts (`D-031`); the census CSVs live in the IMAGE. An edit that
    "corrected" one to the other would move the loader's population onto a volume that has never
    held it."""
    assert re.search(r'destination\s*=\s*"/data/artifacts"', FLY_TOML), (
        "fly.toml's mount destination moved — the /srv/data vs /data/artifacts distinction this "
        "suite records is stated against that line"
    )
    assert '"/srv' not in FLY_TOML, "the Fly Volume must never be mounted inside /srv"


# ─────────────── hard stops: D-144 stands, and nothing is run


#: sha256 over LF-normalised bytes (RESERVED.md's hash-discipline ruling) of the D-144 surface as
#: it merged at `2170bd8`. ⚠ A pin, not a hope: this PR is image permanence, so a byte moving in
#: any of these files means the PR is no longer what its entry says it is.
#:
#: ⚠⚠ **ONE DIGEST MOVED AT `D-147`, AND THE PIN IS WHAT DEMANDED THE RULING — which is the pin
#: working, not the pin failing.** Its own failure message says *"a formula, schema or route edit
#: belongs to a different entry with its own ruling"*, and `### D-147` is that entry: the
#: `ecd_intermittent` serve-time join. So `app/census_structural_read.py` is **re-pinned** and the
#: superseded value is recorded here rather than overwritten in silence (D-129-C):
#:     app/census_structural_read.py  D-144/D-145/D-146: 7f581c690ebc95bc… → D-147: 0fff62b0b947…
#: ⚠⚠ **AND WHAT DID *NOT* MOVE IS THE LOAD-BEARING HALF.** `core/census_structural.py`,
#: `scripts/census_structural_rank.py`, `db/models.py`, migration `0012` and `app/read_routes.py`
#: are **byte-identical** through D-147, so *"no formula, no schema, no loader, no route"* is a
#: measurement rather than a claim — and `formula_version()` therefore still returns
#: `c859da97f73d`, the value the live run recorded. **The pins were not relaxed; one was moved by
#: name and five were left to prove the rest.**
D144_SURFACE = dict(D144_OWN_FILES)

# ⚠⚠ THE TWO SHARED FILES MOVED TO A REGION PIN — D-149. `app/read_routes.py` holds every read
# route and `db/models.py` holds every table, so a WHOLE-FILE pin on them never asserted "D-144 did
# not move": it asserted "nothing else was ever added", which is a different and false property.
# `D-149` added two routes and two tables that touch nothing of D-144's, and this guard's own
# failure message licenses exactly that — "belongs to a different entry with its own ruling".
# ⚠ THE PIN IS NARROWER, NOT LOOSER: the expected region digests in `tests/_d144_surface.py` are
# taken from `2170bd8`, the commit where D-144 MERGED, not recomputed from this tree — a pin
# recomputed from the thing it pins is a mirror. Measured 2026-09-09: both regions are byte-
# identical between `2170bd8` and this branch. The four D-144-OWN whole-file pins are untouched.


@pytest.mark.parametrize("rel,digest", sorted(D144_SURFACE.items()))
def test_no_formula_schema_or_route_byte_moved(rel, digest):
    """⚠⚠ *"No formula/schema/route change — D-144 stands"*, as a property rather than an
    intention. ⚠ Normalised line endings, per `RESERVED.md`'s hash-discipline ruling: git's
    `LF→CRLF` conversion on checkout means a committed file's delivered bytes differ from its
    committed ones, and a rule that raises a false alarm on every checkout trains its readers to
    ignore it."""
    assert whole_file_digest(rel) == digest, (
        f"{rel} changed — D-145 is image permanence only; a formula, schema or route edit "
        f"belongs to a different entry with its own ruling (as D-147's route edit did: see the "
        f"note on D144_SURFACE, where one digest moved by name and five did not)"
    )


@pytest.mark.parametrize("rel", sorted(D144_SHARED_REGIONS))
def test_d144s_own_region_of_each_shared_file_has_not_moved(rel):
    """⚠⚠ The narrowed half of the pin above: `app/read_routes.py` and `db/models.py` are SHARED,
    so what must not move is **D-144's block inside them**, not the whole file.

    ⚠ The expected digest is `2170bd8`'s — D-144's merge commit — so this asserts *"identical to
    what shipped"* rather than *"identical to itself"*.
    """
    _start, _stops, expected = D144_SHARED_REGIONS[rel]
    assert region_digest(rel) == expected, (
        f"D-144's own region of {rel} changed. D-145 is image permanence only; a formula, schema "
        f"or route edit inside D-144's block belongs to a different entry with its own ruling"
    )


@pytest.mark.parametrize("rel", sorted(D144_SHARED_REGIONS))
def test_the_region_extractor_actually_reaches_a_region(rel):
    """⚠⚠ `A-017` — the fixture must reach the code under test. A region extractor that returned
    `""` would hash the empty string identically forever and this pin would pass on a deleted
    route. So the region is asserted to be non-trivially large, at the size measured at
    `2170bd8`."""
    region = extract_region(rel)
    assert region.count("\n") >= D144_REGION_MIN_LINES[rel], (
        f"the extracted D-144 region of {rel} is only {region.count(chr(10))} lines; a pin over a "
        f"near-empty region asserts nothing"
    )
    assert "census_structural" in region.lower() or "CensusStructural" in region


def test_nothing_in_this_pr_runs_the_loader():
    """⚠ Hard stop from the GO: **no ops `--load`**. The ranking is already loaded on Fly, and a
    rerun would mark the live `valid` run `superseded` and insert a fresh one for no reason —
    a change to served data wearing a packaging PR's clothes.

    ⚠ The image gives the loader its CODE, never a credential: `--load` needs a `DATABASE_URL`
    that only Fly holds. That separation is the same one `D-144` recorded when it shipped
    `result_status: not_run` rather than claiming a rank.
    """
    instructions = _instructions(DOCKERFILE)
    for line in instructions:
        verb = line.split()[0].upper()
        if verb in ("RUN", "CMD", "ENTRYPOINT"):
            assert "census_structural_rank" not in line, (
                f"the image must not EXECUTE the loader, only carry it: {line}"
            )
    assert any(ln.startswith("CMD [\"uvicorn\"") for ln in instructions), (
        "the container's command is still uvicorn — D-145 adds a file, not a startup step"
    )
    workflows = ROOT / ".github" / "workflows"
    for path in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        assert "census_structural_rank" not in path.read_text(encoding="utf-8"), (
            f"{path.name} references the loader — CI must not run an ops load"
        )


def test_no_gpu_world_and_no_worker_entered_the_image():
    """⚠ DEP-001 / D-004 / D-018, restated because this PR touches the `Dockerfile` at all."""
    lowered = "\n".join(_instructions(DOCKERFILE)).lower()
    for forbidden in ("torch", "transformers", "bitsandbytes", "streamlit",
                      "copy worker", "add worker"):
        assert forbidden not in lowered, f"DEP-001: {forbidden!r} must not be in the image"
    assert "worker/" in DOCKERIGNORE, ".dockerignore must keep worker/ out of the context"


# ─────────────── the living log leads it, and the id guards were widened by ADDING


def _d145_entry() -> str:
    """The D-145 entry only, bounded by the NEXT `### ` heading whatever it is."""
    start = LOG.index("\n### D-145 —") + 1
    nxt = re.search(r"^### (?!D-145\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠ The check is the `### D-145` HEADING, never a citation of it (D-062 / method-note item
    7). PR #90 named `D-062` in its title and added no entry, and thirteen later citations
    treated the missing entry as settled authority."""
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     LOG, re.M)
    assert len(re.findall(r"^### D-145 —", LOG, re.M)) == 1, "exactly one D-145 entry"
    assert LOG.index("### D-145 —") < LOG.index("### D-144 —"), "newest first"


def test_the_entry_leads_with_what_this_build_could_not_verify():
    """⚠⚠ D-016, and the disqualifying fact first: no image was built here. A packaging entry
    that reads as though it had verified the artefact is the `F-047` shape — clean, plausible,
    and about a different thing than it appears to be."""
    lowered = " ".join(_d145_entry().split()).lower()
    assert "docker" in lowered, "the absent daemon must be named"
    assert "which docker flyctl fly psql" in lowered, "the command behind the claim, not a summary"
    assert "declaration" in lowered, "what IS established must be distinguished from what is not"
    assert "no fly credential" in lowered, "the second absence, which bounds the ops-scar claim"


def test_the_entry_records_the_ops_scar_as_reported_rather_than_observed():
    """⚠ The scar is Trinity's word and cannot be checked from here — no Fly credential, so
    `/srv/scripts/` is unreadable from this build. **What IS checkable is the hazard**, and the
    entry has to separate the two rather than let a report read as a measurement (`F-022`)."""
    flat = " ".join(_d145_entry().split())
    lowered = flat.lower()
    assert "kaylee" in lowered and "sftp" in lowered
    assert "/srv/scripts/" in flat
    assert "reported" in lowered, "a report must be labelled as one"
    assert "2170bd8" in flat, "the tree the hazard was measured against must be named"


def test_the_entry_states_the_two_line_shape_and_its_precedent():
    """⚠ The `.dockerignore` half is the one that reads as optional. The entry states it, and
    names `b2196e9` — the commit that shipped the ingest's three files together — rather than
    asserting the shape from memory."""
    flat = " ".join(_d145_entry().split())
    lowered = flat.lower()
    assert "b2196e9" in flat, "the precedent commit must be named, not alluded to"
    assert ".dockerignore" in flat
    assert "fails the build" in lowered
    assert "no docker daemon runs in ci" in lowered or "no docker daemon" in lowered


def test_the_entry_carries_a_deep_learning_justification():
    """⚠ CLAUDE.md's prime directive — and the honest form for a packaging PR: it adds no deep
    learning, and it protects the reproducibility of the one learned factor in a served number.
    An entry claiming new deep learning here would be the over-claim; an entry claiming none is
    relevant would be missing why the rule exists."""
    entry = _d145_entry()
    assert "Deep-learning justification" in entry
    lowered = " ".join(entry.split()).lower()
    assert "esmfold" in lowered and "plddt" in lowered
    assert "score_model" in lowered, "the factor the network supplies must be named"
    assert "adds no deep learning" in lowered, "the honest limit, stated rather than implied"


def test_the_entry_states_the_hard_stops_from_the_go():
    lowered = " ".join(_d145_entry().split()).lower()
    for claim, why in (
        ("copy scripts/", "the wholesale copy must be named as refused"),
        ("fit_scorer.py", "the fitter must be named, not left to a category"),
        ("d-079", "the ruling that bars the refit"),
        ("--load", "the ops step this PR does not take"),
        ("/srv/data/census/census_manifest.v7.csv", "the population path on the machine"),
        ("/data/artifacts", "the volume it must not be confused with"),
        ("f-014", "the duplicate-path class a second CSV copy would join"),
    ):
        assert claim in lowered, why


def test_the_entry_records_that_its_own_invariant_prediction_was_wrong():
    """⚠⚠ `D-016` / `F-044`: this entry predicted the citation-invariant output and the
    prediction was wrong — `origin/main` reports `['D-131', 'F-067']`, not a hole containing 145,
    because the RESERVED row is exactly what kept 145 resolved. **The wrong reading is kept
    beside the measured one** (D-129-C), because an entry that silently replaced it would read
    as though the checker had agreed with it all along."""
    flat = " ".join(_d145_entry().split())
    lowered = flat.lower()
    assert "was wrong" in lowered, "the failed prediction must be recorded, not overwritten"
    assert "['d-131', 'f-067']" in lowered, "the measured output, quoted"
    assert "caught this pr" in lowered, "the direction of the catch is the point"


def test_the_next_free_integer_is_named_and_barred_across_every_guard():
    """⚠⚠ The TENTH pass through this resolution, and the SECOND reserved integer to be SPENT
    rather than skipped (`D-142` was the first, the same day).

    **Bar OR name, never neither.** While an integer is unspent every enumerated guard must bar
    it; once an entry spends it, every guard must assert THAT ENTRY by heading. The third state —
    neither barred nor named — is how the #266/#267 collision got in, and it stays forbidden.

    ⚠⚠ **The bar is matched on `\\n### D-NNN" not in`, WITH the newline, and the first draft of
    this test matched without it and reported a contradiction that was not there.**
    `tests/test_d143_track_b_structural_only.py` is the meta-guard: it holds
    `'### D-145" not in'` as *data*, to check the other files, so a newline-less pattern found a
    "bar" in the very file whose job is to look for one and declared it both barring and naming.
    A guard that cannot tell an assertion from a string describing an assertion is the `F-026`
    shape — a check that shares its subject's vocabulary.
    """
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 145 in ids
    # ⚠⚠ 146 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS THIS TEST'S OWN DOCSTRING SAID IT
    # WOULD — the ELEVENTH pass, and the THIRD reserved integer SPENT rather than skipped. D-146
    # retires the Track B copy clause that denied the D-144 route existed, now that
    # `GET /api/census-structural-ranking` answers `valid`; it is copy only and ships no
    # `Dockerfile`, `.dockerignore` or image change, so nothing this suite measures moves. The bar
    # is REPLACED BY A NAME and `### D-147` takes it. Never a `>=`.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 must be the Track B live-route copy entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-147** by ADDING — the TWELFTH pass, and the FOURTH reserved integer
    # SPENT rather than skipped (142, 145 and 146 were the first three, all the same day). D-147
    # adds the `ecd_intermittent` disclosure on the **read** side only: the loader this entry baked
    # into the image is **byte-identical** (its sha256 pin below is untouched), **no `--load`
    # runs**, and no `Dockerfile` / `.dockerignore` byte moves. The bar is REPLACED BY A NAME and
    # `### D-148` takes it. Never a `>=`.
    assert re.search(r"^### D-147 — The census rank stops presenting a loop as an ectodomain",
                     LOG, re.M), (
        "D-147 must be the census `ecd_intermittent` entry, not some other entry that took "
        "the number"
    )
    assert "\n### D-148" not in LOG, (
        "D-148 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`"
    )

    guards = (
        "tests/test_d129_phase5_named_refuse_spec.py",
        "tests/test_d130_residual_rmsd_spec.py",
        "tests/test_d136_cancer_type.py",
        "tests/test_d139_served_path_flip.py",
        "tests/test_d140_pipeline_programme.py",
        "tests/test_d141_land_confidence_kabsch.py",
        "tests/test_d143_track_b_structural_only.py",
        "tests/test_d144_census_structural_rank.py",
    )
    for rel in guards:
        text = (ROOT / rel).read_text(encoding="utf-8")
        barred = r'\n### D-145" not in' in text
        named = "D-145 — The D-144 loader stops living on the production host" in text
        assert barred or named, (
            f"{rel} neither bars 145 nor names the entry that spends it"
        )
        assert not (barred and named), (
            f"{rel} both bars 145 and names an entry for it; both cannot be true"
        )
        barred_146 = r'\n### D-146" not in' in text
        named_146 = "D-146 — Track B stops denying the surface it is served on" in text
        assert barred_146 or named_146, (
            f"{rel} neither bars 146 nor names the entry that spends it"
        )
        assert not (barred_146 and named_146), (
            f"{rel} both bars 146 and names an entry for it; both cannot be true"
        )
        # ⚠⚠ WIDENED THE SAME WAY AT D-147 — and the pattern this check holds as *data* moved with
        # it. 147 is spent by the census `ecd_intermittent` disclosure, which is a **read-side**
        # change: the loader this entry baked into the image is byte-identical and no `--load`
        # runs. Bar OR name, never neither; the next free integer, 148, takes the bar.
        barred_147 = r'\n### D-147" not in' in text
        named_147 = "D-147 — The census rank stops presenting a loop as an ectodomain" in text
        assert barred_147 or named_147, (
            f"{rel} neither bars 147 nor names the entry that spends it"
        )
        assert not (barred_147 and named_147), (
            f"{rel} both bars 147 and names an entry for it; both cannot be true"
        )
        assert r'\n### D-148" not in' in text, (
            f"{rel} does not bar the next free integer"
        )


def test_the_reserved_row_is_retired_marker_safe_and_146_has_a_row():
    """⚠⚠ MARKER-SAFE, and the reason is another suite's guard rather than a style preference.
    `tests/test_d144_census_structural_rank.py` locates this row with
    `re.search(r"^\\| \\*\\*D-145\\*\\*", …)`, so striking the marker to `~~**D-145**~~` — the
    convention `~~**D-143**~~` uses — would break that guard instead of satisfying it. The `D-142`
    row records the same trap of itself, in the open."""
    assert re.search(r"^\| \*\*D-145\*\*", RESERVED, re.M), (
        "the D-145 row must keep its literal marker; retirement is recorded INSIDE the cell"
    )
    assert "~~**D-145**~~" not in RESERVED, (
        "striking the D-145 marker breaks tests/test_d144_census_structural_rank.py's lookup"
    )
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-145**"))
    assert "WRITTEN" in row, "the retired row must say it was written"
    assert "Original reservation text" in row, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)"
    )
    assert re.search(r"^\| \*\*D-146\*\*", RESERVED, re.M), (
        "D-146 is cited in order to bar it, so it must be a RESERVED row or the citation "
        "invariant has a hole indistinguishable from D-062's"
    )


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ `RESERVED.md`'s own command, run rather than quoted. **Read the output, not an exit
    code**: the only passing result is that nothing new is unresolved. `D-131` (the suffix half
    of `### D-130-B / D-131`) and `F-067` (open in #222) are pre-existing."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}"
    )


def test_the_architecture_doc_records_the_baked_paths():
    """⚠ CLAUDE.md rule 2: a PR that changes deployment shape updates `ARCHITECTURE.md` in the
    same PR, and before the PR is filed."""
    flat = " ".join(ARCH.split())
    assert "/srv/scripts/census_structural_rank.py" in flat
    assert "/srv/data/census/census_manifest.v7.csv" in flat
    assert "/data/artifacts" in flat, "the volume the image data dir is NOT must stay named"
    assert "D-145" in flat


def test_the_test_plan_carries_the_d145_addendum_on_an_id_nobody_else_holds():
    """⚠ T-ids have collided four times in six days here. The check is that this addendum's id
    appears in NO other addendum, not merely that a number was chosen."""
    plan = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
    start = plan.index("### D-145 (this PR;")
    nxt = plan.index("## Addendum", start)
    mine, others = plan[start:nxt], plan[:start] + plan[nxt:]
    assert "(this PR; T-1252)" in mine
    assert "| **T-1252** |" in mine, "T-1252 has no row in the D-145 addendum"
    assert "| **T-1252** |" not in others, (
        "T-1252 is claimed by another addendum as well — the collision is not resolved"
    )
    assert "no docker daemon" in mine.lower(), (
        "the addendum must state what these tests cannot establish"
    )
