from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "ata-rag-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }
