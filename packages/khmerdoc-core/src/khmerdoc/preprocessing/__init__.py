"""Lightweight image preprocessing helpers.

Kept optional and dependency-light (Pillow + OpenCV) so the rest of the
package still works without them. The :func:`preprocess_image` function
returns a Pillow image; callers may save it back to disk before passing to an
OCR adapter.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

try:  # OpenCV is optional at import time, but we use it when present.
    import cv2  # type: ignore[import-not-found]
    import numpy as np  # type: ignore[import-not-found]

    _HAS_CV2 = True
except ImportError:  # pragma: no cover
    _HAS_CV2 = False


def load_image(file_path: str | Path) -> Image.Image:
    """Open an image from disk and convert to RGB."""
    img = Image.open(file_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def preprocess_image(
    file_path: str | Path,
    *,
    max_side: int = 1600,
    autocontrast: bool = True,
) -> Image.Image:
    """Load + downscale + auto-contrast an image.

    Parameters
    ----------
    file_path:
        Path to the image on disk.
    max_side:
        Largest side after downscaling. Keeps the aspect ratio.
    autocontrast:
        Whether to apply :func:`PIL.ImageOps.autocontrast`. Helpful for
        low-light phone photos.
    """
    img = load_image(file_path)
    w, h = img.size
    longest = max(w, h)
    if longest > max_side:
        scale = max_side / float(longest)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    if autocontrast:
        img = ImageOps.autocontrast(img)
    return img


def deskew(img: Image.Image) -> Image.Image:
    """Best-effort deskew. Returns the input unchanged if OpenCV is unavailable."""
    if not _HAS_CV2:
        return img
    arr = np.array(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    h, w = arr.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        arr, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return Image.fromarray(rotated)


__all__ = ["load_image", "preprocess_image", "deskew"]
