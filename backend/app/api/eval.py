from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.data_item import DataItem
from app.models.eval_run import EvalRun
from app.models.failure_case import FailureCase
from app.schemas.eval import (
    TextEvalRunCreate,
    EvalRunRead,
    FailureCaseRead,
)
from app.services.search import rank_items

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.post("/runs/text-baseline", response_model=EvalRunRead)
def run_text_baseline_eval(payload: TextEvalRunCreate, db: Session = Depends(get_db)):
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

    if not items:
        raise HTTPException(status_code=400, detail="No data items found for latest dataset version")

    total = len(payload.queries)
    hits = 0
    reciprocal_rank_sum = 0.0

    eval_run = EvalRun(
        dataset_id=payload.dataset_id,
        dataset_version_id=latest_version.id,
        run_name=payload.run_name,
        scorer="keyword-overlap-baseline",
        top_k=payload.top_k,
        metrics_json={},
    )
    db.add(eval_run)
    db.commit()
    db.refresh(eval_run)

    for query_item in payload.queries:
        ranked = rank_items(query_item.query, items, payload.top_k)
        ranked_keys = [item.item_key for item, _ in ranked]

        found_rank = None
        for i, item_key in enumerate(ranked_keys, start=1):
            if item_key == query_item.expected_item_key:
                found_rank = i
                break

        if found_rank is not None:
            hits += 1
            reciprocal_rank_sum += 1.0 / found_rank
        else:
            failure = FailureCase(
                eval_run_id=eval_run.id,
                query_text=query_item.query,
                expected_item_key=query_item.expected_item_key,
                failure_type="not_in_top_k",
                details_json={
                    "returned_item_keys": ranked_keys,
                    "top_k": payload.top_k,
                },
            )
            db.add(failure)

    recall_at_k = hits / total if total > 0 else 0.0
    mrr = reciprocal_rank_sum / total if total > 0 else 0.0

    eval_run.metrics_json = {
        "num_queries": total,
        "hits_at_k": hits,
        "recall_at_k": recall_at_k,
        "mrr": mrr,
    }
    db.commit()
    db.refresh(eval_run)

    return eval_run


@router.get("/runs", response_model=list[EvalRunRead])
def list_eval_runs(db: Session = Depends(get_db)):
    return db.query(EvalRun).order_by(EvalRun.id.desc()).all()


@router.get("/runs/{eval_run_id}", response_model=EvalRunRead)
def get_eval_run(eval_run_id: int, db: Session = Depends(get_db)):
    row = db.query(EvalRun).filter(EvalRun.id == eval_run_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Eval run not found")
    return row


@router.get("/runs/{eval_run_id}/failures", response_model=list[FailureCaseRead])
def list_eval_failures(eval_run_id: int, db: Session = Depends(get_db)):
    return (
        db.query(FailureCase)
        .filter(FailureCase.eval_run_id == eval_run_id)
        .order_by(FailureCase.id.asc())
        .all()
    )