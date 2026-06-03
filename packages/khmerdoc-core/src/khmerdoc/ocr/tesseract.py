"""Tesseract adapter (optional dependency, requires the system ``tesseract`` binary)."""

from __future__ import annotations

from pathlib import Path

from ..schemas import OCRResult, OCRToken


class TesseractOCRAdapter:
    """Wrapper around :mod:`pytesseract`."""

    name = "tesseract"

    def __init__(self, lang: str = "eng+khmer") -> None:
        self.lang = lang

    def _get_engine(self):  # pragma: no cover - depends on optional install
        try:
            import pytesseract  # type: ignore[import-not-found]
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "Tesseract backend requires the 'pytesseract' package and the "
                "system 'tesseract' binary. "
                "Install with: pip install 'khmerdoc-core[tesseract]'."
            ) from e
        return pytesseract

    def extract_text(self, file_path: str | Path) -> OCRResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        pytesseract = self._get_engine()
        from PIL import Image  # local import keeps top-level import light

        img = Image.open(path)
        data = pytesseract.image_to_data(
            img, lang=self.lang, output_type=pytesseract.Output.DICT
        )
        tokens: list[OCRToken] = []
        lines: list[str] = []
        confidences: list[float] = []
        current_line: list[str] = []
        current_block = (-1, -1, -1)
        for i, word in enumerate(data["text"]):
            txt = (word or "").strip()
            if not txt:
                continue
            block = (
                data["block_num"][i],
                data["par_num"][i],
                data["line_num"][i],
            )
            if block != current_block:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [txt]
                current_block = block
            else:
                current_line.append(txt)
            try:
                conf = float(data["conf"][i])
            except (TypeError, ValueError):
                conf = -1.0
            if conf >= 0:
                confidences.append(conf / 100.0)
            tokens.append(OCRToken(text=txt, confidence=max(conf / 100.0, 0.0)))
        if current_line:
            lines.append(" ".join(current_line))

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return OCRResult(
            text="\n".join(lines),
            tokens=tokens,
            language=self.lang,
            confidence=avg_conf,
            engine=self.name,
            raw={"engine": "tesseract", "lang": self.lang},
        )
