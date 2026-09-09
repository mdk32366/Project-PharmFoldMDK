"""D-153 — the D-149 SEER burden loader is baked into the serving image. All of these must go red.

⚠⚠ **THE SAME DEFECT `D-145` FIXED, ARRIVING AGAIN FOUR MERGES LATER — which is the argument for
this file rather than for a convention.** `### D-149` shipped `data/burden/`, migration `0013`, two
tables and two routes, and left `scripts/seer_cancer_burden.py` out of the image. Reported
2026-09-09: the cancer-burden API answered **500** on Fly until `alembic upgrade head` applied
`0013` and the loader — put on `/srv/scripts/` by a one-shot `sftp` — was run with `--load`,
persisting `cancer_burden_runs` id=1 with 174 figures. **A rebuilt image would have dropped it.**
Measured on the tree rather than taken on trust: `git show 6f9613c:Dockerfile | rg 'COPY scripts/'`
(D-149's merge) and the same command on `41b9b3b` (this branch's base) each return **exactly two**
lines, and neither names the burden loader.

⚠ **What this suite adds, and it is a DIRECTION rather than a count.**
`tests/test_serving_image_contents.py` holds the UPPER bound — the scripts in the image are a subset
of the permitted three — and **a subset test is satisfied perfectly by an empty set**. Deleting the
`COPY` line keeps it green. So the property the GO asks for (*"must go red if the COPY is
deleted"*) needs a **positive** assertion, and it is here, in `tests/test_image_contents.py` and in
`tests/test_d145_bake_structural_loader.py`.

⚠ **What this suite CANNOT establish, said plainly rather than implied away.** No docker daemon runs
in the gate, so nothing here proves the *built image* contains the file. These are assertions about
the **declaration** — the `Dockerfile` names it, the build context admits it, the file exists so the
`COPY` is not a typo. The build is the other half of the proof, and it is a loud half: a `COPY` of a
path `.dockerignore` excludes fails the build rather than shipping nothing.

⚠ Tree properties throughout, never a `git diff` against `origin/main` — the gate checks out a merge
ref at depth 1, so a diff-based check would pass by erroring (D-139's precedent, restated at D-145).
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")
DOCKERIGNORE = (ROOT / ".dockerignore").read_text(encoding="utf-8")
FLY_TOML = (ROOT / "fly.toml").read_text(encoding="utf-8")
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")

INGEST = "scripts/census_ingest_features.py"
RANK_LOADER = "scripts/census_structural_rank.py"
BURDEN_LOADER = "scripts/seer_cancer_burden.py"

#: The scripts the serving image is permitted to hold, in the order they are copied.
BAKED = (INGEST, RANK_LOADER, BURDEN_LOADER)

#: The two files `COPY data/` already ships and that the burden loader reads. ⚠ Named so that a
#: *second*, narrower copy aimed at `data/burden/` is caught as the duplicate-path defect it is.
BURDEN_INPUTS = (
    "data/burden/seer_us_cancer_burden.v1.csv",
    "data/burden/seer_us_cancer_burden.provenance.json",
)


def _instructions(text: str) -> list[str]:
    """Dockerfile INSTRUCTION lines only. A comment is a line whose first non-whitespace character
    is `#`; inline `#` is not a comment in Dockerfile syntax. ⚠ Stripping comments is not tidiness —
    every comment in that file *discusses* the things these assertions forbid, so a grep over the
    raw text is satisfied by the prose that warns against them (F-044)."""
    return [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def _runtime_instructions() -> list[str]:
    """Instructions from the LAST ``FROM`` onward — the runtime stage. Stage 1 is the Node builder,
    and DEP-001's rules are about what *runs*."""
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


def _dockerignore_lines() -> list[str]:
    return [ln.strip() for ln in DOCKERIGNORE.splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


# ─────────────── T-1256 — the COPY is present, named, and one file at a time


def test_the_burden_loader_is_baked_in_and_this_is_the_assertion_the_scar_needed():
    """⚠⚠ THE ONE THE OPS SCAR ASKS FOR. Delete this `COPY` line and this reddens;
    `test_only_the_allowed_scripts_are_copied` stays green, because
    `{ingest, rank} ⊆ {ingest, rank, burden}` is true. **A set bound cannot see an absence**, and
    the absence is what happened — twice now, which is why the positive assertion is per file."""
    assert f"COPY {BURDEN_LOADER} ./scripts/" in _runtime_instructions(), (
        "D-153: the runtime stage must carry `COPY scripts/seer_cancer_burden.py ./scripts/` "
        "verbatim — an absent COPY is invisible to every subset guard in "
        "tests/test_serving_image_contents.py"
    )
    assert (ROOT / BURDEN_LOADER).is_file(), (
        f"{BURDEN_LOADER} is copied into the image but does not exist — that fails the BUILD during "
        f"a deploy, not here, so it is caught here instead"
    )


@pytest.mark.parametrize("rel", BAKED)
def test_the_runtime_stage_names_each_baked_script_as_its_own_copy(rel):
    """⚠ The GO's exact shape: *one explicit COPY, not `COPY scripts/`.* Asserted per file, so the
    failure message says WHICH one went missing rather than that a set changed size. ⚠ All three are
    checked and not only the new one: a guard written for one file and left there stops watching the
    moment a second arrives, which is precisely how this defect recurred."""
    expected = f"COPY {rel} ./scripts/"
    assert expected in _runtime_instructions(), (
        f"D-153: the runtime stage must carry `{expected}` verbatim"
    )


def test_the_three_copies_are_the_whole_set_and_the_directory_is_never_copied():
    """⚠ The bar the growing file list must not become. `D-079` dec 1 bars a refit outright and
    `scripts/fit_scorer.py` IS the fitter — `COPY scripts/` would leave a barred operation one
    `fly ssh` away behind no guard at all.

    ⚠⚠ **It is the DIRECTORY bar that protects the fitter, not the by-name check that reads as
    though it did** — D-145 measured this under revert. A Dockerfile `COPY` yields its *source
    token*, which for a directory is `scripts/` and never `scripts/fit_scorer.py`, so a
    `WRITERS` intersection is empty on exactly the edit that ships the fitter. Both halves are
    asserted, the directory bar first because it is the one that bites.
    """
    sources = _copy_sources(_instructions(DOCKERFILE))
    bad = [s for s in sources if s.rstrip("/.") == "scripts" or s.startswith("scripts/*")]
    assert not bad, f"D-153: a scripts DIRECTORY is copied ({bad}) — never the directory"
    assert {s for s in sources if s.startswith("scripts/")} == set(BAKED), (
        f"the scripts entering the image must be exactly {list(BAKED)}; "
        f"found {sorted(s for s in sources if s.startswith('scripts/'))}"
    )
    assert "fit_scorer" not in "\n".join(_instructions(DOCKERFILE)), (
        "D-079 dec 1: the fitter must never reach the production host"
    )


def test_the_build_context_re_includes_exactly_the_three_named_files():
    """⚠⚠ The half of the shape that reads as optional and is not. `scripts/` is excluded from the
    build CONTEXT, so a `COPY` with no matching `!` line names a path docker cannot see and **fails
    the build** — during a deploy, because no daemon runs in the gate. `b2196e9` shipped the
    ingest's `Dockerfile` line, its `.dockerignore` negation and its test in ONE commit for exactly
    this reason; `a0ac6ce` did the same for the second file; this is the third."""
    lines = _dockerignore_lines()
    assert "scripts/" in lines, "`scripts/` must stay excluded from the build context"
    negations = {ln[1:] for ln in lines if ln.startswith("!")}
    assert {n for n in negations if n.startswith("scripts/")} == set(BAKED), (
        f"the context must re-include exactly {list(BAKED)} — never a pattern, never the "
        f"directory; found {sorted(n for n in negations if n.startswith('scripts/'))}"
    )
    assert f"!{BURDEN_LOADER}" in lines, (
        "D-153: the negation is the half that looks optional — without it the COPY above names a "
        "path docker cannot see and the DEPLOY fails, not the gate"
    )


def test_a_negation_is_never_a_pattern_or_the_directory():
    """⚠ The convenient broadening is `!scripts/*.py`, which reads as tidier and re-admits the
    fitter to the build context in one keystroke. It is barred here explicitly rather than left to
    the set equality above, because a set can be satisfied by editing the set."""
    negations = [ln[1:] for ln in _dockerignore_lines() if ln.startswith("!")]
    offenders = [n for n in negations
                 if n.startswith("scripts") and ("*" in n or n.rstrip("/.") == "scripts")]
    assert not offenders, (
        f"D-153: the re-inclusions must be named files; found the pattern/directory {offenders}"
    )


# ─────────────── the inputs are already shipped, and the paths resolve on the machine


def test_no_csv_is_re_copied_for_the_burden_loader():
    """⚠ Hard stop from the GO. `COPY data/ ./data/` already ships `data/burden/`; a second,
    narrower copy aimed at it would be two paths to one artefact — `F-014`'s class."""
    data_copies = [s for s in _copy_sources(_instructions(DOCKERFILE))
                   if s.split("/")[0] == "data"]
    assert data_copies == ["data/"], (
        f"data/ must be copied exactly once and as the whole directory; found {data_copies}"
    )


@pytest.mark.parametrize("rel", BURDEN_INPUTS)
def test_the_burden_inputs_exist_under_data_so_copy_data_really_ships_them(rel):
    """⚠ A loader whose artefact is absent fails at run time on the production host, and the
    provenance sidecar is not optional: `load_provenance` raises `IngestRefused` without it,
    because the sha256, the release pin and the attribution live there."""
    assert (ROOT / rel).is_file(), f"{rel} must exist under data/ — COPY data/ is what ships it"


def test_the_loader_and_its_artefact_resolve_under_srv_without_a_path_constant_moving():
    """⚠ A loader that cannot find its inputs is worse than one that is absent, so the path is
    derived here rather than asserted as a string in a comment.

    `WORKDIR /srv` + the loader's own two-parents rule puts it at
    `/srv/scripts/seer_cancer_burden.py` and its artefact at
    `/srv/data/burden/seer_us_cancer_burden.v1.csv`. **Both are the repo's own relative shape**,
    which is precisely why baking the file in changes no constant.

    ⚠⚠ **THE IDIOM IS NOT `D-145`'s AND THE PIN HAD TO CHANGE WITH IT.**
    `scripts/census_structural_rank.py` writes `.resolve().parent.parent`; this loader writes
    `.resolve().parents[1]`. Same rule, different spelling — reusing D-145's literal here would have
    asserted a string this file does not contain, so the assertion is made on the **parsed** call
    instead of on a substring that happens to appear.
    """
    assert "WORKDIR /srv" in _runtime_instructions()

    src = (ROOT / BURDEN_LOADER).read_text(encoding="utf-8")
    tree = ast.parse(src)
    repo_assign = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "REPO" for t in node.targets)
    ]
    assert len(repo_assign) == 1, "the loader must derive REPO exactly once"
    expr = ast.unparse(repo_assign[0].value)
    assert expr == "pathlib.Path(__file__).resolve().parents[1]", (
        f"the loader's repo root is the file's grandparent; it now reads `{expr}` — if that rule "
        f"changes, /srv/scripts/ stops resolving to /srv and the artefact path moves with it"
    )
    assert 'BURDEN_DIR = REPO / "data" / "burden"' in src, (
        "the artefact directory must stay derived from REPO, not re-rooted"
    )


def test_the_fly_volume_is_not_the_images_data_directory():
    """⚠⚠ `/srv/data` and `/data` are one path segment apart in a way that reads as a typo. The
    Volume holds fold artifacts (`D-031`); the burden CSV lives in the IMAGE. An edit that
    "corrected" one to the other would move the loader's input onto a volume that has never held
    it."""
    assert re.search(r'destination\s*=\s*"/data/artifacts"', FLY_TOML), (
        "fly.toml's mount destination moved — the /srv/data vs /data/artifacts distinction this "
        "suite records is stated against that line"
    )
    assert '"/srv' not in FLY_TOML, "the Fly Volume must never be mounted inside /srv"


# ─────────────── hard stops: nothing is run, and no writer sneaks in behind the copy


def test_nothing_in_this_pr_runs_the_loader_or_the_migration():
    """⚠ Hard stops from the GO: **no `--load`, no migration.** `alembic 0013` is already applied on
    Fly and burden run id=1 is already `valid` with its 174 figures; a rerun would mark that live run
    `superseded` and insert a fresh one for no reason — a change to served data wearing a packaging
    PR's clothes.

    ⚠ The image gives the loader its CODE, never a credential: `--load` needs a `DATABASE_URL` that
    only Fly holds, which is why `build_engine` refuses loudly when it is absent.
    """
    instructions = _instructions(DOCKERFILE)
    for line in instructions:
        verb = line.split()[0].upper()
        if verb in ("RUN", "CMD", "ENTRYPOINT"):
            for forbidden in ("seer_cancer_burden", "census_structural_rank", "alembic", "--load"):
                assert forbidden not in line, (
                    f"the image must not EXECUTE {forbidden}, only carry the file: {line}"
                )
    assert any(ln.startswith('CMD ["uvicorn"') for ln in instructions), (
        "the container's command is still uvicorn — D-153 adds a file, not a startup step"
    )
    workflows = ROOT / ".github" / "workflows"
    for path in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        assert "seer_cancer_burden" not in path.read_text(encoding="utf-8"), (
            f"{path.name} references the burden loader — CI must not run an ops load"
        )


def test_the_loader_still_refuses_to_reach_the_network_now_that_it_ships():
    """⚠⚠ THE PROPERTY THAT MAKES BAKING IT IN SAFE, RE-ASSERTED HERE RATHER THAN INHERITED.
    `D-149` proved the loader imports no HTTP client while the loader was **not** on the production
    host. It is on it now, so the claim has to hold from the image's side too: a serving host must
    not be able to silently re-derive a figure this repository was never reviewed with.

    ⚠ And the converse, so the check is not vacuous: `scripts/fetch_seer_burden.py` — the network
    half — is asserted to be **absent** from the image, which is the whole reason there are two
    files.
    """
    tree = ast.parse((ROOT / BURDEN_LOADER).read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    for client in ("httpx", "requests", "urllib", "urllib.request", "http.client", "socket",
                   "aiohttp"):
        assert client not in modules, (
            f"the baked loader imports {client} — a serving host must not be able to re-fetch"
        )
    assert "scripts/fetch_seer_burden.py" not in _copy_sources(_instructions(DOCKERFILE)), (
        "the network half must never enter the image; if it did, the check above would be moot"
    )


def test_no_writing_script_reached_the_image_alongside_the_new_copy():
    """⚠ Stated against the writers BY NAME rather than by category, because the edit that ships
    them is a diff one keystroke wider than the one this PR makes."""
    copied = {s for s in _copy_sources(_instructions(DOCKERFILE)) if s.startswith("scripts/")}
    writers = {
        "scripts/fit_scorer.py",
        "scripts/extract_features.py",
        "scripts/census_ingest.py",
        "scripts/hpa_census_coverage.py",
        "scripts/hpa_v22_verify.py",
        "scripts/tranche6_domain_survey.py",
        "scripts/fetch_seer_burden.py",
    }
    leaked = sorted(copied & writers)
    assert not leaked, f"scripts that WRITE or FETCH reached the serving image: {leaked}"


def test_no_gpu_world_and_no_worker_entered_the_image():
    """⚠ DEP-001 / D-004 / D-018, restated because this PR touches the `Dockerfile` at all."""
    lowered = "\n".join(_instructions(DOCKERFILE)).lower()
    for forbidden in ("torch", "transformers", "bitsandbytes", "streamlit",
                      "copy worker", "add worker"):
        assert forbidden not in lowered, f"DEP-001: {forbidden!r} must not be in the image"
    assert "worker/" in DOCKERIGNORE, ".dockerignore must keep worker/ out of the context"


# ─────────────── the living log leads it, and the id guards were widened by ADDING


def _d153_entry() -> str:
    """The D-153 entry only, bounded by the NEXT `### ` heading whatever it is."""
    start = LOG.index("\n### D-153 —") + 1
    nxt = re.search(r"^### (?!D-153\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠ The check is the `### D-153` HEADING, never a citation of it (D-062 / method-note item 7).
    PR #90 named `D-062` in its title and added no entry, and thirteen later citations treated the
    missing entry as settled authority."""
    assert re.search(r"^### D-153 — The D-149 burden loader stops living on the production host",
                     LOG, re.M)
    assert len(re.findall(r"^### D-153 —", LOG, re.M)) == 1, "exactly one D-153 entry"
    assert LOG.index("### D-153 —") < LOG.index("### D-151 —"), "newest first"
    # ⚠ NAMES NO LEADER BY NUMBER — an assertion that pins *which* entry is newest expires the
    # moment anything newer lands, for reasons that have nothing to do with this entry (D-147's
    # recorded trap).
    assert re.search(r"^## Log \(newest first\)\s*\n\s*### D-\d{3} — ", LOG, re.M)


def test_the_entry_leads_with_what_this_build_could_not_verify():
    """⚠⚠ D-016, and the disqualifying fact first: no image was built here. A packaging entry that
    reads as though it had verified the artefact is the `F-047` shape — clean, plausible, and about
    a different thing than it appears to be."""
    lowered = " ".join(_d153_entry().split()).lower()
    assert "docker" in lowered, "the absent daemon must be named"
    assert "which docker flyctl fly psql" in lowered, "the command behind the claim, not a summary"
    assert "declaration" in lowered, "what IS established must be distinguished from what is not"
    assert "no fly credential" in lowered, "the second absence, which bounds the ops-scar claim"


def test_the_entry_records_the_ops_scar_as_reported_rather_than_observed():
    """⚠ The scar is Kaylee's word and cannot be checked from here — no Fly credential, so
    `/srv/scripts/` is unreadable and `cancer_burden_runs` unqueryable from this build. **What IS
    checkable is the hazard**, and the entry has to separate the two rather than let a report read
    as a measurement (`F-022`)."""
    flat = " ".join(_d153_entry().split())
    lowered = flat.lower()
    assert "kaylee" in lowered and "sftp" in lowered
    assert "/srv/scripts/" in flat
    assert "unverified" in lowered or "word, not a discovery" in lowered, (
        "a report must be labelled as one"
    )
    assert "500" in flat, "the symptom the scar was seen as must be named"
    assert "id=1" in flat and "174" in flat, "the reported run and row count, quoted as reported"
    assert "6f9613c" in flat and "41b9b3b" in flat, (
        "the trees the hazard was measured against must be named, not alluded to"
    )


def test_the_entry_states_the_two_line_shape_and_its_precedent():
    """⚠ The `.dockerignore` half is the one that reads as optional. The entry states it and names
    the commits that shipped the pattern twice before, rather than asserting it from memory."""
    flat = " ".join(_d153_entry().split())
    lowered = flat.lower()
    assert "b2196e9" in flat, "the ingest's precedent commit must be named"
    assert "a0ac6ce" in flat, "D-145's commit — the second time the shape was used — must be named"
    assert ".dockerignore" in flat
    assert "fails the build" in lowered
    assert "no docker daemon runs in ci" in lowered or "no docker daemon" in lowered


def test_the_entry_carries_a_deep_learning_justification_and_states_its_own_limit():
    """⚠⚠ CLAUDE.md's prime directive, and the honest form for a packaging PR on a surface that
    joins to no score. `D-145` could point at `score_model` (the ESMFold pLDDT) as the learned
    factor its permanence protected. **This entry cannot**, because `cancer_burden_stat` carries no
    score at all — so it must claim the narrower thing (the rebuild-from-committed-bytes property of
    the serving tier) rather than borrow D-145's argument."""
    entry = _d153_entry()
    assert "Deep-learning justification" in entry
    lowered = " ".join(entry.split()).lower()
    assert "adds no deep learning" in lowered, "the honest limit, stated rather than implied"
    assert "esmfold" in lowered and "score_model" in lowered, (
        "the learned factor must be named in order to say this surface does NOT carry it"
    )
    assert "joins to no protein and no score" in lowered, "D-093 dec 1's wall, restated"


def test_the_entry_states_the_hard_stops_from_the_go():
    lowered = " ".join(_d153_entry().split()).lower()
    for claim, why in (
        ("copy scripts/", "the wholesale copy must be named as refused"),
        ("fit_scorer.py", "the fitter must be named, not left to a category"),
        ("d-079", "the ruling that bars the refit"),
        ("--load", "the ops step this PR does not take"),
        ("0013", "the migration that is already applied and is not re-run"),
        ("/srv/data/burden/seer_us_cancer_burden.v1.csv", "the artefact path on the machine"),
        ("/data/artifacts", "the volume it must not be confused with"),
        ("f-014", "the duplicate-path class a second CSV copy would join"),
    ):
        assert claim in lowered, why


def test_the_entry_records_that_the_defect_recurred_rather_than_presenting_it_as_new():
    """⚠⚠ The finding-shaped part, and it is uncomfortable rather than flattering: `D-145` ruled
    this exact permanence rule four merges earlier and `D-149` shipped a loader outside the image
    anyway. An entry that read as *"a loader needs baking in"* would be true and would hide that the
    rule already existed and was not applied."""
    lowered = " ".join(_d153_entry().split()).lower()
    assert "d-145" in lowered, "the entry that already ruled this must be named"
    assert "again" in lowered or "recurred" in lowered or "second time" in lowered, (
        "the recurrence must be recorded, not presented as a first discovery"
    )
    assert "d-149" in lowered, "the entry that shipped the loader without the image line"


def test_the_next_free_integer_is_named_and_both_holds_stay_barred():
    """⚠⚠ **Bar OR name, never neither.** `### D-153` is claimed by name here; `### D-148` is a
    `RESERVED.md` HOLD for the trafficking Spec and stays BARRED; `### D-152` is a HOLD for the
    concurrent sitewide-layout lane and stays BARRED; `### D-154` takes the next-free bar. ⚠ Nothing
    is relaxed to a `>=`: a `>=` here would pass on a log with no entries at all.

    ⚠⚠ **THIS IS THE FIRST PASS WHERE THE CLAIMED INTEGER IS NOT THE ONE THE GUARDS BARRED.** The
    inherited bar sat on **152**, and 152 is not this entry's to spend — so 153 was claimed *over*
    an unbarred hole, which is the state the #266/#267 collision came from. It is made safe the only
    way available: 153 gets a heading AND a `RESERVED.md` row in the same commit, 152 keeps its bar
    and gains a hold row, and the pointer skips both holds.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as *data* in
    order to check the others; a newline-less match would find a "bar" in the file whose job is to
    look for one. That is D-145's recorded mistake, not rediscovered here.
    """
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 153 in ids, "this entry did not claim its own integer"
    assert 148 not in ids and 152 not in ids and 154 not in ids
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until that Spec "
        "claims it by name — never admitted by a `>=`")
    assert "\n### D-152" not in LOG, (
        "D-152 is a RESERVED HOLD for the concurrent sitewide-layout lane and must stay unspent "
        "until that lane claims it by name — never admitted by a `>=`")
    assert "\n### D-154" not in LOG, (
        "D-154 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`")


def test_the_inherited_guards_were_widened_by_adding_a_name_and_never_by_relaxing():
    """⚠⚠ The enumerated successor lists are what actually catch a collision, and they are checked
    here as *data*: each must NAME `D-153` and must NOT have grown a `>=`. A relaxation would be
    invisible in a diff that also adds a legitimate name."""
    for rel in ("tests/test_d129_phase5_named_refuse_spec.py",
                "tests/test_d130_residual_rmsd_spec.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "D-153 — The D-149 burden loader stops living on the production host" in text, (
            f"{rel} does not NAME the entry that spent 153")
        assert r'\n### D-154" not in' in text, f"{rel} does not bar the next free integer"
        assert r'\n### D-148" not in' in text, f"{rel} stopped barring the trafficking hold"
        assert r'\n### D-152" not in' in text, f"{rel} does not bar the sitewide-layout hold"
        assert "if i > 129] >=" not in text and "if i > 130] >=" not in text, (
            f"{rel} relaxed its enumeration to a `>=` — the widening must ADD a name")


def test_the_reserved_map_retires_153_marker_safe_and_records_both_holds():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: this suite locates the
    153 row with `re.search(r"^\\| \\*\\*D-153\\*\\*", …)`, so striking it to `~~**D-153**~~` — the
    convention `~~**D-143**~~` uses — would break this guard instead of satisfying it. The D-142 /
    D-145 / D-146 / D-147 / D-150 / D-151 rows each record the same trap of themselves."""
    assert re.search(r"^\| \*\*D-153\*\*", RESERVED, re.M), (
        "the D-153 row must keep its literal marker; retirement is recorded INSIDE the cell")
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-153**"))
    assert "WRITTEN" in row, "the retired row must say it was written"
    assert re.search(r"^\| \*\*D-154\*\*", RESERVED, re.M), (
        "D-154 is cited in order to bar it, so it must be a RESERVED row or the citation invariant "
        "has a hole indistinguishable from D-062's")
    # ⚠ the two holds are rows, and each says what it is held FOR — an unexplained gap in an
    # enumerated set reads as an oversight to the next reader
    row152 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-152**"))
    assert "layout" in row152.lower(), "the 152 hold does not say what it is held FOR"
    row148 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-148**"))
    assert "trafficking" in row148.lower(), "the 148 hold stopped saying what it is held FOR"
    # ⚠ AT LINE START, not anywhere in the file: those cells EXPLAIN that their markers must not be
    # struck, so they necessarily quote the struck form (`F-024` — match the thing you mean).
    assert not re.search(r"^\| ~~\*\*D-15[234]\*\*~~", RESERVED, re.M), (
        "a marker is struck through; that breaks this suite's lookup instead of satisfying it")


def test_the_pointer_moved_in_this_commit_and_skips_both_holds():
    """⚠ `RESERVED.md`'s own rule: *the pointer moves in the SAME commit that spends the integer*,
    and *"next free"* means the lowest AVAILABLE integer rather than the lowest unwritten one."""
    assert "Next free `D-` integer: **`D-154`**" in RESERVED
    for unavailable in ("D-148", "D-149", "D-150", "D-151", "D-152", "D-153"):
        assert f"Next free `D-` integer: **`{unavailable}`**" not in RESERVED, (
            f"the pointer still names {unavailable}, which would hand a spent or held integer to "
            f"the next writer")


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ `RESERVED.md`'s own command, run rather than quoted. **Read the output, not an exit code**:
    the only passing result is that nothing NEW is unresolved. `D-131` (the suffix half of
    `### D-130-B / D-131`) and `F-067` (open in #222) are pre-existing and untouched by this ship."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}")


def test_the_architecture_doc_records_the_third_baked_path():
    """⚠ CLAUDE.md rule 2: a PR that changes deployment shape updates `ARCHITECTURE.md` in the same
    PR, and before the PR is filed."""
    flat = " ".join(ARCH.split())
    assert "/srv/scripts/seer_cancer_burden.py" in flat
    assert "/srv/data/burden/seer_us_cancer_burden.v1.csv" in flat
    assert "/data/artifacts" in flat, "the volume the image data dir is NOT must stay named"
    assert "D-153" in flat


def test_the_test_plan_carries_the_d153_addendum_on_an_id_nobody_else_holds():
    """⚠ T-ids have collided repeatedly here. The check is that this addendum's id appears in NO
    other addendum, not merely that a number was chosen."""
    plan = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
    start = plan.index("### D-153 (this PR;")
    nxt = plan.index("## Addendum", start)
    mine, others = plan[start:nxt], plan[:start] + plan[nxt:]
    assert "(this PR; T-1256)" in mine
    assert "| **T-1256** |" in mine, "T-1256 has no row in the D-153 addendum"
    assert "| **T-1256** |" not in others, (
        "T-1256 is claimed by another addendum as well — the collision is not resolved")
    assert "no docker daemon" in mine.lower(), (
        "the addendum must state what these tests cannot establish")
