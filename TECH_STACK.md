# TenderLens — Tech Stack & Working Map

> Concise project memory reference · Reviewed 2026-10-24

## One-line summary

TenderLens is a **static multi-page procurement UI** backed by a **Python
FastAPI tender-intelligence API**, combining deterministic eligibility checks,
document precedence, optional LLM review, and Supabase account persistence.

## Stack at a glance

| Layer | Technology |
|---|---|
| UI | Semantic HTML, Vanilla ES6+ JavaScript, responsive CSS |
| Visual components | React 19 + TypeScript, inline SVG, esbuild |
| Styling/utilities | CSS custom properties, Tailwind config, `clsx`, `tailwind-merge` |
| Backend | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| Async/API | `httpx`, SSE via `sse-starlette` |
| Documents | PyMuPDF (`pymupdf`) |
| Web intelligence | TinyFish Search/Fetch/Agent; Tavily fallback |
| AI review | Google Gemini SDK with LangChain fallback |
| Auth/database | Supabase Auth + PostgreSQL + PostgREST + RLS |
| Hosting | Vercel static deployment; FastAPI local/API deployment |
| Testing | Pytest, pytest-asyncio, FastAPI TestClient, Node checks, TypeScript |
| Package management | `uv`/`uv.lock` for Python; npm/package-lock for frontend tooling |

## Runtime architecture

```text
Browser
  ├─ HTML pages + app.js/auth.js/strategy.js/theme.js
  ├─ React/TS doodle hero bundle
  └─ JSON/SSE requests
        ↓
FastAPI: backend/main.py
  ├─ TinyFish/Tavily discovery and fetching
  ├─ PyMuPDF clause extraction
  ├─ deterministic_gatekeeper.py
  ├─ precedence_rag_engine.py
  ├─ qualification_engine.py
  ├─ five strategy engines
  ├─ fair_play_guardian.py
  └─ Supabase service
        ↓
Supabase Auth + PostgreSQL + Row-Level Security
```

## Frontend map

- `index.html` + `app.js`: landing page, illustrative report, local sample
  explorer/checklist/profile, optional live search.
- `strategy.html` + `strategy.js`: Strategy Studio, presets, gate results,
  legal pack, consortium matching, compliance CSV/affidavits, EMD optimizer,
  forensics, and RAG workbench.
- `signin.html`, `signup.html`, `account.html`, `saved-tenders.html` +
  `auth.js`: Supabase sign-in, profile sync, and explicitly saved live links.
- `styles.css`: themes, responsive layouts, accessibility, animations.
- `theme.js`: saved light/dark preference.
- `components/`: React/TypeScript doodle hero/footer; bundled with esbuild.
- `frontend/`: mirrored static frontend used by the FastAPI/Vercel workflows.

**Local-only:** sample searches, filters, presets, checklists, and sample
interactions.  
**Cloud-backed:** signed-in bidder profile, explicitly saved official notice
links, and saved audit records.

## Backend map

- `backend/main.py`: FastAPI app, request models, routes, SSE, static mounting.
- `backend/config.py`: `.env` settings, provider keys, CORS, portal allowlist,
  crawl limits, cache paths.
- `backend/services/tinyfish_service.py`: search, batch fetch, recursive ATC
  discovery, Tavily fallback.
- `backend/services/document_processor.py`: PDF text/blocks, tables, hidden
  links, bounding boxes, precedence ranks.
- `backend/services/supabase_service.py`: JWT-scoped Supabase access and
  profile/audit persistence.
- `backend/engine/deterministic_gatekeeper.py`: turnover, experience, EMD,
  MII local content, OEM MAF, certifications, CPWD 80/50/40.
- `backend/engine/precedence_rag_engine.py`: ranked clause resolution and
  ambiguity/manual-review handling.
- `backend/engine/qualification_engine.py`: criteria extraction, optional
  Gemini review, scorecard and strategy synthesis.
- `backend/engine/prebid_legal_generator.py`: pre-bid challenge pack.
- `backend/engine/consortium_matchmaker.py`: quantified capability gaps.
- `backend/engine/compliance_matrix_engine.py`: matrix, CSV, affidavits.
- `backend/engine/emd_capital_optimizer.py`: cash lock-up and instrument choice.
- `backend/engine/competitor_forensics.py`: authority-specific rejection risks.
- `backend/engine/fair_play_guardian.py`: startup shield, zero-history proof,
  MSE quota, and fair-play alerts.

## Main API flow

### Live audit

```text
POST /api/v1/audit/evaluate
  → TinyFetch tender + linked ATCs/corrigenda
  → create clause chunks
  → assign precedence ranks
  → extract explicit criteria
  → run deterministic gates
  → optional Gemini conflict review
  → return evidence-backed QualificationScorecard
```

### Strategy preview

```text
POST /api/v1/strategy/preview
  → bidder profile + explicit tender criteria
  → deterministic gates
  → five strategy pillars
  → startup/fair-play equalizer
  → StrategyToolkitResponse
```

### Other important routes

```text
POST /api/v1/tenders/search
POST /api/v1/tenders/fetch
POST /api/v1/rag/query
POST /api/v1/rag/precedence-graph
GET  /api/v1/strategy/forensics
GET  /api/v1/audit/stream/{task_id}
GET  /healthz
```

## Core domain rule: document precedence

```text
1. Latest corrigendum
2. Earlier corrigenda
3. Buyer ATC/RFP PDF
4. Buyer text ATC
5. Main tender PDF
```

Lower rank number wins for the same requirement. Same-rank conflicts and legal
uncertainty become `AMBIGUOUS_MANUAL_REVIEW`; the system should not guess.

## Supabase data

Defined in `supabase/setup.sql`:

- `profiles`: bidder identity, MSME/startup status, turnover, experience,
  certifications, local content, projects.
- `saved_tenders`: official links explicitly saved by a user.
- `tender_audits`: scorecard JSON and recommendation history.

All tables use RLS with owner checks equivalent to:

```sql
auth.uid() = user_id
```

Browser code may use only the public Supabase key. Service-role and provider
secrets stay server-side in `.env`.

## Run locally

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn backend.main:app --reload --port 8000
```

Optional static server:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Useful checks:

```powershell
uv run pytest -q
npm run typecheck
node --check app.js
node --check auth.js
node --check strategy.js
node --check theme.js
```

## Remember

- This is currently **static frontend + FastAPI**, not an active Next.js app.
- Sample reports, presets, partner archetypes, and recommendations are
  illustrative; verify official tender documents before acting.
- Deterministic math handles explicit values; LLM output is supplementary.
- Preserve source-linked evidence, precedence ordering, human review for
  ambiguity, Supabase Auth, and RLS.
- Next major gaps: production OAuth verification, upload consent/retention,
  multi-PDF audit flow, and reconciliation of older Next.js/Docker plans.

## Source references

- [`README.md`](./README.md)
- [`PROJECT_INFO.md`](./PROJECT_INFO.md)
- [`backend/main.py`](./backend/main.py)
- [`contracts/schema.py`](./contracts/schema.py)
- [`supabase/setup.sql`](./supabase/setup.sql)
- [`docs/API.md`](./docs/API.md)
- [`docs/DATABASE.md`](./docs/DATABASE.md)
- [`docs/SECURITY.md`](./docs/SECURITY.md)
