import re
import unicodedata


POLISH_CHARACTERS = set(
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
)

POLISH_TERMS = {
    "ile",
    "wynosi",
    "czesne",
    "studia",
    "kierunek",
    "specjalnosc",
    "specjalność",
    "rekrutacja",
    "dokumenty",
    "oplata",
    "opłata",
    "warszawa",
    "wroclaw",
    "wrocław",
    "jak",
    "gdzie",
    "kiedy",
    "czy",
    "potrzebuje",
    "potrzebuję",
}

ENGLISH_TERMS = {
    "what",
    "how",
    "where",
    "when",
    "which",
    "tuition",
    "admission",
    "application",
    "documents",
    "programme",
    "program",
    "study",
    "studies",
    "cost",
    "fee",
    "fees",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        value.lower(),
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


def detect_language(text: str) -> str:
    """
    Detect Polish or English using lightweight lexical rules.

    This is sufficient for the ATA MVP and avoids an additional
    language-detection dependency.
    """
    if any(
        character in POLISH_CHARACTERS
        for character in text
    ):
        return "pl"

    normalized = normalize_text(text)

    words = set(
        re.findall(
            r"[a-zA-Z]+",
            normalized,
        )
    )

    polish_score = len(
        words & {
            normalize_text(term)
            for term in POLISH_TERMS
        }
    )

    english_score = len(
        words & ENGLISH_TERMS
    )

    if polish_score > english_score:
        return "pl"

    if english_score > polish_score:
        return "en"

    # ATA users will commonly ask in Polish.
    return "pl"
