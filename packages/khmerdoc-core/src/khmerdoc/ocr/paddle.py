"""PaddleOCR adapter (optional dependency).

The adapter is only useful when the ``paddleocr`` package is installed.
We import it lazily so the rest of KhmerDocKit works without it.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..schemas import OCRResult, OCRToken

_log = logging.getLogger(__name__)


class PaddleOCRAdapter:
    """Thin wrapper around :mod:`paddleocr`.

    Parameters
    ----------
    lang:
        Language code passed to PaddleOCR. ``"en"``, ``"km"`` (Khmer) and
        ``"en+km"``-style strings are typical.
    use_angle_cls:
        Forwarded to PaddleOCR — enables the text-angle classifier, which
        helps on slightly rotated phone photos.
    """

    name = "paddle"

    def __init__(self, lang: str = "en", use_angle_cls: bool = True) -> None:
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self._engine = None  # lazy

    def _get_engine(self):  # pragma: no cover - depends on optional install
        if self._engine is None:
            try:
                from paddleocr import PaddleOCR  # type: ignore[import-not-found]
            except ImportError as e:  # pragma: no cover
                raise ImportError(
                    "PaddleOCR backend requires the 'paddleocr' package. "
                    "Install with: pip install 'khmerdoc-core[paddle]'."
                ) from e
            self._engine = PaddleOCR(use_angle_cls=self.use_angle_cls, lang=self.lang, show_log=False)
        return self._engine

    def extract_text(self, file_path: str | Path) -> OCRResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        engine = self._get_engine()
        # ``ocr`` returns a list with one element per input image.
        result = engine.ocr(str(path), cls=True)
        if not result or not result[0]:
            return OCRResult(text="", tokens=[], language=self.lang, engine=self.name)

        tokens: list[OCRToken] = []
        lines: list[str] = []
        confidences: list[float] = []
        for box, (text, conf) in result[0]:
            tokens.append(
                OCRToken(
                    text=text,
                    confidence=float(conf),
                    bbox=[(float(x), float(y)) for x, y in box],
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
            raw={"engine": "paddleocr", "lang": self.lang},
        )
