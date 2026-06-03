"""FastAPI application factory + module-level ``app`` for ``uvicorn``."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .routes import health, ocr, parse, schemas
from .services.extraction import ExtractionService
from .settings import get_settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    app = FastAPI(
        title="KhmerDocKit API",
        version=__version__,
        description=(
            "HTTP API for **KhmerDocKit** — extract structured data from "
            "Cambodian business documents (receipts, invoices, quotations, "
            "bank slips)."
        ),
        contact={"name": "KhmerDocKit contributors"},
        license_info={"name": "MIT"},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Initialise shared service.
    app.state.extraction_service = ExtractionService(settings)

    # Routers
    app.include_router(health.router)
    app.include_router(parse.router)
    app.include_router(ocr.router)
    app.include_router(schemas.router)

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {
            "service": "khmerdoc-api",
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
