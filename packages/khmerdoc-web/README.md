# KhmerDocKit Web

A minimal Next.js 14 (TypeScript + Tailwind) demo for **KhmerDocKit**.

* Upload a document (image, PDF, or paste a `.txt`).
* The page calls the API at `NEXT_PUBLIC_API_BASE_URL` (default
  `http://localhost:8000`) and shows the structured JSON, confidence, and
  warnings.
* Ships with three example documents generated from the synthetic dataset.

## Run

```bash
make install-web    # or: (cd packages/khmerdoc-web && npm install)
make web            # or: (cd packages/khmerdoc-web && npm run dev)
```

By default the web demo expects the API at `http://localhost:8000`. To
point at a different host, set `NEXT_PUBLIC_API_BASE_URL` before running
`npm run dev`.

## Build for production

```bash
npm run build
npm start
```

## Docker

A `Dockerfile` is provided at this package's root. It is used by the top-level
`docker-compose.yml`.
