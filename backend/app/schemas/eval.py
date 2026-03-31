from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class EvalQueryItem(BaseModel):
    query: str
    expected_item_key: str


class TextEvalRunCreate(BaseModel):
    dataset_id: int
    run_name: str
    top_k: int = 3
    queries: list[EvalQueryItem]


class EvalRunRead(BaseModel):
    id: int
    dataset_id: int
    dataset_version_id: int
    run_name: str
    scorer: str
    top_k: int
    metrics_json: Optional[dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FailureCaseRead(BaseModel):
    id: int
    eval_run_id: int
    query_text: str
    expected_item_key: str
    failure_type: str
    details_json: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)