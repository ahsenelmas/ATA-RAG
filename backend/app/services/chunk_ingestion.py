from dataclasses import dataclass
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.markdown_chunker import MarkdownChunker


@dataclass(slots=True)
class ChunkIngestionResult:
    document_id: str
    title: str
    chunks_created: int
    chunks_skipped: int


def normalize_for_deduplication(
    content: str,
) -> str:
    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    cleaned_lines: list[str] = []

    for line in lines:
        normalized_line = line.casefold()

        if (
            cleaned_lines
            and normalized_line
            == cleaned_lines[-1].casefold()
        ):
            continue

        cleaned_lines.append(line)

    return " ".join(
        cleaned_lines
    ).casefold()


def is_low_value_chunk(
    content: str,
    section_title: str | None,
) -> bool:
    normalized_content = " ".join(
        content.split()
    ).strip()

    if len(normalized_content) < 80:
        return True

    link_count = content.count("](")

    low_value_titles = {
        "student",
        "college",
        "candidate",
        "rekrutacja",
        "menu",
        "navigation",
    }

    normalized_title = (
        section_title.strip().casefold()
        if section_title
        else ""
    )

    if (
        normalized_title
        in low_value_titles
        and link_count >= 4
    ):
        return True

    if (
        link_count >= 8
        and len(normalized_content) < 800
    ):
        return True

    return False


def _existing_chunks_are_current(
    *,
    db: Session,
    document: Document,
) -> tuple[bool, int]:
    """
    Check whether existing chunks were generated from
    the current version of the document.

    Returns:
        (is_current, existing_chunk_count)
    """
    existing_chunk = db.scalar(
        select(Chunk)
        .where(
            Chunk.document_id == document.id
        )
        .order_by(
            Chunk.chunk_index.asc()
        )
        .limit(1)
    )

    if existing_chunk is None:
        return False, 0

    existing_chunk_count = (
        db.scalar(
            select(
                func.count(Chunk.id)
            ).where(
                Chunk.document_id
                == document.id
            )
        )
        or 0
    )

    stored_hash = (
        existing_chunk.chunk_metadata
        or {}
    ).get(
        "document_content_hash"
    )

    is_current = (
        stored_hash
        == document.content_hash
    )

    return (
        is_current,
        int(existing_chunk_count),
    )


def create_chunks_for_document(
    db: Session,
    document: Document,
    chunker: MarkdownChunker,
) -> ChunkIngestionResult:
    (
        chunks_are_current,
        existing_chunk_count,
    ) = _existing_chunks_are_current(
        db=db,
        document=document,
    )

    if chunks_are_current:
        return ChunkIngestionResult(
            document_id=str(
                document.id
            ),
            title=document.title,
            chunks_created=0,
            chunks_skipped=(
                existing_chunk_count
            ),
        )

    generated_chunks = (
        chunker.chunk_document(
            document.markdown
        )
    )

    db.execute(
        delete(Chunk).where(
            Chunk.document_id
            == document.id
        )
    )

    seen_contents: set[str] = set()

    stored_index = 0
    skipped_count = 0

    for generated_chunk in generated_chunks:
        if is_low_value_chunk(
            generated_chunk.content,
            generated_chunk.section_title,
        ):
            skipped_count += 1
            continue

        content_key = (
            normalize_for_deduplication(
                generated_chunk.content
            )
        )

        if not content_key:
            skipped_count += 1
            continue

        if content_key in seen_contents:
            skipped_count += 1
            continue

        seen_contents.add(
            content_key
        )

        chunk = Chunk(
            document_id=document.id,
            section_title=(
                generated_chunk.section_title
            ),
            content=(
                generated_chunk.content
            ),
            chunk_index=stored_index,
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
                "document_content_hash": (
                    document.content_hash
                ),
            },
        )

        db.add(chunk)

        stored_index += 1

    db.commit()

    return ChunkIngestionResult(
        document_id=str(
            document.id
        ),
        title=document.title,
        chunks_created=stored_index,
        chunks_skipped=skipped_count,
    )


def create_chunks_for_all_documents(
    db: Session,
    chunker: MarkdownChunker,
) -> list[ChunkIngestionResult]:
    documents = db.scalars(
        select(Document)
        .order_by(
            Document.created_at.asc()
        )
    ).all()

    results: list[
        ChunkIngestionResult
    ] = []

    for document in documents:
        result = (
            create_chunks_for_document(
                db=db,
                document=document,
                chunker=chunker,
            )
        )

        results.append(
            result
        )

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
            "Document not found: "
            f"{document_id}"
        )

    return create_chunks_for_document(
        db=db,
        document=document,
        chunker=chunker,
    )
