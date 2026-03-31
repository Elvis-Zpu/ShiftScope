import json
from typing import Any


def parse_uploaded_dataset_json(file_bytes: bytes) -> list[dict[str, Any]]:
    payload = json.loads(file_bytes.decode("utf-8"))

    if not isinstance(payload, list):
        raise ValueError("Uploaded dataset must be a JSON list of items")

    normalized_items = []
    for i, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {i} is not a JSON object")

        normalized_items.append(
            {
                "item_key": str(item.get("item_key", f"item-{i}")),
                "text_content": item.get("text_content"),
                "image_path": item.get("image_path"),
                "metadata_json": item.get("metadata_json", {}),
                "split": item.get("split"),
            }
        )

    return normalized_items