FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for tesseract, pillow, and opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-khm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY packages/khmerdoc-core/pyproject.toml /app/packages/khmerdoc-core/
COPY packages/khmerdoc-core/src /app/packages/khmerdoc-core/src
COPY packages/khmerdoc-api/pyproject.toml /app/packages/khmerdoc-api/
COPY packages/khmerdoc-api/src /app/packages/khmerdoc-api/src

RUN pip install --upgrade pip \
    && pip install -e /app/packages/khmerdoc-core \
    && pip install -e /app/packages/khmerdoc-api

# Bundle datasets for offline use
COPY datasets /app/datasets

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "khmerdoc_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
