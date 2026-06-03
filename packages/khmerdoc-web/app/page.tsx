import Uploader from "@/components/Uploader";
import Examples from "@/components/Examples";
import { headers } from "next/headers";

export default function HomePage() {
  const h = headers();
  return (
    <div className="space-y-10">
      <section className="space-y-3">
        <h2 className="text-3xl md:text-4xl font-semibold text-zinc-50">
          Extract structured data from Cambodian business documents.
        </h2>
        <p className="text-zinc-400 max-w-2xl">
          Upload a receipt, invoice, quotation, or bank transfer screenshot and
          get a typed JSON object back — merchant, date, currency, line items,
          totals, and warnings. Powered by{" "}
          <code className="font-mono text-brand-100">khmerdoc-core</code>.
        </p>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Uploader apiBase={process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"} />
        <Examples apiBase={process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"} />
      </section>

      <section className="card space-y-2">
        <h3 className="text-lg font-semibold">How it works</h3>
        <ol className="list-decimal list-inside text-zinc-300 space-y-1">
          <li>
            The browser posts your file to the FastAPI server
            (<code className="font-mono">POST /v1/parse</code>).
          </li>
          <li>
            An OCR adapter (mock by default, PaddleOCR/Tesseract optional)
            turns the image into text.
          </li>
          <li>
            A rule-based extractor fills the typed schema, then a Cambodia
            validator adds warnings for things like unusual phone numbers or
            weird dates.
          </li>
          <li>The typed JSON is shown back here, with confidence and warnings.</li>
        </ol>
        <p className="text-zinc-500 text-sm pt-2">
          Try the synthetic samples on the right, or upload your own.
        </p>
      </section>
    </div>
  );
}
