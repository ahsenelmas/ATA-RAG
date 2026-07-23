import uuid
from datetime import datetime

from pydantic import BaseModel


class DashboardStatisticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    embedded_chunks: int
    total_chat_messages: int
    grounded_messages: int
    grounded_rate: float
    total_feedback: int
    helpful_feedback: int
    not_helpful_feedback: int
    positive_feedback_rate: float
    total_crawl_runs: int
    total_crawl_errors: int
    latest_crawl_at: datetime | None


class RecentChatItem(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    question: str
    answer: str
    language: str | None
    is_answered: bool
    retrieval_score: float | None
    confidence: float | None
    latency_ms: int | None
    created_at: datetime


class RecentChatsResponse(BaseModel):
    items: list[RecentChatItem]


class FeedbackItem(BaseModel):
    id: uuid.UUID
    message_id: uuid.UUID
    rating: str
    comment: str | None
    created_at: datetime
    question: str
    answer: str


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItem]


class CrawlErrorItem(BaseModel):
    id: uuid.UUID
    url: str
    error_type: str
    error_message: str
    created_at: datetime


class CrawlRunItem(BaseModel):
    id: uuid.UUID
    status: str
    started_at: datetime
    finished_at: datetime | None
    pages_discovered: int
    pages_processed: int
    pages_failed: int
    pages_updated: int
    pages_unchanged: int
    chunks_created: int
    error_message: str | None
    errors: list[CrawlErrorItem]


class CrawlRunsResponse(BaseModel):
    items: list[CrawlRunItem]
