"""D-167 — READ-ONLY capture of the artifact directories of jobs 4866-4905, run ON the Fly machine.

⚠⚠ Never in the image, never pasted as text. It is delivered as the base64 of THIS committed file by
`python scripts/d167_reattach.py --print-capture-command`, and a test asserts that payload decodes to
this file byte for byte — so nothing outside version control determines what the capture reads
(`D-162` rule 8).

⚠ Standard library only: the machine's `python` runs it with nothing from this repository importable.
The CA residue names are recorded as three-letter codes; the one-letter map stays in one home
(`scripts/f078_identity_check.py::THREE`) and is applied locally by `verify()`.

⚠ It opens exactly one file for writing, `OUT`, and prints that file's sha256 as its LAST line. The
owner pastes that line; the local run refuses if the transferred file's sha256 differs.
"""

import datetime
import hashlib
import json
import os

OUT = "/tmp/d167_capture.json"
ROOT = "/data/artifacts"
FIRST, LAST = 4866, 4905


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _ca_residues(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                out.append(line[17:20])
    return out


def capture(root, first, last, now):
    root = root.replace("\\", "/").rstrip("/")
    dirs = {}
    for job in range(first, last + 1):
        d = f"{root}/{job}"
        if not os.path.isdir(d):
            dirs[str(job)] = {"present": False, "path": d}
            continue
        files = {}
        for name in sorted(os.listdir(d)):
            p = f"{d}/{name}"
            if os.path.isfile(p):
                files[name] = {"path": p, "size": os.path.getsize(p), "sha256": _sha256(p)}
        dirs[str(job)] = {
            "present": True,
            "path": d,
            "files": files,
            "provenance": _json(f"{d}/provenance.json") if "provenance.json" in files else None,
            "plddt": _json(f"{d}/plddt.json") if "plddt.json" in files else None,
            "ca_residues": _ca_residues(f"{d}/structure.pdb") if "structure.pdb" in files else [],
        }
    return {"captured_at": now.astimezone(datetime.timezone.utc).isoformat(), "root": root,
            "first": first, "last": last, "dirs": dirs}


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    result = capture(ROOT, FIRST, LAST, now)
    body = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode("utf-8")
    with open(OUT, "wb") as fh:
        fh.write(body)
    present = sum(1 for d in result["dirs"].values() if d["present"])
    print(f"captured {present} of {LAST - FIRST + 1} directories under {ROOT} at {result['captured_at']}")
    print(f"wrote {OUT} ({len(body)} bytes); sha256 on the next line")
    print(hashlib.sha256(body).hexdigest())


if __name__ == "__main__":
    main()
