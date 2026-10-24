# TenderLens API Reference & Integration Guide
===============================================

## 1. Base Configuration
- **Development**: `http://localhost:8000` or `http://127.0.0.1:8000`
- **Interactive Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Response Format**: `application/json` (or `text/event-stream` for SSE)
- **API Prefix**: `/api/v1`

## 2. Authentication & Authorization
Protected persistence routes accept an `Authorization: Bearer <Supabase_JWT>` header. The backend validates the JWT with Supabase Auth and enforces Row-Level Security:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 3. Endpoints

### 3.1 Health & Public Configuration
- **`GET /healthz`**
  - **Description**: Returns server health, environment, and Supabase / TinyFish connectivity status.
  - **Response 200**:
    ```json
    {
      "status": "healthy",
      "service": "TenderLens Backend Engine",
      "version": "1.0.3",
      "environment": "development",
      "tinyfish_configured": true,
      "supabase_configured": true,
      "supabase_status": { "configured": true, "connected": true, "free_tier_ready": true }
    }
    ```
- **`GET /api/v1/auth/config`**
  - **Description**: Exposes public Supabase URL, publishable key, and optional Google Client ID to frontend clients.
  - **Response 200**:
    ```json
    {
      "configured": true,
      "supabase_url": "https://qiwpkvjzqdyguygowzci.supabase.co",
      "publishable_key": "sb_publishable_...",
      "google_client_id": "747711661688-...apps.googleusercontent.com"
    }
    ```

---

### 3.2 Tender Discovery & Crawling
- **`POST /api/v1/tenders/search`**
  - **Payload**: `{"keywords": "33kV substation switchgear", "portal": "gem.gov.in", "limit": 10}`
  - **Response 200**: List of discovered tender notices (`title`, `url`, `snippet`, `source_portal`, `published_date`).
- **`POST /api/v1/tenders/fetch`**
  - **Payload**: `{"tender_url": "https://gem.gov.in/...", "max_depth": 2}`
  - **Response 200**: List of crawled tender documents and child ATCs/corrigenda in markdown.

---

### 3.3 Strategy Studio & 5-Pillar Endpoints
- **`POST /api/v1/strategy/preview`**
  - **Description**: Evaluates deterministic gates and synthesizes all 5 Strategy Pillars from explicit bidder profile and tender criteria.
  - **Payload**:
    ```json
    {
      "tender_id": "GEM/2026/B/900123",
      "tender_title": "BHEL Substation Panels",
      "source_portal": "BHEL",
      "bidder_profile": { ... },
      "criteria": { ... }
    }
    ```
  - **Response 200**: `StrategyToolkitResponse` containing:
    - `deterministic_gates`: List of gate results (3Y Avg Turnover, Experience, GFR 170 EMD, MII Class-I/II, OEM MAF, Mandatory Certs, CPWD 80/50/40).
    - `prebid_legal_pack`: Statutory challenge representations & formal Markdown letter.
    - `consortium_recommendation`: Quantified shortfalls & illustrative partner archetypes.
    - `compliance_binder`: Compliance matrix rows, CSV export string, and ready-to-sign statutory affidavit drafts.
    - `emd_capital_report`: Working capital lock-up, opportunity cost, and recommended instrument.
    - `competitor_forensics`: Historical authority-specific rejection traps & countermeasures.
- **`POST /api/v1/strategy/prebid-queries`**: Generates Pillar 01 pre-bid legal pack.
- **`POST /api/v1/strategy/consortium-match`**: Generates Pillar 02 consortium recommendations.
- **`POST /api/v1/strategy/compliance-matrix`**: Generates Pillar 03 compliance binder.
- **`POST /api/v1/strategy/emd-optimizer`**: Generates Pillar 04 EMD capital risk report.
- **`GET  /api/v1/strategy/forensics`**: Returns Pillar 05 competitor rejection forensics (with optional `live_search=true`).

---

### 3.4 Precedence DAG RAG Endpoints
- **`POST /api/v1/rag/query`**
  - **Payload**: `{"tender_id": "...", "query": "...", "explicit_chunks": [...], "enable_gemini": false}`
  - **Response 200**: Resolves multi-document conflicts using Precedence DAG ordering (Rank 1 Corrigendum overrides Rank 5 Main PDF).
- **`POST /api/v1/rag/precedence-graph`**
  - **Payload**: `{"tender_id": "...", "chunks": [...]}`
  - **Response 200**: Complete DAG topology including nodes, supersession edges, and conflict classifications.

---

### 3.5 Cloud Persistence (Supabase + RLS)
- **`POST /api/v1/audits/save`**: Saves scorecard into `public.tender_audits`.
- **`GET  /api/v1/audits/user/{user_id}`**: Retrieves user's audit history.
- **`GET  /api/v1/profile/sync/{user_id}`**: Loads stored BidderProfile from `public.profiles`.
- **`POST /api/v1/profile/sync`**: Upserts BidderProfile into `public.profiles`.
