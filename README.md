# TenderLens — AI-Powered Indian Public Procurement Qualification & Strategy Engine

> **Deterministic Qualification · Precedence Directed Acyclic Graph (DAG) · Statutory Exemption Shield · 5-Pillar Strategy Studio**  
> Built for the ₹40 Lakh Crore Indian Public Procurement Ecosystem (GeM, CPPP, State e-Procurement Portals).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14_App_Router-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS_v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-fitz_2.0-red.svg)](https://pymupdf.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

---

## Table of Contents

1. [Executive Summary & The ₹40 Lakh Crore Problem](#1-executive-summary--the-40-lakh-crore-problem)
2. [How TenderLens Works (In Plain English)](#2-how-tenderlens-works-in-plain-english)
3. [The Core Algorithmic Breakthrough: Precedence DAG RAG](#3-the-core-algorithmic-breakthrough-precedence-dag-rag)
4. [The 5-Pillar Strategy Studio & 3 Fair Play Equalizers](#4-the-5-pillar-strategy-studio--3-fair-play-equalizers)
5. [End-to-End Technology Stack](#5-end-to-end-technology-stack)
6. [Project Structure & Shadcn / Base-UI Architecture](#6-project-structure--shadcn--base-ui-architecture)
7. [Enterprise Security & Supabase Authentication](#7-enterprise-security--supabase-authentication)
8. [Installation, Local Setup & Stage Demo Guide](#8-installation-local-setup--stage-demo-guide)
9. [API Contract Specifications](#9-api-contract-specifications)
10. [Engineering Implementation & Milestones](#10-engineering-implementation--milestones)
11. [License & Disclaimers](#11-license--disclaimers)

---

## 1. Executive Summary & The ₹40 Lakh Crore Problem

Every year, the Government of India (Ministries, Defense, Railways, PSUs like BHEL/NTPC, Hospitals, and State Departments) procures goods, services, and infrastructure works worth over **₹40 Lakh Crore (>$500 Billion USD)** via public portals including:
* **GeM (Government e-Marketplace)**
* **CPPP (Central Public Procurement Portal)**
* **State e-Procurement Portals** (Karnataka, Maharashtra, UP, etc.)

### The MSME & Startup Qualification Crisis
Although the Government of India has enacted powerful statutory protections for Indian Micro, Small & Medium Enterprises (MSMEs) and DPIIT-recognized Startups—including:
* **GFR 2017 Rule 173(i)** & MoF DoE OM F.20/2/2014-PPD(Pt.): *Mandatory exemption from prior turnover and prior experience criteria.*
* **GFR 2017 Rule 170(i)**: *100% waiver of Earnest Money Deposit (EMD).*
* **Public Procurement Policy for MSEs Order, 2012**: *25% annual mandatory procurement quota with L1+15% price band split-order purchase preference.*
* **DPIIT Public Procurement Order (Make in India), 2017**: *Purchase preference and local content reservation for Class-I Indian manufacturers.*

**Over 68% of startups and MSMEs are disqualified at the technical evaluation stage (L1/L2 stage).**

### Why Indian Tenders Cause Disqualification
1. **Multi-Document Conflict Traps**: Indian tenders are not single documents. A typical tender consists of:
   * Main Notice Inviting Tender (NIT)
   * Buyer-Specific Additional Terms & Conditions (ATC)
   * General Terms & Conditions (GTC)
   * Multiple sequential Corrigenda (amendments) issued days before bid submission.
2. **Ultra Vires Buyer Revocations**: Individual procurement officers frequently insert boilerplate clauses like *"No exemption shall be granted to Startups/MSMEs in this tender"*. Under Indian administrative law and GeM Disclaimer Clauses 12 & 15, such buyer clauses are **ultra vires (legally void ab initio)**. However, bidders don't know how to challenge them before submission.
3. **Proprietary Brand Lock & OEM MAF Cartels**: Tenders often specify single foreign brand models without the statutory phrase *"or equivalent"*, accompanied by restrictive Manufacturer Authorization Form (MAF) requirements designed to shut out independent system integrators.
4. **Working Capital Drain**: Unaware of GFR 170(i) exemptions and IRDAI-approved Insurance Surety Bonds, bidders lock up tens of lakhs in fixed deposit receipts (FDR) and bank guarantees.

**TenderLens solves this deterministically: Discover · Verify Precedence · Decide & Generate Portal-Ready Statutory Packs.**

---

## 2. How TenderLens Works (In Plain English)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  TENDERLENS WORKFLOW                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
 [1. LIVE PORTAL DISCOVERY]
   • Crawls GeM / CPPP in real time via TinyFish & SerpAPI.
   • Downloads and ingests all multi-document attachments (NIT, ATC, Corrigenda).
       │
       ▼
 [2. PRECEDENCE DAG ENGINE (Zero Hallucination)]
   • Builds Directed Acyclic Graph based on Indian legal hierarchy.
   • Corrigendum (Rank 1) automatically overrides Buyer ATC (Rank 3) and Main Tender (Rank 5).
   • Superseded clauses are strikethrough-flagged; only governing terms are evaluated.
       │
       ▼
 [3. DETERMINISTIC GATEKEEPER]
   • 100% mathematical audit of Turnover (₹), Experience (Years), Certifications, and EMD.
   • Applies GFR 173(i) & DPIIT statutory shield rules without LLM guessing.
       │
       ▼
 [4. 5-PILLAR STRATEGY STUDIO & STATUTORY BID PACK]
   • Pre-Bid Legal Representation Pack (CVC/GFR formal challenge letters).
   • Consortium & JV Gap Matchmaker (quantified shortfalls & partner archetypes).
   • Compliance Matrix CSV & Portal-Ready Affidavits (Auto-drafted PDF downloads).
   • EMD Capital & Insurance Surety Optimizer.
   • Competitor Disqualification Forensics.
```

TenderLens operates on three non-negotiable core principles:
1. **Tender Document Precedence**: Later official corrigenda strictly govern over earlier contradictory terms.
2. **Deterministic Checks for Explicit Values**: Monetary turnover, years in business, EMD amounts, and percentage thresholds are calculated with pure mathematical logic—never by hallucinating language models.
3. **Source-Linked Evidence**: Every evaluation score, compliance status, and exemption challenge is backed by exact document, page number, clause reference, and Government of India gazette citations.

---

## 3. The Core Algorithmic Breakthrough: Precedence DAG RAG

Standard semantic Vector RAG (retrieval-augmented generation) fails catastrophically on Indian public tenders. If a 100-page Main RFP mandates *"Turnover of ₹10 Crore"*, and a 1-page Corrigendum issued 3 days later states *"Turnover requirement stands reduced to ₹3 Crore and exempted for Startups"*, semantic vector search frequently matches the 100-page main RFP due to higher keyword density, giving the bidder false disqualification alerts.

TenderLens solves this with a **Topologically Sorted Directed Acyclic Graph (DAG)**:

```
           ┌──────────────────────────────────────┐
           │   Rank 1: Corrigenda & Addenda       │  ◄── HIGHEST LEGAL PRECEDENCE
           └──────────────────┬───────────────────┘
                              │ overrides
                              ▼
           ┌──────────────────────────────────────┐
           │   Rank 2: GeM General Terms (GTC)    │
           └──────────────────┬───────────────────┘
                              │ overrides
                              ▼
           ┌──────────────────────────────────────┐
           │   Rank 3: Buyer Additional ATC       │
           └──────────────────┬───────────────────┘
                              │ overrides
                              ▼
           ┌──────────────────────────────────────┐
           │   Rank 4: Consortium Framework       │
           └──────────────────┬───────────────────┘
                              │ overrides
                              ▼
           ┌──────────────────────────────────────┐
           │   Rank 5: Main RFP / Tender Notice   │  ◄── LOWEST HIERARCHICAL RANK
           └──────────────────────────────────────┘
```

When a user runs a query in the Precedence Workbench (e.g. *"What is the governing turnover requirement and is MSME exempt?"*), TenderLens:
1. Filters candidates using high-dimensional cosine similarity across all ingested chunks.
2. Resolves candidates through the Precedence DAG: if a higher-ranking document (Corrigendum) modifies a lower-ranking document (Buyer ATC), the lower-ranking node is marked `is_superseded = True` with an explicit supersession pointer.
3. Renders the governing term in an authoritative emerald highlight with full statutory citations, and shows superseded terms with strikethrough warnings.

---

## 4. The 5-Pillar Strategy Studio & 3 Fair Play Equalizers

The Strategy Studio (`strategy.html`) empowers bidders with an end-to-end statutory defense toolkit:

### Deterministic Gatekeeper
* **Gate 01: 3-Year Average Turnover**: Evaluates bidder's CA-certified turnover against tender requirement; automatically applies GFR 173(i) startup exemption.
* **Gate 02: Years of Experience**: Compares corporate incorporation date to required operating history.
* **Gate 03: Earnest Money Deposit (EMD)**: Identifies statutory exemption eligibility under GFR Rule 170(i).
* **Gate 04: Make in India (MII) Local Content**: Verifies Class-I (>=50%) or Class-II (>=20%) domestic value addition.
* **Gate 05: Entity Role & OEM Authorization (MAF)**: Analyzes bid-specific vs. standard manufacturer credentials.
* **Gate 06: Mandatory Certifications**: Performs mathematical set-difference between tender-required standards (ISO 9001, BIS, CE, NABL) and bidder credentials.

### Pillar 01: Pre-Bid Legal & Clarification Pack
* Auto-drafts formal representation letters citing CVC Office Memorandum No. 12-02-1-CTE-6 and Ministry of Finance guidelines to challenge anti-competitive buyer terms during the pre-bid clarification window.
* 1-Click **Copy Letter** and **Download .pdf ↓**.

### Pillar 02: Consortium & Capability Gap Matchmaker
* Calculates exact mathematical shortfalls across financial turnover, technical experience, and manufacturing capacity.
* Recommends optimal Joint Venture (JV) and Consortium archetypes (e.g. *Lead Indian EPC Partner + Technology OEM Subcontractor*).

### Pillar 03: Automated Compliance Matrix & Statutory Affidavits Studio
* Clause-by-clause evaluation table with portal-ready CSV export (`tenderlens-compliance-matrix.csv`).
* Auto-drafts four ready-to-sign statutory undertakings:
  1. `BID_SECURITY_DECLARATION` (in lieu of EMD under GFR Rule 170(i))
  2. `DPIIT_MII_LOCAL_CONTENT` (Self-certification for Make in India domestic value addition)
  3. `GFR_144_XI_LAND_BORDER` (Compliance with border sharing restrictions and non-blacklisting)
  4. `STARTUP_MSE_QC_PROFORMA` (Equipment & Quality Control proforma under Annexure-I)
* Instant **Download .pdf ↓** for individual declarations and **Download Final Bid Pack (.pdf) ↓** for a unified submission document.

### Pillar 04: EMD Capital Risk & Working Capital Optimizer
* Analyzes effective cash lock-up, opportunity cost of capital, and highlights the right to submit IRDAI-approved Insurance Surety Bonds in lieu of bank guarantees under GFR Rule 170(i).

### Pillar 05: Competitor Disqualification Forensics
* Public-source intelligence scanning historical L1/L2 technical rejection reasons across government portals to avoid common clerical errors (e.g. missing ICAI UDIN, outdated OEM authorization formats).

### 3 Fair Play Equalizers
* **Pillar 06: Startup Statutory Shield**: Scans and flags buyer ATC clauses attempting to illegally revoke statutory MSME/startup exemptions, issuing formal void revocation notices under GeM GTC Clause 4(xiii)(h).
* **Pillar 07: Zero-History Competency Engine**: Calculates a 100-point composite merit score based on plant capacity, lab standards, and founder pedigree to prove technical equivalence without prior corporate history.
* **Pillar 08: Mandatory 25% MSE Quota Gateway**: Automates split-order matching under the Public Procurement Policy for MSEs Order, 2012, claiming the 25% reserved quota when bidding within the L1+15% price band.

---

## 5. End-to-End Technology Stack

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              TENDERLENS ARCHITECTURE MAP                               │
└────────────────────────────────────────────────────────────────────────────────────────┘

  [CLIENT BROWSERS]
         │
         ▼
  [FRONTEND LAYER]
   • Pure Static UI: index.html, strategy.html, account.html, signin.html, signup.html
   • React / Next.js 14 App Router: components/ui/button.tsx, components/demo.tsx
   • Styling: Tailwind CSS v4 + Custom Enterprise Procurement Design System (styles.css)
   • Components: Shadcn UI + Base-UI Primitive Tactile Controls
         │
         │ REST & Server-Sent Events (SSE)
         ▼
  [FASTAPI BACKEND ORCHESTRATOR (Port 8000)]
   • Framework: FastAPI 2.0.2 + Pydantic v2 + Uvicorn + AsyncIO
   • Health & Configuration: /healthz, /api/v1/auth/config
   • PDF Engine: PyMuPDF (fitz) /api/v1/strategy/export-pdf
         │
         ├──────────────────────────────┬──────────────────────────────┐
         ▼                              ▼                              ▼
  [SEARCH & INGESTION]          [DETERMINISTIC ENGINES]       [PERSISTENCE & JOBS]
   • TinyFish Real-time Crawler  • DeterministicGatekeeper     • Supabase PostgreSQL (RLS)
   • SerpAPI & Tavily Fallback   • PrecedenceDAGBuilder        • Redis Cache (Port 6379)
   • PyMuPDF Clause Chunker      • FairPlayGuardianEngine      • Celery Background Workers
   • Docling TableFormer         • PreBidLegalGenerator        • S3/MinIO Document Vault
```

### Full Dependencies Overview
* **Backend (`pyproject.toml`)**:
  `fastapi`, `uvicorn`, `pydantic`, `pymupdf` (fitz 2.0), `networkx`, `celery`, `redis`, `supabase`, `sse-starlette`, `requests`, `google-genai` (optional LLM verdict auditor).
* **Frontend (`package.json`)**:
  `react`, `react-dom`, `@base-ui/react`, `@tabler/icons-react`, `lucide-react`, `clsx`, `tailwind-merge`, `tailwindcss`, `typescript`, `esbuild`.

---

## 6. Project Structure & Shadcn / Base-UI Architecture

```
TenderLens/
├── backend/                         # FastAPI 2.0.2 Python Backend
│   ├── engine/                      # Deterministic procurement algorithms
│   │   ├── deterministic_gatekeeper.py
│   │   ├── precedence_rag_engine.py
│   │   ├── fair_play_guardian.py
│   │   ├── prebid_legal_generator.py
│   │   ├── compliance_matrix_engine.py
│   │   ├── consortium_matchmaker.py
│   │   ├── emd_capital_optimizer.py
│   │   └── competitor_forensics.py
│   ├── services/                    # Ingestion & external service adapters
│   │   ├── tinyfish_service.py      # Real-time portal crawler
│   │   ├── document_processor.py    # PyMuPDF clause chunker & normalizer
│   │   ├── supabase_service.py      # RLS-isolated cloud database
│   │   └── redis_service.py         # Async cache & task state
│   ├── config.py                    # Environment settings
│   └── main.py                      # FastAPI REST & SSE endpoints
│
├── components/                      # Shadcn UI / React Component Layer
│   ├── ui/                          # Default Shadcn / Base-UI primitives
│   │   ├── button.tsx               # Tactile Base-UI button with hover keyframe motion
│   │   └── doodle-crew-footer.tsx   # Enterprise architectural wordmark footer
│   ├── demo.tsx                     # Interactive component previewer
│   └── tenderlens-hero.tsx          # Dynamic wordmark hero bundle entrypoint
│
├── contracts/                       # Shared Data Model Specifications
│   └── schema.py                    # Pydantic schema contract (BidderProfile, Scorecard)
│
├── data/                            # Raw sample tenders and cache
│   └── raw_tenders/                 # Official GeM, BHEL & ICMR tender PDF benchmarks
│
├── docs/                            # Deep-dive architectural documentation
│   ├── API.md                       # Comprehensive REST endpoint documentation
│   ├── CODE_STYLE.md                # Python & TypeScript coding standards
│   ├── DATABASE.md                  # PostgreSQL schema, RLS policies & tables
│   └── SECURITY.md                  # Supabase RLS, CORS, and credential isolation
│
├── frontend/                        # Complete standalone static mirror for edge deploy
├── public/                          # Static icons, logos, and web manifests
├── supabase/                        # Database migrations & email templates
│   ├── templates/                   # Confirm signup, password recovery, magic link HTML
│   └── setup.sql                    # Production PostgreSQL tables & RLS security rules
│
├── app.js                           # Core live search and audit state management
├── auth.js                          # Supabase Auth client & session management
├── index.html                       # Homepage: Discovery, live search & progress bar
├── strategy.html                    # Strategy Studio & Precedence DAG workbench
├── account.html                     # User profile, company credentials & saved bids
├── signin.html / signup.html        # Enterprise authentication views
├── styles.css                       # Master procurement design system stylesheet
├── components.json                  # Shadcn project configuration
├── tailwind.config.js               # Tailwind CSS theme configuration
└── README.md                        # Master comprehensive project documentation
```

### Why `/components/ui` is the Mandatory Default Path
In the Shadcn UI and Base-UI architecture:
1. **Separation of Primitives vs. Compositions**: `/components/ui` houses standalone, atomic UI primitives (`button.tsx`, `input.tsx`, `card.tsx`) that are framework-agnostic and customizable. Application-specific widgets and composites reside in `/components/` or `/app/`.
2. **CLI Compatibility**: The Shadcn CLI (`npx shadcn@latest add ...`) specifically relies on the `"ui": "@/components/ui"` alias defined in `components.json`. Placing primitives elsewhere breaks automatic component updates and dependency imports.
3. **Consistency Across Portals**: In TenderLens, the tactile button system defined in `components/ui/button.tsx` sets the design tokens (`--primitive-radius-control`, `--primitive-ease`, tactile press micro-interactions) that are mirrored across both React components and the core static procurement stylesheet.

---

## 7. Enterprise Security & Supabase Authentication

TenderLens enforces strict, zero-trust enterprise security standards:

* **Pure Email/Password & Secure Magic Links**: Google OAuth has been completely retired and purged from the codebase to avoid third-party tracking in sensitive government procurement environments.
* **Row-Level Security (RLS)**: Every bidder profile, saved audit, and bookmark is locked to `auth.uid() = user_id`. No user can access or view another bidder's proprietary financial turnover or technical credentials.
* **Zero Secret Exposure**: Only the public Supabase URL and Publishable Anon Key are exposed in client-side code. All service role keys and administrative database connections are restricted to server-side backend operations.
* **Content Security Policy (CSP)**: Hardened headers in `vercel.json` prevent XSS, clickjacking, and unauthorized cross-domain script execution.

---

## 8. Installation, Local Setup & Stage Demo Guide

### Prerequisites
* **Python**: 3.11+
* **Node.js**: 18+ (with `npm`)

### 1. Clone the Repository
```bash
git clone https://github.com/ArshitGupta01/TenderLens.git
cd TenderLens
```

### 2. Backend Setup (FastAPI)
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -e .
# Or via pip directly:
pip install -r <(python -c "import tomli; ...") # or pip install fastapi uvicorn pymupdf pydantic requests
```

### 3. Frontend & Node Setup
```bash
# Install Node dependencies (including Base-UI and Tabler icons)
npm install

# Verify TypeScript compilation
npm run typecheck
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# Backend Server
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
ENVIRONMENT=development

# Web Intelligence & Search
TINYFISH_API_KEY=your_tinyfish_key_here
TAVILY_API_KEY=your_tavily_key_here
SERPAPI_API_KEY=your_serpapi_key_here

# Supabase Auth & Cloud Database
SUPABASE_URL=https://qiwpkvjzqdyguygowzci.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Cache & Storage (Optional for local dev)
REDIS_URL=redis://localhost:6379/0
STORAGE_BACKEND=local
```

### 5. Running the Application for Stage Demonstration

```bash
# Terminal 1: Start FastAPI Backend (with auto-reload)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Static Preview Server
python -m http.server 4177 --bind 127.0.0.1
```

Open your browser to:
* **Interactive Frontend**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or [http://127.0.0.1:4177/](http://127.0.0.1:4177/)
* **Strategy Studio**: [http://127.0.0.1:8000/strategy.html](http://127.0.0.1:8000/strategy.html)
* **API Interactive Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz)

---

## 9. API Contract Specifications

All API payloads conform to strict Pydantic schemas in [`contracts/schema.py`](contracts/schema.py):

| Endpoint | Method | Purpose | Input / Output Schema |
|---|---|---|---|
| `/api/v1/tenders/search` | `POST` | Real-time crawl of public tender notices | `SearchQuery` → `List[DiscoveredTender]` |
| `/api/v1/strategy/preview` | `POST` | Executes Deterministic Gates & 5-Pillar Review | `StrategyPreviewRequest` → `StrategyToolkitResponse` |
| `/api/v1/strategy/export-pdf` | `POST` | Generates official Government of India PDF | `PDFExportRequest` → `application/pdf` |
| `/api/v1/rag/query` | `POST` | Resolves multi-document Precedence DAG | `RAGQueryRequest` → `RAGQueryResponse` |
| `/api/v1/audit/evaluate` | `POST` | Full 5-step qualification evaluation | `EvaluationRequest` → `QualificationScorecard` |
| `/api/v1/auth/config` | `GET` | Returns public Supabase auth configuration | `AuthPublicConfig` |

---

## 10. Engineering Implementation & Milestones

TenderLens engineering has achieved all core milestones across the three project pillars:

### Frontend & UI Experience Milestones
* [x] **Universal Strategy Studio Form Auto-fill**: All 4 form sections (Tender, Bidder, Turnover/Experience criteria, EMD) automatically pre-populate from pre-fetched active tender PDFs and logged-in bidder profiles on page load.
* [x] **Interactive Precedence DAG RAG Workbench**: Real-time conflict resolution demonstrating Corrigendum overrides with smooth scrolling, pulse animations, and authoritative card styling.
* [x] **Complete PDF Export Suite**: Converted all declarations, pre-bid packages, and combined final bid packages from `.md` to formatted `.pdf` documents via both PyMuPDF backend and client-side synthesizers.
* [x] **Tactile Button System**: Integrated Shadcn / Base-UI tactile button architecture (`components/ui/button.tsx`) with press micro-interactions (`active:scale-[0.97]`) and animated icon triggers.
* [x] **Live Stage Demo Telemetry**: Real-time "Progress bar" on live crawl with zero UI freezing and verified fallback benchmarks.
* [x] **Enterprise Dark & Light Mode**: Flawless contrast synchronization, Google typography (`DM Sans`, `DM Mono`, `Newsreader`), and pure SVG navigation icons with zero emojis or buzzwords.

### Backend & Algorithmic Engine Milestones
* [x] **Deterministic Gatekeeper**: Mathematical calculation of 3-year average turnover, operating experience, and CPWD 80/50/40 similar-work ratios with zero hallucinations.
* [x] **Topological Precedence DAG Resolver**: Implemented document ranking hierarchy (Corrigenda > GeM GTC > Buyer ATC > Consortia > Main RFP) with supersession penalty audit trails in NetworkX.
* [x] **Startup Statutory Shield**: Automated detection of ultra vires buyer ATC clauses attempting to illegally override GFR Rule 173(i) and MoF DoE exemptions.
* [x] **Zero-History Competency Proof**: Generates 100-point merit evaluations and Annexure-I Equipment & Quality Control proformas for new companies without prior revenue.
* [x] **25% MSE Subcontracting Quota Gateway**: Automates split-order calculations and tripartite agreement templates under the Public Procurement Policy for MSEs Order, 2012.
* [x] **Real-time Crawl Pipelines**: Multi-portal discovery via TinyFish and SerpAPI with automated document chunking and metadata normalization.

---

## 11. License & Disclaimers

### License
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [LICENSE](LICENSE).

### Statutory Disclaimer
TenderLens is a procurement intelligence and document audit system. While all statutory recommendations and legal representations are generated strictly in accordance with published Government of India orders (General Financial Rules 2017, CVC guidelines, DPIIT orders, and GeM General Terms & Conditions), bidders are advised to review all declarations prior to formal digital signing and portal submission.

---

*TenderLens · Discover · Verify Precedence · Win Public Contracts with Deterministic Proof.*
