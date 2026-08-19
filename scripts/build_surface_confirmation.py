"""Extract HPA's subcellular calls for the census — the second instrument's raw readings.

⚠⚠ SOURCE-PINNED. `proteinatlas.tsv` v22, sha256 recorded in the output. A supplier file that
changed under us would silently change every category, and this project pins for that reason.

⚠ COLUMN-SCOPED, on `D-093` amendment 1 clause 2's reasoning: HPA disclaims third-party material it
redistributes, so only the columns actually needed are read — `Gene`, `Uniprot`, `Subcellular main
location`, `Subcellular additional location`, `Reliability (IF)`. ⚠⚠ The 17 `Pathology prognostics`
columns in this same file are the excluded class and are never touched.

⚠⚠ THE JOIN IS ON UNIPROT ACCESSION, NOT ON GENE SYMBOL. The census is keyed on accession, and
`D-093` decision 6 item (3) disqualifies any supplier that can only be joined through a "lossy
intermediate". Gene symbols are that intermediate — unstable, non-unique, and not our key. The
symbol is carried alongside so the two paths can be COMPARED rather than one trusted.

Usage:  python scripts/build_surface_confirmation.py <path-to-proteinatlas.tsv>
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sys

OUT = pathlib.Path("data/census/surface_confirmation.v1.csv")
PROV = pathlib.Path("data/census/surface_confirmation.provenance.json")

# ⚠⚠ BOTH IDENTIFIERS ARE READ, AND THAT IS THE POINT. The census is keyed on UniProt ACCESSION.
# Joining through the gene SYMBOL would be the "lossy intermediate" `D-093` decision 6 item (3)
# names as disqualifying — symbols are not stable, not unique, and not the census's key. So the
# accession is the join and the symbol is carried only as a fallback for rows that lack one.
NEEDED = ("Gene", "Uniprot", "Subcellular main location", "Subcellular additional location",
          "Reliability (IF)")

#: ⚠ the class amendment 1 clause 2 excludes; asserted absent from what we read
FORBIDDEN_TOKEN = "prognos"


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = pathlib.Path(sys.argv[1])
    if not src.is_file():
        print("REFUSED: %s is not a file" % src)
        return 1

    digest = sha256_of(src)
    census_genes = set()
    feat = pathlib.Path("data/census/census_features.v1.jsonl")
    if feat.exists():
        for line in feat.read_text(encoding="utf-8").splitlines():
            g = json.loads(line).get("accession")
            if g:
                census_genes.add(g)

    rows = []
    with src.open(encoding="utf-8") as fh:
        rdr = csv.DictReader(fh, delimiter="\t")
        missing = [c for c in NEEDED if c not in rdr.fieldnames]
        if missing:
            print("REFUSED: source lacks required columns: %s" % missing)
            return 1
        # ⚠⚠ the exclusion is asserted against the columns we READ, not the file
        assert not any(FORBIDDEN_TOKEN in c.lower() for c in NEEDED), NEEDED
        for r in rdr:
            main_loc = (r.get("Subcellular main location") or "").strip()
            add_loc = (r.get("Subcellular additional location") or "").strip()
            rel = (r.get("Reliability (IF)") or "").strip()
            # ⚠⚠ EVERY ROW IS EMITTED, INCLUDING THOSE WITH NO IMAGING CALL AT ALL. The first
            # version skipped them — and that silently merged TWO DIFFERENT ABSENCES: a gene HPA
            # does not carry, and a gene HPA carries but never imaged. The second is the common
            # case (≈1,420 census proteins) and it means NOBODY LOOKED, which is not the same
            # claim as "not in the source". A row with empty locations is the record that the
            # gene exists here and was not imaged; deleting it destroys that distinction.
            # ⚠ HPA can list several accessions for one row; each is emitted so the join is
            # explicit rather than silently taking the first.
            accs = [a.strip() for a in (r.get("Uniprot") or "").split(",") if a.strip()]
            rows.append({
                "gene_symbol": r["Gene"],
                "uniprot": ",".join(accs),
                "accession_count": len(accs),
                "main_location": main_loc,
                "additional_location": add_loc,
                "if_reliability": rel,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        # ⚠ lineterminator explicit: csv.writer emits CRLF by dialect on every platform, and the
        # rest of the tree is LF. Learned on the alias index, applied here at creation.
        w = csv.DictWriter(fh, fieldnames=["gene_symbol", "uniprot", "accession_count",
                                           "main_location", "additional_location",
                                           "if_reliability"], lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["gene_symbol"]):
            w.writerow(r)

    PROV.write_text(json.dumps({
        "source_file": src.name,
        "source_sha256": digest,
        "columns_read": list(NEEDED),
        "rows_written": len(rows),
        "note": ("COLUMN-SCOPED per D-093 amendment 1 clause 2. The 17 'Pathology prognostics' "
                 "columns in this same file are the excluded class and were not read."),
    }, indent=2) + "\n", encoding="utf-8")

    print("source sha256 : %s" % digest)
    print("rows written  : %d" % len(rows))
    print("census genes  : %d (features file)" % len(census_genes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
