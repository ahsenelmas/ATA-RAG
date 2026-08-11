import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.crawl_error import CrawlError
from app.models.crawl_run import CrawlRun


@dataclass(slots=True)
class PipelineStep:
    name: str
    module: str
    arguments: list[str]


PIPELINE_STEPS = [
    PipelineStep(
        name="Static ATA page scraping",
        module="scripts.scrape_seed_pages",
        arguments=[],
    ),
    PipelineStep(
        name="Fetch live tuition data",
        module="scripts.fetch_tuition_data",
        arguments=[],
    ),
    PipelineStep(
        name="Tuition calculator import",
        module="scripts.import_tuition_data",
        arguments=[],
    ),
    PipelineStep(
        name="Document chunking",
        module="scripts.chunk_documents",
        arguments=[],
    ),
    PipelineStep(
        name="Chunk embedding",
        module="scripts.embed_chunks",
        arguments=[],
    ),
]

def create_crawl_run() -> str:
    db = SessionLocal()

    try:
        crawl_run = CrawlRun(
            status="running",
        )

        db.add(crawl_run)
        db.commit()
        db.refresh(crawl_run)

        return str(crawl_run.id)

    finally:
        db.close()


def update_crawl_run(
    crawl_run_id: str,
    *,
    status: str,
    pages_discovered: int = 0,
    pages_processed: int = 0,
    pages_failed: int = 0,
    pages_updated: int = 0,
    pages_unchanged: int = 0,
    chunks_created: int = 0,
    error_message: str | None = None,
) -> None:
    db = SessionLocal()

    try:
        crawl_run = db.get(
            CrawlRun,
            uuid.UUID(crawl_run_id),
        )

        if crawl_run is None:
            raise RuntimeError(
                "CrawlRun not found: "
                f"{crawl_run_id}"
            )

        crawl_run.status = status
        crawl_run.finished_at = (
            datetime.now(timezone.utc)
            if status in {
                "completed",
                "failed",
            }
            else None
        )

        crawl_run.pages_discovered = (
            pages_discovered
        )
        crawl_run.pages_processed = (
            pages_processed
        )
        crawl_run.pages_failed = (
            pages_failed
        )
        crawl_run.pages_updated = (
            pages_updated
        )
        crawl_run.pages_unchanged = (
            pages_unchanged
        )
        crawl_run.chunks_created = (
            chunks_created
        )
        crawl_run.error_message = (
            error_message
        )

        db.commit()

    finally:
        db.close()


def record_crawl_error(
    crawl_run_id: str,
    *,
    error_type: str,
    error_message: str,
    url: str = "knowledge-base-refresh",
) -> None:
    db = SessionLocal()

    try:
        crawl_error = CrawlError(
            crawl_run_id=crawl_run_id,
            url=url,
            error_type=error_type,
            error_message=error_message,
        )

        db.add(crawl_error)
        db.commit()

    finally:
        db.close()


def run_step(
    step: PipelineStep,
) -> tuple[bool, str]:
    command = [
        sys.executable,
        "-m",
        step.module,
        *step.arguments,
    ]

    print()
    print("=" * 70)
    print(step.name)
    print("=" * 70)

    print(
        "Command:",
        " ".join(command),
    )

    started_at = time.perf_counter()

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    duration = (
        time.perf_counter()
        - started_at
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(
            result.stderr,
            file=sys.stderr,
        )

    combined_output = (
        (result.stdout or "")
        + "\n"
        + (result.stderr or "")
    )

    if result.returncode != 0:
        print()
        print(
            f"FAILED: {step.name}"
        )
        print(
            f"Exit code: "
            f"{result.returncode}"
        )
        print(
            f"Duration: "
            f"{duration:.2f}s"
        )

        return (
            False,
            combined_output,
        )

    print()
    print(
        f"COMPLETED: {step.name}"
    )
    print(
        f"Duration: {duration:.2f}s"
    )

    return (
        True,
        combined_output,
    )


def parse_integer_after_label(
    output: str,
    label: str,
) -> int:
    for line in output.splitlines():
        stripped = line.strip()

        if not stripped.startswith(label):
            continue

        value = stripped[
            len(label):
        ].strip()

        try:
            return int(value)
        except ValueError:
            return 0

    return 0


def run() -> int:
    print()
    print("=" * 70)
    print(
        "ATA RAG KNOWLEDGE BASE REFRESH"
    )
    print("=" * 70)

    pipeline_started_at = (
        time.perf_counter()
    )

    crawl_run_id = (
        create_crawl_run()
    )

    print(
        f"Crawl run ID: "
        f"{crawl_run_id}"
    )

    completed_steps = 0

    pages_discovered = 0
    pages_processed = 0
    pages_failed = 0
    pages_updated = 0
    pages_unchanged = 0
    chunks_created = 0

    try:
        for step in PIPELINE_STEPS:
            (
                success,
                output,
            ) = run_step(step)

            if (
                step.module
                == "scripts.scrape_seed_pages"
            ):
                created = (
                    parse_integer_after_label(
                        output,
                        "Created:",
                    )
                )

                updated = (
                    parse_integer_after_label(
                        output,
                        "Updated:",
                    )
                )

                unchanged = (
                    parse_integer_after_label(
                        output,
                        "Unchanged:",
                    )
                )

                failed = (
                    parse_integer_after_label(
                        output,
                        "Failed:",
                    )
                )

                discovered = (
                    created
                    + updated
                    + unchanged
                    + failed
                )

                pages_discovered += (
                    discovered
                )

                pages_processed += (
                    created
                    + updated
                    + unchanged
                )

                pages_updated += (
                    created
                    + updated
                )

                pages_unchanged += (
                    unchanged
                )

                pages_failed += (
                    failed
                )

            elif (
                step.module
                == "scripts.import_tuition_data"
            ):
                created = (
                    parse_integer_after_label(
                        output,
                        "Created:",
                    )
                )

                updated = (
                    parse_integer_after_label(
                        output,
                        "Updated:",
                    )
                )

                unchanged = (
                    parse_integer_after_label(
                        output,
                        "Unchanged:",
                    )
                )

                processed = (
                    created
                    + updated
                    + unchanged
                )

                pages_discovered += (
                    processed
                )

                pages_processed += (
                    processed
                )

                pages_updated += (
                    created
                    + updated
                )

                pages_unchanged += (
                    unchanged
                )

            elif (
                step.module
                == "scripts.chunk_documents"
            ):
                chunks_created += (
                    parse_integer_after_label(
                        output,
                        "Total chunks created:",
                    )
                )

            if not success:
                error_message = (
                    f"Pipeline failed during "
                    f"{step.name}."
                )

                record_crawl_error(
                    crawl_run_id,
                    error_type=(
                        "PipelineStepError"
                    ),
                    error_message=(
                        output[-4000:]
                        if output
                        else error_message
                    ),
                )

                update_crawl_run(
                    crawl_run_id,
                    status="failed",
                    pages_discovered=(
                        pages_discovered
                    ),
                    pages_processed=(
                        pages_processed
                    ),
                    pages_failed=(
                        pages_failed + 1
                    ),
                    pages_updated=(
                        pages_updated
                    ),
                    pages_unchanged=(
                        pages_unchanged
                    ),
                    chunks_created=(
                        chunks_created
                    ),
                    error_message=(
                        error_message
                    ),
                )

                print()
                print("=" * 70)
                print(
                    "KNOWLEDGE BASE "
                    "REFRESH FAILED"
                )
                print("=" * 70)

                return 1

            completed_steps += 1

        update_crawl_run(
            crawl_run_id,
            status="completed",
            pages_discovered=(
                pages_discovered
            ),
            pages_processed=(
                pages_processed
            ),
            pages_failed=(
                pages_failed
            ),
            pages_updated=(
                pages_updated
            ),
            pages_unchanged=(
                pages_unchanged
            ),
            chunks_created=(
                chunks_created
            ),
        )

    except Exception as exc:
        error_message = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        try:
            record_crawl_error(
                crawl_run_id,
                error_type=(
                    type(exc).__name__
                ),
                error_message=(
                    error_message
                ),
            )

            update_crawl_run(
                crawl_run_id,
                status="failed",
                pages_discovered=(
                    pages_discovered
                ),
                pages_processed=(
                    pages_processed
                ),
                pages_failed=(
                    pages_failed + 1
                ),
                pages_updated=(
                    pages_updated
                ),
                pages_unchanged=(
                    pages_unchanged
                ),
                chunks_created=(
                    chunks_created
                ),
                error_message=(
                    error_message
                ),
            )

        except Exception as tracking_error:
            print(
                "Could not save crawl "
                "failure information:"
            )
            print(
                tracking_error
            )

        raise

    total_duration = (
        time.perf_counter()
        - pipeline_started_at
    )

    print()
    print("=" * 70)
    print(
        "KNOWLEDGE BASE REFRESH COMPLETED"
    )
    print("=" * 70)

    print(
        f"Crawl run ID: "
        f"{crawl_run_id}"
    )

    print(
        f"Steps completed: "
        f"{completed_steps}/"
        f"{len(PIPELINE_STEPS)}"
    )

    print(
        f"Pages discovered: "
        f"{pages_discovered}"
    )

    print(
        f"Pages processed: "
        f"{pages_processed}"
    )

    print(
        f"Pages updated: "
        f"{pages_updated}"
    )

    print(
        f"Pages unchanged: "
        f"{pages_unchanged}"
    )

    print(
        f"Pages failed: "
        f"{pages_failed}"
    )

    print(
        f"Chunks created: "
        f"{chunks_created}"
    )

    print(
        f"Total duration: "
        f"{total_duration:.2f}s"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        run()
    )
