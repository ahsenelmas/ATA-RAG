from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.feedback import (
    FeedbackRequest,
    FeedbackResponse,
)
from app.services.feedback_service import (
    FeedbackAlreadyExistsError,
    FeedbackMessageNotFoundError,
    FeedbackService,
)


router = APIRouter(
    prefix="/api/feedback",
    tags=["feedback"],
)


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    try:
        feedback = FeedbackService.create_feedback(
            db=db,
            message_id=payload.message_id,
            rating=payload.rating,
            comment=payload.comment,
        )

    except FeedbackMessageNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except FeedbackAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unexpected feedback service error.",
        ) from error

    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
    )
