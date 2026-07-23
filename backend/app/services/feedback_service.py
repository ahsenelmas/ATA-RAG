import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.feedback import Feedback


class FeedbackMessageNotFoundError(Exception):
    pass


class FeedbackAlreadyExistsError(Exception):
    pass


class FeedbackService:
    @staticmethod
    def create_feedback(
        *,
        db: Session,
        message_id: uuid.UUID,
        rating: str,
        comment: str | None,
    ) -> Feedback:
        message = db.scalar(
            select(ChatMessage).where(
                ChatMessage.id == message_id
            )
        )

        if message is None:
            raise FeedbackMessageNotFoundError(
                "Chat message was not found."
            )

        existing_feedback = db.scalar(
            select(Feedback).where(
                Feedback.message_id == message_id
            )
        )

        if existing_feedback is not None:
            raise FeedbackAlreadyExistsError(
                "Feedback already exists for this message."
            )

        feedback = Feedback(
            message_id=message_id,
            rating=rating,
            comment=comment,
        )

        db.add(feedback)

        try:
            db.commit()
            db.refresh(feedback)

        except IntegrityError as error:
            db.rollback()

            raise FeedbackAlreadyExistsError(
                "Feedback already exists for this message."
            ) from error

        except Exception:
            db.rollback()
            raise

        return feedback
