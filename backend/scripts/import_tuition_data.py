import json
import sys
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document


SOURCE_FILE = Path(
    "data/tuition_network/tuition_payload.json"
)

CALCULATOR_URL = (
    "https://akademiata.pl/"
    "kalkulator-czesnego/"
)


def city_name(
    city_code: str,
) -> str:
    names = {
        "wwa": "Warszawa",
        "wro": "Wrocław",
    }

    return names.get(
        city_code,
        city_code,
    )


def degree_name(
    degree: int,
    language: str,
) -> str:
    if language == "pl":
        return {
            1: "studia I stopnia",
            2: "studia II stopnia",
        }.get(
            degree,
            f"stopień {degree}",
        )

    return {
        1: "Bachelor / first-cycle studies",
        2: "Master / second-cycle studies",
    }.get(
        degree,
        f"degree {degree}",
    )


def study_mode_name(
    mode: str,
    language: str,
) -> str:
    if language == "pl":
        return {
            "s": "stacjonarne",
            "n": "niestacjonarne",
        }.get(
            mode,
            mode,
        )

    return {
        "s": "full-time",
        "n": "part-time",
    }.get(
        mode,
        mode,
    )


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
        "- Język studiów: polski",
        (
            f"- Poziom: "
            f"{degree_name(degree, 'pl')}"
        ),
        (
            f"- Forma studiów: "
            f"{study_mode_name(mode, 'pl')}"
        ),
        f"- Kierunek: {programme}",
    ]

    if specialization:
        lines.append(
            f"- Specjalność: "
            f"{specialization}"
        )

    lines.extend(
        [
            (
                "- Rata przy wariancie "
                "10 płatności: "
                f"{item['r10']} PLN"
            ),
            (
                "- Rata przy wariancie "
                "12 płatności: "
                f"{item['r12']} PLN"
            ),
            (
                "- Opłata rekrutacyjna: "
                f"{item['rekr']} PLN"
            ),
            (
                "- Wpisowe: "
                f"{item['wps']} PLN"
            ),
        ]
    )

    programme_url = item.get(
        "ps"
    )

    if programme_url:
        lines.append(
            f"- Strona kierunku: "
            f"{programme_url}"
        )

    if application_url:
        lines.append(
            f"- Aplikacja online: "
            f"{application_url}"
        )

    lines.extend(
        [
            (
                "- Oficjalny kalkulator: "
                f"{CALCULATOR_URL}"
            ),
            "",
            (
                "Kwoty pochodzą z "
                "oficjalnego kalkulatora "
                "czesnego ATA."
            ),
        ]
    )

    return "\n".join(
        lines
    )


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

    eu_prices = item.get(
        "eu",
        {},
    )

    non_eu_prices = item.get(
        "ne",
        {},
    )

    lines = [
        f"# Tuition: {title}",
        "",
        f"- City: {city_name(city)}",
        "- Study language: English",
        (
            f"- Level: "
            f"{degree_name(degree, 'en')}"
        ),
        f"- Programme: {programme}",
    ]

    if specialization:
        lines.append(
            f"- Specialisation: "
            f"{specialization}"
        )

    if eu_prices:
        lines.extend(
            [
                (
                    "- EU/CIS/Ukraine "
                    "annual payment: "
                    f"{eu_prices.get('r')} EUR"
                ),
                (
                    "- EU/CIS/Ukraine "
                    "semester payment: "
                    f"{eu_prices.get('s')} EUR"
                ),
            ]
        )

    if non_eu_prices:
        lines.extend(
            [
                (
                    "- Other countries "
                    "annual payment: "
                    f"{non_eu_prices.get('r')} EUR"
                ),
                (
                    "- Other countries "
                    "semester payment: "
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

    programme_url = item.get(
        "ps"
    )

    if programme_url:
        lines.append(
            f"- Programme page: "
            f"{programme_url}"
        )

    if application_url:
        lines.append(
            f"- Online application: "
            f"{application_url}"
        )

    lines.append(
        (
            "- Official calculator: "
            f"{CALCULATOR_URL}"
        )
    )

    return "\n".join(
        lines
    )


def save_document(
    db,
    staged_documents: dict[
        str,
        Document,
    ],
    url: str,
    title: str,
    language: str,
    markdown: str,
) -> str:
    content_hash = sha256(
        markdown.encode(
            "utf-8"
        )
    ).hexdigest()

    document = (
        staged_documents.get(
            url
        )
    )

    if document is None:
        document = db.scalar(
            select(
                Document
            ).where(
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

        db.add(
            document
        )

        staged_documents[
            url
        ] = document

        return "created"

    staged_documents[
        url
    ] = document

    if (
        document.content_hash
        == content_hash
    ):
        return "unchanged"

    document.title = title
    document.language = language
    document.markdown = markdown
    document.content_hash = (
        content_hash
    )

    return "updated"


def run() -> int:
    if not SOURCE_FILE.exists():
        print(
            "Source file not found: "
            f"{SOURCE_FILE}"
        )

        print(
            "Run "
            "'python -m "
            "scripts.fetch_tuition_data' "
            "first."
        )

        return 1

    source_data = json.loads(
        SOURCE_FILE.read_text(
            encoding="utf-8"
        )
    )

    payload = source_data.get(
        "payload"
    )

    if not isinstance(
        payload,
        dict,
    ):
        print(
            "Invalid tuition payload file."
        )

        return 1

    raw = payload.get(
        "RAW"
    )

    if not isinstance(
        raw,
        dict,
    ):
        print(
            "Tuition payload does not "
            "contain valid RAW data."
        )

        return 1

    application_links = (
        payload.get(
            "SA",
            {},
        )
    )

    application_links_en = (
        payload.get(
            "SA_EN",
            {},
        )
    )

    created = 0
    updated = 0
    unchanged = 0
    duplicates = 0

    staged_documents: dict[
        str,
        Document,
    ] = {}

    processed_urls: set[
        str
    ] = set()

    with SessionLocal() as db:
        for (
            language,
            cities,
        ) in raw.items():
            for (
                city,
                city_data,
            ) in cities.items():
                if language == "pl":
                    for (
                        mode,
                        items,
                    ) in city_data.items():
                        for item in items:
                            application_url = (
                                application_links.get(
                                    item.get(
                                        "ak",
                                        "",
                                    )
                                )
                            )

                            markdown = (
                                build_polish_markdown(
                                    city=city,
                                    mode=mode,
                                    item=item,
                                    application_url=(
                                        application_url
                                    ),
                                )
                            )

                            identifier = (
                                item.get(
                                    "ak",
                                    (
                                        f"{city}-"
                                        f"{mode}-"
                                        f"{item['k']}"
                                    ),
                                )
                            )

                            url = (
                                f"{CALCULATOR_URL}"
                                f"#tuition-"
                                f"{identifier}-"
                                f"{mode}"
                            )

                            if (
                                url
                                in processed_urls
                            ):
                                duplicates += 1
                                continue

                            processed_urls.add(
                                url
                            )

                            status = (
                                save_document(
                                    db=db,
                                    staged_documents=(
                                        staged_documents
                                    ),
                                    url=url,
                                    title=(
                                        "Czesne — "
                                        f"{item['k']}"
                                    ),
                                    language="pl",
                                    markdown=markdown,
                                )
                            )

                            if (
                                status
                                == "created"
                            ):
                                created += 1

                            elif (
                                status
                                == "updated"
                            ):
                                updated += 1

                            else:
                                unchanged += 1

                elif language == "en":
                    for item in city_data:
                        application_url = (
                            application_links_en.get(
                                item.get(
                                    "ak",
                                    "",
                                )
                            )
                        )

                        markdown = (
                            build_english_markdown(
                                city=city,
                                item=item,
                                application_url=(
                                    application_url
                                ),
                            )
                        )

                        identifier = (
                            item.get(
                                "ak",
                                (
                                    f"{city}-"
                                    f"{item['k']}"
                                ),
                            )
                        )

                        url = (
                            f"{CALCULATOR_URL}"
                            f"#tuition-"
                            f"{identifier}"
                        )

                        if (
                            url
                            in processed_urls
                        ):
                            duplicates += 1
                            continue

                        processed_urls.add(
                            url
                        )

                        status = (
                            save_document(
                                db=db,
                                staged_documents=(
                                    staged_documents
                                ),
                                url=url,
                                title=(
                                    "Tuition — "
                                    f"{item['k']}"
                                ),
                                language="en",
                                markdown=markdown,
                            )
                        )

                        if (
                            status
                            == "created"
                        ):
                            created += 1

                        elif (
                            status
                            == "updated"
                        ):
                            updated += 1

                        else:
                            unchanged += 1

        db.commit()

    print(
        "Tuition import completed."
    )

    print(
        f"Created: {created}"
    )

    print(
        f"Updated: {updated}"
    )

    print(
        f"Unchanged: {unchanged}"
    )

    print(
        "Duplicate source records "
        f"skipped: {duplicates}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        run()
    )
