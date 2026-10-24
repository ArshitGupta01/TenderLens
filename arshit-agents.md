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
