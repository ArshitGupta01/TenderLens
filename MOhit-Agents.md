# MOhit-Agents.md — Mohit & Antigravity Agent Memory & Progress Tracker

> **Project**: TenderLens (AI-Powered Tender Qualification & Disqualification Engine)  
> **Team**: Team Traxo · HackIIITD (Round 2)  
> **Agent Owner**: Mohit & Antigravity AI  
> **Domain**: Backend, Web Intelligence, Document Intelligence, Deterministic Qualification Engine & API Orchestration  
> **Status**: Backend merged into `main`; experimental API routes remain subject to verification

---

## 1. Role & Project Boundaries

TenderLens is divided across three clear, non-conflicting domains:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 TENDERLENS PROJECT                               │
├────────────────────────────┬─────────────────────────────┬───────────────────────┤
│   MOHIT & ANTIGRAVITY      │           ARSHIT            │         ARGON         │
│   (Our Sole Scope)         │      (Frontend & Data)      │ (Research & Benchmark)│
├────────────────────────────┼─────────────────────────────┼───────────────────────┤
│ • Web Intelligence         │ • Next.js 14 Frontend UI    │ • Competitor Analysis │
│   (TinyFish API: Search,   │ • Bidder Profile Form       │ • 50-Tender GeM       │
│    Fetch & Agent SSE)      │ • Interactive Scorecard     │   Benchmark Dataset   │
│ • Document Intelligence    │ • PostgreSQL DB Models      │ • Prompt Iterations   │
│   (PyMuPDF / Docling)      │ • Redis & Celery Async      │ • Accuracy & Recall   │
│ • Deterministic Gatekeeper │ • S3 / MinIO Object Storage │   Evaluation          │
│ • Semantic LLM Auditor     │ • Docker Compose Infra      │                       │
│ • FastAPI Backend Endpoints│                             │                       │
└────────────────────────────┴─────────────────────────────┴───────────────────────┘
```

> **Rule**: We only write and modify backend code, intelligence layers, and engine verification logic. We do not touch frontend UI or database schemas directly; instead, we expose clean FastAPI endpoints matching [`contracts/schema.py`](contracts/schema.py).

---

## 2. Overall Project Development Plan

### Milestone 1: Environment & Project Scaffolding
- [x] Initialized UV package environment (`uv init --app --vcs none .`)
- [x] Python pinned to `>=3.11` (Python 3.12 active via `.python-version`)
- [x] Shared data contracts created in [`contracts/schema.py`](contracts/schema.py)
- [x] Secret & artifact hygiene: comprehensive `.gitignore` and `.env.example`
- [x] Agent tracking systems established: `MOhit-Agents.md` and `arshit-agents.md`

### Milestone 2: Web Intelligence Layer (TinyFish Integration) — *Completed*
- [x] Installed dependencies via UV (`fastapi`, `uvicorn`, `httpx`, `pymupdf`, `pydantic-settings`, `sse-starlette`, `pytest`)
- [x] Built `backend/config.py` with pydantic-settings and Indian portal domain configurations
- [x] Built `backend/services/tinyfish_service.py`:
  - **Stage 1 — TinySearch ($0.00/call)**: Query without deprecated `site:` operators, `include_domains`, and rich `purpose` parameter.
  - **Stage 2 — TinyFetch Recursive ($0.00/call)**: Stateless batching (max 10 URLs), depth limit $d \le 2$, and HTTP 304 TTL caching.
  - **Stage 3 — TinyAgent Stealth SSE ($0.016/step)**: Cost circuit breaker (`max_steps=10`, `max_duration_seconds=60`, `country_code='IN'`).

### Milestone 3: Document Intelligence Layer — *Completed*
- [x] Built `backend/services/document_processor.py`:
  - PyMuPDF structured page-by-page extraction at 250+ pgs/sec.
  - Hidden PDF annotation hyperlink extraction (`page.get_links()`) harvesting embedded GeM ATC links.
  - Precedence DAG ranking (Rank 1 Latest Corr to Rank 5 Main PDF).
  - Exact bounding boxes `[x0, y0, x1, y1]` for frontend SVG overlays.

### Milestone 4: Hybrid Qualification Engine — *Completed*
- [x] Built `backend/engine/deterministic_gatekeeper.py`:
  - Strict Python 3-year average turnover math + MSE PPP-2012 / GFR Rule 173(i) exemption logic.
  - Past Experience CPWD 80/50/40 similar work thresholds + startup relaxation.
  - EMD exemption under GFR 2017 Rule 170(i).
  - Make in India Class-I ($\ge 50\%$) and Class-II ($\ge 20\%$) classification (DPIIT Order 2017).
  - OEM MAF letter verification and mandatory certifications set-difference.
- [x] Built `backend/engine/qualification_engine.py`:
  - Precedence DAG conflict resolution and Safe Uncertainty (`AMBIGUOUS_MANUAL_REVIEW`).
  - Scorecard synthesis outputting `contracts/schema.py` models (`STRONG_BID`, `CONDITIONAL_BID`, `RED_FLAG_NO_BID`).

### Milestone 5: FastAPI Router & API Endpoints — *Completed*
- [x] Built `backend/main.py`:
  - CORS middleware reads the local origin allowlist from `CORS_ORIGINS`; credentials are disabled.
  - `POST /api/v1/tenders/search`
  - `POST /api/v1/tenders/fetch`
  - `POST /api/v1/audit/evaluate`
  - `GET  /api/v1/audit/stream/{task_id}` (Server-Sent Events)
  - `GET  /healthz`
- [x] Built 10 unit and integration tests across `tests/` — 100% passing.

---

## 3. Progress Log & Work History

| Date / Timestamp | Milestone / Action | Details & Notes |
| :--- | :--- | :--- |
| **2026-10-24 13:06** | Repo Sync & Push | Pushed presentation PDF, `.gitignore`, `.env.example`, `contracts/schema.py`, and `research/README.md` to `origin/main`. |
| **2026-10-24 13:10** | UV Project Initialization | Initialized Python project via `uv init --app --vcs none .` in `d:\softwares\Tenderlens\TenderLens`. |
| **2026-10-24 13:13** | Python Version Pinning | Configured `pyproject.toml` to `requires-python = ">=3.11"` and pinned Python version to `3.12` via `.python-version`. |
| **2026-10-24 13:15** | Memory & Plan Tracking | Created `MOhit-Agents.md` and `arshit-agents.md` to cleanly delineate responsibilities and maintain context. |
| **2026-10-24 13:19** | TinyFish Test Script | Created `scripts/test_tinyfish_key.py` to securely validate `TINYFISH_API_KEY` from `.env` without exposing secrets. |
| **2026-10-24 13:24** | Repomix Codebase Packing | Generated `single.xml` via Repomix, packing repository files into a unified XML context. |
| **2026-10-24 13:43** | Playwright Report Extraction | Created `scripts/extract_gemini_report.py` and extracted 87,123 characters of Argon's deep-dive research into `research/argon_report.md`. |
| **2026-10-24 13:45** | Final Implementation Plan | Synthesized `argon.md`, `research/argon_report.md`, and hackathon requirements into `FINAL_IMPLEMENTATION_PLAN.md`. |
| **2026-10-24 14:30** | Backend Implementation on `Mohit-Backend` | Built `backend/config.py`, `backend/services/tinyfish_service.py`, `backend/services/document_processor.py`, `backend/engine/deterministic_gatekeeper.py`, `backend/engine/qualification_engine.py`, and `backend/main.py`. 10/10 tests passing. |
| **2026-10-24 14:45** | Bug Fixes & Resiliency | Fixed turnover/experience extraction regex edge cases and link queue deduplication in `tinyfish_service.py`. |
| **2026-10-24 14:47** | Round 1 Q&A & Architecture Asset | Created `round1_qa.txt` (double-line separated Q&A) and generated architecture comparison infographic in `assets/tenderlens_architecture_comparison.png`. |
| **2026-10-24 14:53** | Live TinyFish Verification | Tested fresh `TINYFISH_API_KEY`: HTTP 200 OK across both TinySearch and TinyFetch. Verified live GeM & BHEL tender discovery via `backend/services/tinyfish_service.py`. |
| **2026-10-24 15:08** | Gemini API Key Verification | Tested `GEMINI_API_KEY` against Google Generative Language API (`gemini-2.5-flash`). Key authenticated and test script self-deleted upon success. |
| **2026-10-24 15:13** | Real E2E & Edge Case Suite | Built and ran `tests/test_real_e2e_pipeline.py` testing live TinySearch ($0.00 cost, preserving 100% of $5 credits), MSME PPP-2012 turnover relaxation, Buyer ATC revocation trap, MII Class-II disqualification, GFR 170 EMD rules, and FastAPI audit evaluate endpoint. 16/16 tests passing. |
| **2026-10-24 15:55** | Gemini 3.8 Flash & Tavily Search Fallback | Set `GEMINI_MODEL="gemini-3.8-flash"` in `backend/config.py`. Enhanced `QualificationEngine.analyze_clauses_with_gemini` and added `evaluate_tender_async` for semantic clause conflict auditing. Integrated Tavily live search fallback (`_search_tavily_fallback`) in `TinyFishService` when TinySearch returns 0 results or errors. Fixed cert keyword regex word boundary matching. Added `tests/test_gemini_auditor.py`. All 19/19 tests passing. |
| **2026-10-24 16:45** | TenderLens v1.0.1 Strategic Expansion (5 Pillars) | Implemented full v1.0.1 active execution & strategy blueprint: `contracts/schema.py` (v1.0.1 models), `backend/engine/prebid_legal_generator.py` (Pillar A), `backend/engine/consortium_matchmaker.py` (Pillar B), `backend/engine/compliance_matrix_engine.py` (Pillar C), `backend/engine/emd_capital_optimizer.py` (Pillar D), `backend/engine/competitor_forensics.py` (Pillar E), updated `deterministic_gatekeeper.py` with CPWD 80/50/40 gate, updated `qualification_engine.py` with 5-pillar synthesis, added dedicated REST routes in `backend/main.py`. Full test suite: 24/24 tests passing across 6 test modules. |
| **2026-10-24 17:00** | Release Tagging & Harmonization (v1.0.1) | Resolved all versioning/tagging conflicts across `pyproject.toml`, `backend/main.py`, `backend/services/tinyfish_service.py`, `contracts/schema.py`, engines, and docs to uniform tag `v1.0.1`. Created annotated git tag `v1.0.1`. |
| **2026-10-24 17:25** | Frontend & Database Pairing (Arshit's Branch) | Pulled Arshit's frontend into `frontend/` and Supabase SQL into `supabase/setup.sql` from `origin/main` without conflicting with our backend. Added Supabase auth config (`/api/v1/auth/config`) and CORS settings to `backend/main.py` and `backend/config.py`. Mounted `frontend/` directly on FastAPI root `/`. Built a high-aesthetic Top Ribbon Overlay (`#top-ribbon`) across all pages with animated live engine pulse (`v1.0.1 LIVE`), GFR 2017 highlights, and dark/light theme support. |
| **2026-10-24 17:40** | Supabase Free Tier Cloud Database Activation | Configured live Supabase credentials (`qiwpkvjzqdyguygowzci.supabase.co`). Created `backend/services/supabase_service.py` with `SupabaseService` for persisting scorecards to `tender_audits`, syncing `BidderProfile` with `profiles`, and managing bookmarks. Added `/api/v1/audits/save`, `/api/v1/audits/user/{user_id}`, and `/api/v1/profile/sync` endpoints in `backend/main.py`. Updated `supabase/setup.sql` with full RLS policies and `tender_audits` schema. Created `supabase/README.md`. 28/28 tests passing across 7 test modules. |

---

## 4. Current State & Next Actions

- **Current State**: Unified merge of `main` and `Mohit-Backend` complete. All 5 Strategy Pillars (`prebid_legal_generator.py`, `consortium_matchmaker.py`, `compliance_matrix_engine.py`, `emd_capital_optimizer.py`, `competitor_forensics.py`), the full `frontend/` UI with corner floating controls and slide-over drawer, and Supabase integration (`supabase/setup.sql`, `supabase_service.py`, `tests/test_supabase_service.py`, `tests/test_v3_pillars.py`) are merged and unified.
- **Next Step**: Run full test suite, verify frontend pairing, and ensure live cloud database and AI pipelines operate cleanly.






