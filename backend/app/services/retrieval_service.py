from dataclasses import dataclass
import re
import unicodedata

from langsmith import traceable
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import (
    EmbeddingService,
)


def normalize_text(
    value: str | None,
) -> str:
    """
    Normalize text for lexical comparison.

    The function:
    - converts text to lowercase,
    - removes Polish and other accents,
    - normalizes whitespace.
    """
    if not value:
        return ""

    normalized = unicodedata.normalize(
        "NFKD",
        value.lower(),
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )

    return re.sub(
        r"\s+",
        " ",
        without_accents,
    ).strip()


def contains_term(
    text: str,
    term: str,
) -> bool:
    """Check whether a normalized term is present."""
    return (
        normalize_text(term)
        in normalize_text(text)
    )


def calculate_lexical_bonus(
    query: str,
    title: str,
    section: str,
    content: str,
) -> float:
    """
    Calculate an additional ranking score using exact lexical signals.

    Vector similarity remains the primary ranking signal.
    """
    normalized_query = normalize_text(
        query
    )
    normalized_title = normalize_text(
        title
    )
    normalized_section = normalize_text(
        section
    )
    normalized_content = normalize_text(
        content
    )

    bonus = 0.0

    tuition_terms = {
        "czesne",
        "tuition",
        "oplata",
        "oplaty",
        "fee",
        "fees",
        "koszt",
        "cost",
        "price",
    }

    query_is_about_tuition = any(
        term in normalized_query
        for term in tuition_terms
    )

    document_is_about_tuition = (
        "czesne" in normalized_title
        or "tuition" in normalized_title
        or "czesne" in normalized_section
        or "tuition" in normalized_section
    )

    if query_is_about_tuition:
        if document_is_about_tuition:
            bonus += 0.15
        else:
            bonus -= 0.05

    programme_aliases = {
        "informatyka": {
            "informatyka",
            "computer engineering",
            "computer science",
        },
        "zarzadzanie": {
            "zarzadzanie",
            "management",
        },
        "budownictwo": {
            "budownictwo",
            "civil engineering",
        },
        "architektura": {
            "architektura",
            "architecture",
        },
        "mechanika i budowa maszyn": {
            "mechanika i budowa maszyn",
            "mechanical engineering",
        },
        "ochrona srodowiska": {
            "ochrona srodowiska",
            "environmental protection",
            "environmental engineering",
        },
    }

    for (
        canonical_programme,
        aliases,
    ) in programme_aliases.items():
        query_matches_programme = any(
            normalize_text(alias)
            in normalized_query
            for alias in aliases
        )

        if not query_matches_programme:
            continue

        section_matches_programme = any(
            normalize_text(alias)
            in normalized_section
            for alias in aliases
        )

        content_matches_programme = any(
            normalize_text(alias)
            in normalized_content
            for alias in aliases
        )

        exact_base_sections = {
            (
                "czesne: "
                f"{canonical_programme}"
            ),
            (
                "tuition: "
                f"{canonical_programme}"
            ),
        }

        if (
            normalized_section
            in exact_base_sections
        ):
            bonus += 0.22

        elif section_matches_programme:
            bonus += 0.10

        if content_matches_programme:
            bonus += 0.04

    city_aliases = {
        "warszawa": {
            "warszawa",
            "warsaw",
        },
        "wroclaw": {
            "wroclaw",
            "wrocław",
        },
    }

    for (
        canonical_city,
        aliases,
    ) in city_aliases.items():
        query_matches_city = any(
            normalize_text(alias)
            in normalized_query
            for alias in aliases
        )

        if not query_matches_city:
            continue

        if (
            canonical_city
            in normalized_content
        ):
            bonus += 0.12
        else:
            bonus -= 0.20

    specialisation_aliases = {
        "sztuczna inteligencja": {
            "sztuczna inteligencja",
            "artificial intelligence",
            "ai",
        },
        "cyberbezpieczenstwo": {
            "cyberbezpieczenstwo",
            "cybersecurity",
        },
        "programowanie aplikacji": {
            "programowanie aplikacji",
            "applications programming",
            "application programming",
        },
        "animacja 3d": {
            "animacja 3d",
            "3d animation",
        },
        "inzynieria oprogramowania": {
            "inzynieria oprogramowania",
            "software engineering",
        },
        "programowanie gier": {
            "programowanie gier",
            "game programming",
        },
    }

    requested_specialisations: set[
        str
    ] = set()

    for (
        canonical_specialisation,
        aliases,
    ) in specialisation_aliases.items():
        query_contains_specialisation = any(
            normalize_text(alias)
            in normalized_query
            for alias in aliases
        )

        if query_contains_specialisation:
            requested_specialisations.add(
                canonical_specialisation
            )

    document_specialisations: set[
        str
    ] = set()

    for (
        canonical_specialisation,
        aliases,
    ) in specialisation_aliases.items():
        document_contains_specialisation = (
            any(
                (
                    normalize_text(alias)
                    in normalized_section
                )
                or (
                    normalize_text(alias)
                    in normalized_content
                )
                for alias in aliases
            )
        )

        if document_contains_specialisation:
            document_specialisations.add(
                canonical_specialisation
            )

    if requested_specialisations:
        if (
            requested_specialisations
            & document_specialisations
        ):
            bonus += 0.20

        elif document_specialisations:
            bonus -= 0.10

    elif document_specialisations:
        bonus -= 0.08

    base_programme_query = (
        "informatyka" in normalized_query
        or (
            "computer engineering"
            in normalized_query
        )
        or (
            "computer science"
            in normalized_query
        )
    )

    base_informatics_section = (
        normalized_section
        in {
            "czesne: informatyka",
            (
                "tuition: "
                "computer engineering"
            ),
            (
                "tuition: "
                "computer science"
            ),
        }
    )

    if (
        base_programme_query
        and not requested_specialisations
        and base_informatics_section
    ):
        bonus += 0.12

    return bonus


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_title: str
    url: str
    language: str | None
    section_title: str | None
    content: str
    chunk_index: int
    token_count: int | None
    distance: float
    similarity: float
    lexical_bonus: float
    final_score: float


@traceable(
    name="retrieve_ata_chunks",
    run_type="retriever",
    tags=[
        "ata-rag",
        "pgvector",
        "lexical-reranking",
    ],
)
def retrieve_chunks(
    db: Session,
    question: str,
    embedding_service: EmbeddingService,
    limit: int = 5,
    language: str | None = None,
    max_chunks_per_document: int = 2,
) -> list[RetrievedChunk]:
    """
    Retrieve relevant chunks using vector similarity and lexical reranking.

    Retrieval process:
    1. Generate an embedding for the question.
    2. Retrieve a larger candidate pool using pgvector cosine distance.
    3. Calculate lexical bonuses.
    4. Sort candidates using the combined score.
    5. Apply per-document diversity limits.
    """
    cleaned_question = (
        question.strip()
    )

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

    if limit < 1 or limit > 50:
        raise ValueError(
            "limit must be between 1 and 50."
        )

    if max_chunks_per_document < 1:
        raise ValueError(
            "max_chunks_per_document must "
            "be greater than zero."
        )

    normalized_language = (
        language.strip().lower()
        if language
        else None
    )

    query_embedding = (
        embedding_service.embed_text(
            cleaned_question
        )
    )

    distance_expression = (
        Chunk.embedding.cosine_distance(
            query_embedding
        )
    )

    statement = (
        select(
            Chunk.id.label(
                "chunk_id"
            ),
            Chunk.document_id.label(
                "document_id"
            ),
            Document.title.label(
                "document_title"
            ),
            Document.url.label(
                "url"
            ),
            Document.language.label(
                "language"
            ),
            Chunk.section_title.label(
                "section_title"
            ),
            Chunk.content.label(
                "content"
            ),
            Chunk.chunk_index.label(
                "chunk_index"
            ),
            Chunk.token_count.label(
                "token_count"
            ),
            distance_expression.label(
                "distance"
            ),
        )
        .join(
            Document,
            (
                Document.id
                == Chunk.document_id
            ),
        )
        .where(
            Chunk.embedding.is_not(None)
        )
    )

    if normalized_language is not None:
        statement = statement.where(
            Document.language
            == normalized_language
        )

    candidate_multiplier = 6

    candidate_limit = min(
        max(
            limit
            * candidate_multiplier,
            20,
        ),
        300,
    )

    statement = (
        statement
        .order_by(
            distance_expression.asc()
        )
        .limit(
            candidate_limit
        )
    )

    rows = db.execute(
        statement
    ).all()

    candidates: list[
        RetrievedChunk
    ] = []

    for row in rows:
        distance = float(
            row.distance
        )

        similarity = max(
            -1.0,
            min(
                1.0,
                1.0 - distance,
            ),
        )

        document_title = (
            row.document_title
            or ""
        )

        section_title = (
            row.section_title
            or ""
        )

        content = (
            row.content
            or ""
        )

        lexical_bonus = (
            calculate_lexical_bonus(
                query=cleaned_question,
                title=document_title,
                section=section_title,
                content=content,
            )
        )

        final_score = (
            similarity
            + lexical_bonus
        )

        candidates.append(
            RetrievedChunk(
                chunk_id=str(
                    row.chunk_id
                ),
                document_id=str(
                    row.document_id
                ),
                document_title=(
                    document_title
                ),
                url=row.url,
                language=row.language,
                section_title=(
                    row.section_title
                ),
                content=content,
                chunk_index=(
                    row.chunk_index
                ),
                token_count=(
                    row.token_count
                ),
                distance=distance,
                similarity=similarity,
                lexical_bonus=(
                    lexical_bonus
                ),
                final_score=(
                    final_score
                ),
            )
        )

    candidates.sort(
        key=lambda item: (
            item.final_score,
            item.similarity,
        ),
        reverse=True,
    )

    results: list[
        RetrievedChunk
    ] = []

    document_counts: dict[
        str,
        int,
    ] = {}

    for candidate in candidates:
        current_count = (
            document_counts.get(
                candidate.document_id,
                0,
            )
        )

        if (
            current_count
            >= max_chunks_per_document
        ):
            continue

        results.append(
            candidate
        )

        document_counts[
            candidate.document_id
        ] = current_count + 1

        if len(results) >= limit:
            break

    return results
