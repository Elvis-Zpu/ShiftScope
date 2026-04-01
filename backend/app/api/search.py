from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.index import Index
from app.models.search_log import SearchLog
from app.schemas.search import (
    TextSearchRequest,
    TextSearchResponse,
    SearchResultItem,
)
from app.services.artifacts import read_json_artifact
from app.services.search import rank_indexed_items

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

    latest_index = (
        db.query(Index)
        .filter(Index.dataset_version_id == latest_version.id)
        .order_by(Index.id.desc())
        .first()
    )
    if not latest_index:
        raise HTTPException(status_code=404, detail="No index found for latest dataset version")

    index_artifact = read_json_artifact(latest_index.artifact_path)
    indexed_items = index_artifact.get("items", [])

    ranked = rank_indexed_items(payload.query, indexed_items, payload.top_k)

    results = [
        SearchResultItem(
            item_id=item["item_id"],
            item_key=item["item_key"],
            text_content=item.get("text_content"),
            image_path=item.get("image_path"),
            metadata_json=item.get("metadata_json"),
            score=score,
        )
        for item, score in ranked
    ]

    log_row = SearchLog(
        dataset_id=payload.dataset_id,
        dataset_version_id=latest_version.id,
        query_text=payload.query,
        top_k=payload.top_k,
        scorer="lexical-index-baseline",
        result_count=len(results),
    )
    db.add(log_row)
    db.commit()

    return TextSearchResponse(
        query=payload.query,
        dataset_id=payload.dataset_id,
        dataset_version_id=latest_version.id,
        scorer="lexical-index-baseline",
        top_k=payload.top_k,
        results=results,
    )