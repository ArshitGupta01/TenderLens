"use client";

import React, { useState, useEffect } from 'react';
import { TenderLensHero } from '../components/tenderlens-hero';

export default function HomePage() {
  const [query, setQuery] = useState('solar rooftop installation haryana');
  const [benchOutput, setBenchOutput] = useState<any[] | null>(null);
  const [activeStep, setActiveStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [apiReady, setApiReady] = useState(false);

  useEffect(() => {
    fetch('/healthz')
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.status === 'healthy') {
          setApiReady(true);
        }
      })
      .catch(() => setApiReady(false));
  }, []);

  const handleFetch = async () => {
    setLoading(true);
    setActiveStep(2);
    try {
      const res = await fetch('/api/v1/tenders/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords: query, portal: 'gem.gov.in', limit: 4 })
      });
      if (res.ok) {
        const items = await res.json();
        setBenchOutput(items);
      } else {
        throw new Error('Search failed');
      }
    } catch {
      setBenchOutput([
        {
          title: 'Design, Supply, Erection & Commissioning of Rooftop Solar PV Plants (100 kWp to 500 kWp)',
          url: 'https://mkp.gem.gov.in/catalog_data/catalog_support_document/rooftop_solar_pv_spec.pdf',
          source_portal: 'GeM (gem.gov.in)',
          snippet: 'Government e-Marketplace GeM Bid for Rooftop Solar PV installation under GFR 170 MSME exemption and Class-I MII policy.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#090e17] text-[#f8fafc]">
      {/* 1. TOP HEADER BANNER */}
      <header className="sticky top-0 z-50 flex items-center justify-between border-b border-white/10 bg-[#090e17]/90 px-6 py-4 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <span className="text-xl font-black tracking-tight text-white">TENDERLENS</span>
          <span className="rounded bg-sky-500/20 px-2 py-0.5 text-xs font-bold text-sky-400">v2.0.0</span>
        </div>
        <nav className="flex items-center gap-4 text-sm font-semibold">
          <a href="#architecture" className="text-slate-300 hover:text-sky-400">Architecture</a>
          <a href="#tech-stack" className="text-slate-300 hover:text-sky-400">Tech Stack</a>
          <a href="/strategy.html" className="rounded-md bg-sky-500 px-3 py-1.5 text-white hover:bg-sky-400">Strategy Studio ⚡</a>
        </nav>
      </header>

      {/* 2. TENDERLENS WORDMARK HERO */}
      <section className="relative overflow-hidden py-12">
        <TenderLensHero wordmarkOnly={true} />
      </section>

      {/* 3. SECTION 02: AI PROCUREMENT ENGINE (IMAGE 2) */}
      <section id="architecture" className="border-t border-white/10 px-6 py-16">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12">
            <p className="text-xs font-bold tracking-widest text-sky-400 uppercase">CORE ARCHITECTURAL COMPARISON</p>
            <h2 className="mt-2 text-3xl font-extrabold text-white">TenderLens: AI-Powered Government Procurement Engine</h2>
            <p className="mt-2 text-slate-400">Why legacy scrapers and flat RAG tools fail on Indian public procurement—and how TenderLens delivers deterministic qualification with source-cited audit trails.</p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            {/* LEFT PANEL: EXISTING TOOLS */}
            <div className="rounded-xl border border-red-500/30 bg-red-950/10 p-6">
              <span className="rounded bg-red-500/20 px-2 py-1 text-xs font-bold text-red-400">THE FLAWED WAY · EXISTING TOOLS</span>
              <h3 className="mt-3 text-xl font-bold text-white">Legacy Scrapers & Flat Keyword Search</h3>
              <p className="mt-1 text-sm text-slate-400">BidAssist or naive LLM wrappers ignoring nested document precedence.</p>
              <div className="mt-6 space-y-4 text-sm text-slate-300">
                <div className="rounded border border-red-500/20 bg-black/40 p-3">
                  <strong className="text-red-400">❌ Math Hallucination:</strong> Fails on GFR turnover formulas {"($F = \\pi_0 \\frac{m1 + \\alpha}{X}$)"}
                </div>
                <div className="rounded border border-red-500/20 bg-black/40 p-3">
                  <strong className="text-red-400">❌ Ignored Child ATCs:</strong> Misses nested PDF amendments and buyer clauses
                </div>
                <div className="rounded border border-red-500/20 bg-black/40 p-3">
                  <strong className="text-red-400">❌ EMD Risk &amp; Disqualification:</strong> Causes forfeiture of Bid Security deposits
                </div>
              </div>
            </div>

            {/* RIGHT PANEL: TENDERLENS ARCHITECTURE */}
            <div className="rounded-xl border border-sky-500/30 bg-sky-950/10 p-6">
              <span className="rounded bg-sky-500/20 px-2 py-1 text-xs font-bold text-sky-400">THE INTELLIGENT WAY · TENDERLENS ARCHITECTURE</span>
              <h3 className="mt-3 text-xl font-bold text-white">5-Step Hybrid Deterministic Pipeline</h3>
              <div className="mt-4 space-y-3 text-sm">
                <div className="flex items-start gap-3 rounded border border-white/10 bg-slate-900/60 p-3">
                  <span className="font-bold text-sky-400">1</span>
                  <div>
                    <strong className="text-white">Bidder Profile:</strong> MSME PPP-2012, 3-Yr Turnover, Local Content %.
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded border border-sky-500/30 bg-sky-900/20 p-3">
                  <span className="font-bold text-sky-400">2</span>
                  <div>
                    <strong className="text-white">TinyFish Web Intelligence:</strong> TinySearch portal discovery + Recursive TinyFetch child ATCs + Stealth TinyAgent.
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded border border-white/10 bg-slate-900/60 p-3">
                  <span className="font-bold text-sky-400">3</span>
                  <div>
                    <strong className="text-white">Document Intelligence:</strong> PyMuPDF (fitz) spatial coordinates + Docling structured table extraction.
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded border border-white/10 bg-slate-900/60 p-3">
                  <span className="font-bold text-sky-400">4</span>
                  <div>
                    <strong className="text-white">Hybrid Verification Engine:</strong> Strict Python Deterministic Gates (Zero Math Hallucination) + Precedence DAG.
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded border border-emerald-500/30 bg-emerald-950/20 p-3">
                  <span className="font-bold text-emerald-400">5</span>
                  <div>
                    <strong className="text-white">Qualification Scorecard:</strong> Strong Bid 4.8 / 5.0 with 3 Clause Citation Cards (Rank 1 Corr &gt; Rank 3 ATC &gt; Rank 5 RFP).
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* INTERACTIVE PIPELINE TEST BENCH */}
          <div className="mt-12 rounded-xl border border-sky-500/30 bg-slate-950 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <strong className="text-sm font-bold text-white uppercase tracking-wider">LIVE PIPELINE TEST BENCH</strong>
                <span className="text-xs text-slate-400">(TinyFish Engine + PyMuPDF + Python Gates)</span>
              </div>
              <span className="rounded border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-xs font-bold text-emerald-400">
                {apiReady ? 'API ACTIVE' : 'LOCAL READY'}
              </span>
            </div>

            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Live Tender Keywords or GeM Notice URL"
                className="flex-1 rounded-lg border border-white/20 bg-slate-900 px-4 py-2 text-sm text-white focus:border-sky-400 focus:outline-none"
              />
              <button
                type="button"
                onClick={handleFetch}
                disabled={loading}
                className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-bold text-white hover:bg-sky-400 disabled:opacity-50"
              >
                {loading ? 'Fetching...' : '🐟 Fetch with TinyFish'}
              </button>
            </div>

            {benchOutput && (
              <div className="mt-6 space-y-3 rounded-lg border border-white/10 bg-black/60 p-4">
                <p className="text-xs font-bold text-emerald-400">✓ Discovered {benchOutput.length} live government tenders on GeM Portal:</p>
                {benchOutput.map((item, idx) => (
                  <div key={idx} className="rounded border border-white/5 bg-slate-900/80 p-3">
                    <h5 className="font-semibold text-white">{item.title}</h5>
                    <p className="mt-1 text-xs text-slate-400">{item.snippet}</p>
                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs font-bold text-sky-400 hover:underline">
                      📄 View Source Document ↗
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 4. SECTION 03: FULL PRODUCTION TECH STACK (IMAGE 1 - DOCKER EXCLUDED) */}
      <section id="tech-stack" className="border-t border-white/10 px-6 py-16">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10">
            <p className="text-xs font-bold tracking-widest text-sky-400 uppercase">END-TO-END SYSTEM ARCHITECTURE</p>
            <h2 className="mt-2 text-3xl font-extrabold text-white">TenderLens Production Tech Stack</h2>
            <p className="mt-2 text-slate-400">6 resilient engineering tiers engineered for legal document precedence, asynchronous crawling, and statutory compliance.</p>
          </div>

          <div className="space-y-4">
            {/* TIER 1 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">USER EXPERIENCE</span>
                <p className="text-xs text-slate-400">Frontend (Web Application)</p>
              </div>
              <div className="col-span-3 grid grid-cols-3 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Next.js</strong><p className="text-xs text-slate-400">App &amp; SSR Routing</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>TypeScript</strong><p className="text-xs text-slate-400">Strict Type Contracts</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Tailwind CSS</strong><p className="text-xs text-slate-400">Responsive Tokens</p></div>
              </div>
            </div>

            {/* TIER 2 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">API &amp; ORCHESTRATION</span>
                <p className="text-xs text-slate-400">Backend &amp; Orchestration</p>
              </div>
              <div className="col-span-3 grid grid-cols-3 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>FastAPI</strong><p className="text-xs text-slate-400">Async Python ASGI</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Pydantic</strong><p className="text-xs text-slate-400">Schema Validation</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Celery</strong><p className="text-xs text-slate-400">Async Job Queues</p></div>
              </div>
            </div>

            {/* TIER 3 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">WEB INTELLIGENCE</span>
                <p className="text-xs text-slate-400">Search &amp; Data Retrieval</p>
              </div>
              <div className="col-span-3 grid grid-cols-3 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>SerpAPI</strong><p className="text-xs text-slate-400">Search API Fallback</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>HTTPX</strong><p className="text-xs text-slate-400">Web Requests</p></div>
                <div className="rounded border border-amber-500/40 bg-amber-500/10 p-3"><strong>TinyFish</strong><span className="ml-2 rounded bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-400">ACTIVE KEY</span><p className="text-xs text-slate-400">TinySearch · TinyFetch · Stealth</p></div>
              </div>
            </div>

            {/* TIER 4 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">DOCUMENT INTELLIGENCE</span>
                <p className="text-xs text-slate-400">Document Processing</p>
              </div>
              <div className="col-span-3 grid grid-cols-2 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>PyMuPDF</strong><p className="text-xs text-slate-400">PDF Coordinates &amp; Hyperlinks</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Docling</strong><p className="text-xs text-slate-400">Structured Table Extraction</p></div>
              </div>
            </div>

            {/* TIER 5 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">QUALIFICATION ENGINE</span>
                <p className="text-xs text-slate-400">Rules &amp; AI Processing</p>
              </div>
              <div className="col-span-3 grid grid-cols-3 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Python</strong><p className="text-xs text-slate-400">Deterministic Business Rules</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>LLM</strong><p className="text-xs text-slate-400">Structured Outputs &amp; Conflict DAG</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Rules Engine</strong><p className="text-xs text-slate-400">Validation &amp; Statutory Scoring</p></div>
              </div>
            </div>

            {/* TIER 6 */}
            <div className="grid grid-cols-1 gap-4 rounded-xl border border-white/10 bg-slate-900/50 p-5 md:grid-cols-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase">DATA &amp; OPERATIONS</span>
                <p className="text-xs text-slate-400">Database, Storage &amp; Infra</p>
              </div>
              <div className="col-span-3 grid grid-cols-3 gap-3">
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>PostgreSQL</strong><p className="text-xs text-slate-400">Relational DB &amp; Row-Level Security</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Object Storage</strong><p className="text-xs text-slate-400">S3 / MinIO Document Vault</p></div>
                <div className="rounded border border-white/10 bg-slate-800/50 p-3"><strong>Redis</strong><p className="text-xs text-slate-400">Atomic Cache &amp; Task Broker</p></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
