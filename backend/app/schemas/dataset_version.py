from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetVersionRead(BaseModel):
    id: int
    dataset_id: int
    version_tag: str
    original_filename: str
    storage_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)