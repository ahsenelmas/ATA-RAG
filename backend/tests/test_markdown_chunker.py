import pytest

from app.services.markdown_chunker import (
    MarkdownChunker,
)


def test_empty_markdown_returns_no_chunks() -> None:
    chunker = MarkdownChunker()

    assert chunker.chunk_document("") == []


def test_markdown_is_split_by_headings() -> None:
    chunker = MarkdownChunker(
        max_tokens=100,
        overlap_tokens=10,
    )

    markdown = """
# Computer Engineering

General information about the programme.

## Tuition Fees

The tuition fee information is provided here.

## Admission Requirements

Applicants must submit the required documents.
"""

    chunks = chunker.chunk_document(
        markdown
    )

    assert len(chunks) == 3

    assert (
        chunks[0].section_title
        == "Computer Engineering"
    )

    assert (
        chunks[1].section_title
        == "Tuition Fees"
    )

    assert (
        chunks[2].section_title
        == "Admission Requirements"
    )

    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        MarkdownChunker(
            max_tokens=100,
            overlap_tokens=100,
        )

def test_large_section_is_split() -> None:
    chunker = MarkdownChunker(
        max_tokens=50,
        overlap_tokens=10,
    )

    repeated_text = " ".join(
        ["programme information"] * 150
    )

    markdown = (
        "# Computer Engineering\n\n"
        f"{repeated_text}"
    )

    chunks = chunker.chunk_document(markdown)

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk.token_count <= 50
        assert chunk.content
