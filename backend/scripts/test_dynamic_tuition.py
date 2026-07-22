from app.services.dynamic_scraper import (
    DynamicWebScraper,
)


def run() -> None:
    scraper = DynamicWebScraper()

    page = scraper.scrape(
        "https://akademiata.pl/kalkulator-czesnego/"
    )

    print(f"Title: {page.title}")
    print(f"URL: {page.url}")
    print(f"Language: {page.language}")
    print(f"Length: {len(page.markdown)}")
    print("-" * 70)
    print(page.markdown[:5000])


if __name__ == "__main__":
    run()
