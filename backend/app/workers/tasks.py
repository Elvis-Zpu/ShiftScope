import os
from datetime import datetime

from app.db.session import SessionLocal
from app.models.job import Job
from app.models.dataset_version import DatasetVersion
from app.models.data_item import DataItem
from app.models.index import Index
from app.services.artifacts import ensure_artifact_dirs, write_json_artifact
from app.services.search import build_lexical_index
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

        dataset_version = (
            db.query(DatasetVersion)
            .filter(DatasetVersion.id == dataset_version_id)
            .first()
        )
        if not dataset_version:
            raise ValueError(f"DatasetVersion {dataset_version_id} not found")

        items = (
            db.query(DataItem)
            .filter(DataItem.dataset_version_id == dataset_version_id)
            .order_by(DataItem.id.asc())
            .all()
        )
        if not items:
            raise ValueError(f"No DataItems found for dataset_version_id={dataset_version_id}")

        item_payloads = [
            {
                "item_id": item.id,
                "item_key": item.item_key,
                "text_content": item.text_content,
                "image_path": item.image_path,
                "metadata_json": item.metadata_json,
            }
            for item in items
        ]

        lexical_index_payload = build_lexical_index(item_payloads)
        lexical_index_payload["dataset_version_id"] = dataset_version_id
        lexical_index_payload["model_name"] = model_name
        lexical_index_payload["generated_at"] = datetime.utcnow().isoformat()

        index_relative_path = f"indexes/{dataset_version_id}/{model_name}.json"
        index_full_path = write_json_artifact(index_relative_path, lexical_index_payload)

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
            "message": "lexical index artifact generated",
            "dataset_version_id": dataset_version_id,
            "model_name": model_name,
            "artifact_path": index_full_path,
            "artifact_exists": os.path.exists(index_full_path),
            "index_id": index_record.id,
            "num_items": len(items),
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