from pathlib import Path
import json


ARTIFACT_ROOT = Path("artifacts")


def ensure_artifact_dirs():
    (ARTIFACT_ROOT / "embeddings").mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / "indexes").mkdir(parents=True, exist_ok=True)


def write_json_artifact(relative_path: str, payload: dict) -> str:
    full_path = ARTIFACT_ROOT / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return str(full_path)


def read_json_artifact(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)