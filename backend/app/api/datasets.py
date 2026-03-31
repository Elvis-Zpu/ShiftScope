from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetRead

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetRead)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    dataset = Dataset(
        name=payload.name,
        description=payload.description,
        modality_type=payload.modality_type,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).order_by(Dataset.id.desc()).all()


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset