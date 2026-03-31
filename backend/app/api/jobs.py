from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import EmbedJobCreate, IndexJobCreate, JobRead
from app.workers.tasks import run_embed_job, run_index_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/embed", response_model=JobRead)
def create_embed_job(payload: EmbedJobCreate, db: Session = Depends(get_db)):
    job = Job(
        job_type="embed",
        target_type="dataset_version",
        target_id=payload.dataset_version_id,
        status="queued",
        params_json={
            "dataset_version_id": payload.dataset_version_id,
            "model_name": payload.model_name,
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    run_embed_job.delay(job.id)
    return job


@router.post("/index", response_model=JobRead)
def create_index_job(payload: IndexJobCreate, db: Session = Depends(get_db)):
    job = Job(
        job_type="index",
        target_type="dataset_version",
        target_id=payload.dataset_version_id,
        status="queued",
        params_json={
            "dataset_version_id": payload.dataset_version_id,
            "model_name": payload.model_name,
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    run_index_job.delay(job.id)
    return job


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.id.desc()).all()


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job