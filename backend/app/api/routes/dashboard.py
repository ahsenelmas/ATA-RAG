from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import (
    CrawlErrorItem,
    CrawlRunItem,
    CrawlRunsResponse,
    DashboardStatisticsResponse,
    FeedbackItem,
    FeedbackListResponse,
    RecentChatItem,
    RecentChatsResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get(
    "/statistics",
    response_model=DashboardStatisticsResponse,
)
def get_statistics(
    db: Session = Depends(get_db),
) -> DashboardStatisticsResponse:
    try:
        statistics = (
            DashboardService.get_statistics(
                db=db,
            )
        )

        return DashboardStatisticsResponse(
            **statistics # type: ignore
        )

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to load dashboard statistics."
            ),
        ) from error


@router.get(
    "/recent-chats",
    response_model=RecentChatsResponse,
)
def get_recent_chats(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> RecentChatsResponse:
    try:
        messages = (
            DashboardService.get_recent_chats(
                db=db,
                limit=limit,
            )
        )

        return RecentChatsResponse(
            items=[
                RecentChatItem(
                    id=message.id,
                    session_id=(
                        message.session_id
                    ),
                    question=message.question,
                    answer=message.answer,
                    language=message.language,
                    is_answered=(
                        message.is_answered
                    ),
                    retrieval_score=(
                        message.retrieval_score
                    ),
                    confidence=(
                        message.confidence
                    ),
                    latency_ms=(
                        message.latency_ms
                    ),
                    created_at=(
                        message.created_at
                    ),
                )
                for message in messages
            ]
        )

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to load recent chats."
            ),
        ) from error


@router.get(
    "/feedback",
    response_model=FeedbackListResponse,
)
def get_feedback(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> FeedbackListResponse:
    try:
        feedback_items = (
            DashboardService.get_feedback(
                db=db,
                limit=limit,
            )
        )

        return FeedbackListResponse(
            items=[
                FeedbackItem(
                    id=feedback.id,
                    message_id=(
                        feedback.message_id
                    ),
                    rating=feedback.rating,
                    comment=feedback.comment,
                    created_at=(
                        feedback.created_at
                    ),
                    question=(
                        feedback.message.question
                    ),
                    answer=(
                        feedback.message.answer
                    ),
                )
                for feedback in feedback_items
            ]
        )

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to load feedback."
            ),
        ) from error


@router.get(
    "/crawls",
    response_model=CrawlRunsResponse,
)
def get_crawl_runs(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
) -> CrawlRunsResponse:
    try:
        crawl_runs = (
            DashboardService.get_crawl_runs(
                db=db,
                limit=limit,
            )
        )

        return CrawlRunsResponse(
            items=[
                CrawlRunItem(
                    id=crawl_run.id,
                    status=crawl_run.status,
                    started_at=(
                        crawl_run.started_at
                    ),
                    finished_at=(
                        crawl_run.finished_at
                    ),
                    pages_discovered=(
                        crawl_run.pages_discovered
                    ),
                    pages_processed=(
                        crawl_run.pages_processed
                    ),
                    pages_failed=(
                        crawl_run.pages_failed
                    ),
                    pages_updated=(
                        crawl_run.pages_updated
                    ),
                    pages_unchanged=(
                        crawl_run.pages_unchanged
                    ),
                    chunks_created=(
                        crawl_run.chunks_created
                    ),
                    error_message=(
                        crawl_run.error_message
                    ),
                    errors=[
                        CrawlErrorItem(
                            id=error.id,
                            url=error.url,
                            error_type=(
                                error.error_type
                            ),
                            error_message=(
                                error.error_message
                            ),
                            created_at=(
                                error.created_at
                            ),
                        )
                        for error in crawl_run.errors
                    ],
                )
                for crawl_run in crawl_runs
            ]
        )

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to load crawl information."
            ),
        ) from error
