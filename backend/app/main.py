from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.api.routes.documents import router as documents_router
from app.api.routes.chunks import (
    router as chunks_router,
)
from app.api.routes.chat import (
    router as chat_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
    ],
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chunks_router)
app.include_router(chat_router)
app.include_router(feedback_router)

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "ATA RAG API is running.",
        "documentation": "/docs",
    }
