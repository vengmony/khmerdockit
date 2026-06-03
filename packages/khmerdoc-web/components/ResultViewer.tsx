"use client";

import { useState } from "react";

type ExtractionPayload = {
  document_type: string;
  confidence: number;
  warnings: { code: string; message: string; field?: string | null }[];
  raw_ocr_text?: string;
  engine?: string;
  merchant_name?: string;
  buyer_name?: string;
  bank_name?: string;
  sender_name?: string;
  receiver_name?: string;
  date?: string;
  due_date?: string;
  valid_until?: string;
  currency?: string;
  subtotal?: number;
  discount?: number;
  tax?: number;
  total?: number | null;
  amount?: number | null;
  phone_numbers?: string[];
  invoice_number?: string;
  quotation_number?: string;
  reference?: string;
  line_items?: { name: string; quantity: number; unit_price?: number; total?: number }[];
};

const fmt = (n: number | null | undefined) =>
  typeof n === "number" ? n.toFixed(2) : "—";

export default function ResultViewer({ result }: { result: ExtractionPayload }) {
  const [showRaw, setShowRaw] = useState(false);
  const confidencePct = Math.round((result.confidence || 0) * 100);
  const confClass =
    confidencePct >= 80 ? "tag-ok" : confidencePct >= 50 ? "tag-warn" : "tag-err";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="tag-info">
          {result.document_type || "unknown"}
        </span>
        <span className={confClass}>confidence {confidencePct}%</span>
        <span className="tag-info">engine {result.engine || "—"}</span>
        {result.warnings?.length ? (
          <span className="tag-warn">{result.warnings.length} warning(s)</span>
        ) : (
          <span className="tag-ok">no warnings</span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        {result.merchant_name && <Field label="Merchant" value={result.merchant_name} />}
        {result.buyer_name && <Field label="Buyer" value={result.buyer_name} />}
        {result.bank_name && <Field label="Bank" value={result.bank_name} />}
        {result.sender_name && <Field label="Sender" value={result.sender_name} />}
        {result.receiver_name && <Field label="Receiver" value={result.receiver_name} />}
        {result.date && <Field label="Date" value={result.date} />}
        {result.due_date && <Field label="Due date" value={result.due_date} />}
        {result.valid_until && <Field label="Valid until" value={result.valid_until} />}
        {result.invoice_number && <Field label="Invoice #" value={result.invoice_number} />}
        {result.quotation_number && <Field label="Quote #" value={result.quotation_number} />}
        {result.reference && <Field label="Reference" value={result.reference} />}
        {result.currency && <Field label="Currency" value={result.currency} />}
        {typeof result.subtotal === "number" && (
          <Field label="Subtotal" value={fmt(result.subtotal)} />
        )}
        {typeof result.tax === "number" && result.tax > 0 && (
          <Field label="Tax" value={fmt(result.tax)} />
        )}
        {typeof result.discount === "number" && result.discount > 0 && (
          <Field label="Discount" value={fmt(result.discount)} />
        )}
        {typeof result.total === "number" && (
          <Field label="Total" value={fmt(result.total)} strong />
        )}
        {typeof result.amount === "number" && (
          <Field label="Amount" value={fmt(result.amount)} strong />
        )}
        {result.phone_numbers && result.phone_numbers.length > 0 && (
          <Field label="Phone(s)" value={result.phone_numbers.join(", ")} />
        )}
      </div>

      {result.line_items && result.line_items.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-zinc-300 mb-2">Line items</h4>
          <div className="overflow-x-auto border border-zinc-800 rounded-lg">
            <table className="w-full text-sm">
              <thead className="bg-zinc-900/70 text-zinc-400">
                <tr>
                  <th className="text-left px-3 py-2">Name</th>
                  <th className="text-right px-3 py-2">Qty</th>
                  <th className="text-right px-3 py-2">Unit</th>
                  <th className="text-right px-3 py-2">Total</th>
                </tr>
              </thead>
              <tbody>
                {result.line_items.map((it, i) => (
                  <tr key={i} className="odd:bg-zinc-900/30">
                    <td className="px-3 py-2">{it.name}</td>
                    <td className="px-3 py-2 text-right">{it.quantity}</td>
                    <td className="px-3 py-2 text-right">{fmt(it.unit_price ?? null)}</td>
                    <td className="px-3 py-2 text-right">{fmt(it.total ?? null)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {result.warnings && result.warnings.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-zinc-300 mb-2">Warnings</h4>
          <ul className="space-y-1 text-sm">
            {result.warnings.map((w, i) => (
              <li key={i} className="tag-warn inline-block mr-2 mb-2">
                <span className="font-mono mr-1">{w.code}</span>
                <span>{w.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <button
          type="button"
          onClick={() => setShowRaw((v) => !v)}
          className="btn-ghost text-xs"
        >
          {showRaw ? "Hide" : "Show"} raw JSON
        </button>
        {showRaw && (
          <pre className="mt-2 bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </div>

      {result.raw_ocr_text && (
        <details className="text-xs text-zinc-400">
          <summary className="cursor-pointer">Raw OCR text</summary>
          <pre className="mt-2 whitespace-pre-wrap break-words text-zinc-500">
            {result.raw_ocr_text}
          </pre>
        </details>
      )}
    </div>
  );
}

function Field({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg px-3 py-2">
      <div className="text-xs uppercase tracking-wide text-zinc-500">{label}</div>
      <div className={strong ? "text-zinc-50 font-semibold" : "text-zinc-200"}>{value}</div>
    </div>
  );
}
