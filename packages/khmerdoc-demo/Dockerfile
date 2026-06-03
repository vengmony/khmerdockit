FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY packages/khmerdoc-core/pyproject.toml /app/packages/khmerdoc-core/
COPY packages/khmerdoc-core/src /app/packages/khmerdoc-core/src
COPY packages/khmerdoc-demo/pyproject.toml /app/packages/khmerdoc-demo/
COPY packages/khmerdoc-demo/src /app/packages/khmerdoc-demo/src

RUN pip install --upgrade pip \
    && pip install -e /app/packages/khmerdoc-core \
    && pip install -e /app/packages/khmerdoc-demo

EXPOSE 7860

CMD ["khmerdoc-demo", "--host", "0.0.0.0", "--port", "7860"]
