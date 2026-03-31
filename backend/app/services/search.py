import re
from typing import Iterable

from app.models.data_item import DataItem


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def score_item(query: str, item: DataItem) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0

    text = (item.text_content or "").lower()
    text_tokens = set(tokenize(text))

    overlap = len(query_tokens & text_tokens)

    substring_bonus = 0.0
    if query.lower() in text:
        substring_bonus = 2.0

    metadata_bonus = 0.0
    metadata = item.metadata_json or {}
    metadata_values = " ".join(str(v).lower() for v in metadata.values())
    metadata_tokens = set(tokenize(metadata_values))
    metadata_overlap = len(query_tokens & metadata_tokens)
    metadata_bonus = 0.5 * metadata_overlap

    return float(overlap) + substring_bonus + metadata_bonus


def rank_items(query: str, items: Iterable[DataItem], top_k: int) -> list[tuple[DataItem, float]]:
    scored = []
    for item in items:
        score = score_item(query, item)
        if score > 0:
            scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]