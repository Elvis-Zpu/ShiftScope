from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class DataItemRead(BaseModel):
    id: int
    dataset_version_id: int
    item_key: str
    text_content: Optional[str] = None
    image_path: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None
    split: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)