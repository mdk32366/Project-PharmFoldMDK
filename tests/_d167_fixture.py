"""D-167 — a synthetic volume capture built from COMMITTED evidence only.

⚠ No production byte is read. The 37's provenance fields and CA residues come from the committed
volume dump (`data/control/f078/`), the controls' full provenance and sequence from the committed
Phase B read (`data/control/d167/state_before.json`), and sizes from slice 2's `progress.csv`. What the
dump does not hold (the per-residue pLDDT array, the file hashes, the provenance fields beyond five)
is synthesised — and each synthesised value is chosen so the good capture is exactly what `verify()`
must accept, which makes every mutation a single, named departure from it.
"""

from __future__ import annotations

import copy
import csv
import datetime as dt
import hashlib
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
STATE_BEFORE = REPO / "data" / "control" / "d167" / "state_before.json"
PROGRESS = REPO / "data" / "control" / "task4_slice2" / "progress.csv"

ROOT = "/data/artifacts"
FIRST, LAST = 4869, 4905
CONTROLS = (4866, 4867, 4868)
OWED = tuple(range(FIRST, LAST + 1))


def load_state_before() -> dict:
    return json.loads(STATE_BEFORE.read_text(encoding="utf-8"))


def load_progress() -> dict[int, dict]:
    with open(PROGRESS, newline="", encoding="utf-8") as fh:
        return {int(r["job_id"]): r for r in csv.DictReader(fh)}


def structure_body(job_id: int) -> bytes:
    """The bytes a fake serving surface returns for a job's structure."""
    return f"HEADER synthetic structure for job {job_id}\n".encode("ascii")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def synthetic_capture(now: dt.datetime) -> dict:
    import scripts.f078_identity_check as ic

    state = load_state_before()
    progress = load_progress()
    dump_prov, dump_seqs = ic.parse_dump(ic.decode(ic.DUMP.read_bytes()))
    three = {one: tri for tri, one in ic.THREE.items()}
    controls = {c["job"]["id"]: c["analysis"] for c in state["control"]}

    dirs: dict[str, dict] = {}
    for job in range(CONTROLS[0], LAST + 1):
        if job in controls:
            prov = copy.deepcopy(controls[job]["metadata"]["fold_provenance"])
            seq = controls[job]["metadata"]["sequence"]
        else:
            d = dump_prov[job]
            prov = {"model_id": "facebook/esmfold_v1",
                    "model_revision": "75a3841ee059df2bf4d56688166c8fb459ddd97a",
                    "dtype": "int8", "chunk_size": 64, "source": "sliced_ecd",
                    "truncated": False, "length_cap": None, "original_length": d["input_length"],
                    "ca_atom_count": d["input_length"], **d}
            seq = dump_seqs[job]
        body = structure_body(job)

        def entry(name: str, size: int, digest: str, _job=job) -> dict:
            return {"path": f"{ROOT}/{_job}/{name}", "size": size, "sha256": digest}

        dirs[str(job)] = {
            "present": True,
            "path": f"{ROOT}/{job}",
            "files": {
                "structure.pdb": entry("structure.pdb", int(progress[job]["served_structure_bytes"]),
                                       sha(body)),
                "plddt.json": entry("plddt.json", 100, sha(b"plddt %d" % job)),
                "pae.json.gz": entry("pae.json.gz", 100, sha(b"pae %d" % job)),
                "provenance.json": entry("provenance.json", 100, sha(b"prov %d" % job)),
            },
            "provenance": prov,
            "plddt": [prov["mean_plddt"]] * len(seq),
            "ca_residues": [three[ch] for ch in seq],
        }
    return {"captured_at": now.astimezone(dt.timezone.utc).isoformat(), "root": ROOT,
            "first": CONTROLS[0], "last": LAST, "dirs": dirs}


def capture_bytes(capture: dict) -> bytes:
    return (json.dumps(capture, indent=1, sort_keys=True) + "\n").encode("utf-8")
