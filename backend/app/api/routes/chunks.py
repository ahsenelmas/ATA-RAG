from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chunk import Chunk
from app.models.document import Document

router = APIRouter(
    prefix="/api/chunks",
    tags=["Chunks"],
)


@router.get("")
def list_chunks(
    document_id: uuid.UUID | None = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    statement = (
        select(
            Chunk.id,
            Chunk.document_id,
            Document.title.label(
                "document_title"
            ),
            Document.url,
            Chunk.section_title,
            Chunk.chunk_index,
            Chunk.token_count,
            Chunk.content,
            Chunk.chunk_metadata,
        )
        .join(
            Document,
            Document.id == Chunk.document_id,
        )
        .order_by(
            Document.title,
            Chunk.chunk_index,
        )
        .limit(limit)
    )

    if document_id is not None:
        statement = statement.where(
            Chunk.document_id == document_id
        )

    rows = db.execute(statement).all()

    return [
        {
            "id": str(row.id),
            "document_id": str(
                row.document_id
            ),
            "document_title": (
                row.document_title
            ),
            "url": row.url,
            "section_title": (
                row.section_title
            ),
            "chunk_index": row.chunk_index,
            "token_count": row.token_count,
            "content": row.content,
            "metadata": row.chunk_metadata,
        }
        for row in rows
    ]
