import os
from datetime import datetime

from app.db.session import SessionLocal
from app.models.job import Job
from app.models.dataset_version import DatasetVersion
from app.models.index import Index
from app.services.artifacts import ensure_artifact_dirs, write_json_artifact, read_json_artifact
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.run_embed_job")
def run_embed_job(job_id: int):
    db = SessionLocal()
    try:
        ensure_artifact_dirs()

        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        params = job.params_json or {}
        dataset_version_id = params.get("dataset_version_id")
        model_name = params.get("model_name", "dummy-encoder")

        dataset_version = (
            db.query(DatasetVersion)
            .filter(DatasetVersion.id == dataset_version_id)
            .first()
        )
        if not dataset_version:
            raise ValueError(f"DatasetVersion {dataset_version_id} not found")

        artifact_relative_path = f"embeddings/{dataset_version_id}/{model_name}.json"
        artifact_payload = {
            "artifact_type": "dummy_embedding_output",
            "dataset_version_id": dataset_version.id,
            "dataset_id": dataset_version.dataset_id,
            "version_tag": dataset_version.version_tag,
            "original_filename": dataset_version.original_filename,
            "source_storage_path": dataset_version.storage_path,
            "model_name": model_name,
            "generated_at": datetime.utcnow().isoformat(),
            "note": "placeholder artifact before real embedding pipeline"
        }

        artifact_full_path = write_json_artifact(artifact_relative_path, artifact_payload)

        job.status = "success"
        job.result_json = {
            "message": "embedding artifact generated",
            "dataset_version_id": dataset_version_id,
            "model_name": model_name,
            "artifact_path": artifact_full_path,
            "artifact_exists": os.path.exists(artifact_full_path),
        }
        job.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_index_job")
def run_index_job(job_id: int):
    db = SessionLocal()
    try:
        ensure_artifact_dirs()

        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        params = job.params_json or {}
        dataset_version_id = params.get("dataset_version_id")
        model_name = params.get("model_name", "dummy-encoder")

        embed_artifact_path = f"artifacts/embeddings/{dataset_version_id}/{model_name}.json"
        if not os.path.exists(embed_artifact_path):
            raise ValueError(f"Embedding artifact not found: {embed_artifact_path}")

        embed_artifact = read_json_artifact(embed_artifact_path)

        index_relative_path = f"indexes/{dataset_version_id}/{model_name}.json"
        index_payload = {
            "artifact_type": "dummy_index_output",
            "dataset_version_id": dataset_version_id,
            "model_name": model_name,
            "source_embedding_artifact": embed_artifact_path,
            "source_embedding_summary": embed_artifact,
            "generated_at": datetime.utcnow().isoformat(),
            "note": "placeholder index artifact before real FAISS pipeline"
        }

        index_full_path = write_json_artifact(index_relative_path, index_payload)

        index_record = Index(
            dataset_version_id=dataset_version_id,
            model_name=model_name,
            artifact_path=index_full_path,
            status="ready",
        )
        db.add(index_record)
        db.commit()
        db.refresh(index_record)

        job.status = "success"
        job.result_json = {
            "message": "index artifact generated",
            "dataset_version_id": dataset_version_id,
            "model_name": model_name,
            "artifact_path": index_full_path,
            "artifact_exists": os.path.exists(index_full_path),
            "index_id": index_record.id,
        }
        job.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()