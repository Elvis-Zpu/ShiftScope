from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class EmbedJobCreate(BaseModel):
    dataset_version_id: int
    model_name: str = "dummy-encoder"

class IndexJobCreate(BaseModel):
    dataset_version_id: int
    model_name: str = "dummy-encoder"

class JobRead(BaseModel):
    id: int
    job_type: str
    target_type: str
    target_id: Optional[int] = None
    status: str
    params_json: Optional[dict[str, Any]] = None
    result_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)