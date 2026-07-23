import re
import unicodedata


OUT_OF_SCOPE_TERMS = {
    "pogoda",
    "weather",
    "temperatura",
    "temperature",
    "bitcoin",
    "cryptocurrency",
    "stock price",
    "mistrzostwa swiata",
    "world cup",
    "pilka nozna",
    "football",
    "api key",
    "klucz api",
    "system prompt",
}


ATA_SCOPE_TERMS = {
    "ata",
    "akademia",
    "uczelnia",
    "university",
    "studia",
    "studies",
    "study",
    "kierunek",
    "programme",
    "program",
    "rekrutacja",
    "admission",
    "apply",
    "application",
    "czesne",
    "tuition",
    "fee",
    "informatyka",
    "computer engineering",
    "computer science",
    "architektura",
    "architecture",
    "zarzadzanie",
    "management",
    "budownictwo",
    "civil engineering",
    "dokumenty",
    "documents",
    "specjalnosc",
    "specialisation",
    "specialization",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        value.casefold(),
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return re.sub(
        r"\s+",
        " ",
        without_accents,
    ).strip()


def is_clearly_out_of_scope(
    question: str,
) -> bool:
    normalized_question = normalize_text(
        question
    )

    has_out_of_scope_term = any(
        normalize_text(term)
        in normalized_question
        for term in OUT_OF_SCOPE_TERMS
    )

    has_ata_scope_term = any(
        normalize_text(term)
        in normalized_question
        for term in ATA_SCOPE_TERMS
    )

    return (
        has_out_of_scope_term
        and not has_ata_scope_term
    )
