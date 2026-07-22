import sys

from app.db.session import SessionLocal
from app.services.chunk_ingestion import (
    create_chunks_for_all_documents,
)
from app.services.markdown_chunker import (
    MarkdownChunker,
)


def run() -> int:
    chunker = MarkdownChunker(
        max_tokens=700,
        overlap_tokens=80,
    )

    print("Starting document chunking.")
    print("-" * 70)

    try:
        with SessionLocal() as db:
            results = (
                create_chunks_for_all_documents(
                    db=db,
                    chunker=chunker,
                )
            )

            total_chunks = 0

            for result in results:
                total_chunks += (
                    result.chunks_created
                )

                print(
                    f"{result.title}: "
                    f"{result.chunks_created} chunks"
                )

            print("-" * 70)
            print(
                f"Documents processed: "
                f"{len(results)}"
            )
            print(
                f"Total chunks created: "
                f"{total_chunks}"
            )

        return 0

    except Exception as error:
        print(
            f"Chunking failed: "
            f"{type(error).__name__}: {error}"
        )

        return 1


if __name__ == "__main__":
    sys.exit(run())
