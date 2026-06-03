"use client";

import { useState } from "react";

type Example = {
  id: string;
  title: string;
  description: string;
  text: string;
  document_type: "receipt" | "invoice" | "quotation" | "bank_slip";
};

// A small set of inline synthetic samples so the demo is fully self-contained
// and works without the dataset on disk. The generator in
// ``khmerdoc.synthetic`` produces the same shape of data.
const SAMPLES: Example[] = [
  {
    id: "sample-receipt",
    title: "Receipt — English, USD",
    description: "Coffee shop receipt, classic line-item layout.",
    document_type: "receipt",
    text: `Example Mart
RECEIPT
No: INV-001
Date: 2026-06-02
Tel: 012345678
------------------------
Classic Clog        1 x 12.50   12.50
USB-C Cable 1m      2 x  3.00    6.00
------------------------
SUBTOTAL    $18.50
TOTAL       $18.50
Thank you!`,
  },
  {
    id: "sample-invoice",
    title: "Invoice — English, USD",
    description: "Tax invoice with buyer, due date, and line items.",
    document_type: "invoice",
    text: `Mekong Minimart
INVOICE
Invoice No: INV-123
Date: 02/06/2026
Due Date: 16/06/2026
Bill To: Sokha Construction
Tel: +85512345678
--------------------------------
Rice 5kg            2 x 25.00  =  50.00
Soap Bar            5 x  1.50  =   7.50
--------------------------------
SUBTOTAL    $57.50
TOTAL       $57.50`,
  },
  {
    id: "sample-quotation",
    title: "Quotation — KHR",
    description: "Estimate in Khmer Riel with a valid-until date.",
    document_type: "quotation",
    text: `Riverside Restaurant
QUOTATION
Quote No: QUOT-007
Date: 2026-06-01
Valid Until: 2026-06-15
Attn: Mey Mom Cosmetics
Tel: 093 222 333
--------------------------------
Set Lunch A          20 x 12,000  =  240,000 ៛
Set Lunch B          10 x 18,000  =  180,000 ៛
--------------------------------
SUBTOTAL    420,000 ៛
TOTAL       420,000 ៛`,
  },
  {
    id: "sample-bank-slip",
    title: "Bank slip — USD transfer",
    description: "Bank transfer confirmation with sender/receiver accounts.",
    document_type: "bank_slip",
    text: `ACLEDA Bank
BANK TRANSFER CONFIRMATION
Reference: TRF123456
Date: 2026-05-30
From: Sokha Construction  Acc: 12345678
To:   Mekong Minimart     Acc: 87654321
Amount: $250.00
Status: SUCCESS`,
  },
];

export default function Examples({ apiBase }: { apiBase: string }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);

  async function runSample(s: Example) {
    setBusy(s.id);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", new Blob([s.text], { type: "text/plain" }), `${s.id}.txt`);
      fd.append("document_type", s.document_type);
      const res = await fetch(`${apiBase.replace(/\/$/, "")}/v1/parse`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
      setResult(await res.json());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="card space-y-4">
      <div>
        <h3 className="text-lg font-semibold">Sample documents</h3>
        <p className="text-zinc-400 text-sm">
          Pre-baked synthetic samples. Click to send to the API and see the
          extracted JSON.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {SAMPLES.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => runSample(s)}
            disabled={busy !== null}
            className="text-left bg-zinc-900/40 border border-zinc-800 hover:border-brand-500 rounded-xl p-3 transition-colors disabled:opacity-50"
          >
            <div className="text-sm font-medium text-zinc-100">{s.title}</div>
            <div className="text-xs text-zinc-400">{s.description}</div>
            <div className="text-[10px] text-zinc-500 font-mono mt-1">
              {busy === s.id ? "running…" : "click to parse"}
            </div>
          </button>
        ))}
      </div>

      {error && <div className="tag-err text-sm">⚠ {error}</div>}

      {result != null && (
        <pre className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-xs overflow-x-auto max-h-72">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
