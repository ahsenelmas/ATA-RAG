import argparse
import sys

from app.db.session import SessionLocal
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import retrieve_chunks


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search ATA RAG chunks using semantic similarity."
    )

    parser.add_argument(
        "question",
        type=str,
        help="Question to search for.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results.",
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional document language filter.",
    )

    return parser.parse_args()


def run() -> int:
    arguments = parse_arguments()

    try:
        embedding_service = EmbeddingService()

        with SessionLocal() as db:
            results = retrieve_chunks(
                db=db,
                question=arguments.question,
                embedding_service=embedding_service,
                limit=arguments.limit,
                language=arguments.language,
            )

        print()
        print(f"Question: {arguments.question}")
        print(f"Results: {len(results)}")
        print("=" * 80)

        for index, result in enumerate(
            results,
            start=1,
        ):
            print("=" * 80)
            print(
                f"{index}. "
                f"{result.document_title}"
            )
            print(
                "Section: "
                f"{result.section_title or 'N/A'}"
            )
            print(
                f"Language: "
                f"{result.language or 'N/A'}"
            )
            print(
                f"Similarity: "
                f"{result.similarity:.4f}"
            )
            print(
                f"Lexical bonus: "
                f"{result.lexical_bonus:+.4f}"
            )
            print(
                f"Final score: "
                f"{result.final_score:.4f}"
            )
            print(
                f"Distance: "
                f"{result.distance:.4f}"
            )
            print(
                f"URL: {result.url}"
            )
            print()
            print(result.content)
            print()

        return 0

    except Exception as error:
        print(
            f"Search failed: "
            f"{type(error).__name__}: {error}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(run())
