# LLM extractors (planned v0.3)

> **Status:** not implemented in v0.1. This document sketches the design
> so the rest of the system is ready to host it.

## Why an LLM adapter at all?

The rule-based extractor (`khmerdoc.extractors.rules.RuleBasedExtractor`)
is fast, deterministic, and offline. It struggles with:

* Handwritten or low-light documents.
* Free-form merchant names in Khmer script.
* Multi-page invoices, sub-totalled purchase orders.
* Phrases that wrap across lines.

An LLM adapter fills those gaps.

## Design goals

* **Optional.** The API must keep working with the rule-based extractor
  when `KHMERDOC_LLM_ENABLED=false`. The LLM is a *boost*, not a
  requirement.
* **OpenAI-compatible.** `openai` Python client, or any HTTP client that
  speaks the same request/response shape. Local models served by
  `vllm`, `ollama`, or `llama.cpp` should plug in unchanged.
* **Schema-bound.** The LLM is asked to return JSON that matches one of
  the Pydantic models in `khmerdoc.schemas`. The adapter validates the
  response and falls back to the rule-based extractor on failure.
* **Blended confidence.** The final confidence is a weighted average of
  the rule-based and LLM confidences, weighted by inter-extractor
  agreement per field.

## Planned interface

```python
from khmerdoc.extractors import Extractor
from khmerdoc.schemas import ExtractionResult, OCRResult, DocumentType

class LLMExtractor(Extractor):
    name = "llm"

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        fallback: Extractor | None = None,
    ) -> None: ...

    def extract(
        self,
        ocr: OCRResult | str,
        document_type: DocumentType | str | None = None,
    ) -> ExtractionResult: ...
```

## Prompting principles

1. **Send the OCR text, not the image.** Keeps the adapter small and
   model-agnostic. (Future versions may accept images directly.)
2. **Constrain the output to JSON.** We rely on the model's
   `response_format={"type": "json_object"}` mode (or the local equivalent).
3. **Pass the document type hint if known.** Otherwise let the model pick
   from `receipt | invoice | quotation | bank_slip | unknown`.
4. **Return a confidence in [0, 1].** We will ask the model for a
   per-field self-assessment and aggregate.

## Configuration

| Env var                | Default                | Meaning                              |
| ---------------------- | ---------------------- | ------------------------------------ |
| `KHMERDOC_LLM_ENABLED` | `false`                | Toggle the LLM adapter               |
| `OPENAI_API_KEY`       | (none)                 | API key                              |
| `OPENAI_BASE_URL`      | `https://api.openai.com/v1` | Endpoint URL (override for local) |
| `OPENAI_MODEL`         | `gpt-4o-mini`          | Model name                           |

## Out of scope for v0.3

* Fine-tuning on Khmer receipts. Public Khmer OCR data is sparse;
  the v0.3 adapter will be **prompt-only** so we don't accidentally
  memorise a single merchant.
* Streaming responses. Document extraction is small enough to fit in a
  single response.
* Multi-document uploads. The API accepts one document per request.
