"""Task E of ORDERS-Code-2026-08-17 (second) — the Kathad reproduction, committed and testable.

`D-100` recorded this reproduction while it existed only in a Planner sandbox that is now gone.
⚠ Until this file existed, **D-100 cited nothing that runs** — *a pointer is not proof of its
target*, and that one pointed at a shell.

⚠⚠ NOTHING HERE IS VENDORED. `D-093` decision 7 bars committing S3 or any HPA table until their
terms are read and dated. Inputs are referenced BY PATH, and `--s3` is **refused if it resolves
inside the repository working tree** — the decision is enforced by the code rather than remembered.

⚠ Two paths to one quantity, compared on purpose. Every number is re-derived here; the Planner's
measurements are transcribed only for comparison. A disagreement is a DEFECT, not a rounding
difference.

    python scripts/kathad_reproduction.py \
        --s3 ~/Downloads/journal.pone.0308604.s004.xls \
        --held data/cancer_associations.csv

⚠ Reading a legacy `.xls` needs `xlrd`, which is deliberately in NO lock file: this is operator
tooling over a file the repository will never contain, and CI cannot run it. The import is lazy and
says so if absent. **The pure functions below need neither, which is why the tests run in CI.**
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys
from typing import Iterable, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]

CUTOFF = 150.0
SHEET = "Target_expression_in_tumor"

#: The Planner's measurements, 2026-08-17, transcribed for COMPARISON ONLY — never used to compute.
PLANNER = {
    "s3_rows": 1640, "s3_cols": 16, "genes": 82, "cancers": 20,
    "total_identity": 1640, "percent_law_identity": 1640,
    "A_kept": 337, "A_exact": 337, "A_ours_only": 0, "A_theirs_only": 0,
    "B_kept": 766, "B_exact": 204,
    "P_kept": 329, "P_exact": 329, "P_ours_only": 8,
    "below_cutoff_excluded": 1303,
    "panel_min": 2, "panel_median": 11, "panel_max": 12, "panel_le4": 246,
    "at_exactly_150": 52, "gt_kept": 286,
    "one_move_kept": 83, "one_move_excluded": 33, "one_move_grid": 116,
    "two_move_kept": 151, "two_move_excluded": 85, "two_move_grid": 236,
}


# ────────────────────────────────────────────────────────────────── pure functions ──

def qh_score(*, high: int, medium: int, low: int, total: int) -> Optional[float]:
    """`100 × (Low + 2·Medium + 3·High) / total`, where `total` INCLUDES `Not detected`.

    ⚠ Returns None when `total == 0`. An empty panel has no score, and returning 0.0 would rank it
    below a genuinely low-expressing protein — an absence dressed as a measurement.
    """
    if not total:
        return None
    return 100.0 * (low + 2 * medium + 3 * high) / total


def normalise_cancer(label: str) -> str:
    """⚠ Case and whitespace only. It must NOT collapse genuinely different cancers — a normaliser
    that made everything match would pass a naive test and be useless."""
    return " ".join(str(label).strip().casefold().split())


def join_key(row: dict, *, symbol_field: str = "Gene name") -> tuple[str, str]:
    """⚠⚠ `symbol_field` DEFAULTS TO `Gene name`, and that default is the finding. S3's `Gene` is
    an Ensembl id; matching on it gives 0 of 82 — a clean, plausible, entirely spurious empty
    intersection that raises nothing. The parameter exists so a test can force the wrong column."""
    return (str(row[symbol_field]).strip(), normalise_cancer(row["Cancer"]))


def is_kept(score: Optional[float], *, inclusive: bool = True) -> bool:
    """⚠ The inequality sign is worth 51 pairs (`F-043`): 52 pairs sit at exactly 150.0."""
    if score is None:
        return False
    return score >= CUTOFF if inclusive else score > CUTOFF


CATEGORIES = ("high", "medium", "low", "not_detected")
WEIGHT = {"high": 3, "medium": 2, "low": 1, "not_detected": 0}


def available_one_moves(*, high: int, medium: int, low: int, not_detected: int
                        ) -> list[tuple[str, str]]:
    """⚠ TASK F. Every (from, to) move for which a patient ACTUALLY EXISTS in `from`.

    The unconstrained flip count treats any pair within one step of the cutoff as flippable. **It
    does not check that the source category is occupied** — a row with `Low = 0` cannot lose a Low.
    That makes the unconstrained figure an UPPER BOUND, and the gap between the two is the result.
    """
    counts = {"high": high, "medium": medium, "low": low, "not_detected": not_detected}
    return [(src, dst) for src in CATEGORIES if counts[src] > 0
            for dst in CATEGORIES if dst != src]


def one_move_flippable(*, high: int, medium: int, low: int, not_detected: int, total: int,
                       constrained: bool = True, inclusive: bool = True) -> bool:
    """Does moving ONE patient between categories cross the cutoff?

    `constrained=False` reproduces the upper bound: any move of one step, occupied or not.
    """
    base = qh_score(high=high, medium=medium, low=low, total=total)
    if base is None:
        return False
    side = is_kept(base, inclusive=inclusive)

    if constrained:
        moves = available_one_moves(high=high, medium=medium, low=low, not_detected=not_detected)
    else:
        moves = [(s, d) for s in CATEGORIES for d in CATEGORIES if s != d]

    counts = {"high": high, "medium": medium, "low": low, "not_detected": not_detected}
    for src, dst in moves:
        c = dict(counts)
        c[src] -= 1
        c[dst] += 1
        moved = qh_score(high=c["high"], medium=c["medium"], low=c["low"], total=total)
        if moved is not None and is_kept(moved, inclusive=inclusive) != side:
            return True
    return False


# ───────────────────────────────────────────────────────────────────── the I/O shim ──

def load_s3(path: pathlib.Path) -> list[dict]:
    """⚠⚠ REFUSES a path inside the repository working tree — `D-093` decision 7 enforced by the
    gate rather than by memory."""
    p = path.expanduser().resolve()
    try:
        p.relative_to(REPO)
    except ValueError:
        pass                                   # outside the repo: correct
    else:
        raise SystemExit(
            f"⚠⚠ REFUSING — {p} is inside the repository working tree.\n"
            "   D-093 decision 7 bars committing S3 or any HPA table until their terms are read "
            "and dated. Reference it by a path OUTSIDE the repo.")
    if not p.is_file():
        raise SystemExit(f"⚠ no such file: {p}")

    try:
        import pandas as pd                     # noqa: PLC0415 — operator tooling, lazy on purpose
    except ImportError:
        raise SystemExit("⚠ needs pandas + xlrd (operator tooling, in no lock): "
                         "pip install pandas xlrd") from None
    try:
        df = pd.ExcelFile(p).parse(SHEET)
    except ImportError:
        raise SystemExit("⚠ reading a legacy .xls needs xlrd: pip install xlrd") from None
    return df.to_dict("records")


def load_held(path: pathlib.Path) -> list[dict]:
    """Our committed derivation. ⚠ Comment lines are skipped, not parsed — the header carries the
    D-053 method note, including a hypothesis `D-100` retires."""
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    return list(csv.DictReader(lines))


# ─────────────────────────────────────────────────────────────────────── the report ──

def _cmp(name: str, mine, theirs) -> tuple[str, bool]:
    ok = mine == theirs
    return (f"  {name:34s} {str(mine):>10s} {str(theirs):>10s}  "
            f"{'agree' if ok else '⚠ DISAGREE'}"), ok


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--s3", required=True, help="path to journal.pone.0308604 s004.xls (OUTSIDE the repo)")
    ap.add_argument("--held", default=str(REPO / "data" / "cancer_associations.csv"))
    args = ap.parse_args(argv)

    s3 = load_s3(pathlib.Path(args.s3))
    held = load_held(pathlib.Path(args.held))

    print("=" * 84)
    print("TASK E — the Kathad reproduction, re-derived")
    print("⚠ two paths to one quantity; a disagreement is a defect, not a rounding difference")
    print("=" * 84)
    print(f"  {'quantity':34s} {'mine':>10s} {'planner':>10s}  verdict")
    print("  " + "-" * 66)

    defects = []
    mine: dict = {}

    mine["s3_rows"] = len(s3)
    mine["genes"] = len({str(r["Gene name"]).strip() for r in s3})
    mine["cancers"] = len({normalise_cancer(r["Cancer"]) for r in s3})

    total_ok = sum(1 for r in s3 if int(r["total"]) ==
                   int(r["High"]) + int(r["Medium"]) + int(r["Low"]) + int(r["Not detected"]))
    mine["total_identity"] = total_ok

    law_ok = 0
    for r in s3:
        t = int(r["total"])
        if t and abs(float(r["percent_law"]) - 100.0 * int(r["Low"]) / t) < 1e-6:
            law_ok += 1
    mine["percent_law_identity"] = law_ok

    # conventions
    def rows_with(score_fn):
        out = []
        for r in s3:
            s = score_fn(r)
            out.append((join_key(r), s))
        return out

    def conv_A(r):
        return qh_score(high=int(r["High"]), medium=int(r["Medium"]),
                        low=int(r["Low"]), total=int(r["total"]))

    def conv_B(r):
        det = int(r["High"]) + int(r["Medium"]) + int(r["Low"])
        return qh_score(high=int(r["High"]), medium=int(r["Medium"]), low=int(r["Low"]), total=det)

    def conv_P(r):
        return float(r["percent_law"]) + 2 * float(r["percent_med"]) + 3 * float(r["percent_high"])

    held_keys = {(h["symbol"].strip(), normalise_cancer(h["cancer"])) for h in held}

    for tag, fn in (("A", conv_A), ("B", conv_B), ("P", conv_P)):
        scored = rows_with(fn)
        kept = {k for k, s in scored if is_kept(s)}
        mine[f"{tag}_kept"] = len(kept)
        mine[f"{tag}_ours_only"] = len(kept - held_keys)
        mine[f"{tag}_theirs_only"] = len(held_keys - kept)
        exact = 0
        by_key = {k: s for k, s in scored}
        for h in held:
            k = (h["symbol"].strip(), normalise_cancer(h["cancer"]))
            s = by_key.get(k)
            if s is not None and abs(s - float(h["qh_score"])) < 0.005:
                exact += 1
        mine[f"{tag}_exact"] = exact

    scored_A = rows_with(conv_A)
    mine["below_cutoff_excluded"] = sum(1 for _, s in scored_A if not is_kept(s))
    mine["at_exactly_150"] = sum(1 for _, s in scored_A if s is not None and abs(s - 150.0) < 1e-9)
    mine["gt_kept"] = sum(1 for _, s in scored_A if is_kept(s, inclusive=False))

    panels = sorted(int(r["total"]) for r in s3)
    mine["panel_min"] = panels[0]
    mine["panel_max"] = panels[-1]
    mine["panel_median"] = panels[len(panels) // 2]
    mine["panel_le4"] = sum(1 for p in panels if p <= 4)

    for key in ("s3_rows", "genes", "cancers", "total_identity", "percent_law_identity",
                "A_kept", "A_exact", "A_ours_only", "A_theirs_only",
                "B_kept", "B_exact", "P_kept", "P_exact", "P_ours_only",
                "below_cutoff_excluded", "at_exactly_150", "gt_kept",
                "panel_min", "panel_median", "panel_max", "panel_le4"):
        line, ok = _cmp(key, mine[key], PLANNER[key])
        print(line)
        if not ok:
            defects.append((key, mine[key], PLANNER[key]))

    # ── Task F — the availability constraint ───────────────────────────────────────────────
    print("\n" + "=" * 84)
    print("TASK F — one-move flips, UNCONSTRAINED (upper bound) vs CONSTRAINED (available moves)")
    print("⚠ the gap between them IS the result; collapsing to one number discards the check")
    print("=" * 84)
    kept_rows = [r for r in s3 if is_kept(conv_A(r))]
    excl_rows = [r for r in s3 if not is_kept(conv_A(r))]

    def count(rows, constrained):
        n = 0
        for r in rows:
            if one_move_flippable(high=int(r["High"]), medium=int(r["Medium"]),
                                  low=int(r["Low"]), not_detected=int(r["Not detected"]),
                                  total=int(r["total"]), constrained=constrained):
                n += 1
        return n

    print(f"  {'population':22s} {'unconstrained':>14s} {'constrained':>12s} {'dropped':>8s}")
    print("  " + "-" * 60)
    for label, rows in (("kept (the 337)", kept_rows), ("excluded", excl_rows), ("grid", s3)):
        u, c = count(rows, False), count(rows, True)
        pct = f"{100*c/len(rows):.1f}%" if rows else "-"
        print(f"  {label:22s} {u:14d} {c:12d} {u - c:8d}   constrained = {pct} of {len(rows)}")

    # ── ⚠⚠ THE DEFINITION IS AMBIGUOUS AND THE AMBIGUITY IS THE RESULT ────────────────────────
    # F-043 publishes 83 / 33 / 116. NONE of the definitions below reproduces it — including the
    # rule F-043 itself states (|qh - 150| < 100/total), which gives 71.
    # ⚠ No search was made for a rule that yields 83. Fitting a definition to a known answer is
    # choosing a method for the result it gives (order §0 P1). The rule must be STATED, then
    # measured — so every candidate is printed and none is privileged.
    print("\n" + "-" * 84)
    print("⚠⚠ FLIP DEFINITION MATRIX — F-043 publishes 83/33/116; no definition here reproduces it")
    print("-" * 84)

    def _planner_rule(r):
        s = conv_A(r)
        t = int(r["total"])
        return s is not None and t and abs(s - CUTOFF) < 100.0 / t

    def _enum(r, adjacent_only, constrained):
        t = int(r["total"])
        c0 = {"high": int(r["High"]), "medium": int(r["Medium"]),
              "low": int(r["Low"]), "not_detected": int(r["Not detected"])}
        base = qh_score(high=c0["high"], medium=c0["medium"], low=c0["low"], total=t)
        if base is None:
            return False
        side = is_kept(base)
        for src in CATEGORIES:
            if constrained and c0[src] == 0:
                continue
            for dst in CATEGORIES:
                if dst == src or (adjacent_only and abs(WEIGHT[src] - WEIGHT[dst]) != 1):
                    continue
                c = dict(c0)
                c[src] -= 1
                c[dst] += 1
                m = qh_score(high=c["high"], medium=c["medium"], low=c["low"], total=t)
                if m is not None and is_kept(m) != side:
                    return True
        return False

    defs = [
        ("F-043's stated rule: |qh-150| < 100/total", _planner_rule),
        ("adjacent move, availability ignored", lambda r: _enum(r, True, False)),
        ("adjacent move, availability APPLIED", lambda r: _enum(r, True, True)),
        ("any single move, availability ignored", lambda r: _enum(r, False, False)),
        ("any single move, availability APPLIED", lambda r: _enum(r, False, True)),
    ]
    print(f"  {'definition':44s} {'kept':>6s} {'excl':>6s} {'grid':>6s}")
    for label, fn in defs:
        k = sum(1 for r in kept_rows if fn(r))
        e = sum(1 for r in excl_rows if fn(r))
        print(f"  {label:44s} {k:6d} {e:6d} {k + e:6d}")
    print(f"  {'F-043 as published':44s} {83:6d} {33:6d} {116:6d}   ⚠ matches none of the above")

    print()
    if defects:
        print("⚠⚠ DISAGREEMENTS — defects, not rounding:")
        for k, m, p in defects:
            print(f"    {k}: mine={m} planner={p}")
        return 1
    print("✓ every transcribed quantity reconciles.")
    print("⚠ Reconciling makes the two paths the SAME, not correct — both could share an")
    print("  assumption. What it excludes is that one of them slipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
