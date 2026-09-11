import os
from pathlib import Path
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from db.dburl import normalize_db_url
from db.models import JobRecord, ProteinAnalysis
from core.hold48 import emit_tile_jobs, IGF2R_ACCESSION, MUCIN_ACCESSIONS

for line in Path(".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

eng = create_engine(
    normalize_db_url(os.environ["DATABASE_URL"]),
    connect_args={"connect_timeout": 10},
)

MUCINS = sorted(MUCIN_ACCESSIONS) if "MUCIN_ACCESSIONS" in dir() else ["Q8WXI7", "Q9UKN1", "Q685J3"]

with Session(eng) as session:
    # Prefer pending hold parent, tier NULL; never failed historical job 57
    parents = session.execute(
        select(JobRecord, ProteinAnalysis)
        .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
        .where(ProteinAnalysis.input_value == IGF2R_ACCESSION)
        .order_by(JobRecord.id)
    ).all()
    print("P11717_CANDIDATES")
    for job, a in parents:
        meta = a.meta or {}
        print(
            {
                "job_id": job.id,
                "status": job.status,
                "tier": job.tier,
                "analysis_id": a.id,
                "span_aa": meta.get("span_aa") or meta.get("fold_length"),
                "hold48_kind": meta.get("hold48_kind"),
                "parent_job_id": (job.inference_settings or {}).get("parent_job_id"),
                "tile_index": (job.inference_settings or {}).get("tile_index"),
            }
        )

    chosen = None
    for job, a in parents:
        if job.id == 57:
            continue
        if job.tier is not None:
            continue
        if job.status not in ("pending", "claimed", "failed", "complete"):
            continue
        # hold parent: no parent_job_id on itself, not a tile
        settings = job.inference_settings or {}
        if settings.get("parent_job_id") is not None:
            continue
        if settings.get("tile_index") is not None:
            continue
        meta = a.meta or {}
        if meta.get("hold48_kind") == "tile":
            continue
        chosen = (job, a)
        # prefer pending
        if job.status == "pending" and job.tier is None:
            break

    if chosen is None:
        # fallback: first tier-NULL non-57 non-tile
        for job, a in parents:
            if job.id == 57:
                continue
            if job.tier is None and (job.inference_settings or {}).get("parent_job_id") is None:
                chosen = (job, a)
                break

    if chosen is None:
        raise SystemExit("NO_SUITABLE_P11717_PARENT")

    parent_job, parent_a = chosen
    print("CHOSEN_PARENT", parent_job.id, parent_job.status, parent_job.tier, parent_a.id)
    assert parent_job.tier is None
    assert parent_job.id != 57

    # existing rental children before emit
    before_tiles = session.execute(
        select(JobRecord)
        .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
        .where(
            ProteinAnalysis.input_value == IGF2R_ACCESSION,
            JobRecord.tier == "rental",
        )
    ).scalars().all()
    print("BEFORE_RENTAL_CHILD_COUNT", len(before_tiles), [j.id for j in before_tiles])

    if before_tiles:
        # if already 2 pending tiles for this parent, do not double-emit
        linked = [
            j
            for j in before_tiles
            if (j.inference_settings or {}).get("parent_job_id") == parent_job.id
        ]
        if len(linked) >= 2:
            print("ALREADY_EMITTED", [(j.id, j.status, (j.inference_settings or {}).get("tile_index")) for j in linked])
            session.rollback()
            raise SystemExit("ALREADY_EMITTED_SKIP")

    specs = emit_tile_jobs(session, parent_job, parent_a)
    session.commit()
    session.refresh(parent_job)
    assert len(specs) == 2, specs
    assert parent_job.tier is None
    print("SPECS", [(s.tile_index, s.start, s.end, s.length) for s in specs])

    children = session.execute(
        select(JobRecord, ProteinAnalysis)
        .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
        .where(
            ProteinAnalysis.input_value == IGF2R_ACCESSION,
            JobRecord.tier == "rental",
        )
        .order_by(JobRecord.id)
    ).all()
    print("AFTER_P11717_RENTAL")
    for job, a in children:
        settings = job.inference_settings or {}
        meta = a.meta or {}
        if settings.get("parent_job_id") != parent_job.id:
            continue
        length = meta.get("span_aa") or meta.get("fold_length")
        print(
            {
                "job_id": job.id,
                "status": job.status,
                "tier": job.tier,
                "tile_index": settings.get("tile_index"),
                "tile_start": settings.get("tile_start"),
                "tile_end": settings.get("tile_end"),
                "length": length,
                "dtype": settings.get("dtype"),
                "chunk_size": settings.get("chunk_size"),
            }
        )
        assert job.status == "pending"
        assert job.tier == "rental"
        assert int(length) <= 1656

    # mucin dry-check: zero NEW rental jobs (report counts)
    print("MUCIN_RENTAL_JOBS")
    for acc in ("Q8WXI7", "Q9UKN1", "Q685J3"):
        n = session.execute(
            select(JobRecord)
            .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
            .where(ProteinAnalysis.input_value == acc, JobRecord.tier == "rental")
        ).scalars().all()
        print(acc, len(n), [j.id for j in n])

    print("EMIT_COMMITTED parent_job_id=", parent_job.id)
