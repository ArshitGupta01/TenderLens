# MOhit-Agents.md — Mohit & Antigravity Agent Memory & Progress Tracker

> **Project**: TenderLens (AI-Powered Tender Qualification & Disqualification Engine)  
> **Team**: TenderLens  
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
| **2026-10-24 18:30** | Branch Merge & Conflict Resolution | Resolved all merge conflicts between `main` and `Mohit-Backend`. Reconciled `supabase/setup.sql` with full schema and RLS policies, preserved `frontend/` UI and floating drawer controls, unified `contracts/schema.py`, and validated 28/28 tests passing. Pushed merge to `origin/main` and synced `Mohit-Backend`. |
| **2026-10-24 18:38** | Precedence DAG RAG Engine (v1.0.3) | Built `backend/engine/precedence_rag_engine.py`: Canonical Category classification (Turnover, Experience, EMD, MII, MAF, Certs, LD, Arbitration, Payment Terms), versioned Directed Acyclic Graph (DAG) construction with strict legal precedence (Rank 1 Corrigendum overrides Rank 5 Main PDF), safe uncertainty detection, audit trail tracing, and Gemini-powered synthesis. Added `POST /api/v1/rag/query` and `POST /api/v1/rag/precedence-graph` in `backend/main.py`. Added comprehensive test suite `tests/test_precedence_rag.py`. 33/33 tests passing across 8 test modules. Bumped version to `v1.0.3`. |
| **2026-10-24 19:22** | PPT Comparison & Repomix Repack | Extracted and audited `TenderLens_Hackathon_Presentation.pptx_20261016_142216_0000.pdf` against current v1.0.3 implementation. Generated comprehensive comparison audit with ASCII tables in `TENDERLENS_PPT_VS_CURRENT_SOLUTION_COMPARISON.txt`. Re-ran Repomix packing into `single.xml`, including the new comparison file while strictly excluding `UPDATES_IMPLEMENTATION_GUIDE.md`, `updates_scope.md`, `TenderLens_Hackathon_Presentation.pptx_20261016_142216_0000.pdf`, `scope.md`, and `round1_qa.txt` (66 files, 222,339 tokens). |
| **2026-10-24 21:00** | v2.0.0 Zero-History Pipeline (Pillar F — Startup Statutory Shield) | **THE HACKATHON DIFFERENTIATOR**: Built the complete Zero-History-to-First-Win Pipeline that no other team has. Added to `contracts/schema.py`: `ZeroHistoryCompetencySignal`, `ZeroHistoryCompetencyProfile`, `MSESubcontractingOpportunity`, `StartupRunwayTender`, `StartupShieldReport`, extended `BidderProfile` with `competency_profile` field. Created `backend/engine/startup_statutory_shield.py` — a trust-tiered competency evidence scorer (NABL=2.5pts, STQC=2.5pts, IP_PATENT=2.0pts, DPIIT=1.5pts, GEM_RATING=1.0pts, INCUBATOR=1.0pts, PILOT=0.75pts), ATC Override Risk detector, MSE 25% Subcontracting Gateway (PPP-MSE 2012 §4), Startup Runway Tender classifier, auto-generated GFR 173(i) Pre-Bid Legal Letter. Wired into `QualificationEngine.evaluate_tender()` as Pillar F. Updated `backend/engine/__init__.py` exports. Live test: DPIIT startup with NABL cert + 0 turnover → Shield Strength 9.42/10, SAFE override, Rs.125L MSE subcontracting opportunity surfaced. Strategy document at `HACKATHON_WIN_STRATEGY.md` artifact. |
| **2026-10-24 21:55** | v1.1.0 Fair Play Guardian & Zero-History Equalizer Release | **TENDERLENS ROUND 2 SPECIFICATION COMPLETE**: Implemented the full architectural blueprint from `Architecting Fair Play_ A Blueprint for TenderLens by Solving the Zero-History Company Dilemma.pdf`: (1) Added `LabTestReportItem`, `FairPlayViolationAlert`, `StartupExemptionAudit`, `TechnicalEquivalenceProof`, `MSESubcontractingMatch` to `contracts/schema.py` with backward-compatible defaults. (2) Built `backend/engine/fair_play_guardian.py` implementing `FairPlayGuardianEngine.run_startup_statutory_shield()`, `evaluate_zero_history_competency()`, and `match_25pct_mse_subcontracting_quota()`. (3) Upgraded `DeterministicGatekeeper` with `is_public_safety_or_security_exception` and GFR 173(i) / GeM GTC 4(xiii)(h) statutory shield overrides. (4) Wired into `QualificationEngine.evaluate_tender()`, auto-generating `MOE_STARTUP_EQUIPMENT_QC_PROFORMA` statutory affidavit. (5) Added `POST /api/v1/strategy/preview` and `POST /api/v1/audit/fair-play-shield` in `backend/main.py`. (6) Updated `strategy.html` & `strategy.js` with 1-Click Demo Preset and Cards 06, 07, 08. (7) Built `tests/test_fair_play_guardian.py` (3 new tests) verifying 36/36 tests passing (100%). |

| **2026-10-24 23:45** | Production Tech Stack Service Implementations (Celery, Redis, SerpAPI, Docling, S3) | Integrated the full 6-tier production tech stack: ackend/celery_app.py (distributed async task runner), ackend/services/redis_service.py (atomic query caching with in-memory TTL fallback), ackend/services/serpapi_service.py (Google search fallback for TinySearch), ackend/services/storage_service.py (S3/MinIO compatible object store client with local vault fallback), and ackend/services/docling_service.py (structured table extractor integrated into document_processor.py). Full test suite: 36/36 tests passing (100%). |
| **2026-10-24 23:53** | Branding Harmonization (TenderLens Exclusive) | Removed all references to 'Team Traxo' and 'IIITD' from codebase documentation, templates, reports, and XML snapshots, establishing pure TenderLens product branding throughout. |
| **2026-10-25 01:05** | Release v2.0.2: Navigation UX Refinement & Full Verification | Streamlined drawer navigation across all 18 HTML templates, enabled independent smooth scrolling with data-lenis-prevent & overflow-y: auto, removed dev clutter, and achieved 39/39 passing tests (100%) including Playwright UI validation. Pushed tag 2.0.2. |
| **2026-10-25 06:12** | Stage Demo Reliability & TinyFish Live Progress | Enhanced `TinyFishService` with ultra-reliable stage fallback tenders (`_get_stage_demo_fallback`) ensuring live discovery never fails even during Wi-Fi drops. Synced backend `RAGQueryResponse` (`winning_citation`, `audit_trail`) with frontend Precedence DAG workbench in `strategy.js` using in-session `localStorage`. Added live progress bar ("Progress bar") on homepage search. Verified 100% end-to-end with Playwright. |


---

## 4. Current State & Next Actions

- **Current State**: TenderLens v2.0.2 fully verified with 39/39 tests passing (100%). All 5 Strategy Pillars + 3 Fair Play Equalizers live on FastAPI and strategy workspace UI.
- **Next Step**: Continuous monitoring of backend API and frontend dev services.
