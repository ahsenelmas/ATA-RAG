import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


FeedbackRating = Literal[
    "helpful",
    "not_helpful",
]


class FeedbackRequest(BaseModel):
    message_id: uuid.UUID

    rating: FeedbackRating

    comment: str | None = Field(
        default=None,
        max_length=1000,
    )


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    message_id: uuid.UUID
    rating: FeedbackRating
    comment: str | None
    created_at: datetime
