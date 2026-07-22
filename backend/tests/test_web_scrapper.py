import pytest

from app.services.web_scraper import WebScraper


def test_validate_allowed_url() -> None:
    WebScraper._validate_url(
        "https://akademiata.pl/zasady-rekrutacji/"
    )


def test_validate_rejects_external_domain() -> None:
    with pytest.raises(
        ValueError,
        match="Domain is not allowed",
    ):
        WebScraper._validate_url(
            "https://example.com/page"
        )


def test_parse_html() -> None:
    scraper = WebScraper(min_content_length=20)

    html = """
    <!doctype html>
    <html lang="en">
        <head>
            <title>Computer Science</title>
        </head>
        <body>
            <nav>Navigation should be removed</nav>

            <main>
                <h1>Computer Science</h1>
                <h2>Tuition</h2>
                <p>
                    The example tuition information is
                    available in this section.
                </p>
            </main>

            <footer>Footer should be removed</footer>
        </body>
    </html>
    """

    page = scraper._parse_html(
        url="https://akademiata.pl/test",
        html=html,
    )

    assert page.title == "Computer Science"
    assert page.language == "en"
    assert "# Computer Science" in page.markdown
    assert "Tuition" in page.markdown
    assert "Navigation should be removed" not in page.markdown
    assert "Footer should be removed" not in page.markdown
    assert len(page.content_hash) == 64
