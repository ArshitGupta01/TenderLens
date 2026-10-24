# MOhit-Agents.md — Mohit & Antigravity Agent Memory & Progress Tracker

> **Project**: TenderLens (AI-Powered Tender Qualification & Disqualification Engine)  
> **Team**: Team Traxo · HackIIITD (Round 2)  
> **Agent Owner**: Mohit & Antigravity AI  
> **Domain**: Backend, Web Intelligence, Document Intelligence, Deterministic Qualification Engine & API Orchestration  
> **Status**: Active / Initialized with UV (Python 3.12)  

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
  - CORS middleware enabled for `http://localhost:3000` (Arshit's Next.js frontend).
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

---

## 4. Current State & Next Actions

- **Current State**: TinyFish API is 100% authenticated and operational. Live Indian procurement search retrieves live GeM/BHEL PDFs in real time. Backend engine is fully verified.
- **Next Step**: Support Arshit with frontend integration (connecting UI to FastAPI endpoints) and support Argon with the 50-tender evaluation benchmark.





