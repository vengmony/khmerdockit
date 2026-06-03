"""``GET /health`` — liveness probe."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__

router = APIRouter(tags=["meta"])


@router.get("/health", summary="Liveness check")
def health() -> dict:
    return {
        "status": "ok",
        "service": "khmerdoc-api",
        "version": __version__,
    }
