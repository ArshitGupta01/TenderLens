# TenderLens Agent Handoff

Updated: 2026-10-24

## Current project state

- TenderLens unifies the responsive HTML/CSS/JavaScript frontend (in both the repository root and `frontend/`) with the full `Mohit-Backend` v1.0.3 FastAPI engine on `main`.
- The **Strategy tools** page (`strategy.html` / `strategy.js`) connects to `POST /api/v1/strategy/preview`, `GET /api/v1/strategy/forensics`, and `POST /api/v1/rag/query`. It provides:
  - One-click scenario presets and one-click profile loading from the signed-in user's Supabase Bidder Profile
  - Deterministic Gatekeeper Scorecard cards (3Y Average Turnover, Experience, GFR 170 EMD, Make in India Class-I/II, OEM MAF, Mandatory Certifications, CPWD 80/50/40 Similar Work)
  - Pillar 01: Pre-Bid Legal Representation & Clarification Pack with copy/download Markdown letter
  - Pillar 02: Dynamic Consortium & Capability Gap Matchmaker with quantified gap cards and illustrative partner archetypes
  - Pillar 03: Automated Compliance Matrix with CSV export and interactive Statutory Affidavit & Undertaking templates (`GFR_170_BID_SECURITY`, `DPIIT_MII_LOCAL_CONTENT`, `GFR_144_XI_LAND_BORDER`, `OEM_MAF_FORMAT`)
  - Pillar 04: EMD Capital Risk & IRDAI Insurance Surety Bond Optimizer
  - Pillar 05: Competitor Disqualification Forensics with static authority checkpoints and explicit public-source search
  - Section 06: Interactive Precedence DAG & RAG Conflict Resolver Workbench showing how Rank 1 Corrigenda override Rank 3 Buyer ATCs and Rank 5 Main Tender PDFs
- **Supabase Auth & Postgres RLS**:
  - Connected to Supabase project `qiwpkvjzqdyguygowzci` (`https://qiwpkvjzqdyguygowzci.supabase.co`) with tables `public.profiles`, `public.saved_tenders`, and `public.tender_audits` protected by Row-Level Security (`auth.uid() = user_id`).
  - Shared demo user `cm@gmail.com` is provisioned and confirmed in Supabase Auth (`auth.users` and `auth.identities`) and seeded in `public.profiles` (password is never stored in git).
  - Supports both Supabase Google OAuth redirect (`signInWithOAuth`) and Google Identity Services (`google.accounts.id` + `signInWithIdToken` via `GOOGLE_CLIENT_ID` or local Client ID helper).
  - Backend persistence routes (`/api/v1/audits/save`, `/api/v1/audits/user/{user_id}`, `/api/v1/profile/sync/{user_id}`, `/api/v1/profile/sync`) verify Bearer JWT tokens and scope PostgREST requests to the user's JWT so RLS is enforced.

## Verification recorded for the latest main update

- Full pytest suite: **34 passed** across 8 test modules (`tests/test_api_endpoints.py`, `tests/test_deterministic_gatekeeper.py`, `tests/test_document_processor.py`, `tests/test_gemini_auditor.py`, `tests/test_precedence_rag.py`, `tests/test_real_e2e_pipeline.py`, `tests/test_supabase_service.py`, `tests/test_v3_pillars.py`).
- JavaScript syntax validation: `node --check app.js`, `node --check auth.js`, `node --check strategy.js`, and `node --check theme.js` all passed with zero errors.
- Live Supabase Auth & RLS verification against `https://qiwpkvjzqdyguygowzci.supabase.co` passed.

## Next milestones

1. Add the Google Cloud OAuth 2.0 Client ID and Client Secret in the Supabase Dashboard (`Authentication -> Providers -> Google`) using callback URI `https://qiwpkvjzqdyguygowzci.supabase.co/auth/v1/callback`.
2. Connect multi-PDF tender upload to the source-document audit view once document retention and consent controls are finalized.

## Working rules

- Read `AGENTS.md`, `README.md`, `FINAL_IMPLEMENTATION_PLAN.md`, the relevant team tracker and contracts before project changes.
- Preserve document precedence, source-linked evidence, deterministic checks for explicit values, and human review for ambiguous rules.
- Keep fictional workflows local and label them clearly. Describe a feature as implemented only when its code path is connected and verified.
- Update this handoff and the relevant tracker (`MOhit-Agents.md` for backend work, `arshit-agents.md` for website work) with actual changes and the next open milestone.
- Never record passwords, API secrets, private profiles or private tender documents here.
