"""The census `structural_profile`, against `D-079` amendment 1's rulings and amendment 2's bar.

⚠ Each test names the ruling it enforces. A test that cannot say which decision it defends is a
test nobody will dare delete and nobody can justify keeping.
"""

from __future__ import annotations

import ast
import csv
import json
import math
import pathlib

import pytest

from core.structural_profile import (
    MOUNT_PRECONDITIONS,
    PROFILE_REFUSALS,
    ProfileMisuse,
    ProfileRefusal,
    ProfileResult,
    load_model,
    load_support,
    out_of_range,
    profile_many,
    structural_profile,
)

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = REPO / "data" / "census" / "run2_cohort_reproduction_fixture.csv"
ORDER = load_model()["feature_order"]


def _mid() -> dict[str, float]:
    """A feature vector comfortably inside the cohort's support on every feature."""
    sup = load_support()
    return {n: (lo + hi) / 2 for n, (lo, hi) in sup.items()}


# ── the model is the model: reproduction, not resemblance ────────────────────

def test_the_thirteen_parameters_reproduce_every_persisted_score():
    """⚠⚠ THE LOAD-BEARING TEST. The profile applies run 2's model from parameters RECOVERED from
    persisted values rather than by importing the fitter. That is only legitimate if it is the same
    function — so it is checked against 56 committed rows carrying their persisted scores, to full
    float precision. *Accept by reproduction, not by label.*"""
    rows = list(csv.DictReader(FIXTURE.open(encoding="utf-8")))
    assert len(rows) == 56, f"the fixture is {len(rows)} rows, not the 56 of run 2's ranking set"
    worst = 0.0
    for r in rows:
        feats = {n: float(r[n]) for n in ORDER}
        got = structural_profile(feats, accession=r["accession"])
        assert got.value is not None, f"{r['accession']} refused — the fixture is the FIT set"
        worst = max(worst, abs(got.value - float(r["persisted_score"])))
    assert worst < 1e-12, f"max deviation from the persisted score is {worst:.3e}"


def test_a_wrong_parameter_breaks_the_reproduction():
    """⚠ `F-045`: a proof that cannot fail is not a proof. If the test above passes with a corrupted
    model, it is checking nothing."""
    model = load_model()
    model["intercept"] += 0.01
    rows = list(csv.DictReader(FIXTURE.open(encoding="utf-8")))[:5]
    off = max(abs(structural_profile({n: float(r[n]) for n in ORDER},
                                     accession=r["accession"], model=model).value
                  - float(r["persisted_score"])) for r in rows)
    assert off > 1e-4, "perturbing the intercept did not move the output — the model is not wired in"


# ── ruling 1: the name is the ruling ────────────────────────────────────────

def test_the_module_never_calls_it_a_score_a_rank_or_a_suitability():
    src = (REPO / "core" / "structural_profile.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = ("score", "rank", "suitability")
    named = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            named.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            named.add(node.id)
        elif isinstance(node, ast.arg):
            named.add(node.arg)
    bad = sorted(n for n in named for b in banned if b in n.lower())
    assert not bad, (
        f"identifiers naming the value a score/rank/suitability: {bad} — ruling 1 makes the NAME "
        f"the ruling, and F-049's family is a word meaning two things on two surfaces")


# ── ruling 2: never ranked, including by sort order ─────────────────────────

def test_profiles_cannot_be_sorted():
    """⚠⚠ *A sortable column is a ranking with extra steps.* Ordering is absent by construction,
    not by convention — `sorted()` must raise rather than quietly produce a ranking."""
    a = ProfileResult("A", 0.2, None)
    b = ProfileResult("B", 0.3, None)
    with pytest.raises(TypeError):
        sorted([a, b])


def test_the_module_exposes_no_ranking_helper():
    """⚠⚠ AST, NOT A TEXT SCAN — and this test reddened on correct code before it was fixed. The
    first version searched the raw source for `top_n` and matched the DOCSTRING that says *"no
    `top_n`"*. A text scan cannot tell a prohibition from a violation, which is precisely what
    `F-052` records about three earlier guards. The predicate is what the module DEFINES and
    CALLS, not what it mentions."""
    tree = ast.parse((REPO / "core" / "structural_profile.py").read_text(encoding="utf-8"))

    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    ordering_names = sorted(n for n in defined
                            if n.startswith(("rank", "top")) or "sort" in n)
    assert not ordering_names, f"the module defines an ordering helper: {ordering_names}"

    called = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                called.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                called.add(n.func.attr)
    banned = {"sorted", "sort", "nlargest", "nsmallest"} & called
    assert not banned, f"the module calls {sorted(banned)} — ruling 2 forbids producing an ordering"

    # ⚠ and no rich-comparison dunder on the result type: `sorted()` must raise, not succeed.
    classes = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    result = classes.get("ProfileResult")
    assert result is not None
    comparisons = {m.name for m in result.body if isinstance(m, ast.FunctionDef)} & {
        "__lt__", "__gt__", "__le__", "__ge__"}
    assert not comparisons, f"ProfileResult defines {sorted(comparisons)} — that IS an ordering"


def test_profile_many_preserves_the_callers_order_and_drops_nothing():
    rows = [{"accession": f"A{i}", "features": _mid()} for i in range(5)]
    out = profile_many(rows)
    assert [r.accession for r in out] == [r["accession"] for r in rows]


# ── ruling 3: refusal is a CATEGORY, never a number, clamp or None ──────────

def test_out_of_range_is_refused_not_clamped():
    sup = load_support()
    feats = _mid()
    hi = sup["ecd_length"][1]
    feats["ecd_length"] = hi * 10
    got = structural_profile(feats, accession="OOD")
    assert got.is_refused and got.value is None
    assert got.refusal.category == "refused_out_of_distribution"
    assert "ecd_length" in got.out_of_range_features
    assert f"{hi:.6g}" in got.refusal.detail, "the refusal must name the bound it failed"


def test_a_result_can_never_be_both_absent_or_both_present():
    with pytest.raises(ProfileMisuse):
        ProfileResult("X", None, None)          # a silent null
    with pytest.raises(ProfileMisuse):
        ProfileResult("X", 0.2, ProfileRefusal("refused_out_of_distribution", "d"))


def test_an_unlisted_refusal_category_is_rejected():
    with pytest.raises(ProfileMisuse):
        ProfileRefusal("probably_fine", "d")


def test_an_incomplete_vector_is_a_category_not_a_zero():
    feats = _mid()
    feats["sasa_normalized"] = None
    got = structural_profile(feats, accession="PARTIAL")
    assert got.refusal.category == "refused_features_incomplete"
    assert "sasa_normalized" in got.refusal.detail


def test_the_boundary_itself_is_inside_the_support():
    """⚠ The bar is the OBSERVED min–max, so a value equal to the cohort's own extreme was seen by
    the model and must not be refused. An off-by-one here would refuse real training data."""
    sup = load_support()
    for name in ORDER:
        for bound in sup[name]:
            feats = _mid()
            feats[name] = bound
            assert not structural_profile(feats, accession="EDGE").is_refused, name


# ── ruling 6: F-048's set excluded AT COMPUTATION ───────────────────────────

def test_a_below_floor_span_is_refused_before_any_arithmetic():
    feats = _mid()
    got = structural_profile(feats, accession="Q9ULH0", span_below_floor=True)
    assert got.value is None and got.refusal.category == "refused_span_below_floor"


def test_the_floor_refusal_wins_even_when_the_features_are_in_range():
    """⚠ *A value computed and then hidden is a value that will eventually be exported.* The
    refusal must precede the arithmetic, not filter it afterwards."""
    got = structural_profile(_mid(), accession="X", span_below_floor=True)
    assert got.refusal.category == "refused_span_below_floor"


# ── ruling 8: the bar is min–max, not p05–p95 and not ±3 sd ────────────────

def test_the_bar_reads_only_min_and_max():
    """⚠ The baseline file also carries p05/p95/sd. Reading them here would make the bar a
    parameter of whoever calls this, which amendment 2 ruled it is not."""
    sup = load_support()
    assert all(len(v) == 2 for v in sup.values())
    baseline = json.loads((REPO / "data" / "census" / "cohort_feature_baseline.json")
                          .read_text(encoding="utf-8"))["features"]
    for name in ORDER:
        assert sup[name] == (baseline[name]["min"], baseline[name]["max"])


def test_a_value_inside_min_max_but_outside_p05_p95_is_NOT_refused():
    """⚠⚠ The discriminating test between the ruled bar and the rejected one. `p05–p95` fires
    inside the training support; if this row were refused, the wrong bar is wired."""
    baseline = json.loads((REPO / "data" / "census" / "cohort_feature_baseline.json")
                          .read_text(encoding="utf-8"))["features"]
    feats = _mid()
    name = "ecd_length"
    below_p05 = (baseline[name]["min"] + baseline[name]["p05"]) / 2
    assert below_p05 < baseline[name]["p05"] and below_p05 >= baseline[name]["min"]
    feats[name] = below_p05
    assert not structural_profile(feats, accession="INSIDE").is_refused


# ── ruling 5: THE WALL ──────────────────────────────────────────────────────

def _imports_of(rel: str) -> set[str]:
    tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_the_profile_does_not_import_the_scorer_or_the_fitter():
    """⚠⚠ `D-079` decision 1: *"no census path imports `core/scorer.py` or the fitter, asserted by
    test and proven by revert."* Measured 2026-08-20: the only such assertion in the tree ran the
    OTHER direction (`core/scorer.py` must not import census). **This is the missing half**, built
    where the decision said it already was."""
    mods = _imports_of("core/structural_profile.py")
    bad = sorted(m for m in mods if "scorer" in m or "fit_scorer" in m)
    assert not bad, f"the profile imports {bad} — D-079 dec 1 bars it"


def test_the_wall_holds_under_a_RENAME_too():
    """⚠ The `EE-0` route: a token scan for the literal string `core.scorer` is defeated by
    `import core.scorer as m`. Import NODES are inspected, so an alias cannot slip past — asserted
    here by constructing the alias form and confirming the detector sees it."""
    tree = ast.parse("import core.scorer as anything_at_all\n")
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert "core.scorer" in mods, "the detector reads the module name, not the bound alias"


def test_nothing_the_cohort_ranking_reads_imports_the_profile():
    """⚠⚠ THE WALL'S OTHER FACE, and the one that matters for `P-001`. If a census profile ever
    reaches the cohort's arc, the comparison is contaminated and P-001 is unanswerable."""
    for rel in ("core/scorer.py", "core/features.py", "app/reads.py", "scripts/fit_scorer.py"):
        bad = sorted(m for m in _imports_of(rel) if "structural_profile" in m)
        assert not bad, f"{rel} imports {bad} — ruling 5 is the wall"


def test_feature_names_stays_at_six():
    """⚠ `D-027`'s six IS the pre-registration; ruling 5 keeps it there."""
    from core.features import FEATURE_NAMES
    assert len(FEATURE_NAMES) == 6
    assert list(ORDER) == list(FEATURE_NAMES), "the model's order drifted from FEATURE_NAMES"


# ── ruling 4: the mount preconditions exist and are not a footnote ──────────

def test_the_mount_preconditions_name_all_five_things():
    joined = " ".join(MOUNT_PRECONDITIONS).lower()
    for token in ("unlabelled", "leave-one-out", "fit population", "not a probability",
                  "f-006", "f-051", "a-014", "selection artefact"):
        assert token in joined, f"the mount preconditions omit {token!r} (ruling 4 / amendment 2)"


def test_every_refusal_category_is_documented_in_the_vocabulary():
    assert set(PROFILE_REFUSALS) == {
        "refused_out_of_distribution", "refused_span_below_floor", "refused_features_incomplete"}
