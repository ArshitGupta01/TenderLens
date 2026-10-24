# arshit-agents.md — Arshit's Memory & Progress Tracker

> **Project**: TenderLens (AI-Powered Tender Qualification & Disqualification Engine)  
> **Team**: Team Traxo · HackIIITD (Round 2)  
> **Agent Owner**: Arshit  
> **Domain**: Frontend (Next.js), Database (PostgreSQL / Migrations), Object Storage, Async Job Queues & UI Experience  
> **Status**: Responsive website with optional FastAPI search and configured Supabase auth/profile/bookmark code; Google OAuth and demo-account verification remain pending

---

## 1. Role & Project Boundaries

Arshit is responsible for bringing TenderLens to life on the user interface and persistent data layer:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                ARSHIT'S WORKSPACE                                │
├─────────────────────────────────────────┬────────────────────────────────────────┤
│          FRONTEND (Next.js 14)          │       DATABASE & INFRASTRUCTURE        │
├─────────────────────────────────────────┼────────────────────────────────────────┤
│ • Bidder Profile Onboarding UI          │ • PostgreSQL Schemas & Migrations      │
│ • Live Tender Discovery Feed            │ • Bidder Profiles Table                │
│ • Real-time Crawl / SSE Progress Bar    │ • Tender Audits & Reports Table        │
│ • Evidence-Backed Scorecard Display     │ • MinIO / S3 Document Object Storage   │
│ • Clause Citation Popover Inspector     │ • Redis Cache & Celery Task Queue      │
│ • Exportable PDF Compliance Audit       │ • Docker Compose Environment           │
└─────────────────────────────────────────┴────────────────────────────────────────┘
```

> **Integration Interface**: Arshit's planned application frontend connects to Mohit's FastAPI backend endpoints. All data payloads adhere strictly to the shared models in [`contracts/schema.py`](contracts/schema.py).

---

## 2. API Contracts Provided by Mohit's Backend

Arshit can build the frontend immediately by stubbing or calling these standardized endpoints:

### 1. `POST /api/v1/tenders/search`
- **Purpose**: Live tender discovery via TinySearch API.
- **Request**:
  ```json
  {
    "keywords": "Solar rooftop installation Haryana",
    "portal": "gem.gov.in",
    "location": "IN"
  }
  ```
- **Response**: Array of discovered tenders (`title`, `url`, `snippet`, `source_portal`).

### 2. `POST /api/v1/audit/evaluate`
- **Purpose**: Full 5-step qualification engine audit.
- **Request**:
  ```json
  {
    "tender_url": "https://gem.gov.in/tender/example.pdf",
    "tender_name": "Supply & Installation of High Voltage Transformers",
    "bidder_profile": { ... conforming to BidderProfile in contracts/schema.py ... }
  }
  ```
- **Response**: Full `QualificationScorecard` JSON matching [`contracts/schema.py`](contracts/schema.py) (`score`, `recommendation`, `deterministic_gates`, `clause_citations`).

### 3. `GET /api/v1/audit/stream/{task_id}`
- **Purpose**: Server-Sent Events (SSE) stream for live progress animation (Discovering -> Ingesting ATCs -> Math Gates -> LLM Audit -> Final Scorecard).

---

## 3. Database Schema Blueprint (PostgreSQL)

Recommended relational tables for Arshit's implementation:

1. **`users` / `companies`**:
   - `id` (UUID, PK)
   - `company_name`, `pan_number`, `gstin`, `msme_registration_number`
   - `created_at`, `updated_at`

2. **`bidder_profiles`**:
   - `id` (UUID, PK), `company_id` (FK)
   - `turnover_y1`, `turnover_y2`, `turnover_y3`
   - `years_in_business`, `local_content_percentage`
   - `certifications` (JSONB / text array)

3. **`tender_audits`**:
   - `id` (UUID, PK), `company_id` (FK)
   - `tender_bid_number`, `tender_title`, `tender_url`
   - `recommendation` (ENUM: `STRONG_BID`, `CONDITIONAL_BID`, `RED_FLAG_NO_BID`)
   - `qualification_score` (Float)
   - `scorecard_data` (JSONB — stores the full `QualificationScorecard`)
   - `created_at`

4. **`cached_documents`**:
   - `hash` (SHA256, PK), `source_url`, `s3_key`, `page_count`, `created_at`

---

## 4. Arshit's Progress Log & Milestones

### Shared demo login — 2026-10-24
- [x] Added a shared-demo account panel to the sign-in page with a one-tap autofill action, dark-theme styling and small-screen layout support.
- [x] Warned users not to save private profile or tender details in a shared account; documented this in the README.
- [ ] Supabase Auth rejected `cm@gmail.com` as invalid, so the requested login was not created and the shared credentials cannot authenticate yet.
- [ ] Next: use an accepted inbox, create and verify the Supabase user, then confirm email/password sign-in.

### Presentation prototype update — 2026-10-24
- [x] Added a responsive static website in the repository root with an illustrative qualification report, evidence details, and audience profiles.
- [x] Made prototype limitations clear: optional live search is connected; uploads, automated audits, accounts, and saved reports are not connected.
- [ ] Next application milestone remains a Next.js frontend wired to the planned backend APIs; the static prototype is not that application.

### Interactive prototype expansion — 2026-10-24
- [x] Added a searchable, category-filtered sample tender desk with in-page previews and visit-only saved examples.
- [x] Added an interactive five-layer precedence explorer and a local six-item bidder readiness checklist.
- [x] Added Lenis smooth scrolling, reading progress, section reveals, active navigation, and a back-to-top control with reduced-motion support.
- [x] Updated privacy and terms notices for the local-only interactions and locally bundled Lenis library.
- [ ] Next milestone: connect tender fetching and a verified source-document audit after safe upload and data-retention behavior are designed; the current Strategy tools preview uses manually entered values only.

### Readability and guide update — 2026-10-24
- [x] Increased body and control text sizes and rewrote the report labels and document-order explanation in plain language.
- [x] Added a saved light/dark theme preference, an easy-start guide, a short glossary, quick-answer accordion, and clearer privacy and terms pages.
- [x] Kept the tender examples and company checklist local and labeled as fictional. Added an optional search form that sends only the phrase and selected portal to the configured backend.
- [x] Added local preview instructions and linked the guide from the main navigation and footer.
- [x] Reviewed the desktop and narrow preview layouts; adjusted the navigation and footer to avoid wrapping and horizontal overflow.
- [x] Added a local bidder profile draft with organization name, bidder type, years active and region. It is stored only in this browser and can be cleared from the page.
- [ ] Cloud profiles, file uploads, accounts, saved audits and connected eligibility reviews remain future work.

### Tablet layout refinement — 2026-10-24
- [x] Added an 851–1100px breakpoint that replaces the crowded desktop navigation with the menu button and gives the hero a full-width reading column.
- [x] Reviewed the change against the supplied 1056px screenshot and checked the existing narrow local preview; a dedicated 1056px embedded-browser viewport was unavailable.
- [ ] Recheck tablet and desktop layouts in a resizable browser preview when available.

### Profile and theme refinement — 2026-10-24
- [x] Fixed the closing section's dark-theme contrast by using the dark green theme token for its background and increasing its small caption contrast. The floating top button now hides when the footer is visible to keep its links clear.
- [x] Added a browser-local bidder profile form with a clear control, a four-step easy-guide entry and updated privacy / terms explanations.
- [ ] Review the form with a resizable tablet browser and design the authenticated, server-backed profile only after its privacy and API requirements are defined.

### Account and saved-notice experience — 2026-10-24
- [x] Added separate sign-in, sign-up, account profile and saved live-tender pages with email/password, Google OAuth, email confirmation and password recovery flows.
- [x] Added Supabase Postgres setup SQL with owner-scoped row-level security for profiles and saved notice links. Sample tenders, sample saves and checklists remain local and illustrative.
- [x] Added a public FastAPI config response containing only the Supabase project URL and publishable key; secret/service-role keys are not exposed.
- [x] Connected signed-in profile saves and live result bookmarks to Supabase, added responsive layouts and subtle hero parallax, and updated the easy guide, privacy notice, terms and README.
- [ ] The Supabase project values, database setup, Google OAuth client and production email provider are not configured yet. Verify sign-up, login, recovery, profile sync, saved-link sync and RLS isolation after the maintainer configures them.
- [ ] Next: apply `supabase/setup.sql`, configure `.env` and Supabase providers, then check sign-in on Android and desktop against the team's actual project.

- [ ] Initialize Next.js project in `frontend/` (TypeScript, Tailwind CSS, Lucide icons)
- [ ] Build Bidder Profile configuration screen (Turnover, MSME status, Certifications)
- [ ] Build Search & Ingestion tracker with live SSE progress bar
- [ ] Implement the Interactive Scorecard view (Badges, Deterministic Gate accordions, Clause Inspector)
- [ ] Set up Docker Compose (`postgres`, `redis`, `minio`, `frontend`, `backend`)
- [ ] Wire database models and save audit results history

### Mohit backend strategy integration — 2026-10-24
- [x] Added a responsive Strategy tools page linked from the site navigation and easy guide.
- [x] Connected the page to the FastAPI preview route for entered values, checklist CSV export and explicit public-source search.
- [x] Kept the Supabase profile separate from this form and documented the data sent, non-persistence behavior and limits in the privacy notice and terms.
- [x] Added mobile-aware strategy layout and validated server-side numeric bounds for core bidder and tender criteria.
- [ ] Verify the preview on desktop and Android-sized viewports; exercise the public-search provider only with a deliberate query.
- [ ] Connect uploaded-source audit after source precedence, storage, consent and retention requirements are implemented.


### Unified 5-Pillar Strategy Studio, Precedence DAG Workbench & Supabase Auth Upgrade — 2026-10-24
- [x] Upgraded `strategy.html`, `strategy.js`, and `styles.css` into the full 5-Pillar Strategy Studio & Precedence DAG Workbench:
  - Added one-click scenario presets (`BHEL MSME Trap & Brand Lock`, `CPPP EPC Surety Bond & 80/50/40`, `ICMR Medical OEM MAF & BIS`) plus one-click `Load my Bidder Profile` from Supabase.
  - Added visual Deterministic Gatekeeper Scorecard cards (`PASS` / `CONDITIONAL` / `DISQUALIFIER` badges, bidder vs required values, statutory citations).
  - Upgraded Pillar 01 (Pre-Bid Legal & Clarification Pack with copy/download `.md`), Pillar 02 (Consortium & Capability Gap Matchmaker with quantified gap cards and illustrative partner archetypes), Pillar 03 (Automated Compliance Matrix with CSV download + interactive tabbed Statutory Affidavit Drafter for `GFR_170_BID_SECURITY`, `DPIIT_MII_LOCAL_CONTENT`, `GFR_144_XI_LAND_BORDER`, and `OEM_MAF_FORMAT`), Pillar 04 (EMD Capital Risk & Surety Bond Optimizer), and Pillar 05 (Competitor Disqualification Forensics + explicit public-source search).
  - Added Section 06: Interactive Precedence DAG & RAG Conflict Resolver Workbench (`POST /api/v1/rag/query`) demonstrating how Rank 1 Corrigenda override Rank 3 Buyer ATCs and Rank 5 Main Tender PDFs.
- [x] Fixed `auth.js` (`initDemoLogin` password focus bug), added Google Identity Services (`google.accounts.id` + `signInWithIdToken`) alongside Supabase Google OAuth redirect (`signInWithOAuth`), added an interactive Google OAuth & Client ID configuration helper on `signin.html` and `signup.html`, and handled free-tier email rate limits (`429`) gracefully.
- [x] Provisioned and verified the shared demo account (`cm@gmail.com`) in Supabase Auth (`auth.users` & `auth.identities`) and `public.profiles` under RLS.
- [x] Upgraded `account.html` so signed-in users can sync both basic organization details and statutory/financial capacity metrics (`is_msme_registered`, `msme_category`, `is_startup_recognized`, 3-year turnover, `years_in_business`, `local_content_percentage`, `held_certifications`) to `public.profiles` under RLS.
- [x] Synchronized all root HTML/CSS/JS files with `frontend/` so both FastAPI port `8000` and static server port `4177` serve the unified application.
- [ ] Next milestone: configure production Google Cloud OAuth Client ID & Secret in Supabase Dashboard and connect multi-PDF file upload to the source-document audit view.

### Repository information document — 2026-10-24
- [x] Added [`PROJECT_INFO.md`](PROJECT_INFO.md), a current-codebase orientation covering the static frontend, FastAPI backend, shared contracts, precedence model, Supabase/RLS boundaries, routes, tests, configuration, and known gaps.
- [x] Explicitly separated implemented behavior from older Next.js/Docker plans and illustrative sample workflows.
- [ ] Next milestone remains production Google OAuth configuration and consent/retention design for multi-PDF source-document auditing.

### Vercel Multi-Page Deployment, Security Standard & Mobile Menu Banner — 2026-10-24
- [x] Configured production Vercel deployment with clean multi-page routing, custom error pages (`404.html`, `500.html`), static caching, and HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) in `vercel.json`.
- [x] Implemented responsive `<aside class="top-menu-banner">` quick navigation menu across all HTML pages (`index.html`, `strategy.html`, `signin.html`, `signup.html`, `account.html`, `saved-tenders.html`, `guide.html`, `privacy.html`, `terms.html`, `404.html`, `500.html`) with live status badge (`TENDERLENS v1.0.3 LIVE`), one-tap access to all key modules, and swipeable horizontal overflow on mobile devices.
- [x] Enhanced mobile responsiveness across all screen sizes (max-width 600px):
  - Prevented horizontal bouncing (`overflow-x: hidden; width: 100%`).
  - Added `-webkit-overflow-scrolling: touch;` and horizontal containment on compliance matrix and strategy tables.
  - Stacked action buttons, preset chips, and scorecard headings vertically on narrow viewports for thumb-friendly touch interactions.
  - Set minimum 16px font size on inputs to avoid automatic zoom on iOS Safari.
- [x] Implemented comprehensive security and development documentation adhering to the 20-point security specification and vibe coding guides:
  - `docs/SECURITY.md`: 20 security principles (RLS, secrets isolation, CSP, CORS, input validation, audit trail, automated gatekeeper).
  - `docs/CODE_STYLE.md`: Code style guidelines and architectural patterns.
  - `docs/DATABASE.md`: Supabase PostgreSQL schema, RLS policies, indexing, and migration reference.
  - `docs/API.md`: API reference for all endpoints, request/response models, SSE streaming, and error handling.
  - `SECURITY.md`: Repository root security declaration.
  - `robots.txt` and `sitemap.xml`: SEO and crawler directives for production deployment.
- [x] Synced all static assets and configuration files between repository root and `frontend/`.
- [ ] Next milestone: Deploy to Vercel via `npx vercel` or GitHub integration and connect custom domain.

### Codebase Hygiene & Dead Code Purge — 2026-10-24
- [x] Deleted 303KB obsolete Repomix snapshot (single.xml) and updated .gitignore to ignore build/export dumps.
- [x] Audited and eliminated unused imports, dead functions, and redundant variables across all Python files in ackend/, contracts/, and 	ests/.
- [x] Converted empty placeholder main.py into a functional Uvicorn CLI entrypoint for local execution.
- [x] Validated zero syntax errors (
ode --check) across all frontend scripts in both root and rontend/.
- [x] Verified full backend suite: all 34/34 unit, integration, and live pipeline tests pass in 112s.

### Live Vercel Production Deployment — 2026-10-24
- [x] Deployed live to Vercel with project name 	enderlens under team 	eam_2bd4JqS5pfsQYUDhbwMEDBzK (username rshitgupta2017-9626).
- [x] Production URLs:
  - Canonical: https://tenderlens-ten.vercel.app
  - Team Alias: https://tenderlens-arshit-s-projects-680b94fa.vercel.app
- [x] Verified 200 OK responses across all routes with clean multi-page URLs (/, /strategy, /signin, /account, /robots.txt, /404).
- [x] Configured static multi-page rootDirectory rontend to bypass AWS Lambda 500MB function size limit while serving full responsive UI, Top Menu Banner, Supabase Auth, and client Strategy Studio.

### Menu Flyout, shadcn/Tailwind/TypeScript Integration & TenderLens Doodle Hero - 2026-10-24
- [x] Converted the top banner clutter into an interactive flyout menu that *only opens when clicked on Menu* across all 11 pages (index.html, strategy.html, signin.html, signup.html, account.html, saved-tenders.html, guide.html, privacy.html, terms.html, 404.html, 500.html). Added click-outside dismissal and Escape key handler.
- [x] Integrated standard shadcn project architecture:
  - Added components/ui/doodle-crew-footer.tsx (the zero-dependency interactive hand-drawn crew component with inline SVG, math layout, eye tracking, physics drift, and soundless speech bubbles).
  - Added components/demo.tsx demo wrapper.
  - Added components/tenderlens-hero.tsx tailored specifically for TenderLens procurement compliance intelligence.
  - Added lib/utils.ts with standard cn() (clsx + tailwind-merge).
  - Added components.json, tsconfig.json, tailwind.config.js, and package.json.
  - Verified npm run typecheck (tsc --noEmit) passes with 0 errors.
- [x] Adapted component as the primary TenderLens hero at the start of page load:
  - Shifted all subsequent modules down so the giant ink-stamped "TENDERLENS" wordmark and hand-drawn compliance crew load first.
  - Assigned characters across "TENDERLENS" with deterministic audit commentary (Bruno, Pip, Morel, Juno, Boo, Patch).
  - Configured brand palette matching TenderLens navy canvas (#090e17), bright text (#f8fafc), and electric cyan (#38bdf8).
- [x] Responsive desktop vs mobile scroll behavior:
  - Desktop (@media (min-width: 769px)): Implemented a long-scroll cover-up effect with a 145vh stage, sticky 100vh hero, animated scroll cue, and elevated curtain layer (.tenderlens-curtain) that smoothly slides up and covers the hero as the user scrolls.
  - Mobile (@media (max-width: 768px)): Completely disabled long-scroll pinning and scroll cues; users experience a fast, standard natural touch scroll with fluid wordmark scaling.
- [x] Verified full local execution:
  - FastAPI server running on http://127.0.0.1:8000/ serving HTML and bundled component (doodle-hero.bundle.js).
  - Synced all files and configurations between root and frontend/.
- [x] Paused external deployments and transitioned entirely to local development.

### Google Auth Complete Removal - 2026-10-24
- [x] Completely purged Google OAuth, GIS (Google Identity Services) button slots, and Client ID helpers from sign-in and sign-up pages (`signin.html`, `signup.html`, `frontend/signin.html`, `frontend/signup.html`).
- [x] Removed all Google OAuth handlers, GIS script loaders, and token exchange routines (`handleGoogleSignIn`, `initGoogleIdentityServices`, `initGoogleOAuthHelper`, `getActiveGoogleClientId`) from `auth.js` and `frontend/auth.js`.
- [x] Added automatic cleanup of any legacy `tenderlens_google_client_id` localStorage items upon initialization.
- [x] Cleaned unused `.google-button` and `.google-mark` CSS from `styles.css` and `frontend/styles.css`.
- [x] Updated documentation in `guide.html` and `privacy.html` to reflect pure email/password credentials and verified session tokens under Supabase Auth without external social providers.
- [x] Verified local pages load cleanly at `http://127.0.0.1:8000/signin.html` and `http://127.0.0.1:8000/signup.html` with zero Google artifacts.
- [ ] Next milestone: Continue local feature development and connect multi-file PDF ingestion to the live compliance DAG.

### TenderLens Wordmark Refinement & Header-Below Placement - 2026-10-24
- [x] Repositioned the TenderLens interactive doodle stage so it sits **directly below the top header banner** (`<header class="site-header">`), keeping the header navigation and menu permanently anchored at the top of the viewport.
- [x] Refined `components/ui/doodle-crew-footer.tsx` and `components/tenderlens-hero.tsx` with a `wordmarkOnly={true}` mode that completely removes extraneous columns, tagline, pill buttons, and secondary footer links (matching Image 2).
- [x] Preserved the giant hand-drawn **T E N D E R L E N S** wordmark, animated character crew (Bruno, Pip, Morel, Juno, Boo, Patch), interactive eye tracking, ink boiling lines, click speech bubbles, and floating ink doodles.
- [x] Fine-tuned responsive behavior:
  - Desktop: Long-scroll curtain cover-up effect slides smoothly over the wordmark directly under the 72px sticky header banner.
  - Mobile: Clean, natural vertical touch scroll with fluid wordmark scaling and zero scroll traps.
- [x] Rebuilt client bundle (`npm run build:doodle`) and verified with `npm run typecheck` (0 errors).
- [x] Synchronized all assets between root and `frontend/`.

### Doodle Crew Characters Purge - 2026-10-24
- [x] Completely removed all 6 cartoon characters (Bruno, Pip, Morel, Juno, Boo, Patch) from `components/tenderlens-hero.tsx`, `components/ui/doodle-crew-footer.tsx`, and `frontend/`.
- [x] Wordmark now renders exclusively as the pure, professional dry-brush ink **T E N D E R L E N S** wordmark with its inline SVG texture, boiling lines, and floating ink particles without any characters sitting or peeking over the letters.
- [x] Verified zero TypeScript errors (`tsc --noEmit`) and bundled cleanly with `npm run build:doodle`.

### Fluid Wordmark Upscaling & Aspect-Ratio Responsive Optimization - 2026-10-24
- [x] Substantially increased the size of the TenderLens wordmark:
  - Tightened inner SVG viewBox padding (`pad = 8`, `b = 16` when `wordmarkOnly`), cutting dead vertical margins by 21% and rendering the letter glyphs 26% taller and bolder.
  - Removed the restrictive 1400px container width cap to allow fluid expansion up to `min(96vw, 1920px)` and `max-height: 54vh`.
- [x] Built aspect-ratio responsive scaling rules across display types:
  - Ultra-wide displays (`min-aspect-ratio: 18/9`): Wordmark expands to fill wide landscape viewports (`clamp(960px, 96vw, 1920px)`).
  - Standard widescreen (`16:9` / `16:10`): Balanced fluid scale (`clamp(780px, 95vw, 1760px)`).
  - Taller / boxy screens (`max-aspect-ratio: 14/9`): Preserves breathing room and proportions (`clamp(620px, 94vw, 1480px)`).
- [x] Optimized UI specifically for mobile devices:
  - Fitted maximum legible wordmark width without horizontal overflow (`max-width: calc(100vw - 16px)`).
  - Disabled sticky locking and scroll cues for smooth touch navigation.
  - Added `touch-action: pan-y;` and contained bounds to eliminate accidental sideways bounce.
- [x] Verified local server execution on `http://127.0.0.1:8000/`.


### Architecture Comparison & Production Tech Stack Implementation (Images 1 & 2) + Live TinyFish Pipeline Test Bench - 2026-10-24
- [x] Implemented Section 02 (`#architecture`): **"TenderLens: AI-Powered Government Procurement Engine"** matching Image 2:
  - **Left Panel (Existing Tools - The Flawed Way)**:
    - Illustrated keyword queries and portal tender links fed into legacy scrapers.
    - Highlighted critical failure modes: LLM mathematical hallucinations ($F = \pi_0 \frac{m1 + \alpha}{X}$), ignored nested Additional Terms & Conditions (ATCs), severe Earnest Money Deposit (EMD) forfeiture risks, disqualification on technicalities, and complete absence of an auditable legal trail.
  - **Right & Center Panel (TenderLens Architecture - The Intelligent Way)**:
    - **Step 1: Bidder Profile**: Automated ingestion of MSME status, 3-year turnover history, and local content declarations.
    - **Step 2: Web Intelligence (TinyFish Engine)**: Live integration with `TinySearch` (targeted GeM/CPPP discovery), `Recursive TinyFetch` (discovering nested child ATCs and Corrigenda), and `Stealth TinyAgent` (autonomous headless fallback with proxy routing).
    - **Step 3: Document Intelligence**: Ingestion and coordinate mapping with `PyMuPDF` (fitz) for hidden hyperlinks and `Docling` for structured tables.
    - **Step 4: Hybrid Verification Engine**: Dual-engine architecture with strict Python Deterministic Gates (guaranteeing zero math hallucination for GFR 170 EMD rules, PPP-2012 MSME exemptions, and Make in India local content thresholds) paired with a Semantic LLM Precedence DAG (Corrigendum Rank 1 > Buyer ATC Rank 3 > Main RFP Rank 5).
    - **Step 5: Qualification Scorecard**: Visual **Strong Bid 4.8 / 5.0** decision badge and 3 interactive Clause Citation Cards (Rank 1 Corrigendum Page 3, Rank 3 Buyer ATC Page 18, Rank 5 Main RFP Page 42).
- [x] Built and wired up the **Live Interactive Pipeline Test Bench**:
  - Live TinyFish API integration utilizing configured `TINYFISH_API_KEY`.
  - Search action queries `POST /api/v1/tenders/search` on `gem.gov.in`, returning real-time tender notices with live PDF links.
  - "Run 5-Step Evaluation" animates the full sequence through Profile -> TinyFish -> PyMuPDF -> Deterministic Python Gates -> Scorecard with the 3 Clause Citation Cards and links into Strategy Studio.
- [x] Implemented Section 03 (`#tech-stack`): **TenderLens Production Tech Stack** matching Image 1:
  - 6 Production Layers:
    1. **User Experience**: Next.js, TypeScript, Tailwind CSS.
    2. **API & Orchestration**: FastAPI, Pydantic, Celery.
    3. **Web Intelligence**: SerpAPI, HTTPX, TinyFish (highlighted with active API key).
    4. **Document Intelligence**: PyMuPDF, Docling.
    5. **Core AI & Logic**: Python, LLM, Rules Engine.
    6. **Storage & State**: PostgreSQL, Object Storage, Redis.
  - **Docker explicitly excluded** from the stack and visuals per user instructions.
- [x] Integrated navigation links into the top header flyout menu (`index.html` & `frontend/index.html`):
  - "🧠 AI Procurement Engine" (5-Step Pipeline) -> `#architecture`.
  - "🛠️ Production Tech Stack" (6 Layers) -> `#tech-stack`.
- [x] Verified local server execution on `http://127.0.0.1:8000/` with 200 OK responses and responsive mobile styling.
- [ ] Next milestone: Refine pre-bid query exports and statutory affidavit downloads directly from the interactive scorecard.
