from dataclasses import dataclass
import re

import tiktoken


@dataclass(slots=True)
class MarkdownChunk:
    section_title: str | None
    content: str
    chunk_index: int
    token_count: int


class MarkdownChunker:
    def __init__(
        self,
        max_tokens: int = 700,
        overlap_tokens: int = 80,
        encoding_name: str = "cl100k_base",
    ) -> None:
        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

        if overlap_tokens < 0:
            raise ValueError(
                "overlap_tokens cannot be negative."
            )

        if overlap_tokens >= max_tokens:
            raise ValueError(
                "overlap_tokens must be smaller than max_tokens."
            )

        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding(
            encoding_name
        )

    def chunk_document(
        self,
        markdown: str,
    ) -> list[MarkdownChunk]:
        """
        Split a Markdown document by headings, then split any
        oversized sections into overlapping token windows.
        """
        cleaned_markdown = markdown.strip()

        if not cleaned_markdown:
            return []

        sections = self._split_by_headings(
            cleaned_markdown
        )

        chunks: list[MarkdownChunk] = []

        for section_title, section_content in sections:
            section_chunks = self._split_section(
                content=section_content,
            )

            for content in section_chunks:
                chunks.append(
                    MarkdownChunk(
                        section_title=section_title,
                        content=content,
                        chunk_index=len(chunks),
                        token_count=self.count_tokens(
                            content
                        ),
                    )
                )

        return chunks

    def count_tokens(
        self,
        text: str,
    ) -> int:
        """Return the number of tokens in the supplied text."""
        return len(
            self.encoding.encode(text)
        )

    def _split_by_headings(
        self,
        markdown: str,
    ) -> list[tuple[str | None, str]]:
        """
        Split Markdown whenever a level 1–6 heading appears.

        The heading remains inside the corresponding section content.
        """
        lines = markdown.splitlines()

        sections: list[
            tuple[str | None, str]
        ] = []

        current_title: str | None = None
        current_lines: list[str] = []

        heading_pattern = re.compile(
            r"^(#{1,6})\s+(.+?)\s*$"
        )

        for line in lines:
            stripped_line = line.strip()

            heading_match = heading_pattern.match(
                stripped_line
            )

            if heading_match:
                if current_lines:
                    content = "\n".join(
                        current_lines
                    ).strip()

                    if content:
                        sections.append(
                            (
                                current_title,
                                content,
                            )
                        )

                heading_marks = heading_match.group(1)
                heading_text = (
                    heading_match.group(2).strip()
                )

                current_title = heading_text

                current_lines = [
                    f"{heading_marks} {heading_text}"
                ]

            else:
                current_lines.append(line)

        if current_lines:
            content = "\n".join(
                current_lines
            ).strip()

            if content:
                sections.append(
                    (
                        current_title,
                        content,
                    )
                )

        return sections

    def _split_section(
        self,
        content: str,
    ) -> list[str]:
        """
        Return the section as one chunk when it fits.

        Oversized sections are divided into overlapping token windows.
        Every returned chunk is guaranteed to contain no more than
        max_tokens tokens.
        """
        tokens = self.encoding.encode(content)

        if len(tokens) <= self.max_tokens:
            return [content]

        step_size = (
            self.max_tokens
            - self.overlap_tokens
        )

        chunks: list[str] = []
        start = 0

        while start < len(tokens):
            end = min(
                start + self.max_tokens,
                len(tokens),
            )

            token_slice = tokens[start:end]

            chunk_text = self.encoding.decode(
                token_slice
            ).strip()

            if chunk_text:
                chunks.append(chunk_text)

            if end >= len(tokens):
                break

            start += step_size

        return chunks
