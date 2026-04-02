from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.search_log import SearchLog

router = APIRouter(prefix="/search-logs", tags=["search_logs"])


@router.get("")
def list_search_logs(db: Session = Depends(get_db)):
    rows = (
        db.query(SearchLog)
        .order_by(SearchLog.id.desc())
        .all()
    )

    return [
        {
            "id": row.id,
            "dataset_id": row.dataset_id,
            "dataset_version_id": row.dataset_version_id,
            "query_text": row.query_text,
            "top_k": row.top_k,
            "scorer": row.scorer,
            "result_count": row.result_count,
            "created_at": row.created_at,
        }
        for row in rows
    ]