from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.chat_message import ChatMessage
from app.models.chunk import Chunk
from app.models.crawl_error import CrawlError
from app.models.crawl_run import CrawlRun
from app.models.document import Document
from app.models.feedback import Feedback


class DashboardService:
    @staticmethod
    def get_statistics(
        *,
        db: Session,
    ) -> dict[str, int | float | object | None]:
        total_documents = (
            db.scalar(
                select(func.count(Document.id))
            )
            or 0
        )

        total_chunks = (
            db.scalar(
                select(func.count(Chunk.id))
            )
            or 0
        )

        embedded_chunks = (
            db.scalar(
                select(func.count(Chunk.id)).where(
                    Chunk.embedding.is_not(None)
                )
            )
            or 0
        )

        total_chat_messages = (
            db.scalar(
                select(func.count(ChatMessage.id))
            )
            or 0
        )

        grounded_messages = (
            db.scalar(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.is_answered.is_(True)
                )
            )
            or 0
        )

        total_feedback = (
            db.scalar(
                select(func.count(Feedback.id))
            )
            or 0
        )

        helpful_feedback = (
            db.scalar(
                select(func.count(Feedback.id)).where(
                    Feedback.rating == "helpful"
                )
            )
            or 0
        )

        not_helpful_feedback = (
            db.scalar(
                select(func.count(Feedback.id)).where(
                    Feedback.rating == "not_helpful"
                )
            )
            or 0
        )

        total_crawl_runs = (
            db.scalar(
                select(func.count(CrawlRun.id))
            )
            or 0
        )

        total_crawl_errors = (
            db.scalar(
                select(func.count(CrawlError.id))
            )
            or 0
        )

        latest_crawl_at = db.scalar(
            select(CrawlRun.started_at)
            .order_by(CrawlRun.started_at.desc())
            .limit(1)
        )

        grounded_rate = (
            round(
                grounded_messages
                / total_chat_messages
                * 100,
                2,
            )
            if total_chat_messages > 0
            else 0.0
        )

        positive_feedback_rate = (
            round(
                helpful_feedback
                / total_feedback
                * 100,
                2,
            )
            if total_feedback > 0
            else 0.0
        )

        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "total_chat_messages": total_chat_messages,
            "grounded_messages": grounded_messages,
            "grounded_rate": grounded_rate,
            "total_feedback": total_feedback,
            "helpful_feedback": helpful_feedback,
            "not_helpful_feedback": not_helpful_feedback,
            "positive_feedback_rate": (
                positive_feedback_rate
            ),
            "total_crawl_runs": total_crawl_runs,
            "total_crawl_errors": total_crawl_errors,
            "latest_crawl_at": latest_crawl_at,
        }

    @staticmethod
    def get_recent_chats(
        *,
        db: Session,
        limit: int = 20,
    ) -> list[ChatMessage]:
        statement = (
            select(ChatMessage)
            .order_by(
                ChatMessage.created_at.desc()
            )
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def get_feedback(
        *,
        db: Session,
        limit: int = 20,
    ) -> list[Feedback]:
        statement = (
            select(Feedback)
            .options(
                selectinload(
                    Feedback.message
                )
            )
            .order_by(
                Feedback.created_at.desc()
            )
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def get_crawl_runs(
        *,
        db: Session,
        limit: int = 10,
    ) -> list[CrawlRun]:
        statement = (
            select(CrawlRun)
            .options(
                selectinload(
                    CrawlRun.errors
                )
            )
            .order_by(
                CrawlRun.started_at.desc()
            )
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )
