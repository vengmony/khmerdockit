"""``GET /v1/schemas`` — public JSON schemas for the typed documents."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from khmerdoc.schemas import BankSlip, ExtractionResult, Invoice, LineItem, Quotation, Receipt

router = APIRouter(prefix="/v1", tags=["schemas"])


_MODELS = {
    "Receipt": Receipt,
    "Invoice": Invoice,
    "Quotation": Quotation,
    "BankSlip": BankSlip,
    "LineItem": LineItem,
    "ExtractionResult": ExtractionResult,
}


@router.get("/schemas", summary="List available JSON schemas.")
def list_schemas() -> dict:
    return {
        "schemas": [
            {"name": name, "schema": model.model_json_schema()} for name, model in _MODELS.items()
        ]
    }


@router.get("/schemas/{name}", summary="Get a single JSON schema by name.")
def get_schema(name: str) -> JSONResponse:
    if name not in _MODELS:
        return JSONResponse(status_code=404, content={"detail": f"Unknown schema '{name}'."})
    return JSONResponse(content={"name": name, "schema": _MODELS[name].model_json_schema()})
