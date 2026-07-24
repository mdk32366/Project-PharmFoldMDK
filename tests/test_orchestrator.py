"""D-030 worker-loop tests — pure, injected doubles, no GPU. Written before the loop.

The loop's whole correctness surface is here: done-ordering (upload before complete,
never the reverse), the failure taxonomy (transport retried / fold-failure reported /
nothing re-folded), and the empty-queue poll. `fold` and the queue-client are injected.
"""

from worker.orchestrator import AuthError, FoldError, FoldSpec, TransportError, run_worker

SPEC = FoldSpec(job_id=1, sequence="MELLKAAR", model_revision="abc123",
                dtype="fp16", chunk_size=None, source="whole",
                ecd_start=None, ecd_end=None)

NOSLEEP = lambda _s: None


def _stop_after(n):
    box = {"i": 0}
    def stop():
        box["i"] += 1
        return box["i"] > n
    return stop


class FakeClient:
    """Records the ORDER of upload/complete/fail so the done-ordering is assertable."""

    def __init__(self, specs, *, upload_fails_first=0, claim_raises_first=0, claim_raises_auth=False):
        self._specs = list(specs)
        self._upload_fails_first = upload_fails_first
        self._claim_raises_first = claim_raises_first
        self._claim_raises_auth = claim_raises_auth
        self.claim_calls = 0
        self.uploaded, self.completed, self.failed, self.events = [], [], [], []

    def claim(self, worker_id):
        self.claim_calls += 1
        if self._claim_raises_auth:
            raise AuthError("POST /jobs/claim -> 401 (bearer token rejected)")
        if self._claim_raises_first > 0:
            self._claim_raises_first -= 1
            raise TransportError("claim endpoint down")
        return self._specs.pop(0) if self._specs else None

    def upload(self, job_id, artifacts):
        if self._upload_fails_first > 0:
            self._upload_fails_first -= 1
            raise TransportError("upload endpoint down")
        self.uploaded.append(job_id)
        self.events.append(("upload", job_id))

    def complete(self, job_id):
        self.completed.append(job_id)
        self.events.append(("complete", job_id))

    def fail(self, job_id, error):
        self.failed.append((job_id, error))
        self.events.append(("fail", job_id))


def test_successful_fold_uploads_then_completes_never_fails():
    folded = []
    c = FakeClient([SPEC])
    run_worker(c, lambda s: folded.append(s.job_id) or {"pdb": "x"},
               "w1", sleep=NOSLEEP, should_stop=_stop_after(1))
    assert folded == [1]
    assert c.events == [("upload", 1), ("complete", 1)]   # upload BEFORE complete
    assert c.failed == []


def test_deterministic_fold_failure_reports_fail_never_uploads():
    def fold(_s):
        raise FoldError("CUDA OOM on a 512-residue input")
    c = FakeClient([SPEC])
    run_worker(c, fold, "w1", sleep=NOSLEEP, should_stop=_stop_after(1))
    assert c.failed == [(1, "CUDA OOM on a 512-residue input")]
    assert c.uploaded == [] and c.completed == []         # no result for a failed fold


def test_upload_transport_failure_never_completes():
    """§3 forbidden-state guard: if the upload never lands, complete is NEVER called.
    A `complete` job with no structure behind it is the one error nothing can detect."""
    folded = []
    c = FakeClient([SPEC], upload_fails_first=99)          # upload always fails
    run_worker(c, lambda s: folded.append(1) or {"pdb": "x"},
               "w1", sleep=NOSLEEP, should_stop=_stop_after(1), submit_attempts=3)
    assert folded == [1]                                   # folded once
    assert c.completed == []                               # complete NEVER called


def test_upload_retries_without_refolding():
    """A transport blip on upload is retried — re-uploading is cheap; a rental-tier
    re-fold is PAID. Fold runs once; upload eventually lands, then complete."""
    folded = []
    c = FakeClient([SPEC], upload_fails_first=2)           # fails twice, then succeeds
    run_worker(c, lambda s: folded.append(1) or {"pdb": "x"},
               "w1", sleep=NOSLEEP, should_stop=_stop_after(1), submit_attempts=5)
    assert folded == [1]                                   # folded EXACTLY once
    assert c.uploaded == [1] and c.completed == [1]


def test_claim_transport_failure_touches_nothing_then_recovers():
    folded = []
    c = FakeClient([SPEC], claim_raises_first=1)           # first claim raises, then works
    run_worker(c, lambda s: folded.append(1) or {"pdb": "x"},
               "w1", sleep=NOSLEEP, should_stop=_stop_after(2))
    assert folded == [1]
    assert c.events == [("upload", 1), ("complete", 1)]


def test_auth_error_stops_the_loop_on_the_first_401_not_after_70_minutes():
    """closeout §4b: a truncated token polled and was rejected 401 every 5 s for 70 minutes,
    looking healthy. An AuthError is fatal — the loop stops on the FIRST one, loudly, rather
    than retrying forever."""
    folded = []
    c = FakeClient([SPEC], claim_raises_auth=True)
    run_worker(c, lambda s: folded.append(1), "w1", sleep=NOSLEEP, should_stop=_stop_after(5))
    assert c.claim_calls == 1                              # stopped on the FIRST 401
    assert folded == [] and c.failed == []                # never folded, never failed a job — just stopped


def test_unexpected_fold_exception_fails_the_job_and_the_batch_survives():
    """closeout §3a: an UNEXPECTED fold exception (a torch OOM/internal error the runner did not
    classify as FoldError) previously propagated and KILLED the worker — taking down every good
    fold queued behind it. It must fail the one job and let the batch continue."""
    spec2 = FoldSpec(job_id=2, sequence="MKKK", model_revision="abc123", dtype="fp16",
                     chunk_size=None, source="whole", ecd_start=None, ecd_end=None)
    c = FakeClient([SPEC, spec2])
    folded = []

    def fold(s):
        folded.append(s.job_id)
        if s.job_id == 1:
            raise RuntimeError("CUDA error: an illegal memory access was encountered")  # NOT FoldError
        return {"pdb": "x"}

    run_worker(c, fold, "w1", sleep=NOSLEEP, should_stop=_stop_after(2))
    assert folded == [1, 2]                                # job 1's crash did NOT stop the loop
    assert c.failed and c.failed[0][0] == 1 and "unexpected fold failure" in c.failed[0][1]
    assert c.completed == [2]                              # the good fold behind the bad one still landed


def test_empty_queue_polls_without_folding():
    folded = []
    c = FakeClient([])
    run_worker(c, lambda s: folded.append(1),
               "w1", sleep=NOSLEEP, should_stop=_stop_after(3))
    assert folded == []
    assert c.claim_calls == 3                              # polled each iteration
