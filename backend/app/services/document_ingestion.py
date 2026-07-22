from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.web_scraper import ScrapedPage


@dataclass(slots=True)
class IngestionResult:
    document_id: str
    url: str
    status: str


def save_scraped_page(
    db: Session,
    page: ScrapedPage,
) -> IngestionResult:
    existing_document = db.scalar(
        select(Document).where(
            Document.url == page.url
        )
    )

    if existing_document is None:
        document = Document(
            url=page.url,
            title=page.title,
            language=page.language,
            markdown=page.markdown,
            content_hash=page.content_hash,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return IngestionResult(
            document_id=str(document.id),
            url=document.url,
            status="created",
        )

    if existing_document.content_hash == page.content_hash:
        return IngestionResult(
            document_id=str(existing_document.id),
            url=existing_document.url,
            status="unchanged",
        )

    existing_document.title = page.title
    existing_document.language = page.language
    existing_document.markdown = page.markdown
    existing_document.content_hash = page.content_hash

    db.commit()
    db.refresh(existing_document)

    return IngestionResult(
        document_id=str(existing_document.id),
        url=existing_document.url,
        status="updated",
    )
