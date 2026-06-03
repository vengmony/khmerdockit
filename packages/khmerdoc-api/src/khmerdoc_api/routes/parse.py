"""``POST /v1/parse`` — upload a document and get structured JSON."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from khmerdoc.schemas import DocumentType

from ..deps import get_extraction_service
from ..services.extraction import ExtractionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["parse"])


@router.post(
    "/parse",
    summary="Parse a document image/PDF into structured JSON.",
    response_class=JSONResponse,
)
async def parse_document(
    file: Annotated[UploadFile, File(description="The document image/PDF to parse.")],
    document_type: Annotated[
        str,
        Form(description="Document type hint: 'auto', 'receipt', 'invoice', 'quotation', 'bank_slip'."),
    ] = "auto",
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    try:
        dt = DocumentType(document_type) if document_type != "auto" else DocumentType.UNKNOWN
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_type: {document_type}",
        ) from e

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    # Persist upload to a temp file so the OCR adapter sees a real path.
    # We clean it up in the finally block.
    with tempfile.TemporaryDirectory(prefix="khmerdoc-") as tmp:
        tmp_path = Path(tmp) / Path(file.filename).name
        contents = await file.read()
        tmp_path.write_bytes(contents)
        try:
            result = service.parse_file(
                tmp_path,
                document_type=dt,
                original_filename=file.filename,
                content_type=file.content_type,
            )
        except FileNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    return result
