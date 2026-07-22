from dataclasses import dataclass
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.markdown_chunker import (
    MarkdownChunker,
)


@dataclass(slots=True)
class ChunkIngestionResult:
    document_id: str
    title: str
    chunks_created: int


def create_chunks_for_document(
    db: Session,
    document: Document,
    chunker: MarkdownChunker,
) -> ChunkIngestionResult:
    generated_chunks = chunker.chunk_document(
        document.markdown
    )

    db.execute(
        delete(Chunk).where(
            Chunk.document_id == document.id
        )
    )

    for generated_chunk in generated_chunks:
        chunk = Chunk(
            document_id=document.id,
            section_title=(
                generated_chunk.section_title
            ),
            content=generated_chunk.content,
            chunk_index=(
                generated_chunk.chunk_index
            ),
            token_count=(
                generated_chunk.token_count
            ),
            embedding=None,
            chunk_metadata={
                "url": document.url,
                "title": document.title,
                "section": (
                    generated_chunk.section_title
                ),
                "language": document.language,
                "source": "website",
            },
        )

        db.add(chunk)

    db.commit()

    return ChunkIngestionResult(
        document_id=str(document.id),
        title=document.title,
        chunks_created=len(generated_chunks),
    )


def create_chunks_for_all_documents(
    db: Session,
    chunker: MarkdownChunker,
) -> list[ChunkIngestionResult]:
    documents = db.scalars(
        select(Document).order_by(
            Document.created_at.asc()
        )
    ).all()

    results: list[ChunkIngestionResult] = []

    for document in documents:
        result = create_chunks_for_document(
            db=db,
            document=document,
            chunker=chunker,
        )

        results.append(result)

    return results


def create_chunks_for_document_id(
    db: Session,
    document_id: uuid.UUID,
    chunker: MarkdownChunker,
) -> ChunkIngestionResult:
    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise ValueError(
            f"Document not found: {document_id}"
        )

    return create_chunks_for_document(
        db=db,
        document=document,
        chunker=chunker,
    )
