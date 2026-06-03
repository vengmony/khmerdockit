"""FastAPI dependency providers."""

from __future__ import annotations

from fastapi import Request

from .services.extraction import ExtractionService


def get_extraction_service(request: Request) -> ExtractionService:
    """Return the shared :class:`ExtractionService` stored on the app state."""
    svc = getattr(request.app.state, "extraction_service", None)
    if svc is None:  # pragma: no cover - defensive
        raise RuntimeError("ExtractionService not initialised on app.state.")
    return svc
