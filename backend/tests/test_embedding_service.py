from unittest.mock import MagicMock

import numpy as np
import pytest

from app.services.embedding_service import (
    EmbeddingService,
)


def test_embed_text_rejects_empty_text() -> None:
    service = EmbeddingService.__new__(
        EmbeddingService
    )

    service.model_name = "test-model"
    service.dimensions = 3
    service.model = MagicMock()

    with pytest.raises(
        ValueError,
        match="empty text",
    ):
        service.embed_text("   ")


def test_embed_texts_returns_embeddings() -> None:
    service = EmbeddingService.__new__(
        EmbeddingService
    )

    service.model_name = "test-model"
    service.dimensions = 3
    service.model = MagicMock()

    service.model.encode.return_value = (
        np.array(
            [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
            ],
            dtype=float,
        )
    )

    result = service.embed_texts(
        [
            "First text",
            "Second text",
        ]
    )

    assert result.embeddings == [
        pytest.approx([0.1, 0.2, 0.3]),
        pytest.approx([0.4, 0.5, 0.6]),
    ]

    assert result.total_tokens == 0
    assert result.model == "test-model"

    service.model.encode.assert_called_once()
