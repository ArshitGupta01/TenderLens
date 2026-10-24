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

---

## 4. Current State & Next Actions

- **Current State**: `main` contains the earlier Mohit backend integration, the five lightweight strategy helpers, and the entered-value Strategy preview. It does not contain every update from the current remote `Mohit-Backend` head; see Section 9. External provider access has not been re-verified in this update.
- **Next Step**: Review the branch-only Supabase persistence and expanded strategy work. Port only after adding authenticated-subject checks and preserving row-level security; then run the current backend suite.

## 5. Merge and website connection — 2026-10-24

- [x] Merged the earlier `Mohit-Backend` API, document processor, and qualification engine into `main`.
- [ ] The latest remote `Mohit-Backend` branch has additional commits that are not in `main`; this does not mean the entire current branch is merged.
- [x] Added local CORS origins for preview ports 3000 and 4177, controlled through `CORS_ORIGINS`, with credentialed requests disabled.
- [x] Connected the sample website's optional live-search form to `GET /healthz` and `POST /api/v1/tenders/search`. It submits only the search phrase and selected portal.
- [ ] Tender fetching and bidder scorecard evaluation are still not connected to the website; verify backend behavior against real source documents before production use.
- [ ] Re-run the backend suite and provider checks when a maintainer is ready to validate them; they were not run as part of this interface update.

## 6. Supabase public auth configuration — 2026-10-24

- [x] Added `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` settings to the existing `.env` configuration.
- [x] Added `GET /api/v1/auth/config`, which returns only those public client values and a configured flag. The endpoint does not expose a Supabase secret key, service-role key or database password.
- [ ] The Supabase project, email/Google providers, Postgres tables and redirect URLs still require the maintainer's credentials and dashboard setup.
- [ ] Next: validate the auth config response and RLS behavior against the configured project after setup.

## 7. Backend qualification updates merged — 2026-10-24

- Added configurable Gemini model selection and a Tavily live-search fallback.
- Tender evaluation now calls the asynchronous qualification engine with Gemini analysis enabled.
- Added Gemini auditor and real end-to-end pipeline test modules, plus implementation notes and scope documentation.
- The source branch reported 19 passing tests and live provider verification; those claims have not been independently re-run as part of this website update.

## 8. Mohit backend strategy integration — 2026-10-24

- Added the five strategy modules using the existing Python/FastAPI/Pydantic dependency set; no additional package was needed.
- Extended shared contracts with strategy output models, optional bidder EMD/capability inputs and a review-required marker.
- Added POST /api/v1/strategy/preview for manual values only, with no document fetch or persistence, and GET /api/v1/strategy/forensics for explicitly requested public-source search.
- Added input bounds for turnover, experience, local-content percentage, EMD and supporting values. EMD, exemption and compliance labels now retain a manual-review caveat.
- Public-source search now returns a clear configuration message instead of attempting an unauthenticated provider request when both TinyFish and Tavily keys are absent.
- Updated the audit summary so unknown rule status requests review instead of implying a firm recommendation. Removed unsupported legal and evidence-verification wording.
- No full test suite was run for this update. Python syntax compilation, API import/OpenAPI generation, a synthetic local preview response and page rendering passed. A sample-only provider request received HTTP 401 because the configured TinyFish value is a placeholder. The website/backend update was published to `main` at `527bf0b11f238b05acc5e47e0a196fbff95c4aa3`. Next: compare and safely port the remaining branch work, then verify backend behavior and responsive layouts.

## 9. Latest Mohit branch comparison — 2026-10-24

- Compared `origin/main` (`527bf0b11f238b05acc5e47e0a196fbff95c4aa3`) with `origin/Mohit-Backend` (`ed4cf8d9fa4351a0bbabf9395be25a07c6d9aa9d`). The histories diverge: `main` has 11 commits and `Mohit-Backend` has 4 commits beyond their common base.
- `main` has the five strategy concepts and a manual-value preview, but the branch contains expanded pillar implementations, additional audit/profile persistence through `backend/services/supabase_service.py`, related FastAPI routes, Supabase schema/tests, and a Supabase Python dependency.
- These persistence routes are not safe to merge unchanged: they accept a request-supplied `user_id`, and the service can fall back to a service-role key. Add bearer-token verification, bind operations to the verified JWT subject, and preserve row-level security before integrating persistence.
- This comparison was read-only; no backend source or database schema was changed.





