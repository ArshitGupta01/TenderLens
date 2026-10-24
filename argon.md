# `single.md` — TenderLens Master Context & Engineering Blueprint for Antigravity

> **Project**: TenderLens (AI-Powered Public Procurement Qualification & Disqualification Engine)[cite: 1]  
> **Team**: Team Traxo · HackIIITD (Round 2)[cite: 1]  
> **Active Agent Scope**: **Mohit & Antigravity AI** (Backend, Web Intelligence, Document Intelligence, Deterministic Qualification Engine & API Orchestration)[cite: 1]  
> **Environment**: Python 3.12 (`uv` package manager) · Windows (`d:\softwares\Tenderlens\TenderLens`)[cite: 1]

---

## 1. Operational Boundaries & Team Topology

TenderLens is strictly partitioned across three non-conflicting domains[cite: 1]. **Antigravity operates exclusively within Mohit's Backend & Intelligence scope[cite: 1].**

| Domain Owner | Responsibilities & Scope | Strict Boundary Rules |
| :--- | :--- | :--- |
| **Mohit & Antigravity** *(Our Sole Scope)* | • **Web Intelligence**: TinyFish API (`TinySearch`, `TinyFetch`, `TinyAgent SSE`, `TinyMonitor`)<br>• **Document Intelligence**: Two-tier `PyMuPDF` (`fitz`) + `IBM Docling` (`TableFormer`) pipeline<br>• **Hybrid Qualification Engine**: Deterministic Python math gates + Structured LLM Clause Auditor<br>• **FastAPI Backend**: REST & real-time SSE endpoints (`backend/`) | **DO NOT** touch `frontend/`, PostgreSQL migrations, or `research/`[cite: 1]. Expose clean FastAPI endpoints adhering strictly to `contracts/schema.py`[cite: 1]. |
| **Arshit** *(Frontend & Data)* | • Next.js 14 Frontend UI (TypeScript, Tailwind CSS, `react-pdf` + SVG bbox overlay)<br>• PostgreSQL Schemas (`users`, `bidder_profiles`, `tender_audits`, `cached_documents`)<br>• Redis Cache, Celery Task Queue, MinIO/S3 Object Storage, Docker Compose | Consumes Mohit's FastAPI endpoints and `QualificationScorecard` JSON[cite: 1]. |
| **Argon** *(Research & Evals)* | • 50-Tender GeM Benchmark Dataset (`research/evals/`)<br>• Prompt iterations (`research/prompts/`) & Competitor teardowns (`BidAssist`, `TrackTender`)<br>• Verification of **≥85% Disqualifier Precision**, **≥80% Disqualifier Recall**, and **≥90% Linked ATC Capture Rate** | Works strictly on branch `feat/argon-research` inside `research/`[cite: 1]. |

---

## 2. Current Repository State & File Tree

```text
TenderLens/
├── contracts/
│   └── schema.py             # LOCKED Shared Pydantic Data Contracts (DO NOT rename fields without sync)
├── research/
│   └── README.md             # Argon's workspace instructions
├── scripts/
│   └── test_tinyfish_key.py  # Key verification utility (Stdlib HTTP test for Search & Fetch)
├── .env.example              # Template for TINYFISH_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY
├── .gitignore                # Ignores .env, .venv, data/raw_tenders/*.pdf, data/cache/
├── .python-version           # Pinned to 3.12
├── arshit-agents.md          # Arshit's Frontend & DB specification
├── MOhit-Agents.md           # Mohit & Antigravity progress tracker
├── main.py                   # Entry point stub
└── pyproject.toml            # UV config (requires-python = ">=3.11")
```

### Current Environment Status
* **UV Initialized**: Python 3.12 pinned[cite: 1].
* **TinyFish API Verification**: `scripts/test_tinyfish_key.py` is built and ready[cite: 1]. *(Note: Last run returned HTTP 401 `INVALID_API_KEY`—ensure `.env` has a fresh key from `https://agent.tinyfish.ai/api-keys` and re-verify via `uv run python scripts/test_tinyfish_key.py`)*[cite: 1].

---

## 3. Locked Shared Data Contracts (`contracts/schema.py`)

All backend services, LLM structured outputs, and FastAPI responses **must** validate against these exact Pydantic models[cite: 1]:

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BidderProfile(BaseModel):
    """Bidder business profile used for automated qualification checks."""
    company_name: str
    entity_type: str  # OEM, Manufacturer, Trader, EPC, Reseller
    is_msme_registered: bool = False
    msme_category: Optional[str] = None  # MICRO, SMALL, MEDIUM
    is_startup_recognized: bool = False
    turnover_year_1_lakhs: float
    turnover_year_2_lakhs: float
    turnover_year_3_lakhs: float
    years_in_business: int
    local_content_percentage: float = 20.0  # Make in India compliance
    held_certifications: List[str] = Field(default_factory=list)  # e.g., ["ISO-9001", "BIS"]

class ClauseCitation(BaseModel):
    """Evidence anchor linking findings to exact source coordinates."""
    document_name: str  # e.g., "Main_Tender.pdf", "Buyer_ATC.pdf", "Corrigendum_1.pdf"
    page_number: int
    clause_id: str
    verbatim_text: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH_DISQUALIFIER
    status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, CONDITIONAL, AMBIGUOUS_MANUAL_REVIEW

class GateResult(BaseModel):
    """Deterministic mathematical rule check (Python verified, zero hallucination)."""
    rule_name: str
    passed: bool
    is_hard_disqualifier: bool
    bidder_value: Any
    required_value: Any
    reason: str
    statutory_citation: Optional[str] = None

class QualificationScorecard(BaseModel):
    """The master output report displayed on frontend and evaluated in benchmarks."""
    tender_id: str
    tender_title: str
    source_portal: str  # "GeM", "CPPP", "BHEL", etc.
    recommendation: str  # "STRONG_BID", "CONDITIONAL_BID", "RED_FLAG_NO_BID"
    score: float  # 0.0 to 5.0
    deterministic_gates: List[GateResult]
    clause_citations: List[ClauseCitation]
    discovered_atc_urls: List[str] = Field(default_factory=list)
    executive_summary: str
```

> **Optional Internal Enhancement (`EvidenceField[T]`)**: Inside `backend/engine/`, you may use an internal generic wrapper `EvidenceField[T]` containing `(value, document_name, precedence_rank, page_number, clause_id, bbox, verbatim_quote, parsing_method)` during Step 03/04 extraction, and then map it cleanly into `GateResult` and `ClauseCitation` for the final `QualificationScorecard` response[cite: 1].

---

## 4. Domain Mechanics: Indian Tender Precedence Hierarchy (DAG)

Indian procurement portals (GeM, CPPP, BHEL, ICMR, Haryana e-Procurement) distribute eligibility rules across multiple files. **Standard flat RAG fails** because a Corrigendum or Buyer ATC overrides baseline Main PDF thresholds.

TenderLens models every tender as a **Versioned Directed Acyclic Graph (DAG)** with strict legal precedence:

| Precedence Rank | Document Layer | Source / Format | Supersession & Disqualification Trap Rules |
| :--- | :--- | :--- | :--- |
| **Rank 1 (Highest)** | **Latest Bid Corrigendum ($C_n$)** | Standalone PDF issued post-NIT (`GeM-Bidding-Corr-...`) | Supersedes all prior corrigenda, ATCs, and baseline bid terms. Common traps: last-minute upward turnover revisions, added BIS/ISO certs, or revocation of MSME exemptions. |
| **Rank 2** | **Prior Corrigenda ($C_1 \dots C_{n-1}$)** | Sequential standalone PDFs | Supersedes baseline bid and initial ATCs unless overridden by $C_n$. |
| **Rank 3** | **Buyer Uploaded ATC / RFP PDF** | External hyperlink embedded in Main GeM PDF (`Click here to view the file`) | Overrides standard template parameters. Contains mandatory OEM Authorization (MAF) formats, local state service center rules, and MII Class-I/II local content splits. |
| **Rank 4** | **Buyer Text-Based ATC Clauses** | Numbered text section at bottom of Main GeM Bid PDF | Modifies main bid parameters unless contradicted by uploaded RFP or Corrigendum. Often defines "similar work" past-project thresholds (80% / 50% / 40%). |
| **Rank 5 (Baseline)** | **Main Tender / GeM Bid PDF** | Primary portal-generated PDF | Default parameters (3-yr average bidder turnover, OEM turnover, EMD, ePBG) governing the bid only in the absence of Rank 1–4 overrides. |

### Temporal & Hierarchical Resolution Rule
* Tag every extracted parameter with `(doc_id, doc_layer_rank, publication_timestamp, page_num, bbox, clause_id)`.
* If two clauses map to the same canonical attribute (e.g., `min_annual_turnover` or `msme_turnover_exemption`), the lower rank number ($Rank(C_j) < Rank(C_i)$) overrides the higher rank number while preserving $C_i$ in the audit trail.
* **Safe Uncertainty Principle**: If two clauses at the *same* precedence rank conflict, or if an uploaded Buyer ATC illegally contravenes overarching GeM General Terms and Conditions (GTC) without explicit exemption authority, set `status = "AMBIGUOUS_MANUAL_REVIEW"`[cite: 1] and recommendation to `"CONDITIONAL_BID"`[cite: 1].

---

## 5. Production Architecture & Implementation Specifications

### Module 1: Web Intelligence Layer (`backend/services/tinyfish_service.py`)[cite: 1]
All TinyFish endpoints authenticate via header `X-API-Key: os.environ["TINYFISH_API_KEY"]`[cite: 1].

1. **Stage 1 — Discovery via `TinySearch` (`GET https://api.search.tinyfish.ai`)**[cite: 1]:
   * **CRITICAL FIX**: Do **not** use `site:` or `-site:` operators inside the `query` parameter (deprecated in production TinySearch).
   * Pass target domains via `include_domains="gem.gov.in,eprocure.gov.in,tenders.bhel.com,icmr.nic.in,etenders.hry.nic.in"`.
   * Reserve `query` strictly for commodity, BOQ, and document-type keywords.
   * Pass a rich `purpose` parameter (up to 2,000 chars) dynamically constructed from `BidderProfile`[cite: 1] (e.g., *"Find active government tender bid PDFs and corrigenda in Haryana for LT/HT electrical switchgear manufacturing requiring BIS certification"*).
   * **Temporal Filter Mutual Exclusivity**: Never combine `recency_minutes` with `after_date` or `before_date` in the same request (throws validation error). Use `recency_minutes=1440` for daily cron discovery OR `after_date="YYYY-MM-DD"` for backfills. Always set `location="IN"` and `language="en"`[cite: 1].

2. **Stage 2 — Deep Document Retrieval via `TinyFetch` (`POST https://api.fetch.tinyfish.ai`)**[cite: 1]:
   * **CRITICAL FIX**: Production `TinyFetch` is a stateless single-hop batch endpoint (`urls`: max 10 per call), **not** an autonomous multi-hop crawler (`links: true` in the slide deck is conceptual shorthand)[cite: 1].
   * Implement the **Recursive URL Queue + Deduplication + Depth Limit ($d \le 2$)** directly in Python (`backend/services/tinyfish_service.py`)[cite: 1].
   * Payload configuration:
     ```json
     {
       "urls": ["https://..."],
       "format": "markdown",
       "iframe_links": true,
       "include_etag_and_last_modified": true
     }
     ```
   * **TTL Caching**: Persist `etag` and `last_modified` validators. On subsequent requests for the same URL, pass `if_none_match` or `if_modified_since` to leverage HTTP 304 (`not_modified: true`) and skip redundant PDF parsing.

3. **Stage 3 — Stealth Browser Fallback via `TinyAgent` (`POST https://agent.tinyfish.ai/v1/automation/run-sse`)**[cite: 1]:
   * Trigger **only** when `TinyFetch` returns `bot_blocked`, `login_required`, or `empty_content` in its `errors[]` array, or when a portal gates ATC downloads behind dynamic JS state transitions.
   * **Cost Circuit Breaker (CRITICAL)**: Default EVA agent `max_steps` is 150 ($2.40/run). You **must** enforce strict limits in the payload:
     ```json
     {
       "url": "https://...",
       "goal": "Navigate to the tender detail page, extract the Main Bid PDF URL, Buyer Uploaded ATC PDF URL, and any Corrigendum PDF URLs.",
       "browser_profile": "stealth",
       "proxy_config": {
         "enabled": true,
         "type": "tinyfish",
         "country_code": "IN"
       },
       "agent_config": {
         "mode": "strict",
         "max_steps": 10,
         "max_duration_seconds": 60
       }
     }
     ```
   * Consume the SSE stream (`STARTED` $\rightarrow$ `STREAMING_URL` $\rightarrow$ `PROGRESS` $\rightarrow$ `COMPLETE`) and relay `streaming_url` to the frontend SSE stream so the user can watch live navigation or fall back to manual upload if a hard CAPTCHA/DSC token blocks execution.

4. **Stage 4 (Optional Pro Feature) — `TinyMonitor` (`POST /v1/monitors`)**:
   * Provision corrigenda delta watches on shortlisted tenders ($0.005/completed check) with condition: *"Alert me when a new Corrigendum PDF link, Addendum, or bid submission date extension is added to this tender page."*

---

### Module 2: Document Intelligence Layer (`backend/services/document_processor.py`)[cite: 1]
To meet the **< 5 minutes SLA** and **90%+ Linked ATC Capture Rate**, implement a **Two-Tier Hybrid Page Router**:

1. **Tier 1 Fast Pass — `PyMuPDF` (`fitz`, ~250–300 pages/sec on CPU)**:
   * Open every downloaded PDF via `pymupdf.open()`.
   * **Hidden Hyperlink Extraction (CRITICAL for GeM ATCs)**: GeM PDFs embed `"Buyer uploaded ATC document: Click here to view the file"` inside the PDF URI annotation dictionary (`page.get_links()` and `span["uri"]`), not as visible plain-text URLs. Extract all URIs on every page and push discovered ATC/Corrigendum URLs back into the Stage 2 `TinyFetch` queue ($d \le 2$)[cite: 1].
   * **Bilingual Column Clipping**: Standard GeM bid PDFs use a two-column layout (Hindi on left, English on right). Use spatial rectangle clipping (`page.get_text("dict", sort=True, clip=rect)`) to cleanly isolate text spans, font sizes, style flags, and `[x0, y0, x1, y1]` bounding boxes[cite: 1].
   * **Page Triage Heuristic**: Inspect vector drawing density (`page.get_drawings()`), character count, and tabular structure per page:
     * If a page is standard prose (e.g., boilerplate GTC clauses), retain the fast `fitz` extraction (`parsing_method = "fitz"`).
     * If a page contains complex eligibility grids, multi-column financial tables, or low character counts (< 100 chars, indicating a scanned stamp-paper annexure), route that specific page index to Tier 2 (`parsing_method = "docling"`).

2. **Tier 2 Structural Pass — `IBM Docling` (`DocumentConverter` + `TableFormer` + OCR)**:
   * Run `Docling` selectively on triaged table/scanned pages to reconstruct exact cell coordinates (`start_row_offset_idx`, `start_col_offset_idx`), preserving header-to-threshold relationships and bounding-box provenance (`prov.page_no`, `prov.bbox`).

---

### Module 3: Hybrid Qualification Engine (`backend/engine/`)[cite: 1]
Split strictly into two files to guarantee zero mathematical hallucination[cite: 1]:

#### A. Deterministic Gatekeeper (`backend/engine/deterministic_gatekeeper.py`)[cite: 1]
All numerical comparisons, unit conversions (Crores $\leftrightarrow$ Lakhs, where $1\text{ Crore} = 100\text{ Lakhs}$), date-window checks, and statutory exemptions execute in pure Python and output `List[GateResult]`[cite: 1]:

1. **3-Year Average Annual Turnover Gate**[cite: 1]:
   * Calculate $\text{Bidder Avg Turnover (Lakhs)} = \frac{\text{turnover\_year\_1\_lakhs} + \text{turnover\_year\_2\_lakhs} + \text{turnover\_year\_3\_lakhs}}{3}$[cite: 1].
   * Normalize extracted `min_annual_turnover` to Lakhs.
   * **Statutory Exemption Branching**:
     * If $\text{Bidder Avg} \ge \text{Required}$: `passed = True`, status `COMPLIANT`[cite: 1].
     * If $\text{Bidder Avg} < \text{Required}$: Check if `bidder.is_msme_registered == True` or `bidder.is_startup_recognized == True`[cite: 1] AND whether the tender grants exemption under **Public Procurement Policy for MSEs Order, 2012 / GFR 2017 Rule 173(i)**[cite: 1].
     * If Buyer ATC/Corrigendum explicitly revokes MSME/Startup turnover exemption, fail the gate (`passed = False`, `is_hard_disqualifier = True`)[cite: 1]. If Main PDF allows exemption but ATC is ambiguous, flag for manual review[cite: 1].

2. **Years in Business / Past Experience Gate**[cite: 1]:
   * Compare `bidder.years_in_business >= required_experience_years`[cite: 1]. Apply MSE/Startup relaxation (GFR Rule 173(i)) unless overridden by Rank 1–3 ATC/Corrigendum[cite: 1].
   * Evaluate standard CPWD/GeM "Similar Work" thresholds against estimated bid value $E$:
     * 1 project $\ge 0.80 E$, OR 2 projects $\ge 0.50 E$, OR 3 projects $\ge 0.40 E$.

3. **EMD (Earnest Money Deposit) Exemption & Liquidity Gate**[cite: 1]:
   * Under **GFR 2017 Rule 170(i)**, registered MSEs (`is_msme_registered == True`) and DPIIT-recognized Startups (`is_startup_recognized == True`) are exempt from EMD in standard GeM/CPPP tenders unless the tender falls under a restricted works category or an overriding ATC requires a Bid Security Declaration[cite: 1].

4. **Make in India (MII) Local Content Gate**[cite: 1]:
   * Under **DPIIT Public Procurement (Preference to Make in India) Order, 2017**[cite: 1]:
     * **Class-I Local Supplier**: `local_content_percentage >= 50.0%`[cite: 1]
     * **Class-II Local Supplier**: `20.0% <= local_content_percentage < 50.0%`[cite: 1]
     * **Non-Local Supplier**: `local_content_percentage < 20.0%`[cite: 1]
   * Verify bidder's class against the tender's eligible supplier classes[cite: 1].

5. **Entity Role & OEM Authorization (MAF) Gate**[cite: 1]:
   * Compare `bidder.entity_type` (`OEM`, `Manufacturer`, `Trader`, `EPC`, `Reseller`) against allowed bidder types[cite: 1]. If `bidder.entity_type in ["Trader", "Reseller", "EPC"]` and `oem_authorization_required == True`, flag as a Conditional/Curable action item requiring a bid-specific MAF prior to submission[cite: 1].

6. **Mandatory Certifications Set-Difference Gate**[cite: 1]:
   * Normalize certification strings (e.g., `"ISO 9001"`, `"ISO-9001:2015"` $\rightarrow$ `"ISO-9001"`) and compute $C_{\text{missing}} = C_{\text{required}} \setminus C_{\text{held}}$[cite: 1]. Any non-empty $C_{\text{missing}}$ triggers `passed = False`, `is_hard_disqualifier = True`[cite: 1].

#### B. Semantic Clause Auditor & Scorecard Synthesizer (`backend/engine/qualification_engine.py`)[cite: 1]
1. Uses Gemini / OpenAI structured outputs to extract raw tender parameters and verbatim `ClauseCitation` anchors from thePrecedence-resolved document chunks[cite: 1].
2. Runs `deterministic_gatekeeper.py` on the extracted parameters + `BidderProfile`[cite: 1].
3. Computes the final `QualificationScorecard`[cite: 1]:
   * **`STRONG_BID` (`score`: 4.0 – 5.0)**: All hard deterministic gates pass (directly or via valid MSE/Startup exemption), zero missing certifications, zero unresolved ATC conflicts[cite: 1].
   * **`CONDITIONAL_BID` (`score`: 2.5 – 3.9)**: Core financial/experience gates pass, but either a curable compliance requirement exists (e.g., obtaining OEM MAF letter) or an `AMBIGUOUS_MANUAL_REVIEW` conflict exists between Main PDF and Buyer ATC[cite: 1].
   * **`RED_FLAG_NO_BID` (`score`: 0.0 – 2.4)**: One or more hard deterministic gates fail (`is_hard_disqualifier == True`) without valid exemption[cite: 1].

---

### Module 4: FastAPI Backend & SSE Streaming (`backend/main.py`)[cite: 1]
Expose the exact REST and SSE endpoints expected by Arshit's Next.js frontend (`arshit-agents.md`) and Mohit's plan (`MOhit-Agents.md`)[cite: 1]:

1. **`POST /api/v1/tenders/search`**[cite: 1]
   * **Request**: `{"keywords": str, "portal": Optional[str] = "gem.gov.in", "location": str = "IN"}`[cite: 1]
   * **Action**: Calls `TinySearch` using `include_domains` and `purpose`[cite: 1].
   * **Response**: List of discovered tenders (`title`, `url`, `snippet`, `source_portal`)[cite: 1].

2. **`POST /api/v1/tenders/fetch`**[cite: 1]
   * **Request**: `{"tender_url": str, "max_depth": int = 2}`
   * **Action**: Executes Stage 2 `TinyFetch` + `PyMuPDF` link extraction + Stage 3 `TinyAgent` fallback (if blocked)[cite: 1].
   * **Response**: Extracted document tree, discovered child ATC/Corrigendum URLs, and parsed clause chunks[cite: 1].

3. **`POST /api/v1/audit/evaluate`**[cite: 1]
   * **Request**:
     ```json
     {
       "tender_url": "[https://gem.gov.in/](https://gem.gov.in/)...",
       "tender_name": "Supply & Installation of High Voltage Transformers",
       "bidder_profile": { ... BidderProfile ... }
     }
     ```
   * **Action**: Runs full 5-step pipeline (or dispatches async task with `task_id` for SSE tracking) and returns a complete `QualificationScorecard` JSON matching `contracts/schema.py`[cite: 1].

4. **`GET /api/v1/audit/stream/{task_id}`**[cite: 1]
   * **Action**: Server-Sent Events (`text/event-stream`) endpoint streaming live pipeline stage transitions to Arshit's UI[cite: 1]:
     * `STAGE_1_DISCOVERING` $\rightarrow$ `STAGE_2_INGESTING_ATCS` (with live `streaming_url` if TinyAgent triggers) $\rightarrow$ `STAGE_3_HYBRID_PARSING` $\rightarrow$ `STAGE_4_DETERMINISTIC_GATES` $\rightarrow$ `STAGE_5_FINAL_SCORECARD`[cite: 1].

---

## 6. Ordered Execution Checklist for Antigravity

Execute the following steps sequentially in `d:\softwares\Tenderlens\TenderLens`[cite: 1]:

- [ ] **Step 1: Install Core Dependencies via UV**[cite: 1]
  ```bash
  uv add fastapi uvicorn[standard] httpx pymupdf pydantic pydantic-settings python-dotenv google-genai openai sse-starlette
  ```
  *(Add `docling` optionally or with a graceful fallback toggle so Tier 1 `pymupdf` works immediately even on machines without heavy OCR weights installed).*

- [ ] **Step 2: Configuration & Settings (`backend/config.py`)**
  * Load `.env` via `pydantic-settings` (`TINYFISH_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `BACKEND_PORT=8000`)[cite: 1].
  * Update `scripts/test_tinyfish_key.py` to replace `"query": "site:gem.gov.in tender solar"` with `"query": "tender solar", "include_domains": "gem.gov.in"` per TinySearch production spec[cite: 1].

- [ ] **Step 3: Build Web Intelligence Service (`backend/services/tinyfish_service.py`)**[cite: 1]
  * Implement async `httpx.AsyncClient` wrappers for:
    * `search_tenders()` (`TinySearch` with `include_domains`, `purpose`, `location="IN"`, `recency_minutes`)[cite: 1].
    * `fetch_tender_recursive()` (`TinyFetch` batching up to 10 URLs, depth limit $d \le 2$, `etag`/`last_modified` support)[cite: 1].
    * `run_stealth_agent_sse()` (`TinyAgent` `/v1/automation/run-sse` with `mode="strict"`, `max_steps=10`, `country_code="IN"`)[cite: 1].

- [ ] **Step 4: Build Document Intelligence Processor (`backend/services/document_processor.py`)**[cite: 1]
  * Implement `PyMuPDF` (`fitz`) page parser that extracts text blocks, `[x0, y0, x1, y1]` bounding boxes, clause headings (`Clause X.X`, `Section Y`), and hidden PDF annotation hyperlinks (`page.get_links()`) for linked Buyer ATCs[cite: 1].
  * Implement Precedence Rank classifier (`Rank 1: Latest Corrigendum` $\rightarrow$ `Rank 5: Main Bid PDF`) and Tier 2 `Docling` table fallback hook.

- [ ] **Step 5: Build Deterministic Gatekeeper (`backend/engine/deterministic_gatekeeper.py`)**[cite: 1]
  * Implement pure-Python verification functions returning `List[GateResult]` for:
    1. 3-Year Average Turnover + MSE/Startup Exemption (GFR Rule 173(i))[cite: 1]
    2. Years in Business / Experience + MSE/Startup Relaxation[cite: 1]
    3. EMD Exemption check (GFR Rule 170)[cite: 1]
    4. Make in India (MII) Class-I ($\ge 50\%$) / Class-II ($\ge 20\%$) check (DPIIT Order 2017)[cite: 1]
    5. Entity Type & OEM MAF check[cite: 1]
    6. Mandatory Certifications set-difference check (`ISO-9001`, `BIS`, etc.)[cite: 1]

- [ ] **Step 6: Build Hybrid Qualification Engine (`backend/engine/qualification_engine.py`)**[cite: 1]
  * Implement structured LLM extraction (using `GEMINI_API_KEY` or `OPENAI_API_KEY` with a deterministic regex/heuristic fallback if LLM keys are absent during local offline tests)[cite: 1].
  * Implement Precedence DAG conflict resolution and Safe Uncertainty flagging (`AMBIGUOUS_MANUAL_REVIEW`)[cite: 1].
  * Combine `GateResult` list and `ClauseCitation` list into the final `QualificationScorecard`[cite: 1].

- [ ] **Step 7: Build FastAPI Application (`backend/main.py`) & Update `MOhit-Agents.md`**[cite: 1]
  * Wire CORS middleware (allowing Arshit's `http://localhost:3000` Next.js frontend)[cite: 1].
  * Mount `/api/v1/tenders/search`, `/api/v1/tenders/fetch`, `/api/v1/audit/evaluate`, and `/api/v1/audit/stream/{task_id}`[cite: 1].
  * Write unit tests for `deterministic_gatekeeper.py` and end-to-end API route tests, then log all completed milestones in `MOhit-Agents.md`[cite: 1].