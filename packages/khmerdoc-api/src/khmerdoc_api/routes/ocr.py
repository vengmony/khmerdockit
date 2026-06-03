"""``POST /v1/ocr`` — upload a document, return raw OCR text."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..deps import get_extraction_service
from ..services.extraction import ExtractionService

router = APIRouter(prefix="/v1", tags=["ocr"])


@router.post(
    "/ocr",
    summary="Run OCR on a document and return the raw text.",
    response_class=JSONResponse,
)
async def ocr_only(
    file: Annotated[UploadFile, File(description="The document image/PDF to OCR.")],
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")
    with tempfile.TemporaryDirectory(prefix="khmerdoc-ocr-") as tmp:
        tmp_path = Path(tmp) / Path(file.filename).name
        contents = await file.read()
        tmp_path.write_bytes(contents)
        try:
            text, engine, confidence = service.ocr_only(tmp_path)
        except FileNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return {"text": text, "engine": engine, "confidence": confidence}
