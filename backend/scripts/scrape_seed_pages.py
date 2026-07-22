import sys

from app.db.session import SessionLocal
from app.services.document_ingestion import save_scraped_page
from app.services.seed_urls import SEED_URLS
from app.services.web_scraper import (
    WebScraper,
    WebScraperError,
)


def run() -> int:
    scraper = WebScraper()

    created = 0
    updated = 0
    unchanged = 0
    failed = 0

    print(f"Starting seed crawl for {len(SEED_URLS)} pages.")
    print("-" * 70)

    with SessionLocal() as db:
        for url in SEED_URLS:
            print(f"Scraping: {url}")

            try:
                page = scraper.scrape(url)

                result = save_scraped_page(
                    db=db,
                    page=page,
                )

                print(f"Title: {page.title}")
                print(f"Language: {page.language}")
                print(
                    f"Markdown length: "
                    f"{len(page.markdown)} characters"
                )
                print(f"Database status: {result.status}")

                if result.status == "created":
                    created += 1
                elif result.status == "updated":
                    updated += 1
                else:
                    unchanged += 1

            except Exception as error:
                db.rollback()
                failed += 1
                print(
                    f"FAILED: "
                    f"{type(error).__name__}: {error}"
                )

            print("-" * 70)

    print("Seed crawl completed.")
    print(f"Created: {created}")
    print(f"Updated: {updated}")
    print(f"Unchanged: {unchanged}")
    print(f"Failed: {failed}")

    return 1 if failed == len(SEED_URLS) else 0


if __name__ == "__main__":
    sys.exit(run())
