# TenderLens Project Information

> Repository-level orientation document for the current codebase.  
> Last reviewed: 2026-10-24.

## 1. What the project is

TenderLens is an experimental Team Traxo hackathon application for reviewing
Indian public-procurement tenders. Its central design principle is that a
tender is not a single document: the main bid, buyer-added terms, and
corrigenda form a precedence-ordered evidence set.

The current repository is a working **static multi-page frontend plus a
FastAPI backend**. Older planning documents describe a future Next.js,
PostgreSQL/Redis/MinIO, and Docker Compose architecture; those pieces are not
the current runtime implementation.

The project supports:

- A sample tender explorer and illustrative qualification report.
- Optional live notice discovery through TinyFish, with Tavily fallback.
- Tender-document fetching and clause extraction.
- A deterministic qualification gatekeeper for explicit numeric/statutory
  criteria.
- A precedence-aware RAG/conflict resolver.
- A five-pillar Strategy Studio preview.
- Supabase Auth, bidder-profile persistence, saved live-notice links, and
  audit persistence, subject to environment and Supabase configuration.

Sample tenders, report findings, presets, partner archetypes, and local
checklists are illustrative. They must not be treated as official tender
results or legal advice.

## 2. Runtime architecture

```text
Browser
  ├─ root static pages and scripts
  │    ├─ index.html / app.js
  │    ├─ strategy.html / strategy.js
  │    ├─ account.html, signin.html, signup.html, saved-tenders.html / auth.js
  │    └─ guide.html, privacy.html, terms.html, 404.html, 500.html
  │
  └─ optional frontend/ mirror of the static application
          │
          ├─ HTTP JSON and SSE
          ▼
FastAPI application: backend/main.py
  ├─ TinyFish/Tavily web intelligence
  ├─ PyMuPDF document processing
  ├─ deterministic gatekeeper
  ├─ qualification and five-pillar engines
  ├─ precedence DAG/RAG resolver
  └─ Supabase service using JWT-scoped PostgREST clients
          │
          ├─ TinyFish Search / Fetch / Agent services
          ├─ optional Gemini clause audit
          └─ Supabase Auth + PostgreSQL + RLS
```

The root pages are the primary local entry point. `frontend/` contains a
second copy used by the frontend/deployment workflow; changes to shared
static behavior should keep both copies synchronized.

## 3. Frontend

### Main pages

| Page | Purpose | Persistence/side effects |
|---|---|---|
| `index.html` | Landing page, illustrative report, sample tender desk, local checklist, optional live search | Sample interactions are browser-local; live search submits only after Search |
| `strategy.html` | Five-pillar Strategy Studio and precedence workbench | Preview values are submitted to the API; presets are local; profile loading requires sign-in |
| `signin.html` | Email/password, shared-demo UI, Google OAuth/Identity Services helpers | Supabase Auth |
| `signup.html` | Account creation, email confirmation, Google sign-in | Supabase Auth |
| `account.html` | Signed-in bidder profile and statutory/financial capacity fields | Supabase `profiles` row owned by the signed-in user |
| `saved-tenders.html` | Saved live tender notice links | Supabase `saved_tenders`; explicit Save to account action |
| `guide.html` | Getting-started guide and glossary | Static |
| `privacy.html` / `terms.html` | Data, sample, account, and legal-use notices | Static |
| `404.html` / `500.html` | Deployment error pages | Static |

### Frontend modules

- [`app.js`](./app.js): report tabs, evidence panel, audience profiles, sample
  tender filtering/preview, local profile draft, local checklist, live-search
  UI, scroll/reveal/navigation behavior.
- [`strategy.js`](./strategy.js): preset forms, bidder-profile loading,
  strategy preview requests, gate cards, legal-pack download/copy, compliance
  CSV export, affidavit tabs, EMD report, forensics search, and RAG workbench.
- [`auth.js`](./auth.js): fetches public auth configuration, initializes
  Supabase, manages sessions, email/password flows, Google OAuth/ID-token
  flows, profile sync, saved-tender CRUD, and account UI state.
- [`theme.js`](./theme.js): light/dark preference and theme-color updates.
- [`styles.css`](./styles.css): responsive design system, themes, navigation,
  report, account, and Strategy Studio styles.
- [`doodle-hero.bundle.js`](./doodle-hero.bundle.js): generated browser bundle
  for the React/TypeScript doodle hero.
- [`components/tenderlens-hero.tsx`](./components/tenderlens-hero.tsx) and
  [`components/ui/doodle-crew-footer.tsx`](./components/ui/doodle-crew-footer.tsx):
  React/TypeScript visual components with inline SVG animation helpers. The
  footer contains deterministic layout, gaze, timeline, and floater logic as
  well as the rendered component.

The corresponding files under [`frontend/`](./frontend/) are mirrors. The
tagged doodle footer is a visual component, not part of the FastAPI or tender
qualification pipeline.

## 4. Backend and intelligence

### API application

[`backend/main.py`](./backend/main.py) creates the FastAPI application,
request models, CORS middleware, API routes, audit orchestration, SSE
progress events, and Supabase persistence route handlers.

Current routes:

| Route | Role |
|---|---|
| `GET /healthz` | Environment and service diagnostics |
| `GET /api/v1/auth/config` | Public Supabase URL/key and optional Google client ID |
| `POST /api/v1/tenders/search` | TinySearch discovery with fallback |
| `POST /api/v1/tenders/fetch` | Recursive TinyFetch document/ATC crawl |
| `POST /api/v1/audit/evaluate` | Fetch, parse, gate, audit, and synthesize a scorecard |
| `GET /api/v1/audit/stream/{task_id}` | Demonstration SSE stage stream |
| `POST /api/v1/strategy/preview` | Local-input five-pillar preview without crawling |
| `POST /api/v1/strategy/prebid-queries` | Pillar 1 legal/clarification pack |
| `POST /api/v1/strategy/consortium-match` | Pillar 2 capability-gap match |
| `POST /api/v1/strategy/compliance-matrix` | Pillar 3 compliance binder and affidavits |
| `POST /api/v1/strategy/emd-optimizer` | Pillar 4 capital-risk calculation |
| `GET /api/v1/strategy/forensics` | Pillar 5 static or optional live forensics |
| `POST /api/v1/rag/query` | Precedence-aware tender query |
| `POST /api/v1/rag/precedence-graph` | Precedence graph generation |
| `POST /api/v1/audits/save` | Persist a scorecard for the authenticated user |
| `GET /api/v1/audits/user/{user_id}` | Read the authenticated user's audits |
| `GET /api/v1/profile/sync/{user_id}` | Read the authenticated user's profile |
| `POST /api/v1/profile/sync` | Upsert the authenticated user's profile |

Interactive OpenAPI documentation is available at `/docs` when the backend is
running.

### Backend modules

- [`backend/config.py`](./backend/config.py): `pydantic-settings` configuration,
  provider keys, CORS origins, allowed portal domains, crawl limits, and local
  cache directories.
- [`backend/services/tinyfish_service.py`](./backend/services/tinyfish_service.py):
  TinySearch, TinyFetch batching/metadata, recursive child-link discovery,
  and Tavily fallback.
- [`backend/services/document_processor.py`](./backend/services/document_processor.py):
  PyMuPDF page/block extraction, table detection, embedded hyperlink discovery,
  bounding boxes, and rank assignment.
- [`backend/services/supabase_service.py`](./backend/services/supabase_service.py):
  public/scoped Supabase clients, token verification, profile/audit access, and
  RLS-aware persistence.
- [`backend/engine/deterministic_gatekeeper.py`](./backend/engine/deterministic_gatekeeper.py):
  pure-Python turnover, experience, EMD, Make in India, OEM authorization,
  certifications, and CPWD 80/50/40 checks.
- [`backend/engine/precedence_rag_engine.py`](./backend/engine/precedence_rag_engine.py):
  canonical category resolution, strict rank ordering, conflict detection, and
  manual-review status for unsafe ambiguity.
- [`backend/engine/qualification_engine.py`](./backend/engine/qualification_engine.py):
  document criteria extraction, optional Gemini semantic auditing, scorecard
  synthesis, evidence citations, and Strategy Studio assembly.
- [`backend/engine/prebid_legal_generator.py`](./backend/engine/prebid_legal_generator.py):
  statutory challenge cards and formal representation markdown.
- [`backend/engine/consortium_matchmaker.py`](./backend/engine/consortium_matchmaker.py):
  quantified shortfalls and illustrative partner recommendations.
- [`backend/engine/compliance_matrix_engine.py`](./backend/engine/compliance_matrix_engine.py):
  compliance rows, CSV export, and statutory affidavit drafts.
- [`backend/engine/emd_capital_optimizer.py`](./backend/engine/emd_capital_optimizer.py):
  cash lock-up, opportunity cost, portfolio utilization, and instrument
  recommendation calculations.
- [`backend/engine/competitor_forensics.py`](./backend/engine/competitor_forensics.py):
  authority-specific rejection checkpoints and optional public-source analysis.

## 5. Shared data contracts

[`contracts/schema.py`](./contracts/schema.py) is the Pydantic contract layer
shared by backend engines and API responses. Important models include:

- `BidderProfile` and `ConsortiumPartnerProfile`
- `ClauseCitation` with document, page, clause, quote, risk, status, and optional
  bounding box
- `GateResult` for deterministic checks
- `QualificationScorecard`
- `StrategyToolkitResponse`
- `PreBidLegalRepresentationPack`
- `ConsortiumMatchRecommendation`
- `ComplianceAndBinderPackage`
- `EMDCapitalOptimizationReport`
- `CompetitorForensicsReport`
- `RAGQueryRequest`, `RAGQueryResponse`, and `PrecedenceDAGGraph`

The backend's [`TenderStatutoryCriteria`](./backend/engine/deterministic_gatekeeper.py)
contains explicit tender-side thresholds and flags. The system should only
make deterministic claims where a value is explicit; conflicting or legally
uncertain clauses should remain `AMBIGUOUS_MANUAL_REVIEW`.

## 6. Document precedence model

The intended ordering is:

1. Latest corrigendum
2. Earlier corrigenda
3. Buyer-uploaded ATC/RFP PDF
4. Buyer text-based ATC clauses
5. Main tender PDF

Lower numeric rank wins when clauses target the same canonical requirement.
Same-rank conflicts and potentially impermissible overrides are routed to
human review rather than silently resolved. Clause evidence carries source
coordinates and verbatim text where available.

## 7. Supabase data and authentication

[`supabase/setup.sql`](./supabase/setup.sql) defines three owner-scoped tables:

- `public.profiles`: organization identity, bidder type, MSME/startup status,
  turnover, experience, local content, certifications, and similar-project
  values.
- `public.saved_tenders`: explicitly saved official notice links, with a
  per-user/per-URL uniqueness constraint.
- `public.tender_audits`: saved scorecards and strategy/audit JSON.

All three tables enable RLS. Policies require `auth.uid() = user_id`, and the
frontend uses the signed-in user's Supabase session. Browser code must only use
the public publishable/anon key. Private provider keys and service-role keys
belong in the server environment.

## 8. Configuration and local operation

Python dependencies are declared in [`pyproject.toml`](./pyproject.toml) and
locked in [`uv.lock`](./uv.lock). Frontend component dependencies and scripts
are declared in [`package.json`](./package.json).

Typical local setup:

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn backend.main:app --reload --port 8000
```

For a separate static preview:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000` for the FastAPI-mounted app or
`http://127.0.0.1:4177` for the static server. Configure provider and Supabase
values in `.env`; never commit them.

## 9. Verification and tests

The test suite is under [`tests/`](./tests/):

- `test_api_endpoints.py`: health and audit route behavior.
- `test_deterministic_gatekeeper.py`: statutory/math gates and scorecard
  synthesis.
- `test_document_processor.py`: rank inference, PDF extraction, and embedded
  links.
- `test_gemini_auditor.py`: optional Gemini configuration/fallback behavior.
- `test_precedence_rag.py`: canonical categories, overrides, conflicts, graph,
  and RAG routes.
- `test_real_e2e_pipeline.py`: provider-backed and edge-case flows.
- `test_supabase_service.py`: configuration and profile deserialization.
- `test_v3_pillars.py`: all five strategy pillars and preview route.

Run:

```powershell
uv run pytest -q
node --check app.js
node --check auth.js
node --check strategy.js
node --check theme.js
npm run typecheck
```

The project tracker records a latest baseline of 34 passing tests across eight
test modules and successful JavaScript syntax checks. Those are recorded
verification results; provider-dependent tests still depend on local
configuration and network availability.

## 10. Security and privacy boundaries

The security rules are documented in [`docs/SECURITY.md`](./docs/SECURITY.md).
The important operational boundaries are:

- Keep API keys, service-role keys, credentials, and private tender documents
  out of source control.
- Preserve Supabase Auth and RLS for account data.
- Do not turn sample interactions into cloud records.
- Saving a real notice requires an explicit user action and a valid official
  link.
- Render extracted/user text safely; avoid unsafe HTML sinks.
- Validate external URLs and retain approved procurement-domain restrictions.
- Keep deterministic financial/statutory math separate from optional LLM
  interpretation.
- Treat legal ambiguity as a human-review case.

## 11. Repository map

| Area | Contents |
|---|---|
| Root HTML/JS/CSS | Current static application and deployment pages |
| `frontend/` | Mirrored static app plus TypeScript component source |
| `backend/` | FastAPI routes, providers, document processing, and engines |
| `contracts/` | Shared Pydantic schemas |
| `supabase/` | PostgreSQL schema/RLS setup and setup guide |
| `tests/` | Backend/API/engine/service tests |
| `docs/` | API, database, security, and style references |
| `research/` | Research notes and generated procurement analysis |
| `assets/` | Architecture and presentation images |
| `scripts/` | Small research/report extraction utility |
| `vendor/` | Locally bundled Lenis assets and licenses |
| `data/` | Runtime cache/raw-tender directories created by configuration |

Generated or vendored material such as `node_modules/`, `.venv/`, runtime
`tmp/`, bundled JavaScript, and the presentation PDF should not be used as the
primary source of application behavior.

## 12. Current gaps and next milestones

1. Verify/configure production Google OAuth credentials in Supabase.
2. Re-verify sign-up, login, recovery, profile sync, saved notices, and RLS
   isolation against the maintained Supabase project.
3. Design consent, retention, upload validation, and storage before connecting
   multi-PDF uploads to source-document auditing.
4. Reconcile the older Next.js/Docker plans with the current static
   implementation before starting a migration.
5. Recheck responsive layouts and Strategy Studio flows on desktop and
   Android-sized viewports.
6. Resolve any implementation/documentation drift in deployment and security
   configuration before calling the system production-ready.

