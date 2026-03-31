from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FailureCase(Base):
    __tablename__ = "failure_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    eval_run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), nullable=False, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    expected_item_key: Mapped[str] = mapped_column(String(255), nullable=False)
    failure_type: Mapped[str] = mapped_column(String(100), nullable=False)
    details_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)