"""High-level service that wires OCR + extractor + validator together."""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

from khmerdoc.extractors import ExtractorRegistry
from khmerdoc.ocr import OcrAdapterRegistry
from khmerdoc.schemas import DocumentType, ExtractionResult, OCRResult
from khmerdoc.validators import validate_extraction

from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Max bytes we'll read from an upload before refusing it.
_MAX_UPLOAD_BYTES_HARD_CAP = 50 * 1024 * 1024  # 50 MB hard ceiling


class ExtractionService:
    """Stateless-ish service: configured at startup, called per request.

    The service holds the OCR adapter, the extractor, and the configured
    validation rules. Replace the underlying OCR/extractor by changing the
    Settings — the route layer doesn't care.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ocr = OcrAdapterRegistry.create(settings.ocr_backend)
        # Tesseract & Paddle accept lang; mock just ignores it.
        try:
            self.ocr.configure(lang=settings.ocr_lang)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - best effort
            pass
        self.extractor = ExtractorRegistry.create(settings.extractor_backend)
        self._allowed_mime = {m.strip().lower() for m in settings.api_allowed_mime}
        self._max_bytes = min(settings.api_max_upload_mb * 1024 * 1024, _MAX_UPLOAD_BYTES_HARD_CAP)

    # ---- security helpers ----

    def _check_upload(self, file_path: Path, content_type: str | None) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        size = file_path.stat().st_size
        if size <= 0:
            raise ValueError("Empty upload — file contains 0 bytes.")
        if size > self._max_bytes:
            raise ValueError(
                f"Upload too large: {size} bytes (max {self._max_bytes} bytes). "
                "Lower KHMERDOC_API_MAX_UPLOAD_MB if this is unexpected."
            )
        # Trust the client-supplied content_type if present, otherwise sniff.
        ctype = (content_type or "").lower().strip()
        if not ctype:
            ctype, _ = mimetypes.guess_type(str(file_path))
            ctype = (ctype or "").lower()
        if ctype and ctype not in self._allowed_mime:
            raise ValueError(
                f"Unsupported content type '{ctype}'. "
                f"Allowed: {sorted(self._allowed_mime)}."
            )

    # ---- public API ----

    def parse_file(
        self,
        file_path: Path,
        *,
        document_type: DocumentType,
        original_filename: str | None = None,
        content_type: str | None = None,
    ) -> dict:
        self._check_upload(file_path, content_type)
        logger.info(
            "Parsing file=%s type=%s bytes=%d",
            original_filename or file_path.name,
            document_type.value,
            file_path.stat().st_size,
        )
        ocr_result = self._safe_ocr(file_path)
        # If the OCR backend produced nothing (e.g. mock with no text), and
        # the file looks like plain text, fall back to reading the file
        # directly. This makes the synthetic ``.txt`` files usable.
        if not ocr_result.text and (file_path.suffix.lower() == ".txt" or content_type == "text/plain"):
            ocr_result = OCRResult(
                text=file_path.read_text(encoding="utf-8", errors="replace"),
                tokens=[],
                language=self.settings.ocr_lang,
                confidence=1.0,
                engine="passthrough",
            )

        result: ExtractionResult = self.extractor.extract(
            ocr_result, document_type=document_type or self.settings.document_type_hint  # type: ignore[arg-type]
        )
        validate_extraction(result)
        return result.to_jsonable()

    def ocr_only(self, file_path: Path) -> tuple[str, str, float]:
        self._check_upload(file_path, content_type=None)
        ocr_result = self._safe_ocr(file_path)
        if not ocr_result.text and file_path.suffix.lower() == ".txt":
            return file_path.read_text(encoding="utf-8"), "passthrough", 1.0
        return ocr_result.text, ocr_result.engine, ocr_result.confidence

    # ---- internals ----

    def _safe_ocr(self, file_path: Path) -> OCRResult:
        try:
            return self.ocr.extract_text(file_path)
        except FileNotFoundError:
            raise
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("OCR failed for %s", file_path)
            return OCRResult(
                text="",
                tokens=[],
                language=self.settings.ocr_lang,
                confidence=0.0,
                engine="error",
                raw={"error": str(e)},
            )
