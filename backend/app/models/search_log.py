from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SearchLog(Base):
    __tablename__ = "search_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    scorer: Mapped[str] = mapped_column(String(100), nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)