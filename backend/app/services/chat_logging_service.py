import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage


class ChatLoggingService:
    @staticmethod
    def create_message(
        *,
        db: Session,
        session_id: uuid.UUID,
        question: str,
        answer: str,
        sources: list[dict[str, Any]],
        language: str | None,
        grounded: bool,
        latency_ms: int | None = None,
        retrieval_score: float | None = None,
        confidence: float | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            question=question,
            answer=answer,
            sources=sources,
            retrieval_score=retrieval_score,
            confidence=confidence,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            language=language,
            is_answered=grounded,
        )

        db.add(message)

        try:
            db.commit()
            db.refresh(message)
        except Exception:
            db.rollback()
            raise

        return message
