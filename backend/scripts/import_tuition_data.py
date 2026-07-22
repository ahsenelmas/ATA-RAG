import json
import sys
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document


SOURCE_FILE = Path("data/tuition_network/responses.json")

CALCULATOR_URL = (
    "https://akademiata.pl/kalkulator-czesnego/"
)


def find_tuition_payload(
    captured_responses: list[dict],
) -> dict:
    for response in captured_responses:
        body = response.get("body_json")

        if not isinstance(body, dict):
            continue

        raw = body.get("RAW")

        if isinstance(raw, dict):
            return body

    raise ValueError(
        "No tuition payload containing RAW data was found."
    )


def city_name(city_code: str) -> str:
    names = {
        "wwa": "Warszawa",
        "wro": "Wrocław",
    }

    return names.get(city_code, city_code)


def degree_name(
    degree: int,
    language: str,
) -> str:
    if language == "pl":
        return {
            1: "studia I stopnia",
            2: "studia II stopnia",
        }.get(degree, f"stopień {degree}")

    return {
        1: "Bachelor / first-cycle studies",
        2: "Master / second-cycle studies",
    }.get(degree, f"degree {degree}")


def study_mode_name(
    mode: str,
    language: str,
) -> str:
    if language == "pl":
        return {
            "s": "stacjonarne",
            "n": "niestacjonarne",
        }.get(mode, mode)

    return {
        "s": "full-time",
        "n": "part-time",
    }.get(mode, mode)


def build_polish_markdown(
    city: str,
    mode: str,
    item: dict,
    application_url: str | None,
) -> str:
    programme = item["k"]
    specialization = item.get("s")
    degree = int(item["deg"])

    title = (
        f"{programme} — {specialization}"
        if specialization
        else programme
    )

    lines = [
        f"# Czesne: {title}",
        "",
        f"- Miasto: {city_name(city)}",
        f"- Język studiów: polski",
        f"- Poziom: {degree_name(degree, 'pl')}",
        f"- Forma studiów: {study_mode_name(mode, 'pl')}",
        f"- Kierunek: {programme}",
    ]

    if specialization:
        lines.append(
            f"- Specjalność: {specialization}"
        )

    lines.extend(
        [
            f"- Rata przy wariancie 10 płatności: {item['r10']} PLN",
            f"- Rata przy wariancie 12 płatności: {item['r12']} PLN",
            f"- Opłata rekrutacyjna: {item['rekr']} PLN",
            f"- Wpisowe: {item['wps']} PLN",
        ]
    )

    programme_url = item.get("ps")

    if programme_url:
        lines.append(
            f"- Strona kierunku: {programme_url}"
        )

    if application_url:
        lines.append(
            f"- Aplikacja online: {application_url}"
        )

    lines.extend(
        [
            f"- Oficjalny kalkulator: {CALCULATOR_URL}",
            "",
            (
                "Kwoty pochodzą z oficjalnego kalkulatora "
                "czesnego ATA."
            ),
        ]
    )

    return "\n".join(lines)


def build_english_markdown(
    city: str,
    item: dict,
    application_url: str | None,
) -> str:
    programme = item["k"]
    specialization = item.get("s")
    degree = int(item["deg"])

    title = (
        f"{programme} — {specialization}"
        if specialization
        else programme
    )

    eu_prices = item.get("eu", {})
    non_eu_prices = item.get("ne", {})

    lines = [
        f"# Tuition: {title}",
        "",
        f"- City: {city_name(city)}",
        "- Study language: English",
        f"- Level: {degree_name(degree, 'en')}",
        f"- Programme: {programme}",
    ]

    if specialization:
        lines.append(
            f"- Specialisation: {specialization}"
        )

    if eu_prices:
        lines.extend(
            [
                (
                    "- EU/CIS/Ukraine annual payment: "
                    f"{eu_prices.get('r')} EUR"
                ),
                (
                    "- EU/CIS/Ukraine semester payment: "
                    f"{eu_prices.get('s')} EUR"
                ),
            ]
        )

    if non_eu_prices:
        lines.extend(
            [
                (
                    "- Other countries annual payment: "
                    f"{non_eu_prices.get('r')} EUR"
                ),
                (
                    "- Other countries semester payment: "
                    f"{non_eu_prices.get('s')} EUR"
                ),
            ]
        )

    lines.extend(
        [
            (
                "- Recruitment fee: "
                f"{item.get('rekr', 0)} EUR"
            ),
            (
                "- Enrolment fee: "
                f"{item.get('wps', 0)} EUR"
            ),
        ]
    )

    programme_url = item.get("ps")

    if programme_url:
        lines.append(
            f"- Programme page: {programme_url}"
        )

    if application_url:
        lines.append(
            f"- Online application: {application_url}"
        )

    lines.append(
        f"- Official calculator: {CALCULATOR_URL}"
    )

    return "\n".join(lines)


def save_document(
    db,
    staged_documents: dict[str, Document],
    url: str,
    title: str,
    language: str,
    markdown: str,
) -> str:
    content_hash = sha256(
        markdown.encode("utf-8")
    ).hexdigest()

    # First check documents created or updated during this import run.
    document = staged_documents.get(url)

    # Then check documents already stored in PostgreSQL.
    if document is None:
        document = db.scalar(
            select(Document).where(
                Document.url == url
            )
        )

    if document is None:
        document = Document(
            url=url,
            title=title,
            language=language,
            markdown=markdown,
            content_hash=content_hash,
        )

        db.add(document)
        staged_documents[url] = document

        return "created"

    staged_documents[url] = document

    if document.content_hash == content_hash:
        return "unchanged"

    document.title = title
    document.language = language
    document.markdown = markdown
    document.content_hash = content_hash

    return "updated"


def run() -> int:
    if not SOURCE_FILE.exists():
        print(
            f"Source file not found: {SOURCE_FILE}"
        )
        return 1

    captured = json.loads(
        SOURCE_FILE.read_text(
            encoding="utf-8"
        )
    )

    payload = find_tuition_payload(captured)

    raw = payload["RAW"]
    application_links = payload.get("SA", {})
    application_links_en = payload.get(
        "SA_EN",
        {},
    )

    created = 0
    updated = 0
    unchanged = 0
    duplicates = 0

    staged_documents: dict[str, Document] = {}
    processed_urls: set[str] = set()

    with SessionLocal() as db:
        for language, cities in raw.items():
            for city, city_data in cities.items():
                if language == "pl":
                    for mode, items in city_data.items():
                        for item in items:
                            application_url = (
                                application_links.get(
                                    item.get("ak", "")
                                )
                            )

                            markdown = build_polish_markdown(
                                city=city,
                                mode=mode,
                                item=item,
                                application_url=(
                                    application_url
                                ),
                            )

                            identifier = item.get(
                                "ak",
                                (
                                    f"{city}-{mode}-"
                                    f"{item['k']}"
                                ),
                            )

                            url = (
                                f"{CALCULATOR_URL}"
                                f"#tuition-{identifier}-{mode}"
                            )

                            if url in processed_urls:
                                duplicates += 1
                                continue

                            processed_urls.add(url)

                            status = save_document(
                                db=db,
                                staged_documents=staged_documents,
                                url=url,
                                title=(
                                    "Czesne — "
                                    f"{item['k']}"
                                ),
                                language="pl",
                                markdown=markdown,
                            )

                            if status == "created":
                                created += 1
                            elif status == "updated":
                                updated += 1
                            else:
                                unchanged += 1

                elif language == "en":
                    for item in city_data:
                        application_url = (
                            application_links_en.get(
                                item.get("ak", "")
                            )
                        )

                        markdown = build_english_markdown(
                            city=city,
                            item=item,
                            application_url=(
                                application_url
                            ),
                        )

                        identifier = item.get(
                            "ak",
                            f"{city}-{item['k']}",
                        )

                        url = (
                            f"{CALCULATOR_URL}"
                            f"#tuition-{identifier}"
                        )

                        if url in processed_urls:
                            duplicates += 1
                            continue

                        processed_urls.add(url)

                        status = save_document(
                            db=db,
                            staged_documents=staged_documents,
                            url=url,
                            title=(
                                "Tuition — "
                                f"{item['k']}"
                            ),
                            language="en",
                            markdown=markdown,
)

                        if status == "created":
                            created += 1
                        elif status == "updated":
                            updated += 1
                        else:
                            unchanged += 1

        db.commit()

        print("Tuition import completed.")
        print(f"Created: {created}")
        print(f"Updated: {updated}")
        print(f"Unchanged: {unchanged}")
        print(f"Duplicate source records skipped: {duplicates}")

    return 0


if __name__ == "__main__":
    sys.exit(run())
