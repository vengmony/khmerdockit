import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KhmerDocKit — Cambodia Document AI",
  description:
    "Open-source AI toolkit for extracting structured data from Khmer and English business documents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 grid place-items-center text-white font-bold">
                K
              </div>
              <div>
                <h1 className="text-lg font-semibold text-zinc-100">KhmerDocKit</h1>
                <p className="text-xs text-zinc-400 -mt-0.5">
                  Open-source document AI for Cambodia
                </p>
              </div>
            </div>
            <nav className="flex items-center gap-4 text-sm">
              <a
                href="https://github.com/khmerdoc/khmerdockit"
                className="hover:text-white"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
              <a
                href="https://github.com/khmerdoc/khmerdockit/blob/main/docs/quickstart.md"
                className="hover:text-white"
                target="_blank"
                rel="noreferrer"
              >
                Docs
              </a>
              <a
                href="https://github.com/khmerdoc/khmerdockit/blob/main/ROADMAP.md"
                className="hover:text-white"
                target="_blank"
                rel="noreferrer"
              >
                Roadmap
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
        <footer className="mx-auto max-w-6xl px-6 py-10 text-xs text-zinc-500">
          <p>
            KhmerDocKit is open source under the MIT license. v0.1.0 is an early MVP — see
            the roadmap for what is next.
          </p>
        </footer>
      </body>
    </html>
  );
}
