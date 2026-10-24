# TenderLens

TenderLens is a project for making Indian public tender requirements easier to review. It brings the main tender, extra buyer terms (ATCs), and official corrigenda into one place, with deterministic checks and source-linked evidence.

## What works today

- **Interactive Tender Explorer & Sample Report (`index.html`)**: Includes an illustrative qualification report, sample tender search and filters, an interactive five-layer document-precedence explorer, a local bidder profile draft, and an evidence checklist.
- **Live Portal Discovery (`POST /api/v1/tenders/search`)**: Runs optional live tender search across GeM, CPPP, BHEL, ICMR, and State eProcurement portals through the FastAPI backend when `TINYFISH_API_KEY` (or fallback `TAVILY_API_KEY`) is configured.
- **5-Pillar Strategy Studio & Precedence DAG Workbench (`strategy.html`)**:
  - Connects to `POST /api/v1/strategy/preview`, `GET /api/v1/strategy/forensics`, and `POST /api/v1/rag/query`.
  - Includes one-click illustrative presets (`BHEL MSME Trap & Brand Lock`, `CPPP EPC Surety Bond & 80/50/40`, `ICMR Medical OEM MAF & BIS`) and one-click loading from a signed-in user's synced Supabase Bidder Profile.
  - **Deterministic Gatekeeper**: Evaluates 3-Year Average Turnover, Experience, GFR Rule 170(i) EMD exemption, Make in India Class-I/II local content, OEM MAF requirement, Mandatory Certifications set-difference, and CPWD 80/50/40 similar-work ratios.
  - **Pillar 01 — Pre-Bid Legal & Clarification Pack**: Generates statutory challenge cards and a downloadable/copyable formal representation letter citing CVC, GFR 2017, and DPIIT orders.
  - **Pillar 02 — Consortium & Capability Gap Matchmaker**: Quantifies exact eligibility shortfalls and displays illustrative JV/OEM partner archetypes.
  - **Pillar 03 — Automated Compliance Matrix & Statutory Affidavits**: Builds a clause-by-clause compliance table, exports portal-ready CSVs, and drafts statutory undertaking templates (`GFR_170_BID_SECURITY`, `DPIIT_MII_LOCAL_CONTENT`, `GFR_144_XI_LAND_BORDER`, `OEM_MAF_FORMAT`).
  - **Pillar 04 — EMD Capital Risk & Surety Bond Optimizer**: Computes working-capital lock-up across concurrent bids and compares GFR Rule 170(i) Bid Security Declarations, IRDAI Insurance Surety Bonds, and NeSL e-BGs.
  - **Pillar 05 — Competitor Disqualification Forensics**: Surfaces authority-specific evaluation checkpoints and supports explicit public-source search.
  - **Section 06 — Precedence DAG & RAG Conflict Resolver**: Demonstrates how Rank 1 Corrigenda supersede Rank 3 Buyer ATCs and Rank 5 Main Tender PDFs with a full audit trail.
- **Supabase Auth, Google Sign-In & RLS Persistence (`signin.html`, `signup.html`, `account.html`, `saved-tenders.html`)**:
  - Supports email/password sign-in, shared demo sign-in, Supabase Google OAuth redirect (`signInWithOAuth`), and Google Identity Services (`google.accounts.id` + `signInWithIdToken`).
  - Syncs the signed-in user's Bidder Profile (both basic organization details and optional statutory/financial capacity metrics) and saved live tender links to Supabase Postgres under Row-Level Security (`supabase/setup.sql`).

This is an experimental hackathon project. Sample tenders, partner archetypes, and report results are illustrative. Always check the official tender documents and consult qualified counsel before acting on any tender.

## Technology stack

- **Frontend**: Responsive HTML5, CSS3, and Vanilla ES6+ JavaScript (`index.html`, `strategy.html`, `signin.html`, `signup.html`, `account.html`, `saved-tenders.html`, `guide.html`, `app.js`, `auth.js`, `strategy.js`, `theme.js`, `styles.css`), bundled with Lenis smooth scrolling (`vendor/lenis.min.js`) and `@supabase/supabase-js@2`.
- **Backend API**: Python 3.12, FastAPI, Pydantic v2, Uvicorn, and `sse-starlette` (`backend/main.py`, `backend/config.py`).
- **Qualification & RAG Engines**:
  - `backend/engine/deterministic_gatekeeper.py` — Pure-Python mathematical & statutory gatekeeper (GFR 2017, DPIIT MII Order 2017, PPP-MSE 2012, CPWD 80/50/40).
  - `backend/engine/precedence_rag_engine.py` — Directed Acyclic Graph (DAG) clause conflict resolver (Rank 1 Corrigendum → Rank 5 Main PDF).
  - `backend/engine/prebid_legal_generator.py`, `consortium_matchmaker.py`, `compliance_matrix_engine.py`, `emd_capital_optimizer.py`, `competitor_forensics.py` — 5-Pillar Strategy Engine.
- **Web & Document Intelligence**: TinyFish API (`TinySearch`, `TinyFetch`, `TinyAgent` in `backend/services/tinyfish_service.py`), PyMuPDF (`fitz` in `backend/services/document_processor.py`), Google Gemini SDK (`google-genai` / `langchain-google-genai`, default model `gemini-3.8-flash`), and optional Tavily fallback.
- **Database & Authentication**: Supabase Auth + Supabase PostgreSQL with Row-Level Security (`supabase/setup.sql`, `backend/services/supabase_service.py`).

## Run the project locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and sync the Python environment:

```powershell
uv sync
Copy-Item .env.example .env
```

Start the FastAPI backend (which serves the API at `http://127.0.0.1:8000`, interactive Swagger docs at `http://127.0.0.1:8000/docs`, and mounts the static frontend at `/`):

```powershell
uv run uvicorn backend.main:app --reload --port 8000
```

You can also serve the root static files on port `4177` in a second terminal:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open <http://127.0.0.1:4177> (or <http://127.0.0.1:8000>).

## Configure Supabase & Google OAuth

1. **Supabase URL & Keys**: Set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` (and/or `SUPABASE_ANON_KEY`) in `.env`. Never expose a service-role secret key in browser code.
2. **Database Schema & RLS**: Run [`supabase/setup.sql`](supabase/setup.sql) in Supabase Dashboard → SQL Editor to create `public.profiles`, `public.saved_tenders`, and `public.tender_audits` with owner-scoped RLS policies (`auth.uid() = user_id`).
3. **Google OAuth Setup**:
   - Open [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) and create an **OAuth 2.0 Client ID** (Application type: **Web application**).
   - Under **Authorized JavaScript origins**, add `http://localhost:4177`, `http://127.0.0.1:4177`, `http://localhost:8000`, and `http://127.0.0.1:8000`.
   - Under **Authorized redirect URIs**, add your Supabase Callback URL:
     `https://<your-project-ref>.supabase.co/auth/v1/callback`
   - Copy the **Client ID** and **Client Secret** into **Supabase Dashboard → Authentication → Providers → Google**, and optionally set `GOOGLE_CLIENT_ID=` in `.env` (or in the Sign-In page helper) for Google Identity Services One-Tap / ID-Token sign-in.

## Run tests

```powershell
uv run pytest -q
```
