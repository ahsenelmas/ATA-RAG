from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    statement = (
        select(
            Document.id,
            Document.title,
            Document.url,
            Document.language,
            func.length(
                Document.markdown
            ).label("markdown_length"),
            Document.created_at,
            Document.updated_at,
        )
        .order_by(Document.created_at.desc())
    )

    rows = db.execute(statement).all()

    return [
        {
            "id": str(row.id),
            "title": row.title,
            "url": row.url,
            "language": row.language,
            "markdown_length": row.markdown_length,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]
