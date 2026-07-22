import argparse
import sys

from app.db.session import SessionLocal
from app.services.chunk_embedding import embed_chunks
from app.services.embedding_service import EmbeddingService


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and store embeddings for ATA RAG chunks."
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Number of chunks processed in one batch.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate embeddings that already exist.",
    )

    return parser.parse_args()


def run() -> int:
    arguments = parse_arguments()

    print("Starting chunk embedding.")
    print(f"Batch size: {arguments.batch_size}")
    print(f"Force regeneration: {arguments.force}")
    print("-" * 70)

    try:
        embedding_service = EmbeddingService()

        with SessionLocal() as db:
            result = embed_chunks(
                db=db,
                embedding_service=embedding_service,
                batch_size=arguments.batch_size,
                force=arguments.force,
            )

        print("Embedding completed.")
        print(f"Chunks embedded: {result.chunks_embedded}")
        print(f"Batches processed: {result.batches_processed}")
        print(f"Tokens used: {result.total_tokens}")

        return 0

    except Exception as error:
        print(
            f"Embedding failed: "
            f"{type(error).__name__}: {error}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(run())
