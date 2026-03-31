from typing import Optional, Any
from pydantic import BaseModel


class TextSearchRequest(BaseModel):
    dataset_id: int
    query: str
    top_k: int = 5


class SearchResultItem(BaseModel):
    item_id: int
    item_key: str
    text_content: Optional[str] = None
    image_path: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None
    score: float


class TextSearchResponse(BaseModel):
    query: str
    dataset_id: int
    dataset_version_id: int
    scorer: str
    top_k: int
    results: list[SearchResultItem]