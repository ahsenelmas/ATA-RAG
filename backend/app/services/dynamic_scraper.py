from dataclasses import dataclass
from hashlib import sha256

from bs4 import BeautifulSoup
from markdownify import markdownify as to_markdown
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import sync_playwright


@dataclass(slots=True)
class DynamicScrapedPage:
    url: str
    title: str
    language: str | None
    markdown: str
    content_hash: str


class DynamicScraperError(Exception):
    """Raised when a dynamic page cannot be processed."""


class DynamicWebScraper:
    def __init__(
        self,
        timeout_ms: int = 45_000,
    ) -> None:
        self.timeout_ms = timeout_ms

    def scrape(
        self,
        url: str,
    ) -> DynamicScrapedPage:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True
                )

                page = browser.new_page(
                    viewport={
                        "width": 1440,
                        "height": 1200,
                    },
                    user_agent=(
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    ),
                )

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout_ms,
                )

                page.wait_for_timeout(5000)

                try:
                    page.wait_for_selector(
                        "main, article, body",
                        timeout=10_000,
                    )
                except PlaywrightTimeoutError:
                    pass

                html = page.content()
                final_url = page.url
                title = page.title()

                browser.close()

        except PlaywrightTimeoutError as error:
            raise DynamicScraperError(
                f"Dynamic page timed out: {url}"
            ) from error

        except Exception as error:
            raise DynamicScraperError(
                f"Dynamic scraping failed: {error}"
            ) from error

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        language = self._extract_language(soup)

        self._remove_unwanted_elements(soup)

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"}) # type: ignore
            or soup.body
        )

        if main_content is None:
            raise DynamicScraperError(
                "No readable content found."
            )

        markdown = to_markdown(
            str(main_content),
            heading_style="ATX",
            bullets="-",
        )

        cleaned_markdown = self._clean_markdown(
            markdown
        )

        if not cleaned_markdown:
            raise DynamicScraperError(
                "The rendered page contained no readable text."
            )

        return DynamicScrapedPage(
            url=final_url,
            title=title or "Untitled page",
            language=language,
            markdown=cleaned_markdown,
            content_hash=sha256(
                cleaned_markdown.encode("utf-8")
            ).hexdigest(),
        )

    @staticmethod
    def _extract_language(
        soup: BeautifulSoup,
    ) -> str | None:
        html_element = soup.find("html")

        if html_element is None:
            return None

        language_value = html_element.get("lang")

        if not isinstance(language_value, str):
            return None

        language_value = (
            language_value
            .strip()
            .lower()
        )

        if not language_value:
            return None

        return language_value.split("-")[0]

    @staticmethod
    def _remove_unwanted_elements(
        soup: BeautifulSoup,
    ) -> None:
        unwanted_tags = [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "nav",
            "footer",
        ]

        for tag_name in unwanted_tags:
            for element in soup.find_all(tag_name):
                element.decompose()

        unwanted_selectors = [
            ".cookie",
            ".cookie-banner",
            ".cookies",
            ".popup",
            ".modal",
            ".social-media",
            ".social-links",
            ".breadcrumbs",
            ".breadcrumb",
            ".sidebar",
            ".menu",
            "#cookie-notice",
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

    @staticmethod
    def _clean_markdown(
        markdown: str,
    ) -> str:
        cleaned_lines: list[str] = []
        previous_blank = False

        for raw_line in markdown.splitlines():
            line = raw_line.strip()

            if not line:
                if not previous_blank:
                    cleaned_lines.append("")

                previous_blank = True
                continue

            cleaned_lines.append(line)
            previous_blank = False

        return "\n".join(
            cleaned_lines
        ).strip()
