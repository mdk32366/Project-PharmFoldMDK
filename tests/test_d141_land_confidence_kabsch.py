"""D-141 — the lander that gives D-139's gate bytes to answer with. All of these must go red.

D-139 shipped a served-path gate and printed **eligible 17 / flipped 0**: the
recorded seventeen all resolve to the assembler under
``no_confidence_kabsch_artifacts`` because the D-126-A OPS trees were never on
the serving volume. ``scripts/land_d139_confidence_kabsch.py`` copies them there.
It is a copy and nothing else, and this suite is the proof of the "nothing else".

The hard stops, each written so it fails loudly rather than quietly:

* **the allowlist is the authority** — a parent outside the recorded seventeen is
  refused even with a perfect accepted tree waiting in the source root
  (``test_a_parent_outside_the_seventeen_is_refused_*``);
* **a refused or incomplete run never lands** — ``accepted: false``, a missing
  ``stitched.pdb`` and an unreadable provenance are three *named* skips, and none
  of them puts a byte on the destination;
* **the assembler and ``kabsch/`` are never written** — the two directories this
  script must not become are checked after a real land, on disk;
* **a partial copy reads as not-landed, never as landed-wrong** — proved by
  interrupting one;
* **"landed" is verified through D-139's own resolver**, not counted here.

⚠ Every test writes under ``tmp_path``. Nothing in this suite may create a
``confidence_kabsch/`` directory inside the repository — D-139's
``test_no_confidence_kabsch_tree_is_committed_so_nothing_flips_here`` is the
guard, and a test fixture would trip it exactly like a committed tree.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from app.served_path_policy import (
    D126_SERVED_PASS_SUBSET,
    NO_ARTIFACTS,
    SERVED_ASSEMBLER,
    SERVED_CONFIDENCE_KABSCH,
    resolve_served_path,
)
from scripts.land_d139_confidence_kabsch import (
    COPY_ORDER,
    DECISION,
    LANDED,
    LANDED_FILES,
    PREFERRED_FILES,
    REQUIRED_FILES,
    SKIP_DEST_EXISTS,
    SKIP_NO_SOURCE_TREE,
    SKIP_NO_SUCCESS_PDB,
    SKIP_RUN_REFUSED,
    SKIP_UNREADABLE_PROVENANCE,
    LandRefused,
    land,
    land_parent,
    main,
    require_pass_subset,
)

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (ROOT / "scripts" / "land_d139_confidence_kabsch.py").read_text(encoding="utf-8")
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

#: In the seventeen. 3097 is mid-list, so an off-by-one at either end still reds.
PASS_PARENT = 3097
#: Outside it, and chosen to be the *hardest* case: 3394 is one of the two
#: parents D-126 OPS actually recovered, and it is still barred — by Phase 4
#: `rmsd_gt_10`, recorded later. A lander that trusted `accepted: true` in the
#: provenance instead of the allowlist would flip exactly this parent.
NON_PASS_PARENT = 3394


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _tree(
    out_root: Path,
    parent_id: int,
    *,
    accepted: bool = True,
    with_pdb: bool = True,
    with_seams: bool = True,
    with_siblings: bool = True,
    with_tile_transforms: bool = True,
    provenance_parent: int | None = None,
    provenance_text: str | None = None,
) -> Path:
    """A D-126-A-shaped source tree, in the layout ``confidence_kabsch_out_dir`` writes."""
    d = out_root / "confidence_kabsch" / str(parent_id)
    d.mkdir(parents=True, exist_ok=True)
    if provenance_text is not None:
        (d / "provenance.json").write_text(provenance_text, encoding="utf-8")
    else:
        (d / "provenance.json").write_text(
            json.dumps(
                {
                    "algorithm": "overlap_confidence_kabsch_then_winning_tile",
                    "decision": "D-126",
                    "parent_job_id": (
                        provenance_parent if provenance_parent is not None else parent_id
                    ),
                    "accepted": accepted,
                    "rmsd_refuse_angstrom": 10.0,
                    "seams": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    if with_pdb and accepted:
        (d / "stitched.pdb").write_text(
            f"HEADER d126 {parent_id}\nATOM      1  CA  GLY A   1\nEND\n", encoding="utf-8"
        )
    if with_seams:
        (d / "seams.jsonl").write_text(
            json.dumps({"moving_tile_index": 2, "rmsd_angstrom": 1.25}) + "\n",
            encoding="utf-8",
        )
    if with_siblings and accepted:
        (d / "stitched_plddt.json").write_text(json.dumps([88.0, 91.0]), encoding="utf-8")
        (d / "stitched_pae.json").write_text(json.dumps([[0.0]]), encoding="utf-8")
    if with_tile_transforms:
        (d / "tile2_transformed.pdb").write_text("ATOM      1  CA  GLY A   1\n", encoding="utf-8")
    return d


def _served(dest_root: Path, parent_id: int) -> dict:
    return resolve_served_path(
        dest_root, parent_analysis_id=parent_id, parent_job_id=parent_id
    )


# ───────────────────────── the allowlist is the authority ─────────────────────

def test_a_parent_outside_the_seventeen_is_refused_even_with_a_perfect_tree(tmp_path):
    """⚠⚠ The hard stop. An accepted D-126 tree is not authorisation to serve it."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, NON_PASS_PARENT, accepted=True)
    with pytest.raises(LandRefused) as exc:
        land_parent(src, dest, NON_PASS_PARENT)
    assert str(NON_PASS_PARENT) in str(exc.value)
    assert "PASS subset" in str(exc.value)
    assert not (dest / "confidence_kabsch").exists(), "a refused parent wrote to disk"


def test_a_sweep_never_copies_a_non_allowlisted_tree_sitting_in_the_source(tmp_path):
    """⚠ The quiet version of the same failure: nobody asked for it, it was just *there*."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    for stranger in (NON_PASS_PARENT, 2939, 3272, 9999):
        _tree(src, stranger, accepted=True)
    report = land(src, dest)
    landed_ids = {o.parent_id for o in report.outcomes if o.landed}
    assert landed_ids == {PASS_PARENT}
    on_disk = sorted(int(p.name) for p in (dest / "confidence_kabsch").iterdir())
    assert on_disk == [PASS_PARENT], f"a non-allowlisted tree landed: {on_disk}"
    assert set(o.parent_id for o in report.outcomes) == set(D126_SERVED_PASS_SUBSET)


def test_every_id_the_lander_will_write_is_in_the_policy_subset():
    for pid in D126_SERVED_PASS_SUBSET:
        assert require_pass_subset(pid) == pid
    for pid in (2939, 3272, 3394, 0, -1, 99999):
        with pytest.raises(LandRefused):
            require_pass_subset(pid)


def test_the_allowlist_is_imported_not_retyped():
    """⚠ D-062's shape: a second copy of the seventeen, free to disagree with the first."""
    assert "from app.served_path_policy import" in SCRIPT
    assert "D126_SERVED_PASS_SUBSET" in SCRIPT
    ids = {int(m) for m in re.findall(r"\b(2[89]\d\d|3[0-5]\d\d)\b", SCRIPT)}
    assert ids <= {PASS_PARENT}, f"the script types parent ids of its own: {sorted(ids)}"


# ───────────────────── a refused or incomplete run never lands ────────────────

def test_a_recorded_refusal_is_a_named_skip_and_writes_nothing(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT, accepted=False)
    outcome = land_parent(src, dest, PASS_PARENT)
    assert outcome.outcome == "skip"
    assert outcome.reason == SKIP_RUN_REFUSED == "confidence_kabsch_refused"
    assert not (dest / "confidence_kabsch" / str(PASS_PARENT)).exists()
    assert _served(dest, PASS_PARENT)["served"] == SERVED_ASSEMBLER


def test_an_accepted_run_with_no_stitched_pdb_is_a_named_skip_and_writes_nothing(tmp_path):
    """⚠ Fail-closed: `accepted: true` beside a missing PDB is the shape that would
    put a flipped parent in front of a 404."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    d = _tree(src, PASS_PARENT, accepted=True)
    (d / "stitched.pdb").unlink()
    outcome = land_parent(src, dest, PASS_PARENT)
    assert outcome.reason == SKIP_NO_SUCCESS_PDB == "no_confidence_kabsch_success_pdb"
    assert not (dest / "confidence_kabsch" / str(PASS_PARENT)).exists()


def test_an_unreadable_provenance_is_a_named_skip_not_a_crash_and_not_a_pass(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT, provenance_text="{not json at all")
    assert land_parent(src, dest, PASS_PARENT).reason == SKIP_UNREADABLE_PROVENANCE
    other = tmp_path / "ops2"
    d = _tree(other, PASS_PARENT)
    (d / "provenance.json").unlink()
    assert land_parent(other, dest, PASS_PARENT).reason == SKIP_UNREADABLE_PROVENANCE
    assert not (dest / "confidence_kabsch" / str(PASS_PARENT)).exists()


def test_an_absent_source_tree_is_a_skip_that_names_absence_not_refusal(tmp_path):
    """⚠ An absent tree is not a refusal, and the two must not share a word."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    outcome = land_parent(src, dest, PASS_PARENT)
    assert outcome.reason == SKIP_NO_SOURCE_TREE
    assert outcome.reason != SKIP_RUN_REFUSED
    assert _served(dest, PASS_PARENT)["not_flipped_reason"] == NO_ARTIFACTS


def test_a_tree_whose_provenance_names_another_parent_is_refused(tmp_path):
    """⚠ A tree in the wrong folder would serve one parent another's coordinates."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT, provenance_parent=3153)
    with pytest.raises(LandRefused) as exc:
        land_parent(src, dest, PASS_PARENT)
    assert "3153" in str(exc.value)
    assert not (dest / "confidence_kabsch" / str(PASS_PARENT)).exists()


def test_a_parent_named_on_the_command_line_must_land_or_the_run_fails(tmp_path):
    """A sweep may skip; an explicit request may not — it is a claim the tree is there."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT, accepted=False)
    with pytest.raises(LandRefused) as exc:
        land(src, dest, parent_ids=[PASS_PARENT])
    assert SKIP_RUN_REFUSED in str(exc.value)
    # …and the same tree, in a sweep, is one skipped line rather than a failure.
    report = land(src, dest)
    assert report.n_landed == 0
    assert [o.reason for o in report.outcomes if o.parent_id == PASS_PARENT] == [
        SKIP_RUN_REFUSED
    ]


# ─────────────────────────────── the happy path ───────────────────────────────

def test_the_happy_path_lands_the_tree_and_the_d139_gate_flips(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    before = _served(dest, PASS_PARENT)
    assert before["eligible"] is True and before["flipped"] is False
    assert before["not_flipped_reason"] == NO_ARTIFACTS

    outcome = land_parent(src, dest, PASS_PARENT)
    assert outcome.outcome == LANDED
    assert outcome.flipped_after is True
    landed_dir = dest / "confidence_kabsch" / str(PASS_PARENT)
    assert sorted(p.name for p in landed_dir.iterdir()) == sorted(LANDED_FILES)

    after = _served(dest, PASS_PARENT)
    assert after["served"] == SERVED_CONFIDENCE_KABSCH
    assert after["flipped"] is True
    assert after["not_flipped_reason"] is None
    assert after["download_stem"] == "stitched_confidence_kabsch"
    assert Path(after["served_pdb_path"]) == landed_dir / "stitched.pdb"
    # The bytes are the OPS run's, unchanged.
    assert (landed_dir / "stitched.pdb").read_text(encoding="utf-8") == (
        src / "confidence_kabsch" / str(PASS_PARENT) / "stitched.pdb"
    ).read_text(encoding="utf-8")


def test_the_confidence_arrays_travel_with_the_pdb(tmp_path):
    """D-139 decision 5 — D-126 coordinates coloured by assembler pLDDT is a new lie."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    land_parent(src, dest, PASS_PARENT)
    landed = dest / "confidence_kabsch" / str(PASS_PARENT)
    for name in PREFERRED_FILES:
        assert (landed / name).is_file(), name


def test_a_sweep_reports_one_line_per_parent_and_a_flipped_count_off_the_gate(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    landed_ids = [PASS_PARENT, 2817, 3575]
    for pid in landed_ids:
        _tree(src, pid)
    _tree(src, 3320, accepted=False)
    report = land(src, dest)
    assert len(report.outcomes) == len(D126_SERVED_PASS_SUBSET) == report.eligible == 17
    assert report.n_landed == 3
    assert report.n_skipped == 14
    assert report.flipped_on_dest == sorted(landed_ids)
    lines = [o.line() for o in report.outcomes]
    assert sum(l.startswith("landed") for l in lines) == 3
    assert sum(l.startswith("skip") for l in lines) == 14
    assert any(SKIP_RUN_REFUSED in l for l in lines)
    assert any(SKIP_NO_SOURCE_TREE in l for l in lines)


def test_the_flipped_count_includes_parents_an_earlier_run_landed(tmp_path):
    """⚠ The report states what is TRUE on the volume, not what this run did.

    Counting our own copies would report 1 after a re-run that landed one more
    parent onto sixteen already there — a true number answering the wrong
    question, which is the failure D-016 names.
    """
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, 2817)
    assert land(src, dest).flipped_on_dest == [2817]
    _tree(src, 3575)
    second = land(src, dest)
    assert second.n_landed == 1, "the already-landed parent should not re-land"
    assert second.flipped_on_dest == [2817, 3575]


# ──────────────── never the assembler, never kabsch/, never the repo ──────────

def test_landing_never_writes_the_assembler_dir_or_the_d125_kabsch_tree(tmp_path):
    """⚠ The two directories a D-126 artifact may never become, checked on disk."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    assembler = dest / str(PASS_PARENT)
    assembler.mkdir(parents=True)
    (assembler / "stitched.pdb").write_text("HEADER assembler\nEND\n", encoding="utf-8")
    d125 = dest / "kabsch" / str(PASS_PARENT)
    d125.mkdir(parents=True)
    (d125 / "stitched.pdb").write_text("HEADER d125\nEND\n", encoding="utf-8")

    land(src / "empty", dest)  # a sweep with nothing to land
    _tree(src, PASS_PARENT)
    land_parent(src, dest, PASS_PARENT)

    assert (assembler / "stitched.pdb").read_text(encoding="utf-8") == "HEADER assembler\nEND\n"
    assert (d125 / "stitched.pdb").read_text(encoding="utf-8") == "HEADER d125\nEND\n"
    assert sorted(p.name for p in d125.iterdir()) == ["stitched.pdb"]
    assert sorted(p.name for p in assembler.iterdir()) == ["stitched.pdb"]
    written = {
        str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
    }
    new = {w for w in written if w.startswith("confidence_kabsch/")}
    assert written - new == {f"{PASS_PARENT}/stitched.pdb", f"kabsch/{PASS_PARENT}/stitched.pdb"}


def test_only_the_named_files_land_and_the_rest_are_reported_left_behind(tmp_path):
    """The tile transforms are working intermediates; the volume is not an ops root."""
    src, dest = tmp_path / "ops", tmp_path / "vol"
    d = _tree(src, PASS_PARENT)
    (d / "scratch.log").write_text("noise\n", encoding="utf-8")
    outcome = land_parent(src, dest, PASS_PARENT)
    assert set(outcome.files_landed) == set(LANDED_FILES)
    assert outcome.files_left_behind == ("scratch.log", "tile2_transformed.pdb")
    landed = dest / "confidence_kabsch" / str(PASS_PARENT)
    assert not (landed / "tile2_transformed.pdb").exists()
    assert not (landed / "scratch.log").exists()


def test_a_dry_run_writes_nothing_at_all(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    report = land(src, dest, dry_run=True)
    assert report.n_landed == 1
    assert not dest.exists()
    assert report.to_json()["flipped_on_dest"] == []
    assert _served(dest, PASS_PARENT)["flipped"] is False


def test_an_already_landed_parent_is_not_clobbered_without_overwrite(tmp_path):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    land_parent(src, dest, PASS_PARENT)
    landed_pdb = dest / "confidence_kabsch" / str(PASS_PARENT) / "stitched.pdb"
    landed_pdb.write_text("HEADER edited on the volume\nEND\n", encoding="utf-8")

    assert land_parent(src, dest, PASS_PARENT).reason == SKIP_DEST_EXISTS
    assert landed_pdb.read_text(encoding="utf-8") == "HEADER edited on the volume\nEND\n"
    assert land_parent(src, dest, PASS_PARENT, overwrite=True).outcome == LANDED
    assert "HEADER d126" in landed_pdb.read_text(encoding="utf-8")


def test_source_and_destination_may_not_be_the_same_root(tmp_path):
    src = tmp_path / "ops"
    _tree(src, PASS_PARENT)
    with pytest.raises(LandRefused) as exc:
        land_parent(src, src, PASS_PARENT)
    assert "same directory" in str(exc.value)


# ───────────────── a partial copy reads as not-landed, never landed-wrong ─────

def test_an_interrupted_copy_leaves_a_tree_that_does_not_flip(tmp_path, monkeypatch):
    """⚠⚠ A-016 — the red must fire where it is claimed to.

    ``provenance.json`` is what makes a directory look landed to every D-126
    reader, so it is written LAST. Kill the copy midway and the destination must
    resolve to the assembler: *not yet landed*, never *landed wrong*.
    """
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    real = shutil.copy2
    seen: list[str] = []

    def _die_after_two(a, b, *args, **kwargs):
        seen.append(Path(a).name)
        if len(seen) > 2:
            raise OSError("volume full")
        return real(a, b, *args, **kwargs)

    monkeypatch.setattr(shutil, "copy2", _die_after_two)
    with pytest.raises(OSError):
        land_parent(src, dest, PASS_PARENT)

    partial = dest / "confidence_kabsch" / str(PASS_PARENT)
    assert partial.is_dir(), "the fixture never reached the copy"
    assert "provenance.json" not in {p.name for p in partial.iterdir()}
    block = _served(dest, PASS_PARENT)
    assert block["served"] == SERVED_ASSEMBLER
    assert block["flipped"] is False


def test_provenance_is_written_last_and_the_two_file_lists_cannot_drift():
    assert COPY_ORDER[-1] == "provenance.json"
    assert set(COPY_ORDER) == set(LANDED_FILES)
    assert set(REQUIRED_FILES) == {"provenance.json", "stitched.pdb"}
    assert COPY_ORDER.index("stitched.pdb") < COPY_ORDER.index("provenance.json")


def test_landed_is_verified_through_the_production_resolver_not_recounted(tmp_path, monkeypatch):
    """⚠ If the gate says assembler after a copy, the copy achieved nothing."""
    import scripts.land_d139_confidence_kabsch as lander

    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    monkeypatch.setattr(lander, "gate_flipped", lambda root, pid: False)
    with pytest.raises(LandRefused) as exc:
        lander.land_parent(src, dest, PASS_PARENT)
    assert "still answers 'assembler'" in str(exc.value)
    assert "resolve_served_path" in SCRIPT, "the verifier must be the shipped selector"


# ─────────────────────────────── the CLI surface ──────────────────────────────

def test_the_cli_prints_landed_and_skip_per_parent_and_exits_zero(tmp_path, capsys):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, PASS_PARENT)
    code = main(
        ["--source-out-root", str(src), "--dest-artifact-root", str(dest), "--json"]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert f"landed  {PASS_PARENT}" in out
    assert "skip    2817  no_source_tree" in out
    assert "eligible 17 / landed 1 / skipped 16" in out
    assert f"eligible 17 / flipped 1 — [{PASS_PARENT}]" in out
    payload = json.loads(out[out.index("{") :])
    assert payload["decision"] == DECISION == "D-141"
    assert payload["serves"] == "D-139"
    assert payload["flipped_on_dest"] == [PASS_PARENT]
    assert payload["gate_moved"] is False and payload["solved"] is False


def test_the_cli_exits_nonzero_on_a_refusal_and_says_so_on_stderr(tmp_path, capsys):
    src, dest = tmp_path / "ops", tmp_path / "vol"
    _tree(src, NON_PASS_PARENT)
    code = main(
        [
            "--source-out-root", str(src),
            "--dest-artifact-root", str(dest),
            "--parent-id", str(NON_PASS_PARENT),
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "REFUSED" in captured.err
    assert not (dest / "confidence_kabsch").exists()


def test_the_cli_defaults_the_destination_to_the_serving_artifact_root(tmp_path, monkeypatch, capsys):
    """⚠ `/data/artifacts` is the Fly mount; the default must not drift from it."""
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path / "vol"))
    src = tmp_path / "ops"
    _tree(src, PASS_PARENT)
    assert main(["--source-out-root", str(src)]) == 0
    assert (tmp_path / "vol" / "confidence_kabsch" / str(PASS_PARENT)).is_dir()
    monkeypatch.delenv("ARTIFACT_ROOT")
    assert 'os.environ.get("ARTIFACT_ROOT", "/data/artifacts")' in (
        (ROOT / "app" / "kabsch_path_read.py").read_text(encoding="utf-8")
    )
    assert 'destination = "/data/artifacts"' in (ROOT / "fly.toml").read_text(encoding="utf-8")
    capsys.readouterr()


# ─────────────────────────── the hard stops, as properties ────────────────────

def test_the_lander_moves_no_threshold_and_computes_no_geometry():
    lowered = SCRIPT.lower()
    for banned in ("import numpy", "def kabsch", "rotation", "sqrt(", "align_tiles"):
        assert banned not in lowered, banned
    assert '"gate_moved": False' in SCRIPT and '"gate_angstrom": 10.0' in SCRIPT
    # No re-run of the OPS pass: the D-126 writer is never reached for.
    assert "write_confidence_kabsch_restitch" not in SCRIPT
    assert "TileFold" not in SCRIPT


def test_the_lander_imports_nothing_that_could_fold_queue_or_rank(tmp_path):
    """⚠ The hard stops as an IMPORT ALLOWLIST, not as a banned-words list.

    D-139's suite could ban the word ``rent`` in ``served_path_policy.py``
    because that module has no reason to say it. This script's docstring must
    say it — the hard stops are the first thing an operator about to run it on a
    volume needs to read — so a word check here would force the file to be less
    honest to stay green. What actually binds is *what it can reach*: an
    enumerated import list, and the positive check below that the stops are
    stated.
    """
    imported = set(re.findall(r"^(?:from|import)\s+([\w.]+)", SCRIPT, re.M))
    allowed = {
        "__future__", "argparse", "json", "os", "shutil", "sys",
        "dataclasses", "pathlib", "typing",
        "app.kabsch_path_read", "app.served_path_policy",
        "core.hold48_confidence_kabsch",
    }
    assert imported <= allowed, f"the lander reaches for {sorted(imported - allowed)}"
    for banned in ("torch", "numpy", "requests", "httpx", "sqlalchemy", "alembic"):
        assert banned not in imported
    for banned in ("op.add_column", "JobRecord(", "requests.post", "create_engine"):
        assert banned not in SCRIPT, banned


def test_the_hard_stops_are_stated_where_an_operator_will_read_them():
    """⚠ The positive half of the check above: named in the module docstring."""
    import scripts.land_d139_confidence_kabsch as lander

    doc = _flat(lander.__doc__ or "").lower()
    for stop in ("no kabsch", "no fold", "no gpu", "no rent", "no emit", "no f-004"):
        assert stop in doc, f"the module docstring does not state {stop!r}"
    assert "no threshold" in doc
    assert "artifacts alone never flip a parent" in doc


def test_no_confidence_kabsch_tree_is_created_inside_the_repository_by_this_suite():
    """⚠ D-139's committed-tree guard, restated where a fixture would break it."""
    trees = [p for p in ROOT.rglob("confidence_kabsch") if p.is_dir() and ".git" not in p.parts]
    assert trees == [], f"a confidence_kabsch tree exists in the repo: {trees}"
    assert "tmp_path" in Path(__file__).read_text(encoding="utf-8")
    # ⚠ RULE LINES only. The first draft of this check read the whole file and was
    # satisfied by the COMMENT above the rule — it stayed green with the pattern
    # deleted, which is F-044's shape: a reference that resolves, to the wrong thing.
    rules = [
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert "confidence_kabsch/" in rules, (
        ".gitignore must carry `confidence_kabsch/` as a RULE, so a careless "
        f"`git add -A` on an ops box cannot commit a landed tree; rules are {rules[-4:]}"
    )


def test_the_lander_never_claims_a_seam_is_solved():
    for text, label in ((SCRIPT, "lander"), (_d141_entry(), "log entry")):
        lowered = _flat(text).lower()
        for phrase in ("seams solved", "seam solved", "seams fixed", "kabsch aligned"):
            assert phrase not in lowered, f"{label}: {phrase}"
        assert "not scientifically solved" in lowered or "not a solved" in lowered, label


# ───────────────────────────── the living log entry ───────────────────────────

def _d141_entry() -> str:
    """The D-141 entry only. ⚠ Bounded by the next `### ` heading, whatever it is —
    #263 may land `### D-140` between this entry and D-139, and a boundary written
    as `D-139` would then silently swallow a neighbour's text into these checks."""
    start = LOG.index("\n### D-141 —") + 1
    nxt = re.search(r"^### (?!D-141\b)", LOG[start + 1 :], re.M)
    return LOG[start : start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_and_leads_the_log():
    """⚠ The check is the `### D-141` HEADING, never a citation of it (D-062 / item 7)."""
    entry = _d141_entry()
    assert re.search(r"^### D-141 — The gate had nothing to answer with", LOG, re.M)
    assert LOG.index("### D-141 —") < LOG.index("### D-139 —"), "newest first"
    assert len(re.findall(r"^### D-141", LOG, re.M)) == 1, "exactly one D-141 entry"
    lowered = _flat(entry).lower()
    assert "scripts/land_d139_confidence_kabsch.py" in lowered
    assert "d-126" in lowered and "d-139" in lowered
    assert "10.0 å" in lowered, "the unmoved gate must be named"


def test_the_log_entry_records_why_140_was_not_taken_and_that_263_then_merged():
    """⚠ #263 held D-140 on an unmerged branch, so 141 was taken (D-138's precedent).

    #263 then merged mid-flight at `578f5ac`. The entry must carry **both** readings:
    the original one, and the amendment recording that the predicted red arrived.
    D-129-C — a superseded claim never stands alone, and is never quietly deleted.
    """
    lowered = _flat(_d141_entry()).lower()
    assert "d-140" in lowered and "263" in lowered
    assert "gh pr list --state open" in lowered, "the id must be checked, not assumed"
    assert "amended in place" in lowered, "the mid-flight merge must be recorded"
    assert "578f5ac" in lowered, "the merge commit must be named, not alluded to"
    # And the tree agrees with the entry: 140 is now written, 141 is this one, 142 is HELD by
    # owner ruling (registered in docs/RESERVED.md; the Track B copy work took it, then was
    # renumbered on 2026-09-09), 143 is that entry, and 144 is free. ⚠ Widened by ADDING,
    # never by a `>=`, and the bar on 142 was kept rather than dropped.
    assert re.search(r"^### D-140 — The ADC Pipeline shelf gets a cancer type", LOG, re.M)
    assert re.search(r"^### D-143 — Track B stops claiming a composite", LOG, re.M), (
        "D-143 must be the Track B structural-only copy entry, not some other entry "
        "that took the number"
    )
    # ⚠⚠ 142 IS NOW WRITTEN, AND THE BAR ON IT REDDENED EXACTLY AS ITS OWN MESSAGE PREDICTED.
    # `docs/RESERVED.md` reserved 142 after the Track B copy work was renumbered off it, with the
    # unblock recorded as *"whoever holds it writes `### D-142`"* and the resolution pre-committed:
    # *"if a holder writes it, this reddens BY DESIGN and 142 is ADDED beside 143."* The holder is
    # the `/targets` columns entry (Emma CoS assignment, 2026-09-09), so the bar is REPLACED BY A
    # NAME rather than deleted, and 142 is ADDED to the enumeration beside 143. ⚠ Never a `>=`:
    # this is the eighth widening and the eighth resolution by adding.
    # ⚠ A reserved integer that is later spent must be NAMED here, not merely un-barred — an
    # un-barred integer with no name is exactly what the D-062 defect looked like.
    assert re.search(r"^### D-142 — `/targets` gains a Cancer association", LOG, re.M), (
        "D-142 is the recorded holder of the reserved integer; it must be the target-list "
        "columns entry, not some other entry that took the number"
    )
    # ⚠ Widened again at **D-144** — to `[…, 141, 142, 143, 144]` — for the NINTH time, and
    # by ADDING as every pass before it. D-144 lands the census STRUCTURAL rank in the DB and on
    # its own route (`/api/census-structural-ranking`): the DB/API half of the same
    # structural-only ruling D-143's copy lane describes, and neither of them the cohort-82
    # learned scorer. ⚠⚠ Its GO **assigned** it 144 while 142 and 143 were both unwritten and
    # unpublished, so its own first draft barred `### D-142` and `### D-143` — and both then
    # merged mid-flight (`f243f93` / `22ce1d7` / `b7d933f`), reddening those bars **exactly as
    # they said they would**. The rebase ADDED 142, 143 and 144 by name. Nothing was relaxed to
    # a `>=`, and `### D-145` now takes the next-free bar.
    assert re.search(r"^### D-144 — The offline census ranking stops being a spreadsheet",
                     LOG, re.M), (
        "D-144 must be the census structural-rank entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-145** by ADDING, never by a `>=` — the TENTH pass. ⚠⚠ **The SECOND
    # reserved integer to be SPENT rather than skipped** (142 was the first, the same day): 145
    # sat in `docs/RESERVED.md` as the next free `D-`, `D-144` cited it in order to bar it, and
    # this bar reddened **by design** when an entry claimed it. D-145 bakes the D-144
    # structural-rank loader into the Fly serving image as one explicit `COPY`. ⚠ Adjacent to
    # this suite and deliberately NOT the same thing: D-141 landed OPS *trees* on the serving
    # VOLUME with a script that does not ship; D-145 ships a *script* in the IMAGE and runs
    # nothing. `### D-146` now takes the next-free bar.
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     LOG, re.M), (
        "D-145 must be the image-permanence entry that bakes the structural-rank loader in, "
        "not some other entry that took the number"
    )
    # ⚠ Widened again at **D-146** by ADDING, never by a `>=` — the ELEVENTH pass. ⚠⚠ **The THIRD
    # reserved integer to be SPENT rather than skipped** (142 and 145 were the first two, both the
    # same day): 146 sat in `docs/RESERVED.md` as the next free `D-`, `D-145` cited it in order to
    # bar it, and this bar reddened **by design** when an entry claimed it. D-146 retires Track B's
    # offline clause now that `GET /api/census-structural-ranking` answers `valid`. ⚠ It is COPY,
    # and the distinction this suite cares about holds: D-141 landed OPS trees on the serving
    # VOLUME, D-145 shipped a script in the IMAGE, and D-146 changes only what two documents say.
    # `### D-147` now takes the next-free bar.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 must be the Track B live-route copy entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-147** by ADDING, never by a `>=` — the TWELFTH pass. ⚠⚠ **The FOURTH
    # reserved integer to be SPENT rather than skipped** (142, 145 and 146 were the first three,
    # all the same day): 147 sat in `docs/RESERVED.md` as the next free `D-`, `D-146` cited it in
    # order to bar it, and this bar reddened **by design** the moment an entry claimed it.
    # D-147 adds the `ecd_intermittent` disclosure to the census structural ranking rows and
    # runs no ops, lands no tree and moves no served path.
    # `### D-148` now takes the next-free bar; nothing was relaxed to a `>=` and no bar was
    # deleted, only replaced by a name.
    assert re.search(r"^### D-147 — The census rank stops presenting a loop as an ectodomain",
                     LOG, re.M), (
        "D-147 must be the census `ecd_intermittent` entry, not some other entry that took "
        "the number"
    )
    assert "\n### D-148" not in LOG, (
        "D-148 is the next free integer and must stay unspent until an entry claims it "
        "by name here — never admitted by a `>=`"
    )


def test_the_log_entry_states_the_blocker_rather_than_implying_a_land_happened():
    """⚠⚠ D-016. The disqualifying fact leads: no land ran, because no Fly credential
    reached this build. An entry describing a lander is not evidence of a landing."""
    lowered = _flat(_d141_entry()).lower()
    for claim in ("no fly credential", "flyctl", "runbook", "eligible 17 / flipped 0"):
        assert claim in lowered, claim
    assert "not run" in lowered or "did not run" in lowered


def test_the_architecture_doc_names_the_lander():
    flat = _flat(ARCH).lower()
    assert "land_d139_confidence_kabsch" in flat
    assert "d-140" in flat
