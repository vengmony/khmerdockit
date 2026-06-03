"""EasyOCR adapter (optional dependency).

EasyOCR is a third-party OCR library that supports 80+ languages including
English (``en``) and Khmer is supported through the community model set.
This adapter is the *third* plug-in OCR backend for KhmerDocKit; together
with ``mock`` and ``paddle`` it shows the plugin contract is real.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..schemas import OCRResult, OCRToken

_log = logging.getLogger(__name__)


class EasyOCRAdapter:
    """Thin wrapper around :mod:`easyocr`.

    Parameters
    ----------
    lang:
        Comma-separated list of language codes passed to EasyOCR.
        Defaults to English; ``"en,km"`` enables Khmer script.
    gpu:
        Forwarded to EasyOCR — set to ``False`` to force CPU inference.
    """

    name = "easyocr"

    def __init__(self, lang: str = "en", gpu: bool = False) -> None:
        self.lang = lang
        self.gpu = gpu
        self._reader = None  # lazy

    def _get_reader(self):  # pragma: no cover - depends on optional install
        if self._reader is None:
            try:
                import easyocr  # type: ignore[import-not-found]
            except ImportError as e:
                raise ImportError(
                    "EasyOCR backend requires the 'easyocr' package. "
                    "Install with: pip install 'khmerdoc-core[easyocr]'."
                ) from e
            languages = [s.strip() for s in self.lang.split(",") if s.strip()]
            self._reader = easyocr.Reader(languages, gpu=self.gpu)
        return self._reader

    def extract_text(self, file_path: str | Path) -> OCRResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        reader = self._get_reader()
        # ``readtext`` returns a list of ``(bbox, text, confidence)`` tuples.
        result = reader.readtext(str(path))
        tokens: list[OCRToken] = []
        lines: list[str] = []
        confidences: list[float] = []
        for bbox, text, conf in result:
            tokens.append(
                OCRToken(
                    text=text,
                    confidence=float(conf),
                    bbox=[(float(x), float(y)) for x, y in bbox],
                )
            )
            lines.append(text)
            confidences.append(float(conf))
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return OCRResult(
            text="\n".join(lines),
            tokens=tokens,
            language=self.lang,
            confidence=avg_conf,
            engine=self.name,
            raw={"engine": "easyocr", "lang": self.lang, "gpu": self.gpu},
        )
