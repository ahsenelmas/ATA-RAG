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
    )


class ChatSource(BaseModel):
    title: str
    section: str | None = None
    url: str
    similarity: float
    final_score: float


class ChatResponse(BaseModel):
    answer: str
    language: str
    grounded: bool
    sources: list[ChatSource]
