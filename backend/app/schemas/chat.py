import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Question submitted by the user.",
    )

    language: str | None = Field(
        default=None,
        pattern="^(pl|en)$",
        description=(
            "Optional response language. "
            "When omitted, it is detected automatically."
        ),
    )

    retrieval_limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of retrieved context chunks.",
    )

    session_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Optional conversation session identifier. "
            "A new UUID is generated when omitted."
        ),
    )


class ChatSource(BaseModel):
    title: str

    section: str | None = None

    url: str

    similarity: float

    final_score: float


class ChatResponse(BaseModel):
    message_id: uuid.UUID

    session_id: uuid.UUID

    answer: str

    language: str

    grounded: bool

    sources: list[ChatSource]
