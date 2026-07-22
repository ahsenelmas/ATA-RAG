from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService


@dataclass(slots=True)
class ChunkEmbeddingResult:
    chunks_embedded: int
    batches_processed: int
    total_tokens: int


def embed_chunks(
    db: Session,
    embedding_service: EmbeddingService,
    batch_size: int = 32,
    force: bool = False,
) -> ChunkEmbeddingResult:
    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than zero."
        )

    statement = (
        select(Chunk)
        .order_by(
            Chunk.document_id,
            Chunk.chunk_index,
        )
    )

    if not force:
        statement = statement.where(
            Chunk.embedding.is_(None)
        )

    chunks_to_embed = list(
        db.scalars(statement).all()
    )

    if not chunks_to_embed:
        return ChunkEmbeddingResult(
            chunks_embedded=0,
            batches_processed=0,
            total_tokens=0,
        )

    embedded_count = 0
    batches_processed = 0
    total_tokens = 0

    try:
        for start in range(
            0,
            len(chunks_to_embed),
            batch_size,
        ):
            batch = chunks_to_embed[
                start:start + batch_size
            ]

            texts = [
                chunk.content
                for chunk in batch
            ]

            result = embedding_service.embed_texts(
                texts
            )

            for chunk, embedding in zip(
                batch,
                result.embeddings,
                strict=True,
            ):
                chunk.embedding = embedding

            db.commit()

            embedded_count += len(batch)
            batches_processed += 1
            total_tokens += result.total_tokens

    except Exception:
        db.rollback()
        raise

    return ChunkEmbeddingResult(
        chunks_embedded=embedded_count,
        batches_processed=batches_processed,
        total_tokens=total_tokens,
    )
