from collections.abc import Generator

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSource,
)
from app.services.embedding_service import (
    EmbeddingService,
)
from app.services.llm_service import (
    LLMConfigurationError,
    LLMRequestError,
    LLMService,
)
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


def get_db() -> Generator[
    Session,
    None,
    None,
]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_rag_service() -> RAGService:
    embedding_service = (
        EmbeddingService()
    )

    llm_service = LLMService()

    return RAGService(
        embedding_service=embedding_service,
        llm_service=llm_service,
    )


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        rag_service = (
            create_rag_service()
        )

        result = (
            rag_service.answer_question(
                db=db,
                question=payload.question,
                language=payload.language,
                retrieval_limit=(
                    payload.retrieval_limit
                ),
            )
        )

    except LLMConfigurationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(error),
        ) from error

    except LLMRequestError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unexpected chat service error."
            ),
        ) from error

    return ChatResponse(
        answer=result.answer,
        language=result.language,
        grounded=result.grounded,
        sources=[
            ChatSource(
                title=source.title,
                section=source.section,
                url=source.url,
                similarity=(
                    source.similarity
                ),
                final_score=(
                    source.final_score
                ),
            )
            for source in result.sources
        ],
    )
