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

> **Rule**: We only write and modify backend code, intelligence layers, and engine verification logic. We do not touch frontend UI or database schemas directly; instead, we expose clean FastAPI endpoints matching [`contracts/schema.py`](file:///d:/softwares/Tenderlens/TenderLens/contracts/schema.py).

---

## 2. Overall Project Development Plan

### Milestone 1: Environment & Project Scaffolding
- [x] Initialized UV package environment (`uv init --app --vcs none .`)
- [x] Python pinned to `>=3.11` (Python 3.12 active via `.python-version`)
- [x] Shared data contracts created in [`contracts/schema.py`](file:///d:/softwares/Tenderlens/TenderLens/contracts/schema.py)
- [x] Secret & artifact hygiene: comprehensive `.gitignore` and `.env.example`
- [x] Agent tracking systems established: `MOhit-Agents.md` and `arshit-agents.md`

### Milestone 2: Web Intelligence Layer (TinyFish Integration) — *Our Scope*
- [ ] Install dependencies via UV (`fastapi`, `uvicorn`, `httpx`, `pymupdf`, `pydantic`, `pydantic-settings`)
- [ ] Build `backend/services/tinyfish_service.py`:
  - **Stage 1 — TinySearch ($0.00/call)**: Query `site:gem.gov.in` and Indian PSU tenders by location `IN`.
  - **Stage 2 — TinyFetch Recursive ($0.00/call)**: Fetch clean Markdown and auto-extract child ATC URLs with `links: true`.
  - **Stage 3 — TinyAgent Stealth SSE ($0.016/step)**: Autonomous browser fallback for JS-heavy portals with streaming SSE feedback.

### Milestone 3: Document Intelligence Layer — *Our Scope*
- [ ] Build `backend/services/document_processor.py`:
  - PyMuPDF structured page-by-page extraction.
  - Clause heading regex parsing (`Clause X.X`, `Section Y`, `Sl No`).
  - Table detection and bounding-box preservation for exact legal page citations.

### Milestone 4: Hybrid Qualification Engine — *Our Scope*
- [ ] Build `backend/engine/deterministic_gatekeeper.py`:
  - Strict Python math (3-year average turnover check).
  - Public Procurement Policy for MSEs Order, 2012 / GFR Rule 173(i) exemption logic.
  - EMD exemption verification under GFR Rule 170.
  - DPIIT Public Procurement (Preference to Make in India) Order 2017 local content classification.
- [ ] Build `backend/engine/qualification_engine.py`:
  - Structured LLM clause auditor returning Pydantic `QualificationScorecard`.
  - Safe Uncertainty triage: Flag conflicting buyer ATC clauses as `AMBIGUOUS_MANUAL_REVIEW`.

### Milestone 5: FastAPI Router & API Endpoints — *Our Scope*
- [ ] Expose REST & SSE endpoints in `backend/main.py`:
  - `POST /api/v1/tenders/search` -> TinySearch tender discovery.
  - `POST /api/v1/tenders/fetch` -> TinyFetch tender & linked ATC extraction.
  - `POST /api/v1/audit/evaluate` -> Full hybrid qualification engine evaluation.
  - `GET /api/v1/audit/stream/{task_id}` -> Live SSE execution progress for Arshit's frontend.

### Milestone 6: Handshake with Arshit & Argon
- [ ] Arshit consumes API endpoints and renders the interactive Next.js scorecard.
- [ ] Arshit binds PostgreSQL database for saving bidder profiles and audit histories.
- [ ] Argon tests against the 50-tender GeM evaluation benchmark to verify ≥85% precision and ≥80% recall.

---

## 3. Progress Log & Work History

| Date / Timestamp | Milestone / Action | Details & Notes |
| :--- | :--- | :--- |
| **2026-10-24 13:06** | Repo Sync & Push | Pushed presentation PDF, `.gitignore`, `.env.example`, `contracts/schema.py`, and `research/README.md` to `origin/main`. |
| **2026-10-24 13:10** | UV Project Initialization | Initialized Python project via `uv init --app --vcs none .` in `d:\softwares\Tenderlens\TenderLens`. |
| **2026-10-24 13:13** | Python Version Pinning | Configured `pyproject.toml` to `requires-python = ">=3.11"` and pinned Python version to `3.12` via `.python-version`. |
| **2026-10-24 13:15** | Memory & Plan Tracking | Created `MOhit-Agents.md` and `arshit-agents.md` to cleanly delineate responsibilities and maintain context. |
| **2026-10-24 13:19** | TinyFish Test Script | Created `scripts/test_tinyfish_key.py` to securely validate `TINYFISH_API_KEY` from `.env` without exposing secrets. Tested against Search and Fetch endpoints. |
| **2026-10-24 13:24** | Repomix Codebase Packing | Generated `single.xml` via Repomix, packing repository files into a unified XML context (excluding `.txt` and sensitive keys). |
| **2026-10-24 13:43** | Playwright Report Extraction | Created `scripts/extract_gemini_report.py` and extracted 87,123 characters of Argon's deep-dive research into `research/argon_report.md`. |
| **2026-10-24 13:45** | Final Implementation Plan | Synthesized `argon.md`, `research/argon_report.md`, and hackathon requirements into `FINAL_IMPLEMENTATION_PLAN.md`. |

---

## 4. Current State & Next Actions

- **Current State**: `FINAL_IMPLEMENTATION_PLAN.md` created. `research/argon_report.md` extracted via Playwright. Repository ready for remote synchronization and backend implementation.
- **Next Step**: Install core backend dependencies via `uv add` (`fastapi`, `uvicorn`, `httpx`, `pymupdf`, `pydantic-settings`, `python-dotenv`, `sse-starlette`) and implement `backend/services/tinyfish_service.py` adhering to production specifications.


