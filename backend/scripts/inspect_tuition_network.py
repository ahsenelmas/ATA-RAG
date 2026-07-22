import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Response, sync_playwright


TARGET_URL = "https://akademiata.pl/kalkulator-czesnego/"

OUTPUT_DIRECTORY = Path("data/tuition_network")


def is_interesting_response(
    response: Response,
) -> bool:
    """
    Capture fetch/XHR responses and any response that returns JSON.
    """
    resource_type = response.request.resource_type

    if resource_type in {"xhr", "fetch"}:
        return True

    content_type = response.headers.get(
        "content-type",
        "",
    ).lower()

    return (
        "application/json" in content_type
        or "text/json" in content_type
        or "+json" in content_type
    )


def serialize_json_body(
    response: Response,
) -> tuple[Any | None, str | None]:
    """
    Try to read a JSON response.

    Returns:
        A tuple containing:
        - parsed JSON data, or None
        - an error message, or None
    """
    try:
        return response.json(), None
    except Exception as error:
        return None, (
            f"{type(error).__name__}: {error}"
        )


def read_text_body(
    response: Response,
) -> tuple[str | None, str | None]:
    """
    Try to read a non-JSON response body as UTF-8 text.
    """
    try:
        raw_body = response.body()

        text = raw_body.decode(
            "utf-8",
            errors="replace",
        )

        return text, None

    except Exception as error:
        return None, (
            f"{type(error).__name__}: {error}"
        )


def run() -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    captured_responses: list[
        dict[str, Any]
    ] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            },
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
        )

        def handle_response(
            response: Response,
        ) -> None:
            if not is_interesting_response(
                response
            ):
                return

            request = response.request

            content_type = response.headers.get(
                "content-type",
                "",
            ).lower()

            item: dict[str, Any] = {
                "url": response.url,
                "status": response.status,
                "method": request.method,
                "resource_type": (
                    request.resource_type
                ),
                "content_type": content_type,
                "post_data": request.post_data,
            }

            printable_body = ""

            if (
                "json" in content_type
                or "+json" in content_type
            ):
                json_body, json_error = (
                    serialize_json_body(
                        response
                    )
                )

                if json_body is not None:
                    item["body_json"] = json_body

                    printable_body = json.dumps(
                        json_body,
                        ensure_ascii=False,
                        indent=2,
                    )

                if json_error is not None:
                    item["body_json_error"] = (
                        json_error
                    )

            if not printable_body:
                text_body, text_error = (
                    read_text_body(
                        response
                    )
                )

                if text_body is not None:
                    item["body_text"] = (
                        text_body
                    )
                    printable_body = text_body

                if text_error is not None:
                    item["body_text_error"] = (
                        text_error
                    )

            captured_responses.append(
                item
            )

            print()
            print("=" * 80)
            print(
                f"{request.method} "
                f"{response.url}"
            )
            print(
                f"Status: {response.status}"
            )
            print(
                "Resource type: "
                f"{request.resource_type}"
            )
            print(
                "Content type: "
                f"{content_type or 'unknown'}"
            )

            if request.post_data:
                print("POST data:")
                print(
                    request.post_data[:3000]
                )

            if printable_body:
                print("Body preview:")
                print(
                    printable_body[:5000]
                )

            if (
                "body_json_error" in item
                or "body_text_error" in item
            ):
                print("Body read error:")

                if "body_json_error" in item:
                    print(
                        item["body_json_error"]
                    )

                if "body_text_error" in item:
                    print(
                        item["body_text_error"]
                    )

        page.on(
            "response",
            handle_response,
        )

        try:
            page.goto(
                TARGET_URL,
                wait_until="domcontentloaded",
                timeout=90_000,
            )

            page.wait_for_timeout(
                8000
            )

            print()
            print(
                "The browser is open."
            )
            print(
                "Select city, programme, "
                "study form, country group, "
                "and payment options."
            )
            print(
                "Wait until the final fees "
                "or price placeholders update."
            )
            print(
                "Then return to this terminal "
                "and press Enter."
            )

            input()

        finally:
            output_path = (
                OUTPUT_DIRECTORY
                / "responses.json"
            )

            output_path.write_text(
                json.dumps(
                    captured_responses,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            print()
            print(
                f"Saved "
                f"{len(captured_responses)} "
                f"responses to:"
            )
            print(output_path.resolve())

            browser.close()


if __name__ == "__main__":
    run()
