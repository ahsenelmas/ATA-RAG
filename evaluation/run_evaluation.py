import argparse
import csv
import json
import statistics
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_DATASET_PATH = Path(
    "evaluation/ata_rag_evaluation.json"
)
DEFAULT_OUTPUT_DIRECTORY = Path(
    "evaluation/results"
)


@dataclass(slots=True)
class EvaluationResult:
    case_id: str
    category: str
    question: str

    request_succeeded: bool
    status_code: int | None

    expected_language: str
    actual_language: str | None
    language_passed: bool

    expected_grounded: bool
    actual_grounded: bool | None
    grounded_passed: bool

    expected_terms_passed: bool
    missing_expected_terms: list[str]

    forbidden_terms_passed: bool
    found_forbidden_terms: list[str]

    source_passed: bool
    missing_source_fragments: list[str]

    overall_passed: bool

    latency_ms: int | None
    answer: str
    source_urls: list[str]
    error: str | None


def normalize_text(value: str) -> str:
    return " ".join(
        value.casefold().split()
    )


def load_dataset(
    dataset_path: Path,
) -> list[dict[str, Any]]:
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: "
            f"{dataset_path}"
        )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Evaluation dataset must contain a JSON list."
        )

    return data


def evaluate_terms(
    *,
    answer: str,
    expected_terms: list[str],
    forbidden_terms: list[str],
) -> tuple[
    bool,
    list[str],
    bool,
    list[str],
]:
    normalized_answer = normalize_text(
        answer
    )

    missing_expected_terms = [
        term
        for term in expected_terms
        if (
            normalize_text(term)
            not in normalized_answer
        )
    ]

    found_forbidden_terms = [
        term
        for term in forbidden_terms
        if (
            normalize_text(term)
            in normalized_answer
        )
    ]

    return (
        not missing_expected_terms,
        missing_expected_terms,
        not found_forbidden_terms,
        found_forbidden_terms,
    )


def evaluate_sources(
    *,
    source_urls: list[str],
    expected_fragments: list[str],
) -> tuple[bool, list[str]]:
    normalized_urls = [
        normalize_text(url)
        for url in source_urls
    ]

    missing_fragments = [
        fragment
        for fragment in expected_fragments
        if not any(
            normalize_text(fragment)
            in url
            for url in normalized_urls
        )
    ]

    return (
        not missing_fragments,
        missing_fragments,
    )


def evaluate_case(
    *,
    client: httpx.Client,
    api_url: str,
    case: dict[str, Any],
) -> EvaluationResult:
    case_id = str(
        case.get("id", "UNKNOWN")
    )

    category = str(
        case.get(
            "category",
            "uncategorized",
        )
    )

    question = str(
        case["question"]
    )

    expected_language = str(
        case["language"]
    )

    expected_grounded = bool(
        case["expected_grounded"]
    )

    expected_terms = list(
        case.get(
            "expected_terms",
            [],
        )
    )

    forbidden_terms = list(
        case.get(
            "forbidden_terms",
            [],
        )
    )

    expected_source_fragments = list(
        case.get(
            "expected_source_contains",
            [],
        )
    )

    started_at = time.perf_counter()

    try:
        response = client.post(
            f"{api_url.rstrip('/')}/api/chat",
            json={
                "question": question,
                "language": expected_language,
                "retrieval_limit": 5,
                "session_id": str(
                    uuid.uuid4()
                ),
            },
        )

        latency_ms = int(
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        response.raise_for_status()

        payload = response.json()

        answer = str(
            payload.get(
                "answer",
                "",
            )
        )

        actual_language = payload.get(
            "language"
        )

        actual_grounded = payload.get(
            "grounded"
        )

        source_urls = [
            str(source.get("url", ""))
            for source in payload.get(
                "sources",
                [],
            )
        ]

        (
            expected_terms_passed,
            missing_expected_terms,
            forbidden_terms_passed,
            found_forbidden_terms,
        ) = evaluate_terms(
            answer=answer,
            expected_terms=expected_terms,
            forbidden_terms=forbidden_terms,
        )

        (
            source_passed,
            missing_source_fragments,
        ) = evaluate_sources(
            source_urls=source_urls,
            expected_fragments=(
                expected_source_fragments
            ),
        )

        language_passed = (
            actual_language
            == expected_language
        )

        grounded_passed = (
            actual_grounded
            == expected_grounded
        )

        overall_passed = all(
            [
                language_passed,
                grounded_passed,
                expected_terms_passed,
                forbidden_terms_passed,
                source_passed,
            ]
        )

        return EvaluationResult(
            case_id=case_id,
            category=category,
            question=question,
            request_succeeded=True,
            status_code=response.status_code,
            expected_language=expected_language,
            actual_language=actual_language,
            language_passed=language_passed,
            expected_grounded=expected_grounded,
            actual_grounded=actual_grounded,
            grounded_passed=grounded_passed,
            expected_terms_passed=(
                expected_terms_passed
            ),
            missing_expected_terms=(
                missing_expected_terms
            ),
            forbidden_terms_passed=(
                forbidden_terms_passed
            ),
            found_forbidden_terms=(
                found_forbidden_terms
            ),
            source_passed=source_passed,
            missing_source_fragments=(
                missing_source_fragments
            ),
            overall_passed=overall_passed,
            latency_ms=latency_ms,
            answer=answer,
            source_urls=source_urls,
            error=None,
        )

    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        latency_ms = int(
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        status_code = None

        if isinstance(
            error,
            httpx.HTTPStatusError,
        ):
            status_code = (
                error.response.status_code
            )

        return EvaluationResult(
            case_id=case_id,
            category=category,
            question=question,
            request_succeeded=False,
            status_code=status_code,
            expected_language=expected_language,
            actual_language=None,
            language_passed=False,
            expected_grounded=expected_grounded,
            actual_grounded=None,
            grounded_passed=False,
            expected_terms_passed=False,
            missing_expected_terms=(
                expected_terms
            ),
            forbidden_terms_passed=False,
            found_forbidden_terms=[],
            source_passed=False,
            missing_source_fragments=(
                expected_source_fragments
            ),
            overall_passed=False,
            latency_ms=latency_ms,
            answer="",
            source_urls=[],
            error=str(error),
        )


def calculate_summary(
    results: list[EvaluationResult],
) -> dict[str, Any]:
    total = len(results)

    passed = sum(
        result.overall_passed
        for result in results
    )

    request_successes = sum(
        result.request_succeeded
        for result in results
    )

    language_passes = sum(
        result.language_passed
        for result in results
    )

    grounded_passes = sum(
        result.grounded_passed
        for result in results
    )

    expected_term_passes = sum(
        result.expected_terms_passed
        for result in results
    )

    forbidden_term_passes = sum(
        result.forbidden_terms_passed
        for result in results
    )

    source_passes = sum(
        result.source_passed
        for result in results
    )

    latencies = [
        result.latency_ms
        for result in results
        if result.latency_ms is not None
    ]

    category_summary: dict[
        str,
        dict[str, int | float]
    ] = {}

    categories = sorted(
        {
            result.category
            for result in results
        }
    )

    for category in categories:
        category_results = [
            result
            for result in results
            if result.category == category
        ]

        category_passed = sum(
            result.overall_passed
            for result in category_results
        )

        category_summary[category] = {
            "total": len(
                category_results
            ),
            "passed": category_passed,
            "pass_rate": round(
                (
                    category_passed
                    / len(category_results)
                    * 100
                ),
                2,
            ),
        }

    def percentage(
        value: int,
    ) -> float:
        if total == 0:
            return 0.0

        return round(
            value / total * 100,
            2,
        )

    return {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": (
            total - passed
        ),
        "overall_pass_rate": percentage(
            passed
        ),
        "request_success_rate": percentage(
            request_successes
        ),
        "language_pass_rate": percentage(
            language_passes
        ),
        "grounded_status_pass_rate": (
            percentage(
                grounded_passes
            )
        ),
        "expected_terms_pass_rate": (
            percentage(
                expected_term_passes
            )
        ),
        "forbidden_terms_pass_rate": (
            percentage(
                forbidden_term_passes
            )
        ),
        "source_pass_rate": percentage(
            source_passes
        ),
        "average_latency_ms": (
            round(
                statistics.mean(
                    latencies
                ),
                2,
            )
            if latencies
            else None
        ),
        "median_latency_ms": (
            round(
                statistics.median(
                    latencies
                ),
                2,
            )
            if latencies
            else None
        ),
        "category_summary": (
            category_summary
        ),
    }


def save_json_report(
    *,
    output_path: Path,
    summary: dict[str, Any],
    results: list[EvaluationResult],
) -> None:
    report = {
        "summary": summary,
        "results": [
            asdict(result)
            for result in results
        ],
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_csv_report(
    *,
    output_path: Path,
    results: list[EvaluationResult],
) -> None:
    fieldnames = [
        "case_id",
        "category",
        "question",
        "overall_passed",
        "request_succeeded",
        "status_code",
        "expected_language",
        "actual_language",
        "language_passed",
        "expected_grounded",
        "actual_grounded",
        "grounded_passed",
        "expected_terms_passed",
        "missing_expected_terms",
        "forbidden_terms_passed",
        "found_forbidden_terms",
        "source_passed",
        "missing_source_fragments",
        "latency_ms",
        "answer",
        "source_urls",
        "error",
    ]

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:
            row = asdict(result)

            for field in [
                "missing_expected_terms",
                "found_forbidden_terms",
                "missing_source_fragments",
                "source_urls",
            ]:
                row[field] = json.dumps(
                    row[field],
                    ensure_ascii=False,
                )

            writer.writerow(row)


def print_summary(
    *,
    summary: dict[str, Any],
    results: list[EvaluationResult],
) -> None:
    print()
    print("=" * 70)
    print("ATA RAG EVALUATION SUMMARY")
    print("=" * 70)

    print(
        "Total cases: "
        f"{summary['total_cases']}"
    )

    print(
        "Passed: "
        f"{summary['passed_cases']}"
    )

    print(
        "Failed: "
        f"{summary['failed_cases']}"
    )

    print(
        "Overall pass rate: "
        f"{summary['overall_pass_rate']}%"
    )

    print(
        "Language pass rate: "
        f"{summary['language_pass_rate']}%"
    )

    print(
        "Grounded-status pass rate: "
        f"{summary['grounded_status_pass_rate']}%"
    )

    print(
        "Expected-terms pass rate: "
        f"{summary['expected_terms_pass_rate']}%"
    )

    print(
        "Forbidden-terms pass rate: "
        f"{summary['forbidden_terms_pass_rate']}%"
    )

    print(
        "Source pass rate: "
        f"{summary['source_pass_rate']}%"
    )

    print(
        "Average latency: "
        f"{summary['average_latency_ms']} ms"
    )

    failed_results = [
        result
        for result in results
        if not result.overall_passed
    ]

    if failed_results:
        print()
        print("FAILED CASES")
        print("-" * 70)

        for result in failed_results:
            print(
                f"{result.case_id}: "
                f"{result.question}"
            )

            if result.error:
                print(
                    f"  Error: {result.error}"
                )

            if not result.language_passed:
                print(
                    "  Language mismatch: "
                    f"expected "
                    f"{result.expected_language}, "
                    f"received "
                    f"{result.actual_language}"
                )

            if not result.grounded_passed:
                print(
                    "  Grounded mismatch: "
                    f"expected "
                    f"{result.expected_grounded}, "
                    f"received "
                    f"{result.actual_grounded}"
                )

            if (
                result.missing_expected_terms
            ):
                print(
                    "  Missing terms: "
                    + ", ".join(
                        result.missing_expected_terms
                    )
                )

            if (
                result.found_forbidden_terms
            ):
                print(
                    "  Forbidden terms: "
                    + ", ".join(
                        result.found_forbidden_terms
                    )
                )

            if (
                result.missing_source_fragments
            ):
                print(
                    "  Missing sources: "
                    + ", ".join(
                        result.missing_source_fragments
                    )
                )

    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run ATA RAG API evaluation."
        )
    )

    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
    )

    arguments = parser.parse_args()

    dataset = load_dataset(
        arguments.dataset
    )

    arguments.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S"
    )

    results: list[
        EvaluationResult
    ] = []

    with httpx.Client(
        timeout=arguments.timeout,
    ) as client:
        for index, case in enumerate(
            dataset,
            start=1,
        ):
            print(
                f"[{index}/{len(dataset)}] "
                f"{case['id']} — "
                f"{case['question']}"
            )

            result = evaluate_case(
                client=client,
                api_url=arguments.api_url,
                case=case,
            )

            results.append(result)

            status_text = (
                "PASS"
                if result.overall_passed
                else "FAIL"
            )

            print(
                f"  {status_text} "
                f"({result.latency_ms} ms)"
            )

    summary = calculate_summary(
        results
    )

    json_output = (
        arguments.output_directory
        / f"evaluation_{timestamp}.json"
    )

    csv_output = (
        arguments.output_directory
        / f"evaluation_{timestamp}.csv"
    )

    save_json_report(
        output_path=json_output,
        summary=summary,
        results=results,
    )

    save_csv_report(
        output_path=csv_output,
        results=results,
    )

    print_summary(
        summary=summary,
        results=results,
    )

    print(
        f"JSON report: {json_output}"
    )

    print(
        f"CSV report: {csv_output}"
    )


if __name__ == "__main__":
    main()
