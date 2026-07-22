from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as to_markdown


@dataclass(slots=True)
class ScrapedPage:
    url: str
    title: str
    language: str | None
    markdown: str
    content_hash: str


class WebScraperError(Exception):
    """Raised when a web page cannot be downloaded or processed."""


class WebScraper:
    def __init__(
        self,
        timeout_seconds: float = 30.0,
        user_agent: str = "ATA-RAG-Bot/0.1",
        min_content_length: int = 100,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.min_content_length = min_content_length
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pl,en;q=0.8",
        }

    def scrape(self, url: str) -> ScrapedPage:
        self._validate_url(url)

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                headers=self.headers,
            ) as client:
                response = client.get(url)
                response.raise_for_status()

        except httpx.HTTPError as error:
            raise WebScraperError(
                f"Could not download {url}: {error}"
            ) from error

        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type.lower():
            raise WebScraperError(
                f"Unsupported content type for {url}: {content_type}"
            )

        return self._parse_html(
            url=str(response.url),
            html=response.text,
        )

    def _parse_html(self, url: str, html: str) -> ScrapedPage:
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup)
        language = self._extract_language(soup)

        self._remove_unwanted_elements(soup)

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"}) # type: ignore
            or soup.body
        )

        if main_content is None:
            raise WebScraperError(
                f"No readable content was found on {url}"
            )

        markdown = to_markdown(
            str(main_content),
            heading_style="ATX",
            bullets="-",
        )

        markdown = self._clean_markdown(markdown)

        if len(markdown) < self.min_content_length:
            raise WebScraperError(
                f"Too little readable content was extracted from {url}. "
                f"Extracted {len(markdown)} characters; "
                f"minimum is {self.min_content_length}."
            )

        content_hash = sha256(
            markdown.encode("utf-8")
        ).hexdigest()

        return ScrapedPage(
            url=url,
            title=title,
            language=language,
            markdown=markdown,
            content_hash=content_hash,
        )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        heading = soup.find("h1")

        if heading:
            heading_text = heading.get_text(
                " ",
                strip=True,
            )

            if heading_text:
                return heading_text

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        return "Untitled page"

    @staticmethod
    def _extract_language(
        soup: BeautifulSoup,
    ) -> str | None:
        html_element = soup.find("html")

        if not html_element:
            return None

        language = html_element.get("lang")

        if not isinstance(language, str):
            return None

        language = language.strip().lower()

        if not language:
            return None

        return language.split("-")[0]

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
            "form",
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
    def _clean_markdown(markdown: str) -> str:
        lines = []
        previous_blank = False

        for raw_line in markdown.splitlines():
            line = raw_line.strip()

            if not line:
                if not previous_blank:
                    lines.append("")

                previous_blank = True
                continue

            lines.append(line)
            previous_blank = False

        cleaned = "\n".join(lines).strip()

        return cleaned

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError(
                "The scraper accepts only HTTP or HTTPS URLs."
            )

        allowed_domains = {
            "akademiata.pl",
            "www.akademiata.pl",
            "uczelnia.akademiata.pl",
            "akademiata.edu.pl",
            "www.akademiata.edu.pl",
        }

        if parsed_url.netloc.lower() not in allowed_domains:
            raise ValueError(
                f"Domain is not allowed: {parsed_url.netloc}"
            )
