# KhmerDocKit top-level Makefile
# Run from the repo root. Targets are intentionally simple and runnable on Linux/macOS/Windows (via WSL or Git Bash).

SHELL := /bin/bash
PY   ?= python3
PIP  ?= $(PY) -m pip
UVICORN ?= $(PY) -m uvicorn

# ----- helpers -----
.PHONY: help
help:
	@echo "KhmerDocKit — make targets"
	@echo "  make install   install all packages (core + api + dev)"
	@echo "  make test      run pytest across packages"
	@echo "  make lint      run ruff + (optional) mypy"
	@echo "  make api       run the FastAPI server on :8000"
	@echo "  make web       run the Next.js demo on :3000"
	@echo "  make demo      run api + web together"
	@echo "  make synth     generate the synthetic dataset"
	@echo "  make benchmark run benchmark over datasets/synthetic"
	@echo "  make docker    build & start via docker compose"
	@echo "  make clean     remove caches and build artifacts"

# ----- install -----
.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -e packages/khmerdoc-core[dev]
	$(PIP) install -e packages/khmerdoc-api[dev]
	@echo "Python packages installed. For the web demo, run: (cd packages/khmerdoc-web && npm install)"

.PHONY: install-web
install-web:
	cd packages/khmerdoc-web && npm install

# ----- test -----
.PHONY: test
test:
	$(PY) -m pytest -q packages/khmerdoc-core/tests packages/khmerdoc-api/tests

.PHONY: test-core
test-core:
	$(PY) -m pytest -q packages/khmerdoc-core/tests

.PHONY: test-api
test-api:
	$(PY) -m pytest -q packages/khmerdoc-api/tests

# ----- lint -----
.PHONY: lint
lint:
	$(PY) -m ruff check packages/khmerdoc-core packages/khmerdoc-api

.PHONY: format
format:
	$(PY) -m ruff check --fix packages/khmerdoc-core packages/khmerdoc-api
	$(PY) -m ruff format packages/khmerdoc-core packages/khmerdoc-api

# ----- run -----
.PHONY: api
api:
	cd packages/khmerdoc-api && $(UVICORN) khmerdoc_api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: web
web:
	cd packages/khmerdoc-web && npm run dev

.PHONY: demo
demo:
	@echo "Starting API on :8000 and Web on :3000. Use Ctrl-C to stop."
	@trap 'kill 0' EXIT; \
	  (cd packages/khmerdoc-api && $(UVICORN) khmerdoc_api.main:app --reload --port 8000 &) ; \
	  (cd packages/khmerdoc-web && npm run dev &) ; \
	  wait

# ----- data -----
.PHONY: synth
synth:
	$(PY) -m khmerdoc.synthetic.generate --out datasets/synthetic

.PHONY: benchmark
benchmark:
	$(PY) -m khmerdoc.cli benchmark datasets/synthetic

# ----- docker -----
.PHONY: docker
docker:
	docker compose up --build

.PHONY: docker-down
docker-down:
	docker compose down

# ----- misc -----
.PHONY: clean
clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__ **/*.egg-info
	rm -rf packages/khmerdoc-web/.next packages/khmerdoc-web/node_modules
