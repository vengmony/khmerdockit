"use client";

import { useCallback, useMemo, useState } from "react";
import ResultViewer from "./ResultViewer";

type ExtractionPayload = {
  document_type: string;
  confidence: number;
  warnings: { code: string; message: string; field?: string | null }[];
  raw_ocr_text?: string;
  engine?: string;
  // Document-specific fields
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

const DOC_TYPES: { id: string; label: string }[] = [
  { id: "auto", label: "Auto-detect" },
  { id: "receipt", label: "Receipt" },
  { id: "invoice", label: "Invoice" },
  { id: "quotation", label: "Quotation" },
  { id: "bank_slip", label: "Bank slip" },
];

export default function Uploader({ apiBase }: { apiBase: string }) {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<string>("auto");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionPayload | null>(null);

  const onFile = useCallback((f: File | null) => {
    setFile(f);
    setResult(null);
    setError(null);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLLabelElement>) => {
      e.preventDefault();
      const f = e.dataTransfer.files?.[0];
      if (f) onFile(f);
    },
    [onFile],
  );

  const submit = useCallback(async () => {
    if (!file) {
      setError("Pick a file first.");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("document_type", docType);
      const res = await fetch(`${apiBase.replace(/\/$/, "")}/v1/parse`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API error ${res.status}: ${text}`);
      }
      const data = (await res.json()) as ExtractionPayload;
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, [apiBase, docType, file]);

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  return (
    <div className="card space-y-4">
      <h3 className="text-lg font-semibold">Try it</h3>

      <label
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        htmlFor="file-input"
        className="block border-2 border-dashed border-zinc-700 hover:border-brand-500 rounded-xl p-6 text-center cursor-pointer transition-colors"
      >
        <input
          id="file-input"
          type="file"
          accept="image/*,application/pdf,text/plain"
          className="hidden"
          onChange={(e) => onFile(e.target.files?.[0] ?? null)}
        />
        <p className="text-zinc-300">
          {file ? (
            <>
              <span className="font-medium">{file.name}</span>{" "}
              <span className="text-zinc-500 text-sm">({(file.size / 1024).toFixed(1)} KB)</span>
            </>
          ) : (
            <>
              <strong className="text-white">Drop a file</strong> or click to choose.
              <br />
              <span className="text-zinc-500 text-sm">Image, PDF, or plain text.</span>
            </>
          )}
        </p>
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-zinc-400">Document type</label>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          className="bg-zinc-900 border border-zinc-700 text-zinc-100 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500/60"
        >
          {DOC_TYPES.map((d) => (
            <option key={d.id} value={d.id}>
              {d.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={submit}
          disabled={busy || !file}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {busy ? "Parsing…" : "Parse"}
        </button>
      </div>

      {error && (
        <div className="tag-err text-sm">
          <span>⚠ {error}</span>
        </div>
      )}

      {previewUrl && file?.type.startsWith("image/") && (
        <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt="Document preview"
            className="max-h-72 mx-auto object-contain"
          />
        </div>
      )}

      {result && <ResultViewer result={result} />}
    </div>
  );
}
