from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.data_item import DataItem
from app.schemas.dataset_version import DatasetVersionRead
from app.schemas.data_item import DataItemRead
from app.services.storage import upload_fileobj
from app.services.ingestion import parse_uploaded_dataset_json

router = APIRouter(prefix="/datasets", tags=["dataset_versions"])


@router.post("/{dataset_id}/versions", response_model=DatasetVersionRead)
def create_dataset_version(
    dataset_id: int,
    version_tag: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_bytes = file.file.read()

    object_name = f"datasets/{dataset_id}/{version_tag}/{file.filename}"
    upload_fileobj(
        file_obj=__import__("io").BytesIO(file_bytes),
        object_name=object_name,
        content_type=file.content_type,
    )

    dataset_version = DatasetVersion(
        dataset_id=dataset_id,
        version_tag=version_tag,
        original_filename=file.filename,
        storage_path=object_name,
    )
    db.add(dataset_version)
    db.commit()
    db.refresh(dataset_version)

    # 只处理 JSON 列表格式
    parsed_items = parse_uploaded_dataset_json(file_bytes)

    for item in parsed_items:
        db_item = DataItem(
            dataset_version_id=dataset_version.id,
            item_key=item["item_key"],
            text_content=item["text_content"],
            image_path=item["image_path"],
            metadata_json=item["metadata_json"],
            split=item["split"],
        )
        db.add(db_item)

    db.commit()
    return dataset_version


@router.get("/{dataset_id}/versions", response_model=list[DatasetVersionRead])
def list_dataset_versions(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return (
        db.query(DatasetVersion)
        .filter(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.id.desc())
        .all()
    )


@router.get("/{dataset_id}/items", response_model=list[DataItemRead])
def list_dataset_items(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    latest_version = (
        db.query(DatasetVersion)
        .filter(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.id.desc())
        .first()
    )
    if not latest_version:
        return []

    return (
        db.query(DataItem)
        .filter(DataItem.dataset_version_id == latest_version.id)
        .order_by(DataItem.id.asc())
        .all()
    )