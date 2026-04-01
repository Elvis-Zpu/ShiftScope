import re
from typing import Iterable


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def build_lexical_index(items: list[dict]) -> dict:
    indexed_items = []

    for item in items:
        text_content = item.get("text_content") or ""
        metadata = item.get("metadata_json") or {}

        metadata_text = " ".join(str(v) for v in metadata.values())
        combined_text = f"{text_content} {metadata_text}".strip()

        indexed_items.append(
            {
                "item_id": item["item_id"],
                "item_key": item["item_key"],
                "text_content": text_content,
                "image_path": item.get("image_path"),
                "metadata_json": metadata,
                "tokens": list(sorted(set(tokenize(combined_text)))),
            }
        )

    return {
        "index_type": "lexical-baseline",
        "num_items": len(indexed_items),
        "items": indexed_items,
    }


def score_indexed_item(query: str, indexed_item: dict) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0

    item_tokens = set(indexed_item.get("tokens", []))
    overlap = len(query_tokens & item_tokens)

    text_content = (indexed_item.get("text_content") or "").lower()
    substring_bonus = 2.0 if query.lower() in text_content else 0.0

    return float(overlap) + substring_bonus


def rank_indexed_items(query: str, indexed_items: Iterable[dict], top_k: int) -> list[tuple[dict, float]]:
    scored = []
    for item in indexed_items:
        score = score_indexed_item(query, item)
        if score > 0:
            scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def rank_items(query: str, items, top_k: int):
    normalized_items = []
    for item in items:
        metadata = item.metadata_json or {}
        metadata_text = " ".join(str(v) for v in metadata.values())
        combined_text = f"{item.text_content or ''} {metadata_text}".strip()

        normalized_items.append(
            {
                "item_id": item.id,
                "item_key": item.item_key,
                "text_content": item.text_content,
                "image_path": item.image_path,
                "metadata_json": item.metadata_json,
                "tokens": list(sorted(set(tokenize(combined_text)))),
            }
        )

    ranked = rank_indexed_items(query, normalized_items, top_k)

    # 保持 eval.py 原来的返回格式：[(item_obj, score), ...]
    item_map = {item.id: item for item in items}
    return [(item_map[row["item_id"]], score) for row, score in ranked]