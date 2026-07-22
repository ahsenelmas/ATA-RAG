from dataclasses import dataclass

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()


class EmbeddingServiceError(Exception):
    """Raised when local embeddings cannot be generated."""


@dataclass(slots=True)
class EmbeddingBatchResult:
    embeddings: list[list[float]]
    model: str
    total_tokens: int


class EmbeddingService:
    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:
        self.model_name = (
            model_name
            or settings.embedding_model
        )

        self.dimensions = (
            settings.embedding_dimensions
        )

        try:
            self.model = SentenceTransformer(
                self.model_name
            )
        except Exception as error:
            raise EmbeddingServiceError(
                f"Could not load embedding model: {error}"
            ) from error

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError(
                "Cannot generate an embedding "
                "for empty text."
            )

        result = self.embed_texts(
            [cleaned_text]
        )

        return result.embeddings[0]

    def embed_texts(
        self,
        texts: list[str],
    ) -> EmbeddingBatchResult:
        if not texts:
            return EmbeddingBatchResult(
                embeddings=[],
                model=self.model_name,
                total_tokens=0,
            )

        cleaned_texts = [
            text.strip()
            for text in texts
        ]

        if any(
            not text
            for text in cleaned_texts
        ):
            raise ValueError(
                "Embedding input cannot "
                "contain empty text."
            )

        try:
            vectors = self.model.encode(
                cleaned_texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        except Exception as error:
            raise EmbeddingServiceError(
                f"Local embedding failed: {error}"
            ) from error

        embeddings = [
            vector.astype(float).tolist()
            for vector in vectors
        ]

        for embedding in embeddings:
            if len(embedding) != self.dimensions:
                raise EmbeddingServiceError(
                    "Unexpected embedding dimension. "
                    f"Expected {self.dimensions}, "
                    f"received {len(embedding)}."
                )

        return EmbeddingBatchResult(
            embeddings=embeddings,
            model=self.model_name,
            total_tokens=0,
        )
