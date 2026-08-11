import json
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Response, sync_playwright


TARGET_URL = (
    "https://akademiata.pl/"
    "kalkulator-czesnego/"
)

OUTPUT_DIRECTORY = Path(
    "data/tuition_network"
)

OUTPUT_FILE = (
    OUTPUT_DIRECTORY
    / "tuition_payload.json"
)

PAGE_TIMEOUT_MS = 90_000
PAYLOAD_WAIT_SECONDS = 30


def extract_tuition_payload(
    response: Response,
) -> dict[str, Any] | None:
    """
    Return the JSON response if it contains
    the ATA tuition calculator RAW structure.
    """

    content_type = (
        response.headers.get(
            "content-type",
            "",
        )
        .lower()
    )

    resource_type = (
        response.request.resource_type
    )

    if (
        resource_type not in {"xhr", "fetch"}
        and "json" not in content_type
    ):
        return None

    try:
        body = response.json()
    except Exception:
        return None

    if not isinstance(body, dict):
        return None

    raw = body.get("RAW")

    if not isinstance(raw, dict):
        return None

    return body


def run() -> int:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    captured_payload: dict[
        str,
        Any,
    ] | None = None

    captured_url: str | None = None

    print(
        "Fetching fresh ATA tuition data..."
    )

    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(
                headless=True,
            )
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            },
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; "
                "Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0 "
                "Safari/537.36"
            ),
        )

        def handle_response(
            response: Response,
        ) -> None:
            nonlocal captured_payload
            nonlocal captured_url

            if captured_payload is not None:
                return

            payload = extract_tuition_payload(
                response
            )

            if payload is None:
                return

            captured_payload = payload
            captured_url = response.url

            print(
                "Tuition payload detected."
            )

            print(
                f"Source: {response.url}"
            )

        page.on(
            "response",
            handle_response,
        )

        try:
            page.goto(
                TARGET_URL,
                wait_until="domcontentloaded",
                timeout=PAGE_TIMEOUT_MS,
            )

            deadline = (
                time.monotonic()
                + PAYLOAD_WAIT_SECONDS
            )

            while (
                captured_payload is None
                and time.monotonic()
                < deadline
            ):
                page.wait_for_timeout(
                    500
                )

        finally:
            browser.close()

    if captured_payload is None:
        print(
            "ERROR: No tuition payload "
            "containing RAW was found."
        )

        return 1

    output = {
        "source_url": captured_url,
        "calculator_url": TARGET_URL,
        "payload": captured_payload,
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    raw = captured_payload.get(
        "RAW",
        {},
    )

    print()
    print(
        "Fresh tuition data saved."
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE.resolve()}"
    )

    print(
        f"Languages found: "
        f"{len(raw)}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        run()
    )
