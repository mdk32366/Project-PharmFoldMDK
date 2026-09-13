"""The three Run B attention fetchers, pinned to RECORDED LIVE RESPONSES.

⚠⚠ WHY THE FIXTURES ARE CAPTURES AND NOT HAND-WRITTEN, AND IT IS THE WHOLE POINT OF THIS FILE.

`D-075` decision 3 requires the parse path be pinned to a recorded response. A fixture written
from the author's *belief* about a response shape tests the belief, not the service — and this
project has now recorded that pattern five times under `F-068` and once as its own method note.
The bodies in `tests/fixtures/attention/` were fetched live on 2026-09-12, with their URLs and
counts recorded in `MANIFEST.json` beside them.

⚠⚠ **`E2RYF6` IS THE NEGATIVE CASE AND IT IS A TRAP FOR THREE DIFFERENT WRONG IMPLEMENTATIONS.**
Measured from the capture: **55 cross-references, 0 of them PDB, and 1 AlphaFoldDB.**

  - a "is `uniProtKBCrossReferences` missing?" check → **wrong**, the key is present
  - a "is the list empty?" check → **wrong**, it has 55 entries
  - a "does it have a structure database?" check → ⚠⚠ **wrong, and dangerously so — AlphaFoldDB
    is a PREDICTION, not a solved structure** (`A-014`), and counting it would mark a target with
    no experimental structure as having one

`P04626` is the positive control: **461 cross-references, 63 PDB**, which independently matches
the `n_pdb = 63` in `data/derived/cohort82_pdb_coverage.csv`. ⚠ `A-017` (c): without it, the
negative case proves only that the function returns 0 for everything.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from scripts import attention_control as A   # noqa: E402

FIX = REPO / "tests" / "fixtures" / "attention"


def _body(name: str) -> bytes:
    return (FIX / name).read_bytes()


# ── the fixtures are real, and this test says so out loud ───────────────────────────────────

def test_the_fixtures_are_recorded_live_responses_with_their_provenance():
    """⚠ If this file ever stops being a capture, every assertion below silently becomes an
    assertion about a hand-written document."""
    manifest = json.loads((FIX / "MANIFEST.json").read_text(encoding="utf-8"))
    by_file = {m["file"]: m for m in manifest}
    assert by_file["uniprot_E2RYF6.json"]["url"].startswith("https://rest.uniprot.org/")
    assert by_file["uniprot_E2RYF6.json"]["captured"] == "2026-09-12"
    assert by_file["pubmed_ERBB2_tagged.json"]["url"].startswith(A.PUBMED_ENDPOINT)
    # the negative case's shape, asserted from the capture rather than described
    assert by_file["uniprot_E2RYF6.json"]["n_crossrefs"] == 55
    assert by_file["uniprot_E2RYF6.json"]["n_pdb"] == 0
    assert by_file["uniprot_E2RYF6.json"]["n_alphafolddb"] == 1


# ── pdb_present: the parse path ─────────────────────────────────────────────────────────────

def test_a_populated_crossref_list_with_no_PDB_entry_is_ZERO_not_missing():
    """⚠⚠ E2RYF6: the key is present, the list has 55 entries, and none is PDB. Three plausible
    implementations get this wrong; the answer is 0, and it is a real 0."""
    got = A.parse_pdb_present(_body("uniprot_E2RYF6.json"))
    assert got == 0
    assert got is not None, "a genuine zero is 0, never None - None means the fetch failed"


def test_a_target_with_PDB_crossrefs_is_ONE():
    """⚠ A-017 (c). Without this, `return 0` passes the test above."""
    assert A.parse_pdb_present(_body("uniprot_P04626.json")) == 1


def test_ALPHAFOLD_DOES_NOT_SATISFY_pdb_present():
    """⚠⚠ THE TRAP, AND IT IS NAMED IN THE ORDER. E2RYF6 carries an AlphaFoldDB cross-reference.
    AlphaFold is a PREDICTION, not a solved structure (`A-014`), so a target with one and no PDB
    entry has no experimental structure and must read 0."""
    doc = json.loads(_body("uniprot_E2RYF6.json"))
    dbs = {x.get("database") for x in doc["uniProtKBCrossReferences"]}
    assert "AlphaFoldDB" in dbs, "the fixture must still contain the trap for this to test it"
    assert "PDB" not in dbs
    assert A.parse_pdb_present(_body("uniprot_E2RYF6.json")) == 0


def test_a_malformed_body_raises_rather_than_returning_a_number():
    """⚠ The parser is pure and strict; turning garbage into 0 is how a parse failure becomes a
    low-attention stratum. The FETCHER converts the raise into None - that is its job, not this
    function's."""
    with pytest.raises(Exception):
        A.parse_pdb_present(b"{not json")


# ── pub_count: the parse path ───────────────────────────────────────────────────────────────

def test_the_pubmed_count_is_read_from_esearchresult_count():
    """⚠ Pinned to the recorded esearch body, and the numbers match the 82-target calibration
    run independently on the same day: tagged 11,474, untagged 26,515."""
    assert A.parse_pub_count(_body("pubmed_ERBB2_tagged.json")) == 11474
    assert A.parse_pub_count(_body("pubmed_ERBB2_untagged.json")) == 26515


def test_the_two_pubmed_arms_are_different_queries_and_the_fixtures_prove_it():
    """⚠⚠ If both arms sent the same query the control would have two copies of one measurement
    and the disagreement clause would be unfalsifiable."""
    manifest = {m["file"]: m for m in json.loads((FIX / "MANIFEST.json").read_text(encoding="utf-8"))}
    tagged = manifest["pubmed_ERBB2_tagged.json"]["term"]
    untagged = manifest["pubmed_ERBB2_untagged.json"]["term"]
    assert tagged == "ERBB2[Title/Abstract]" and untagged == "ERBB2"
    assert tagged != untagged
    assert A.parse_pub_count(_body("pubmed_ERBB2_tagged.json")) \
        != A.parse_pub_count(_body("pubmed_ERBB2_untagged.json"))


def test_neither_arm_carries_the_dropped_AND_clause():
    """⚠ `AND (protein OR gene)` is dropped by `D-075 amendment 2`: it discarded 46% of results
    on whether two words appear in an abstract. A template that still carries it is a different
    pre-registration."""
    for tpl in (A.PUBMED_TAGGED_TEMPLATE, A.PUBMED_ATM_TEMPLATE):
        assert "protein" not in tpl and "gene" not in tpl
    assert A.PUBMED_TAGGED_TEMPLATE.format(symbol="ERBB2") == "ERBB2[Title/Abstract]"
    assert A.PUBMED_ATM_TEMPLATE.format(symbol="ERBB2") == "ERBB2"


# ── the fetchers: None is not 0 ─────────────────────────────────────────────────────────────

class _Resp:
    def __init__(self, body: bytes, status: int = 200):
        self._body, self.status = body, status

    def read(self): return self._body
    def __enter__(self): return self
    def __exit__(self, *a): return False


def _opener(body: bytes, status: int = 200):
    seen = []

    def _open(url, timeout=None):
        seen.append(url)
        if status != 200:
            raise OSError(f"HTTP {status}")
        return _Resp(body, status)
    _open.seen = seen
    return _open


def test_fetch_pdb_present_returns_a_REAL_ZERO_for_a_target_with_no_PDB():
    """⚠⚠ THE WHOLE TRAP, IN ONE ASSERTION. A fetch failure and a genuine zero must not be the
    same value: conflating them pushes failures into the low-attention stratum, which is the
    stratum the control is trying to measure."""
    op = _opener(_body("uniprot_E2RYF6.json"))
    got = A.fetch_pdb_present("E2RYF6", opener=op, sleep=lambda s: None)
    assert got == 0 and got is not None
    assert "E2RYF6" in op.seen[0], "A-017: the fixture must have reached the fetcher"


def test_fetch_pdb_present_returns_ONE_for_a_target_with_PDB():
    op = _opener(_body("uniprot_P04626.json"))
    assert A.fetch_pdb_present("P04626", opener=op, sleep=lambda s: None) == 1


@pytest.mark.parametrize("kind,op", [
    ("http error", _opener(b"", status=500)),
    ("malformed body", _opener(b"{not json")),
])
def test_a_failed_pdb_fetch_is_None_never_zero(kind, op):
    assert A.fetch_pdb_present("E2RYF6", opener=op, sleep=lambda s: None) is None, kind


def test_fetch_pub_count_tagged_sends_the_tagged_query_and_returns_its_count():
    op = _opener(_body("pubmed_ERBB2_tagged.json"))
    assert A.fetch_pub_count_tagged("ERBB2", opener=op, sleep=lambda s: None) == 11474
    url = op.seen[0]
    assert "Title%2FAbstract" in url or "Title/Abstract" in url
    assert "protein" not in url and "gene" not in url


def test_fetch_pub_count_atm_sends_the_BARE_symbol():
    """⚠ No field tag at all - the point is to let MeSH Automatic Term Mapping resolve the gene
    CONCEPT rather than match the STRING."""
    op = _opener(_body("pubmed_ERBB2_untagged.json"))
    assert A.fetch_pub_count_atm("ERBB2", opener=op, sleep=lambda s: None) == 26515
    url = op.seen[0]
    assert "Title%2FAbstract" not in url and "Title/Abstract" not in url


@pytest.mark.parametrize("fetcher", ["fetch_pub_count_tagged", "fetch_pub_count_atm"])
def test_a_failed_pubmed_fetch_is_None_never_zero(fetcher):
    """⚠ A throttled or failed call returning 0 would record a real absence of literature where
    there is none, and 0 is a legitimate value for an obscure symbol."""
    op = _opener(b"", status=500)
    assert getattr(A, fetcher)("ERBB2", opener=op, sleep=lambda s: None) is None


def test_every_fetcher_waits_for_the_rate_limit():
    """⚠ 82 targets x 2 PubMed arms = 164 calls. NCBI allows 3/s without a key, and a throttled
    run records real absences as fetch failures - the exact conflation the None rule exists for."""
    for name, arg in (("fetch_pdb_present", "E2RYF6"),
                      ("fetch_pub_count_tagged", "ERBB2"),
                      ("fetch_pub_count_atm", "ERBB2")):
        waited = []
        body = _body("uniprot_E2RYF6.json") if "pdb" in name \
            else _body("pubmed_ERBB2_tagged.json")
        getattr(A, name)(arg, opener=_opener(body), sleep=waited.append)
        assert waited and waited[0] >= A.NCBI_DELAY_S, f"{name} did not wait"


def test_the_three_proxy_names_are_the_amendment_2_set():
    assert A.PROXY_NAMES_V2 == ("pdb_present", "pub_count_tagged", "pub_count_atm")


def test_the_fetchers_use_the_standard_library_only():
    """⚠ No third-party network library: the freeze must be reproducible from a checkout, and
    this module is excluded from the serving image."""
    src = (REPO / "scripts" / "attention_control.py").read_text(encoding="utf-8")
    for banned in ("import requests", "import httpx", "import aiohttp"):
        assert banned not in src


# ── the three-arm snapshot (D-075 amendment 2) ──────────────────────────────────────────────

TARGETS = [("ERBB2", "P04626"), ("MUC22", "E2RYF6"), ("BROKEN", "X00000")]


def _snap(**over):
    """Build a three-arm snapshot with injected fetchers. `BROKEN` fails every arm."""
    def pdb(acc):
        return None if acc == "X00000" else (1 if acc == "P04626" else 0)

    def tagged(sym):
        return None if sym == "BROKEN" else {"ERBB2": 11474, "MUC22": 12}[sym]

    def atm(sym):
        return None if sym == "BROKEN" else {"ERBB2": 26515, "MUC22": 31}[sym]

    kw = dict(frozen_date="2026-09-12", fetch_pdb_present=pdb,
              fetch_pub_count_tagged=tagged, fetch_pub_count_atm=atm)
    kw.update(over)
    return A.build_snapshot(TARGETS, **kw)


def test_the_snapshot_carries_three_proxies_separately_never_merged():
    snap = _snap()
    assert A.PROXY_NAMES == ("pdb_present", "pub_count_tagged", "pub_count_atm")
    assert snap["proxy_names"] == list(A.PROXY_NAMES)
    e = next(t for t in snap["targets"] if t["symbol"] == "ERBB2")
    assert e["pdb_present"] == 1
    assert e["pub_count_tagged"] == 11474
    assert e["pub_count_atm"] == 26515
    assert "pub_count" not in e, "the merged two-arm key must not survive the amendment"


def test_the_snapshot_records_BOTH_query_strings_and_neither_carries_the_dropped_clause():
    """⚠⚠ GATE 3. The query on the snapshot's face must be the query the fetchers SEND. If they
    differ the snapshot is not frozen — it records a query that was not run."""
    snap = _snap()
    assert snap["pubmed_query_tagged"] == A.PUBMED_TAGGED_TEMPLATE == "{symbol}[Title/Abstract]"
    assert snap["pubmed_query_atm"] == A.PUBMED_ATM_TEMPLATE == "{symbol}"
    for q in (snap["pubmed_query_tagged"], snap["pubmed_query_atm"]):
        assert "protein" not in q and "gene" not in q, "the dropped AND clause is still on the face"


def test_the_recorded_query_is_what_the_fetcher_actually_requests():
    """⚠ Gate 3 proven behaviourally rather than by comparing two constants to each other: the
    URL the fetcher builds must contain the term the snapshot claims."""
    import urllib.parse

    op = _opener(_body("pubmed_ERBB2_tagged.json"))
    A.fetch_pub_count_tagged("ERBB2", opener=op, sleep=lambda s: None)
    sent = urllib.parse.parse_qs(urllib.parse.urlparse(op.seen[0]).query)["term"][0]
    assert sent == _snap()["pubmed_query_tagged"].format(symbol="ERBB2")

    op2 = _opener(_body("pubmed_ERBB2_untagged.json"))
    A.fetch_pub_count_atm("ERBB2", opener=op2, sleep=lambda s: None)
    sent2 = urllib.parse.parse_qs(urllib.parse.urlparse(op2.seen[0]).query)["term"][0]
    assert sent2 == _snap()["pubmed_query_atm"].format(symbol="ERBB2")


def test_the_sentence_is_on_the_snapshots_face_verbatim():
    """⚠⚠ Unsoftened, not footnoted, not dropped."""
    assert _snap()["note"] == "The proxies are frozen KNOWING Run A survived."


def test_each_proxy_has_its_OWN_bound():
    bounds = _snap()["bounds"]
    assert set(bounds) == set(A.PROXY_NAMES)
    assert "one bit" in bounds["pdb_present"]
    assert "literal" in bounds["pub_count_tagged"].lower()
    assert "automatic term mapping" in bounds["pub_count_atm"].lower()


def test_a_failed_fetch_is_a_NULL_WITH_A_REASON_per_arm_and_never_a_zero():
    """⚠⚠ Separate null counts, separate reasons. A failure recorded as 0 lands in the
    low-attention stratum — the stratum the control exists to measure."""
    snap = _snap()
    broken = next(t for t in snap["targets"] if t["symbol"] == "BROKEN")
    for p in A.PROXY_NAMES:
        assert broken[p] is None
        assert p in broken["null_reasons"]
    ok = next(t for t in snap["targets"] if t["symbol"] == "MUC22")
    assert ok["pdb_present"] == 0 and "null_reasons" not in ok, "a genuine zero is not a null"


def test_the_snapshot_reports_a_null_count_per_proxy():
    """⚠ A high null rate is a result about the instrument, so it must be readable without
    re-deriving it from the rows."""
    counts = _snap()["null_counts"]
    assert counts == {"pdb_present": 1, "pub_count_tagged": 1, "pub_count_atm": 1}


def test_the_snapshot_carries_its_face_and_n_targets():
    snap = _snap()
    assert snap["frozen_date"] == "2026-09-12"
    assert snap["n_targets"] == 3
    assert snap["uniprot_endpoint"] == A.UNIPROT_ENDPOINT
    assert snap["pubmed_endpoint"] == A.PUBMED_ENDPOINT


def test_build_snapshot_takes_no_clock():
    """⚠ A date recorded by accident is not a freeze (D-075 dec 3)."""
    import inspect
    src = inspect.getsource(A.build_snapshot)
    for banned in ("datetime.now", "date.today", "time.time", "utcnow"):
        assert banned not in src


# ── stratify across three arms ──────────────────────────────────────────────────────────────

def _rows():
    R = A.TargetRow
    # ⚠⚠ THE NUMBERS ARE CHOSEN SO THE TWO ARMS PARTITION THE ROWS COMPLETELY DIFFERENTLY, and
    # so that taking the MEDIAN from one arm while comparing VALUES from the other is visible:
    #   tagged [10, 50, 100] -> median  50 -> low {B, C}, high {A}
    #   atm    [60, 70,  80] -> median  70 -> low {A, B}, high {C}
    # A fixture whose partitions merely differ on one row can still pass an implementation that
    # reads one arm's median against another arm's values - that mutation was run and NOT caught
    # by the first version of this fixture.
    return [R("A", 0.9, 1, pdb_present=1, pub_count_tagged=100, pub_count_atm=60),
            R("B", 0.5, 0, pdb_present=0, pub_count_tagged=10, pub_count_atm=70),
            R("C", 0.7, 1, pdb_present=1, pub_count_tagged=50, pub_count_atm=80),
            R("D", 0.2, 0, pdb_present=None, pub_count_tagged=None, pub_count_atm=None)]


@pytest.mark.parametrize("proxy", ["pdb_present", "pub_count_tagged", "pub_count_atm"])
def test_all_three_arms_stratify_and_keep_the_unknown_stratum(proxy):
    strata = A.stratify(_rows(), proxy)
    assert "unknown" in strata and [r.symbol for r in strata["unknown"]] == ["D"]
    assert sum(len(v) for v in strata.values()) == 4, "no row is dropped"


def test_the_two_pubmed_arms_split_at_their_OWN_medians():
    """⚠⚠ THE ASSERTION THAT STOPS THE ARMS BEING ONE MEASUREMENT TWICE, and it asserts the WHOLE
    partition rather than one row.

    ⚠ Its first version checked only where `C` landed, and a falsification pass proved that
    version VACUOUS: an implementation taking the median from the tagged arm while comparing the
    named arm's values produced the same answer for `C` and was not caught. Each arm's median must
    come from that arm's own values, and only a full-partition assertion sees the difference.
    """
    def members(strata, key):
        return {r.symbol for r in strata.get(key, [])}

    tagged = A.stratify(_rows(), "pub_count_tagged")
    atm = A.stratify(_rows(), "pub_count_atm")
    assert members(tagged, "pub_low") == {"B", "C"} and members(tagged, "pub_high") == {"A"}
    assert members(atm, "pub_low") == {"A", "B"} and members(atm, "pub_high") == {"C"}


def test_an_unknown_proxy_is_still_refused():
    with pytest.raises(ValueError) as e:
        A.stratify(_rows(), "pub_count")
    assert "pub_count" in str(e.value)
