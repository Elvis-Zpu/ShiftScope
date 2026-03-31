from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    modality_type: str = "multimodal"


class DatasetRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    modality_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)