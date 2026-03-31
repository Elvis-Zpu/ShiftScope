from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False, index=True)
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scorer: Mapped[str] = mapped_column(String(100), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)