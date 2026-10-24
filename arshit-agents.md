# arshit-agents.md — Arshit's Memory & Progress Tracker

> **Project**: TenderLens (AI-Powered Tender Qualification & Disqualification Engine)  
> **Team**: Team Traxo · HackIIITD (Round 2)  
> **Agent Owner**: Arshit  
> **Domain**: Frontend (Next.js), Database (PostgreSQL / Migrations), Object Storage, Async Job Queues & UI Experience  
> **Status**: Static prototype with optional live search; production frontend and full API integration remain pending

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

### Presentation prototype update — 2026-10-24
- [x] Added a responsive static website in the repository root with an illustrative qualification report, evidence details, and audience profiles.
- [x] Made prototype limitations clear: optional live search is connected; uploads, automated audits, accounts, and saved reports are not connected.
- [ ] Next application milestone remains a Next.js frontend wired to the planned backend APIs; the static prototype is not that application.

### Interactive prototype expansion — 2026-10-24
- [x] Added a searchable, category-filtered sample tender desk with in-page previews and visit-only saved examples.
- [x] Added an interactive five-layer precedence explorer and a local six-item bidder readiness checklist.
- [x] Added Lenis smooth scrolling, reading progress, section reveals, active navigation, and a back-to-top control with reduced-motion support.
- [x] Updated privacy and terms notices for the local-only interactions and locally bundled Lenis library.
- [ ] Next application milestone remains a real frontend wired to implemented APIs; eligibility evaluation is not connected to the website.

### Readability and guide update — 2026-10-24
- [x] Increased body and control text sizes and rewrote the report labels and document-order explanation in plain language.
- [x] Added a saved light/dark theme preference, an easy-start guide, a short glossary, quick-answer accordion, and clearer privacy and terms pages.
- [x] Kept the tender examples and company checklist local and labeled as fictional. Added an optional search form that sends only the phrase and selected portal to the configured backend.
- [x] Added local preview instructions and linked the guide from the main navigation and footer.
- [x] Reviewed the desktop and narrow preview layouts; adjusted the navigation and footer to avoid wrapping and horizontal overflow.
- [ ] A real company profile, file upload, account, saved audit, and connected eligibility review remain future work.

### Tablet layout refinement — 2026-10-24
- [x] Added an 851–1100px breakpoint that replaces the crowded desktop navigation with the menu button and gives the hero a full-width reading column.
- [x] Reviewed the change against the supplied 1056px screenshot and checked the existing narrow local preview; a dedicated 1056px embedded-browser viewport was unavailable.
- [ ] Recheck tablet and desktop layouts in a resizable browser preview when available.

- [ ] Initialize Next.js project in `frontend/` (TypeScript, Tailwind CSS, Lucide icons)
- [ ] Build Bidder Profile configuration screen (Turnover, MSME status, Certifications)
- [ ] Build Search & Ingestion tracker with live SSE progress bar
- [ ] Implement the Interactive Scorecard view (Badges, Deterministic Gate accordions, Clause Inspector)
- [ ] Set up Docker Compose (`postgres`, `redis`, `minio`, `frontend`, `backend`)
- [ ] Wire database models and save audit results history
