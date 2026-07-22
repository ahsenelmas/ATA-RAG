import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CrawlRun(Base):
    __tablename__ = "crawl_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pages_discovered: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    pages_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    pages_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    pages_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    pages_unchanged: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    chunks_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    errors: Mapped[list["CrawlError"]] = relationship(
        back_populates="crawl_run",
        cascade="all, delete-orphan",
    )


from app.models.crawl_error import CrawlError
