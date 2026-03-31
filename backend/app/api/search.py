from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.data_item import DataItem
from app.models.search_log import SearchLog
from app.schemas.search import (
    TextSearchRequest,
    TextSearchResponse,
    SearchResultItem,
)
from app.services.search import rank_items

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/text", response_model=TextSearchResponse)
def search_text(payload: TextSearchRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    latest_version = (
        db.query(DatasetVersion)
        .filter(DatasetVersion.dataset_id == payload.dataset_id)
        .order_by(DatasetVersion.id.desc())
        .first()
    )
    if not latest_version:
        raise HTTPException(status_code=404, detail="No dataset version found")

    items = (
        db.query(DataItem)
        .filter(DataItem.dataset_version_id == latest_version.id)
        .all()
    )

    ranked = rank_items(payload.query, items, payload.top_k)

    results = [
        SearchResultItem(
            item_id=item.id,
            item_key=item.item_key,
            text_content=item.text_content,
            image_path=item.image_path,
            metadata_json=item.metadata_json,
            score=score,
        )
        for item, score in ranked
    ]

    log_row = SearchLog(
        dataset_id=payload.dataset_id,
        dataset_version_id=latest_version.id,
        query_text=payload.query,
        top_k=payload.top_k,
        scorer="keyword-overlap-baseline",
        result_count=len(results),
    )
    db.add(log_row)
    db.commit()

    return TextSearchResponse(
        query=payload.query,
        dataset_id=payload.dataset_id,
        dataset_version_id=latest_version.id,
        scorer="keyword-overlap-baseline",
        top_k=payload.top_k,
        results=results,
    )