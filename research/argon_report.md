# Argon Research Report

Source: https://share.gemini.google/1s2mmq1tTaM6

---

TenderLens Architectural Blueprint and Strategic Market Analysis: AI-Powered Public Procurement Qualification
Executive Summary and Problem Formulation

Public procurement across India—spanning the Government e-Marketplace (GeM), the Central Public Procurement Portal (CPPP), Public Sector Undertaking (PSU) portals such as Bharat Heavy Electricals Limited (BHEL) and the Indian Council of Medical Research (ICMR), and state-level e-procurement systems—presents a structural asymmetry for Micro, Small, and Medium Enterprises (MSMEs). While discovering open tenders has been largely commoditized by search aggregators and notification bots, verifying whether a specific enterprise legally and technically qualifies to bid remains a fragmented, manual, and high-risk process.   

In the Indian tendering ecosystem, a solicitation is rarely self-contained within a single Portable Document Format (PDF) file. Instead, material eligibility conditions are distributed across a baseline Notice Inviting Tender (NIT) or GeM Bid Document, hyperlinked Buyer Added Bid Specific Additional Terms and Conditions (ATC) files, and sequential corrigenda issued up to hours before bid closure. When an MSME, Original Equipment Manufacturer (OEM), Engineering, Procurement, and Construction (EPC) contractor, or Information Technology (IT) system integrator overlooks a nested sub-clause or an amended financial threshold, the consequences extend beyond administrative rejection. Disqualification during technical evaluation results in sunk bid-preparation engineering hours, forfeiture or prolonged lock-up of working capital committed to Earnest Money Deposits (EMD), and missed revenue cycles.   

TenderLens addresses this verification bottleneck by shifting the paradigm from passive tender discovery to evidence-backed, pre-bid qualification and disqualification auditing. Designed as a decision-support engine rather than an autonomous legal adjudicator, TenderLens ingests a bidder's structured corporate profile, recursively retrieves the complete hierarchy of tender documents via the TinyFish web intelligence stack, parses complex multi-column layouts and tables through a hybrid PyMuPDF and IBM Docling pipeline, and evaluates compliance using deterministic Python rules paired with Large Language Model (LLM) clause analysis. Every identified risk, met criterion, or contractual contradiction is anchored to its exact source document, page number, and clause reference, routing ambiguous or conflicting stipulations to human review before capital is committed.   

Domain Mechanics: Contractual Precedence and Eligibility Traps in Indian Tenders

To engineer a reliable qualification engine capable of achieving TenderLens's target of 85%+ disqualifier precision and 80%+ disqualifier recall, the system must account for how Indian procurement portals structure and amend solicitation documents. On GeM and allied PSU portals—including BHEL, Bharatiya Reserve Bank Note Mudran Private Limited, the Indian Renewable Energy Development Agency, Mazagon Dock Shipbuilders, and the National Industrial Corridor Development Corporation—tender rules are governed by a strict legal hierarchy rather than uniform document weighting.   

The Tripartite Document Structure and Supersession Hierarchy

A standard GeM bid document is generated automatically from portal templates, containing standardized boilerplate alongside parameterized fields for minimum average annual turnover, past experience years, and Earnest Money Deposit amounts. However, procuring authorities routinely customize these baseline requirements at the bottom of the main bid PDF under the section header "Buyer Added Bid Specific Terms and Conditions" (ATC). This section bifurcates into two distinct data modalities that must be parsed concurrently. The first modality consists of Buyer Added Text-Based ATC Clauses, which are numbered textual stipulations appended directly inside the main GeM PDF. The second modality is the Buyer Uploaded ATC Document, an external hyperlink embedded inside the PDF—typically rendered as "Buyer uploaded ATC document: Click here to view the file"—which points to a separate, multi-page Request for Proposal (RFP), technical specification book, or scanned annexure hosted on the portal's object store.   

When a procuring entity modifies technical specifications, extends deadlines, or alters financial qualification thresholds after publication, the portal issues sequential Bid Corrigendum files (such as GeM-Bidding-Corr-...). These files carry an explicit legal override clause stating that the "Following terms and conditions supersede all existing 'Buyer added Bid Specific Terms and conditions' given in the bid document or any previous corrigendum". Simultaneously, portal governance stipulates that while buyer-specific clauses override baseline parameters, any ATC clause that directly contravenes the overarching GeM General Terms and Conditions (GTC) without authorized exemption is legally contentious, and conflicts between the main GeM ATC and the buyer-uploaded RFP are governed by explicit order-of-precedence clauses (for example, "in case of same clause, the clause mentioned in Corrigendum 1 will supersede").   

Document Layer	Typical File Format & Location	Legal Precedence Rank	Common Disqualification Traps Embedded in Layer
Latest Bid Corrigendum (
Corr
𝑁
Corr
N
	​

)	

Standalone PDF issued post-NIT via portal notification

	

Rank 1 (Highest): Supersedes all prior corrigenda, ATCs, and baseline bid terms

	

Last-minute upward revision of turnover thresholds, addition of mandatory ISO/BIS test certificates, or relaxation/removal of MSME exemptions.


Prior Corrigenda (
Corr
1
…
𝑁
−
1
Corr
1…N−1
	​

)	

Sequential standalone PDFs

	

Rank 2: Supersedes baseline bid and initial ATCs unless overridden by 
Corr
𝑁
Corr
N
	​


	

Partial modifications to Bill of Quantities (BOQ) scope or experience calculation windows.


Buyer Uploaded ATC / RFP PDF	

Hyperlinked external PDF inside the main bid document

	

Rank 3: Overrides standard bid template parameters; subject to GeM GTC compliance

	

Mandatory OEM Authorization (MAF) formats, local service center requirements in specific states, and Make in India (MII) Class-I/Class-II local content percentages.


Buyer Text-Based ATC Clauses	

Embedded text section at the end of Main GeM Bid PDF

	

Rank 4: Modifies main bid parameters unless contradicted by uploaded RFP or Corrigendum

	

Specific past-project similarity definitions (e.g., one project at 
80
%
80%, two at 
50
%
50%, or three at 
40
%
40% of estimated bid value).


Main Tender / GeM Bid PDF	

Primary portal-generated PDF document

	

Rank 5 (Baseline): Default parameters governing the bid in the absence of overrides

	

Baseline 3-year average bidder turnover, OEM average turnover, EMD amount, and ePBG percentage.

  
Failure of Naive Retrieval-Augmented Generation (RAG)

Standard vector-database RAG pipelines fail catastrophically on this document topology. If a tender corpus is chunked and embedded into a flat vector store without version awareness, a semantic query for "minimum annual turnover requirement" will retrieve both the baseline Main PDF clause (for instance, requiring ₹5 Crore with MSME exemption enabled) and a Corrigendum 2 clause (for instance, raising the requirement to ₹10 Crore and revoking turnover exemption under specialized technical category rules). Because both chunks exhibit high cosine similarity to the query, a naive LLM synthesizer frequently averages, hallucinates, or selects the wrong threshold.   

TenderLens resolves this by treating the tender document set as a versioned Directed Acyclic Graph (DAG). Every extracted clause is tagged with a metadata tuple:   

𝜏
𝑖
=
(
doc_id
,
doc_type
,
version_rank
,
page_no
,
clause_id
,
bbox
)
τ
i
	​

=(doc_id,doc_type,version_rank,page_no,clause_id,bbox)

During Step 04 (Hybrid Verification Engine), when two clauses map to the same canonical attribute (such as min_annual_turnover or iso_certification_required) with divergent predicates, the rules engine applies temporal and hierarchical resolution: if 
version_rank
(
𝜏
𝑎
)
>
version_rank
(
𝜏
𝑏
)
version_rank(τ
a
	​

)>version_rank(τ
b
	​

) and 
𝜏
𝑎
τ
a
	​

 contains an explicit supersession marker, 
𝜏
𝑎
τ
a
	​

 overrides 
𝜏
𝑏
τ
b
	​

 while preserving 
𝜏
𝑏
τ
b
	​

 in the audit trail as a superseded historical clause. If two clauses within the same precedence rank conflict—or if an uploaded ATC directly violates GeM GTC exemptions without clear precedence—TenderLens enforces its "Safe Uncertainty" design principle, flagging the item as a Conditional Bid conflict for mandatory human review.   

Web Intelligence Layer: Productionizing the TinyFish API Stack

A foundational pillar of the TenderLens architecture is its three-stage integration with TinyFish (tinyfish.ai), an enterprise web execution platform that consolidates live search (TinySearch), content extraction (TinyFetch), remote browser control (TinyBrowser), autonomous goal-driven navigation (TinyAgent), and scheduled change detection (TinyMonitor) behind a single API key (X-API-Key) and unified wallet. While the initial TenderLens proposal outlines a high-level three-stage workflow—Stage 1 TinySearch ($0.00/call), Stage 2 TinyFetch Recursive ($0.00/call), and Stage 3 TinyAgent Stealth SSE ($0.016/step)—a granular inspection of the production TinyFish API specifications (docs.tinyfish.ai) reveals critical parameter constraints, rate limits, and architectural optimizations required for production deployment.   

Stage 1: High-Precision Discovery via TinySearch

In Stage 1, TenderLens queries government portals to discover live tenders matching the bidder's sector, location, and capacity profile. Rather than relying on cached secondary indexes, TinySearch (GET https://api.search.tinyfish.ai) executes real browser-rendered queries against Google's live index and returns structured JSON (position, site_name, title, snippet, url) in under 0.5 seconds.   

To align TenderLens's implementation with the current TinySearch API schema, three specific engineering refinements are necessary. First, the system must transition away from deprecated site: or -site: operators embedded inside the query string for domain filtering. Instead, TenderLens should pass a comma-separated list of target procurement domains via the native include_domains parameter (such as include_domains="gem.gov.in,eprocure.gov.in,tenders.bhel.com,icmr.nic.in,etenders.hry.nic.in") while reserving the query string strictly for commodity, BOQ, and document-type keywords. Second, because terse keyword combinations often return generic portal landing pages rather than active Notice Inviting Tender PDFs, TenderLens should exploit the optional purpose parameter (up to 2,000 characters), which supplies the underlying task intent to TinyFish's ranking engine. Passing a dynamically constructed purpose string derived from the Step 01 Bidder Profile—such as "Find active government tender bid PDFs and corrigenda in Haryana for LT/HT electrical switchgear manufacturing requiring BIS certification"—substantially increases top-10 result relevance. Third, the orchestration engine must enforce mutual exclusivity across temporal filters: while TinySearch offers recency_minutes (accepting integers from 1 to 5,256,000) and calendar bounds after_date and before_date (YYYY-MM-DD), the API strictly rejects requests that combine recency_minutes with calendar date bounds. TenderLens should therefore standardize on recency_minutes=1440 for daily incremental cron discovery and after_date for historical benchmark backfills, paired with location="IN" and language="en".   

Stage 2: Deep Document Retrieval and Link Graph Extraction via TinyFetch

Once candidate tender URLs are queued, Stage 2 utilizes TinyFetch (POST https://api.fetch.tinyfish.ai) to retrieve HTML portal pages and directly accessible PDFs at $0.00 per call. TinyFetch accepts batches of up to 10 URLs per request and natively extracts text from both HTML and PDF content types into token-efficient "markdown", "html", or "json" (document tree) formats.   

A vital technical distinction emerges between the hackathon presentation's conceptual shorthand (TinyFetch Recursive with links:true) and the actual TinyFetch production API. In production, TinyFetch operates as a stateless single-hop batch extraction endpoint—supporting iframe_links: true for embedded frames, include_selectors, and exclude_selectors up to 20 CSS selectors, alongside a per-URL wall-clock timeout budget from 1 to 110,000 milliseconds—rather than an autonomous multi-hop web crawler. Consequently, the "URL Queue + Deduplicate + Depth Limit" module depicted in TenderLens's architecture diagram must reside inside the FastAPI and Celery orchestration layer. When TinyFetch returns the Markdown or JSON document tree of a primary GeM or CPPP tender landing page, a Python URI parser extracts all child hyperlinks matching ATC, Corrigendum, or BOQ patterns at depth 
𝑑
=
1
d=1, deduplicates them by canonical URL, and dispatches a subsequent batch call (client.fetch.get_contents(urls=child_urls, format="markdown")) up to a hard depth limit of 
𝑑
max
⁡
=
2
d
max
	​

=2.   

Furthermore, TinyFetch provides native protocol support for TenderLens's scalability requirement of TTL Caching for versioned PDFs. By setting include_etag_and_last_modified: true on initial retrieval, TenderLens can persist the origin server's etag and last_modified validators in PostgreSQL and Redis alongside each tender's document record. When subsequent users request an audit of the same tender, TenderLens passes if_none_match or if_modified_since in the TinyFetch payload. If the government portal returns HTTP 304 Not Modified, TinyFetch flags not_modified: true in the response, allowing TenderLens to bypass redundant PDF downloading, Docling layout parsing, and LLM evaluation entirely.   

Stage 3: Selective Interactive Fallback via TinyAgent Stealth SSE

Government procurement portals frequently gate search filters, session cookies, or linked ATC downloads behind dynamic JavaScript state transitions that return bot_blocked, login_required, or empty_content errors in standard HTTP fetching. When TinyFetch returns one of these specific error codes in its errors[] array, TenderLens triggers Stage 3: TinyAgent (POST https://agent.tinyfish.ai/v1/automation/run-sse). Achieving 89.9% overall accuracy on the Online-Mind2Web benchmark—and 81.9% on hard tasks, outperforming OpenAI Operator (43.2%) and Anthropic Claude (32.4%)—TinyAgent translates natural-language goals into live browser interactions.   

TinyFish API Component	Production Endpoint & Method	Key Request Parameters Utilized by TenderLens	Rate Limits (Default vs. Startup Tiers)	Billing & Cost Structure
TinySearch	

GET https://api.search.tinyfish.ai

	

query, location="IN", language="en", include_domains, purpose, recency_minutes or after_date

	

30 req/min (Default)




120 req/min (Startup Tier 1 & 2)

	

$0.00 / call up to 12,000 req/day; positive wallet balance required beyond cap


TinyFetch	

POST https://api.fetch.tinyfish.ai

	

urls (max 10/call), format="markdown", purpose, iframe_links=true, include_etag_and_last_modified=true, if_none_match

	

150 URLs/min (Default)




600 URLs/min (Startup Tier 1 & 2)

	

$0.00 / call for all standard extractions


TinyAgent (SSE / Async)	

POST https://agent.tinyfish.ai/v1/automation/run-sse (or /run-async)

	

url, goal, output_schema, browser_profile="stealth", proxy_config={"enabled": true, "type": "tinyfish", "country_code": "IN"}, agent_config={"mode": "strict", "max_steps": 15}

	

50 concurrent runs (Startup Tier 1 & 2)

	

$0.016 / step ($0.048–$0.080 per 3–5 step run); 50% off for 24 mos on Startup Tier 2


TinyMonitor	

POST /v1/monitors & POST /v1/monitors/{id}/runs

	

Target URL or topic query, plain-language alert condition, schedule frequency, webhook_url

	

Up to 50 active monitors per account

	

$0.005 / completed check (includes LLM change judgment + webhook; failed checks unbilled)

  

To prevent runaway credit consumption when navigating complex government portals, TenderLens must enforce strict execution guardrails in the TinyAgent request payload. By default, TinyFish's EVA agent permits up to 150 steps per run—which, if caught in a portal redirect loop, would consume $2.40 for a single tender. TenderLens should explicitly configure agent_config.mode: "strict", which instructs the agent to fail fast when blocked rather than exploring costly workarounds, and set agent_config.max_steps: 10 alongside agent_config.max_duration_seconds: 60, capping worst-case agent expenditure at $0.16 per fallback invocation. Because many Indian PSU and NIC-hosted portals block or throttle foreign IP ranges, passing browser_profile: "stealth" with proxy_config: {"enabled": true, "type": "tinyfish", "country_code": "IN"} routes the cloud browser session through Indian exit nodes.   

When invoked via /v1/automation/run-sse, TinyAgent emits Server-Sent Events in the sequence STARTED 
→
→ STREAMING_URL 
→
→ PROGRESS 
→
→ COMPLETE, where streaming_url provides a live browser preview valid for 24 hours. If a portal presents a hard CAPTCHA or requires a physical Class-III Digital Signature Certificate (DSC) token that cannot be automated, strict mode terminates the run cleanly, and TenderLens surfaces the streaming_url or transitions the user to the manual PDF upload fallback exactly as specified in TenderLens's risk controls. Furthermore, to power the MSME Pro subscription tier's "Delta Alerts: Corrigenda Watch" feature without engineering a bespoke cron-scraping loop, TenderLens can programmatically provision a TinyMonitor (POST /v1/monitors) on each shortlisted tender URL with a natural-language trigger condition such as "Alert me when a new Corrigendum PDF link, Addendum, or bid submission date extension is added to this tender page". At $0.005 per completed check—which includes LLM change judgment and webhook delivery, while failed checks remain unbilled—checking an active tender twice daily for 10 days prior to bid closure costs just $0.10 (~₹8.40) and automatically initiates a Celery delta-reverification workflow whenever an amendment is published.   

Document Intelligence Pipeline: Hybrid PyMuPDF and Docling Extraction

While TinyFetch extracts raw text from simple PDFs, Indian tender documents present severe layout challenges that destroy structural context when flattened into plain text. Main GeM bid PDFs are formatted as dense two-column key-value grids (often bilingual in Hindi and English), while linked ATCs and PSU specifications contain multi-page financial matrices, nested technical compliance tables, and scanned stamp-paper annexures. TenderLens resolves this by pairing PyMuPDF (fitz) with IBM Docling (v2) inside its Document Intelligence layer, balancing computational throughput against structural fidelity to meet the < 5 minutes average processing time target per tender.   

Page-Level Triage and Hybrid Routing Mechanics

Running a deep neural layout and table-structure model across a 300-page PSU tender specification on standard CPU workers can consume several minutes per document, threatening the < 5 minutes end-to-end service-level objective. Conversely, C-based MuPDF bindings (pymupdf and pymupdf4llm-c) process 250 to 300 pages per second on CPU, extracting raw text spans, font sizes, style flags (bold, italic, monospace), embedded URI hyperlinks, and [x0, y0, x1, y1] bounding boxes almost instantaneously. However, when evaluated as a standalone parser on complex document layouts, the PyMuPDF baseline achieves only a 70.2 F1 score (72.4 precision and 68.1 recall), frequently interleaving multi-column clauses or failing silently when tables and figures are rendered as vector drawing operations rather than standard text blocks.   

To capture both the speed of MuPDF and the structural accuracy of Docling, TenderLens should implement a two-tier page router inside its Celery document worker. Upon downloading the Main Tender PDF and any linked files, the Tier 1 Fast Pass (parsing_method = "fitz") opens the document via pymupdf.open() and iterates across all pages in under a second. During this initial sweep, PyMuPDF performs hyperlink extraction critical to hitting the 90%+ Linked ATC Capture Rate target. Because GeM PDFs embed the target URL for "Buyer uploaded ATC document Click here to view the file" inside the PDF annotation and span dictionary (span.uri) rather than printing the raw URL string in visible text, plain Markdown extractors strip the link entirely; PyMuPDF inspects every page's link dictionary and pushes discovered ATC and corrigendum URIs directly into the Stage 2 ingestion queue. Simultaneously, PyMuPDF applies spatial rectangle clipping (page.get_text("dict", sort=True, clip=rect)) to separate bilingual Hindi left-hand columns from English right-hand columns in standard GeM templates, while evaluating each page's vector drawing density, character count, and tabular alignment.   

Standard prose pages—such as boilerplate GeM General Terms and Conditions—are retained directly from the fast fitz pass, whereas pages containing eligibility summary grids, technical specification tables, or low character counts indicative of scanned image annexures are routed to the Tier 2 Structural Pass (parsing_method = "docling"). In Tier 2, IBM Docling's DocumentConverter runs a specialized layout segmentation model trained on DocLayNet to classify visual regions into Text, Tables, Pictures, Section_Header, List, and page furniture (Headers and Footers), followed by TableFormer for cell-level table reconstruction and Tesseract OCR for scanned pixels. Unlike heuristic text extractors that collapse multi-line table cells, TableFormer recovers exact grid coordinates (cell.start_row_offset_idx, cell.start_col_offset_idx, num_rows, num_cols), preserving column headers alongside their corresponding financial or technical requirement thresholds. Post-processing via docling-hierarchical-pdf (ResultPostprocessor) reconstructs the flat blocks into a valid DoclingDocument hierarchy (section 
→
→ sub_section 
→
→ elements with start_page and end_page), stripping repetitive headers while preserving each item's prov (provenance) page number and bbox bounding box. Persisting both fitz and docling outputs in a unified relational table tagged by parsing_method enables downstream verification modules to weight extraction confidence and render precise visual highlights in the user interface.   

Hybrid Qualification and Verification Engine

The core intellectual property of TenderLens resides in Step 04 (Hybrid Verification Engine), which adheres to the architectural principle of "Deterministic Gates" (use code for explicit numerical rules) combined with "Safe Uncertainty" (unknown or conflicting evidence goes to human review). Large Language Models are prone to error when prompted to perform simultaneous multi-variable arithmetic, unit conversion (such as comparing ₹12 Crore against ₹1,000 Lakhs or ₹100 Million), date-window filtering, and exemption conditional branching inside a single generative pass. TenderLens eliminates mathematical hallucination by decoupling structured parameter extraction from rule evaluation.   

Canonical Pydantic Schema and Two-Stage Evaluation

In the first sub-stage of verification, the LLM processes the hierarchically resolved clauses and tables from Step 03 using strict structured output schemas enforced via Pydantic to populate a canonical TenderRequirements object. Every extracted parameter is encapsulated inside an EvidenceField[T] container that binds the extracted value to its exact provenance:   

EvidenceField
[
𝑇
]
=
{
value
:
𝑇
,
doc_id
:
str
,
page
:
int
,
clause
:
str
,
bbox
:
[
float
]
4
,
verbatim_quote
:
str
,
confidence
:
float
}
EvidenceField[T]={value:T,doc_id:str,page:int,clause:str,bbox:[float]
4
,verbatim_quote:str,confidence:float}

Once the LLM extracts the raw parameters and their verbatim citations, deterministic Python business rules execute the qualification logic against the structured BidderProfile created in Step 01.   

Verification Gate Category	Extracted Tender Parameters (EvidenceField)	Bidder Profile Inputs (Step 01)	Deterministic Python Evaluation Logic & Exemption Branching
Bidder & OEM Financial Turnover	

min_annual_turnover_inr, oem_min_turnover_inr, turnover_window_years (typically 3), msme_turnover_exemption, atc_revokes_exemption

	

annual_turnover_3yr (e.g., ₹12 Crore), entity_type, is_msme, is_startup

	

Evaluates 
𝑇
bidder
≥
𝑇
req
T
bidder
	​

≥T
req
	​

 (e.g., ₹12 Cr >= ₹10 Cr 
→
→ MEETS on Pg 8, Cl 4.1). If 
𝑇
bidder
<
𝑇
req
T
bidder
	​

<T
req
	​

, checks if is_msme == True and msme_turnover_exemption == True without ATC revocation (MEETS_VIA_EXEMPTION); if Main PDF and ATC conflict on exemption, flags AMBIGUOUS_CONFLICT for human review.


Past Project Experience & Capacity	

min_experience_years, estimated_bid_value (
𝑉
est
V
est
	​

), similar_work_definition

	

years_of_experience, past_projects[] (completion date, contract value, scope)

	

Filters past_projects within the valid date window where LLM semantic similarity matches similar_work_definition; deterministically checks standard CPWD/GeM thresholds (
1
 project
≥
0.80
𝑉
est
1 project≥0.80V
est
	​

, 
2
≥
0.50
𝑉
est
2≥0.50V
est
	​

, or 
3
≥
0.40
𝑉
est
3≥0.40V
est
	​

).


Entity Role & OEM Authorization (MAF)	

allowed_entity_types, oem_authorization_required (MAF mandatory flag)

	

entity_type (OEM / Manufacturer / Trader / Reseller), held_maf_authorizations[]

	

If entity_type == "OEM", satisfies OEM gate directly; if Trader/Reseller/System Integrator and oem_authorization_required == True, verifies active MAF or flags as a curable pre-bid action item.


Mandatory Certifications (BIS / ISO)	

required_certifications[] (e.g., ISO 9001, BIS, domain-specific test certs)

	

certifications[] (active standard code, validity date, issuing body)

	

Computes set difference 
𝐶
missing
=
𝐶
req
∖
𝐶
bidder
C
missing
	​

=C
req
	​

∖C
bidder
	​

; any non-empty missing set triggers NOT_FOUND anchored to the mandatory ATC/bid clause.


MII Local Content & EMD Exposure	

mii_class_allowed (Class-I >= 50%, Class-II >= 20%), emd_amount_inr, msme_emd_exemption

	

local_content_percentage, emd_liquidity_limit_inr, is_msme

	

Verifies local_content_percentage against MII threshold and compares emd_amount_inr against bidder working-capital cap unless exempted via valid Udyam/MSME status.

  
Composite Qualification Scorecard Formulation

In Step 05, TenderLens aggregates individual criterion evaluations into a 0.0 to 5.0 Qualification Scorecard—illustrated in the system blueprint by a 4.2/5.0 score—and categorizes the opportunity into one of three actionable decision states. A tender is designated as a Strong Bid when all hard numerical and documentary gates evaluate to MEETS or MEETS_VIA_EXEMPTION, no mandatory certifications are absent, and zero unresolved cross-document conflicts exist. Conversely, the engine assigns a Conditional Bid verdict when core financial and experience thresholds are satisfied, but either a curable compliance gap exists—such as a reseller needing to request a bid-specific OEM Authorization Letter before bid closure—or an ambiguous exemption conflict between the Main PDF and a linked ATC requires human clarification during the pre-bid query window. Finally, a Red Flag designation warns of a high probability of technical disqualification due to a failed deterministic gate, such as bidder turnover falling below the required threshold without valid exemption, an ineligible entity type, or an uncurable missing BIS license or EMD capacity shortfall.   

Full-Stack Engineering Blueprint: Async Orchestration and Evidence-Linked UI

To deliver a responsive user experience while executing multi-document fetching, OCR and table parsing, and hybrid verification in under 5 minutes, TenderLens separates synchronous API handling from asynchronous background processing using FastAPI, Pydantic, Celery, Redis, PostgreSQL, S3 Object Storage, and Next.js.   

Asynchronous Pipeline Orchestration with Real-Time SSE Progress

When a user initiates a tender audit in the Next.js frontend, waiting synchronously on a blocking HTTP request for several minutes would trigger browser and load-balancer timeouts. Instead, TenderLens implements an event-driven FastAPI, Celery, and Redis Server-Sent Events (SSE) architecture. Upon receiving a POST /api/v1/audits request, the FastAPI backend validates the input payload via Pydantic, creates an AuditJob record in PostgreSQL, enqueues a Celery task chain (discover_task.s() | fetch_recursive_task.s() | hybrid_parse_task.s() | verify_scorecard_task.s()) via the Redis broker, and immediately returns {"task_id": "...", "status": "in_progress"} within milliseconds.   

The Next.js client then establishes a persistent SSE connection (GET /api/v1/audits/{task_id}/stream) to FastAPI. As Celery worker processes complete each phase of ingestion and verification, they publish structured JSON progress updates to a Redis Pub/Sub channel that FastAPI streams directly to the browser. Crucially, if Stage 3 (TinyAgent) is invoked to navigate a gated GeM or PSU filter page, the Celery worker consumes TinyFish's /v1/automation/run-sse stream (STARTED 
→
→ STREAMING_URL 
→
→ PROGRESS 
→
→ COMPLETE) and relays the streaming_url over the FastAPI SSE channel to the Next.js interface. This integration enables the MSME owner or bid consultant to watch the live cloud browser navigate the government portal in real time inside the TenderLens dashboard.   

Frontend Evidence Viewer: Coordinate-Scaled Bounding Box Highlighting

A defining operational requirement of TenderLens is traceable, evidence-first recommendations: when the Qualification Scorecard reports "Meets (Pg 8, Cl 4.1): The bidder shall have an annual turnover of minimum 10 Crore in the last 3 financial years" or "EMD Requirement: Not satisfied (Pg 7, Cl 2.3)", clicking that citation must navigate the user directly to the exact paragraph or table cell inside the source PDF.   

Implementing this capability in the Next.js, TypeScript, and Tailwind CSS frontend requires a split-pane document verification workspace powered by react-pdf (built on Mozilla's pdf.js) or react-pdf-highlighter paired with an SVG coordinate overlay layer. Versioned PDFs—spanning the Main Bid, Linked ATC, and Corrigenda—are stored in S3 Object Storage and streamed to the Next.js client via short-lived presigned URLs (AWS4-HMAC-SHA256). Because backend bounding boxes extracted by PyMuPDF and Docling ([x0, y0, x1, y1]) are recorded in native PDF points (typically 72 DPI), the frontend dynamically normalizes coordinates to match the responsive HTML5 <canvas> width using the viewport scaling ratio:   

scale_ratio
=
𝑊
canvas
𝑊
pdf_native
scale_ratio=
W
pdf_native
	​

W
canvas
	​

	​


Using this ratio, an absolute SVG overlay layer renders a translucent, status-colored highlight rectangle (x = x0 * scale_ratio, y = y0 * scale_ratio, width = (x1 - x0) * scale_ratio, height = (y1 - y0) * scale_ratio) directly over the rendered text layer, executing element.scrollIntoView() to center the exact clause whenever a user selects a row on the Qualification Scorecard.   

Architectural Layer	Core Technologies	Primary Responsibilities in TenderLens	Reliability & Scaling Controls
Frontend UX	

Next.js, TypeScript, Tailwind CSS, react-pdf + SVG Overlay

	

Bidder profile builder, live SSE progress monitor, split-pane Qualification Scorecard, and bounding-box PDF evidence viewer.

	

Client-side page virtualization (react-pdf lazy page loading) to render 200+ page tender PDFs without browser memory leaks.


API & Orchestration	

FastAPI, Pydantic, Celery, Redis (Broker + Pub/Sub)

	

REST endpoints, schema validation, async task chaining, SSE progress streaming, and portal rate-limit throttling.

	

Separate Celery queues for fast I/O (tinyfish_io) vs. CPU-heavy layout parsing (docling_cpu) to prevent worker starvation.


Web Intelligence	

TinySearch, TinyFetch, TinyAgent, TinyMonitor, SerpAPI, HTTPX

	

Geo-targeted discovery (location="IN"), batch Markdown/PDF fetching, stealth browser fallback, and corrigenda delta webhooks.

	

include_etag_and_last_modified HTTP caching; agent_config.mode="strict" and max_steps=10 cost circuit breakers.


Document Intelligence	

PyMuPDF (fitz), IBM Docling (v2), TableFormer

	

Sub-second URI/text extraction, bilingual column clipping, neural table cell recovery, and hierarchical clause tree reconstruction.

	

Two-tier page router: PyMuPDF parses prose pages at ~250 pages/sec; Docling runs selectively on complex table and scanned pages.


Data & Storage	

PostgreSQL, S3 Object Storage, Redis Cache, Docker

	

Relational storage of versioned clause DAGs, bounding-box provenance, immutable PDF artifacts, and TTL cache.

	

Content-addressable SHA-256 hashing of downloaded PDFs in S3 so multiple MSMEs auditing the same GeM tender share one parsed artifact.

  
Competitive Landscape and Go-To-Market Strategy

To evaluate TenderLens's commercial viability and pricing architecture, its capabilities must be benchmarked against both domestic Indian tender aggregators (BidAssist and TrackTender) and enterprise global capture platforms (Procurement Sciences' Awarded AI).   

Structural Gap in the Indian Procurement Tech Market

The Indian tender discovery market is dominated by high-volume listing aggregators, led by BidAssist (owned by the OfBusiness Group). BidAssist has achieved massive distribution—serving 1.7 million users (with over 60% located in Tier-II and Tier-III cities) and tracking 50,000+ live tenders daily across 2,000+ sources (3 Lakh+ active tenders and 4 Crore+ historical tender results). Its business model relies on a "free-forever" search funnel coupled with a 3-day free trial, monetized via gated document downloads (₹299 per tender after a 2-document monthly free cap) or annual subscriptions starting at ₹3,000/year (~₹250/month billed annually for a single-state Basic/Solo plan, plus ₹1,000 per additional state up to 5 states, and GeM or Bid Advisory plans starting from ₹499). Crucially, BidAssist's subscription revenue exceeds its operating costs, allowing it to function as a self-funded customer acquisition engine for OfBusiness's core B2B raw-material commerce and working-capital lending businesses.   

Meanwhile, newer challengers such as TrackTender attack dashboard fatigue by offering a chat-first (Telegram and WhatsApp) alert pipeline priced at ₹30 for the first month (~₹1/day) and a flat ₹300/month (₹255/month billed yearly) for 3 states and 3 categories, delivering pre-parsed bid documents directly into chat without per-download gating. At the opposite end of the global spectrum, US federal capture platforms like Procurement Sciences (Awarded AI) provide FedRAMP Moderate-authorized enterprise workflows—including Probability of Win (PWIN) scoring, compliance matrices, and proposal drafting—at enterprise license tiers benchmarked around $40,000+/year.   

Neither BidAssist nor TrackTender resolves the cross-document qualification verification problem. BidAssist provides high-level summary cards inside its mobile and web apps, and TrackTender extracts headline metadata such as EMD and submission deadline into Telegram messages, but both leave the bidder to manually cross-reference 50-page uploaded ATCs and sequential corrigenda against their own balance sheets and ISO or BIS certificates.   

Unit Economics, Beachhead Execution, and Second-Order Monetization

TenderLens's go-to-market rollout is anchored in a disciplined three-milestone validation sequence starting with a Phase 1 geographical beachhead in Haryana (6,155 tenders) focused on Electrical and IT MSMEs. In Milestone 01 (50-Tender Benchmark), the engineering team constructs a ground-truth labeled evaluation dataset of 50 GeM tenders—complete with linked ATCs and corrigenda—to verify that the hybrid pipeline meets its 85%+ Disqualifier Precision, 80%+ Disqualifier Recall, and 90%+ Linked ATC Capture Rate targets. Following benchmark validation, Milestone 02 (Head-to-Head ATC Audit) pairs TenderLens against manual review by human bid consultants to quantify error reduction, caught exemption traps, and time saved relative to the < 5 mins processing target. In Milestone 03 (MSME Pilot), electrical and IT contractors are onboarded onto a Freemium tier offering 3 tender audits per month, converting into an MSME Pro monthly SaaS subscription (featuring high-volume audits and TinyMonitor Corrigenda Delta Alerts) and Enterprise Consultant API seats designed for bid advisory agencies managing multiple client profiles.   

Pipeline Cost Component	API / Compute Resource	Unit Cost Basis	Estimated Usage per Audit	Marginal Cost per Tender Audit
Stage 1: Discovery	

TinySearch API

	

$0.00 / call (up to 12,000/day; 120 rpm on Startup Tier)

	

1–3 search queries per discovery run

	

$0.000 (₹0.00)


Stage 2: Document Fetch	

TinyFetch Batch API

	

$0.00 / call (600 URLs/min on Startup Tier)

	

1 Main PDF + 2–4 linked ATC/Corrigenda URLs

	

$0.000 (₹0.00)


Stage 3: Stealth Fallback	

TinyAgent SSE (strict mode)

	

$0.016 / step (50% off on Startup Tier 2)

	

Triggered on ~15–20% of gated tenders (~4 steps/run)

	

~$0.010–$0.013 (~₹0.85–₹1.10)


Stage 4: Hybrid Parse & LLM	

PyMuPDF + Docling CPU + Structured LLM

	

Local CPU worker + LLM token inference

	~8K–15K input tokens on triaged eligibility pages	~$0.015–$0.040 (~₹1.25–₹3.35)
Corrigenda Delta Watch	

TinyMonitor API (Pro Tier)

	

$0.005 / completed check

	

Optional (2 checks/day for 10 days on shortlisted bids)

	

$0.100 (~₹8.40 per watched bid)

  

Because TenderLens caches parsed tender documents across users via S3 and Redis TTL caching, the total marginal cost per uncached tender audit is approximately $0.03 to $0.05 (₹2.50 to ₹4.25), and drops below ₹0.50 when a cached tender is re-evaluated against a second MSME's profile using deterministic Python gates. Serving the Freemium allowance of 3 audits per month costs less than ₹13 per user, enabling highly profitable conversion into an MSME Pro tier priced between ₹499/month and ₹1,499/month.   

Beyond direct SaaS subscriptions, OfBusiness's monetization of BidAssist demonstrates the strategic power of pairing tender intelligence with B2B working-capital credit. TenderLens possesses an even stronger underwriting signal than a discovery portal: verified technical and financial pre-qualification. When an Indian MSME receives a Strong Bid scorecard on TenderLens, it immediately faces capital requirements for Earnest Money Deposit (EMD) bid security prior to submission and Performance Bank Guarantees (ePBG) or invoice discounting upon contract award. Embedding a one-click EMD Surety Bond and working-capital financing workflow directly into the Qualification Scorecard allows TenderLens to pass cryptographically auditable compliance reports to partner lenders, capturing high-margin fintech origination fees alongside recurring software revenue.   

Risk Matrix and Actionable Implementation Roadmap

To transition TenderLens from its hackathon proposal architecture to a production-hardened system capable of auditing thousands of Haryana, GeM, and PSU tenders daily, TenderLens must address six primary operational and legal risk vectors.   

Architectural Risk Vector	Root Technical Cause	Production Mitigation Strategy
Missed External ATC Files (< 90% Capture)	

GeM PDFs embed "Click here to view the file" ATC links inside PDF URI dictionaries rather than visible text, and TinyFetch is a single-hop extractor.

	

Extract all span.uri and /Annots link objects via PyMuPDF during the Tier 1 pass and feed discovered URLs into a Celery recursive fetch queue (depth limit 
𝑑
max
⁡
=
2
d
max
	​

=2).


Hallucinated Eligibility via Superseded Clauses	

Corrigenda override baseline bid and ATC clauses using natural-language supersession declarations.

	

Enforce a strict Precedence DAG (
Corr
𝑁
>
Corr
𝑁
−
1
>
Uploaded ATC
>
Text ATC
>
Main PDF
Corr
N
	​

>Corr
N−1
	​

>Uploaded ATC>Text ATC>Main PDF) in Python before evaluating thresholds.


CPU Bottlenecks Violating < 5 Min SLA	

Running Docling + TableFormer + OCR across every page of a 250-page PSU tender on CPU workers takes several minutes.

	

Implement two-tier page triage: parse all pages in < 1 sec with PyMuPDF (fitz) and route only table-dense or low-character (scanned) pages to DocumentConverter.


TinyAgent Wallet Drain on Broken Portals	

Default EVA max_steps is 150 ($2.40/run), which can exhaust wallet funds if a portal enters an infinite redirect or CAPTCHA loop.

	

Pass agent_config={"mode": "strict", "max_steps": 10, "max_duration_seconds": 60} and route hard CAPTCHA/DSC failures to the Manual Upload fallback.


TinySearch Query Rejection or Low Precision	

Combining recency_minutes with after_date throws a validation error; site: operators in query are deprecated.

	

Use include_domains for portal scoping, pass bidder profile context via the purpose parameter (up to 2,000 chars), and separate recency from calendar date filters.


MuPDF / PyMuPDF AGPLv3 Licensing Exposure	

PyMuPDF (fitz) is licensed under GNU AGPLv3, which can trigger source-code disclosure obligations depending on network service distribution.

	

Isolate PDF parsing inside an internal microservice or evaluate Docling's native docling-parse / pypdfium backends (MIT/Apache-2.0) if commercial MuPDF licensing is not acquired.

  
Immediate Engineering Sequence for Milestone 01 to Milestone 03

Executing this roadmap begins with enrolling TenderLens in the TinyFish for Startups program (tinyfish.ai/startups) under Tier 1 (for independent pre-production teams, providing up to $7,000 in value, $100/month in wallet credits for 6 months, and 50 concurrent TinyAgent runs) or Tier 2 (for accelerator or investor-backed teams, providing up to $12,000 in value, $500 initial wallet credits, and 50% off TinyAgent for 24 months). Both tiers immediately quadrupled standard rate limits to 120 TinySearch requests per minute and 600 TinyFetch URLs per minute, enabling TenderLens to ingest the 6,155-tender Haryana beachhead and construct the 50-tender GeM benchmark dataset at zero infrastructure cost.   

In parallel with API provisioning, the engineering team should assemble the 50-tender GeM evaluation harness by curating a stratified sample across Haryana electrical and IT categories—combining straightforward single-PDF bids, tenders with hyperlinked multi-page buyer ATCs, and complex solicitations featuring multiple superseding corrigenda and MSME or MII exemption overrides. Validating the two-tier PyMuPDF and Docling router alongside the deterministic Python rules engine against this golden dataset will empirically establish the 85%+ precision and 80%+ recall baselines prior to onboarding pilot MSMEs. Finally, wiring TinyMonitor (POST /v1/monitors) into the FastAPI backend will operationalize automated corrigenda monitoring at $0.005 per check, ensuring that whenever an MSME shortlists a Strong Bid or Conditional Bid, any subsequent portal amendment automatically triggers a delta re-verification before bid submission.   

---

Gemini
TenderLens Architectural Blueprint and Strategic Market Analysis: AI-Powered Public Procurement Qualification
Executive Summary and Problem Formulation

Public procurement across India—spanning the Government e-Marketplace (GeM), the Central Public Procurement Portal (CPPP), Public Sector Undertaking (PSU) portals such as Bharat Heavy Electricals Limited (BHEL) and the Indian Council of Medical Research (ICMR), and state-level e-procurement systems—presents a structural asymmetry for Micro, Small, and Medium Enterprises (MSMEs). While discovering open tenders has been largely commoditized by search aggregators and notification bots, verifying whether a specific enterprise legally and technically qualifies to bid remains a fragmented, manual, and high-risk process.   

In the Indian tendering ecosystem, a solicitation is rarely self-contained within a single Portable Document Format (PDF) file. Instead, material eligibility conditions are distributed across a baseline Notice Inviting Tender (NIT) or GeM Bid Document, hyperlinked Buyer Added Bid Specific Additional Terms and Conditions (ATC) files, and sequential corrigenda issued up to hours before bid closure. When an MSME, Original Equipment Manufacturer (OEM), Engineering, Procurement, and Construction (EPC) contractor, or Information Technology (IT) system integrator overlooks a nested sub-clause or an amended financial threshold, the consequences extend beyond administrative rejection. Disqualification during technical evaluation results in sunk bid-preparation engineering hours, forfeiture or prolonged lock-up of working capital committed to Earnest Money Deposits (EMD), and missed revenue cycles.   

TenderLens addresses this verification bottleneck by shifting the paradigm from passive tender discovery to evidence-backed, pre-bid qualification and disqualification auditing. Designed as a decision-support engine rather than an autonomous legal adjudicator, TenderLens ingests a bidder's structured corporate profile, recursively retrieves the complete hierarchy of tender documents via the TinyFish web intelligence stack, parses complex multi-column layouts and tables through a hybrid PyMuPDF and IBM Docling pipeline, and evaluates compliance using deterministic Python rules paired with Large Language Model (LLM) clause analysis. Every identified risk, met criterion, or contractual contradiction is anchored to its exact source document, page number, and clause reference, routing ambiguous or conflicting stipulations to human review before capital is committed.   

Domain Mechanics: Contractual Precedence and Eligibility Traps in Indian Tenders

To engineer a reliable qualification engine capable of achieving TenderLens's target of 85%+ disqualifier precision and 80%+ disqualifier recall, the system must account for how Indian procurement portals structure and amend solicitation documents. On GeM and allied PSU portals—including BHEL, Bharatiya Reserve Bank Note Mudran Private Limited, the Indian Renewable Energy Development Agency, Mazagon Dock Shipbuilders, and the National Industrial Corridor Development Corporation—tender rules are governed by a strict legal hierarchy rather than uniform document weighting.   

The Tripartite Document Structure and Supersession Hierarchy

A standard GeM bid document is generated automatically from portal templates, containing standardized boilerplate alongside parameterized fields for minimum average annual turnover, past experience years, and Earnest Money Deposit amounts. However, procuring authorities routinely customize these baseline requirements at the bottom of the main bid PDF under the section header "Buyer Added Bid Specific Terms and Conditions" (ATC). This section bifurcates into two distinct data modalities that must be parsed concurrently. The first modality consists of Buyer Added Text-Based ATC Clauses, which are numbered textual stipulations appended directly inside the main GeM PDF. The second modality is the Buyer Uploaded ATC Document, an external hyperlink embedded inside the PDF—typically rendered as "Buyer uploaded ATC document: Click here to view the file"—which points to a separate, multi-page Request for Proposal (RFP), technical specification book, or scanned annexure hosted on the portal's object store.   

When a procuring entity modifies technical specifications, extends deadlines, or alters financial qualification thresholds after publication, the portal issues sequential Bid Corrigendum files (such as GeM-Bidding-Corr-...). These files carry an explicit legal override clause stating that the "Following terms and conditions supersede all existing 'Buyer added Bid Specific Terms and conditions' given in the bid document or any previous corrigendum". Simultaneously, portal governance stipulates that while buyer-specific clauses override baseline parameters, any ATC clause that directly contravenes the overarching GeM General Terms and Conditions (GTC) without authorized exemption is legally contentious, and conflicts between the main GeM ATC and the buyer-uploaded RFP are governed by explicit order-of-precedence clauses (for example, "in case of same clause, the clause mentioned in Corrigendum 1 will supersede").   

Document Layer	Typical File Format & Location	Legal Precedence Rank	Common Disqualification Traps Embedded in Layer
Latest Bid Corrigendum (
Corr
𝑁
Corr
N
	​

)	

Standalone PDF issued post-NIT via portal notification

	

Rank 1 (Highest): Supersedes all prior corrigenda, ATCs, and baseline bid terms

	

Last-minute upward revision of turnover thresholds, addition of mandatory ISO/BIS test certificates, or relaxation/removal of MSME exemptions.


Prior Corrigenda (
Corr
1
…
𝑁
−
1
Corr
1…N−1
	​

)	

Sequential standalone PDFs

	

Rank 2: Supersedes baseline bid and initial ATCs unless overridden by 
Corr
𝑁
Corr
N
	​


	

Partial modifications to Bill of Quantities (BOQ) scope or experience calculation windows.


Buyer Uploaded ATC / RFP PDF	

Hyperlinked external PDF inside the main bid document

	

Rank 3: Overrides standard bid template parameters; subject to GeM GTC compliance

	

Mandatory OEM Authorization (MAF) formats, local service center requirements in specific states, and Make in India (MII) Class-I/Class-II local content percentages.


Buyer Text-Based ATC Clauses	

Embedded text section at the end of Main GeM Bid PDF

	

Rank 4: Modifies main bid parameters unless contradicted by uploaded RFP or Corrigendum

	

Specific past-project similarity definitions (e.g., one project at 
80
%
80%, two at 
50
%
50%, or three at 
40
%
40% of estimated bid value).


Main Tender / GeM Bid PDF	

Primary portal-generated PDF document

	

Rank 5 (Baseline): Default parameters governing the bid in the absence of overrides

	

Baseline 3-year average bidder turnover, OEM average turnover, EMD amount, and ePBG percentage.

  
Failure of Naive Retrieval-Augmented Generation (RAG)

Standard vector-database RAG pipelines fail catastrophically on this document topology. If a tender corpus is chunked and embedded into a flat vector store without version awareness, a semantic query for "minimum annual turnover requirement" will retrieve both the baseline Main PDF clause (for instance, requiring ₹5 Crore with MSME exemption enabled) and a Corrigendum 2 clause (for instance, raising the requirement to ₹10 Crore and revoking turnover exemption under specialized technical category rules). Because both chunks exhibit high cosine similarity to the query, a naive LLM synthesizer frequently averages, hallucinates, or selects the wrong threshold.   

TenderLens resolves this by treating the tender document set as a versioned Directed Acyclic Graph (DAG). Every extracted clause is tagged with a metadata tuple:   

𝜏
𝑖
=
(
doc_id
,
doc_type
,
version_rank
,
page_no
,
clause_id
,
bbox
)
τ
i
	​

=(doc_id,doc_type,version_rank,page_no,clause_id,bbox)

During Step 04 (Hybrid Verification Engine), when two clauses map to the same canonical attribute (such as min_annual_turnover or iso_certification_required) with divergent predicates, the rules engine applies temporal and hierarchical resolution: if 
version_rank
(
𝜏
𝑎
)
>
version_rank
(
𝜏
𝑏
)
version_rank(τ
a
	​

)>version_rank(τ
b
	​

) and 
𝜏
𝑎
τ
a
	​

 contains an explicit supersession marker, 
𝜏
𝑎
τ
a
	​

 overrides 
𝜏
𝑏
τ
b
	​

 while preserving 
𝜏
𝑏
τ
b
	​

 in the audit trail as a superseded historical clause. If two clauses within the same precedence rank conflict—or if an uploaded ATC directly violates GeM GTC exemptions without clear precedence—TenderLens enforces its "Safe Uncertainty" design principle, flagging the item as a Conditional Bid conflict for mandatory human review.   

Web Intelligence Layer: Productionizing the TinyFish API Stack

A foundational pillar of the TenderLens architecture is its three-stage integration with TinyFish (tinyfish.ai), an enterprise web execution platform that consolidates live search (TinySearch), content extraction (TinyFetch), remote browser control (TinyBrowser), autonomous goal-driven navigation (TinyAgent), and scheduled change detection (TinyMonitor) behind a single API key (X-API-Key) and unified wallet. While the initial TenderLens proposal outlines a high-level three-stage workflow—Stage 1 TinySearch ($0.00/call), Stage 2 TinyFetch Recursive ($0.00/call), and Stage 3 TinyAgent Stealth SSE ($0.016/step)—a granular inspection of the production TinyFish API specifications (docs.tinyfish.ai) reveals critical parameter constraints, rate limits, and architectural optimizations required for production deployment.   

Stage 1: High-Precision Discovery via TinySearch

In Stage 1, TenderLens queries government portals to discover live tenders matching the bidder's sector, location, and capacity profile. Rather than relying on cached secondary indexes, TinySearch (GET https://api.search.tinyfish.ai) executes real browser-rendered queries against Google's live index and returns structured JSON (position, site_name, title, snippet, url) in under 0.5 seconds.   

To align TenderLens's implementation with the current TinySearch API schema, three specific engineering refinements are necessary. First, the system must transition away from deprecated site: or -site: operators embedded inside the query string for domain filtering. Instead, TenderLens should pass a comma-separated list of target procurement domains via the native include_domains parameter (such as include_domains="gem.gov.in,eprocure.gov.in,tenders.bhel.com,icmr.nic.in,etenders.hry.nic.in") while reserving the query string strictly for commodity, BOQ, and document-type keywords. Second, because terse keyword combinations often return generic portal landing pages rather than active Notice Inviting Tender PDFs, TenderLens should exploit the optional purpose parameter (up to 2,000 characters), which supplies the underlying task intent to TinyFish's ranking engine. Passing a dynamically constructed purpose string derived from the Step 01 Bidder Profile—such as "Find active government tender bid PDFs and corrigenda in Haryana for LT/HT electrical switchgear manufacturing requiring BIS certification"—substantially increases top-10 result relevance. Third, the orchestration engine must enforce mutual exclusivity across temporal filters: while TinySearch offers recency_minutes (accepting integers from 1 to 5,256,000) and calendar bounds after_date and before_date (YYYY-MM-DD), the API strictly rejects requests that combine recency_minutes with calendar date bounds. TenderLens should therefore standardize on recency_minutes=1440 for daily incremental cron discovery and after_date for historical benchmark backfills, paired with location="IN" and language="en".   

Stage 2: Deep Document Retrieval and Link Graph Extraction via TinyFetch

Once candidate tender URLs are queued, Stage 2 utilizes TinyFetch (POST https://api.fetch.tinyfish.ai) to retrieve HTML portal pages and directly accessible PDFs at $0.00 per call. TinyFetch accepts batches of up to 10 URLs per request and natively extracts text from both HTML and PDF content types into token-efficient "markdown", "html", or "json" (document tree) formats.   

A vital technical distinction emerges between the hackathon presentation's conceptual shorthand (TinyFetch Recursive with links:true) and the actual TinyFetch production API. In production, TinyFetch operates as a stateless single-hop batch extraction endpoint—supporting iframe_links: true for embedded frames, include_selectors, and exclude_selectors up to 20 CSS selectors, alongside a per-URL wall-clock timeout budget from 1 to 110,000 milliseconds—rather than an autonomous multi-hop web crawler. Consequently, the "URL Queue + Deduplicate + Depth Limit" module depicted in TenderLens's architecture diagram must reside inside the FastAPI and Celery orchestration layer. When TinyFetch returns the Markdown or JSON document tree of a primary GeM or CPPP tender landing page, a Python URI parser extracts all child hyperlinks matching ATC, Corrigendum, or BOQ patterns at depth 
𝑑
=
1
d=1, deduplicates them by canonical URL, and dispatches a subsequent batch call (client.fetch.get_contents(urls=child_urls, format="markdown")) up to a hard depth limit of 
𝑑
max
⁡
=
2
d
max
	​

=2.   

Furthermore, TinyFetch provides native protocol support for TenderLens's scalability requirement of TTL Caching for versioned PDFs. By setting include_etag_and_last_modified: true on initial retrieval, TenderLens can persist the origin server's etag and last_modified validators in PostgreSQL and Redis alongside each tender's document record. When subsequent users request an audit of the same tender, TenderLens passes if_none_match or if_modified_since in the TinyFetch payload. If the government portal returns HTTP 304 Not Modified, TinyFetch flags not_modified: true in the response, allowing TenderLens to bypass redundant PDF downloading, Docling layout parsing, and LLM evaluation entirely.   

Stage 3: Selective Interactive Fallback via TinyAgent Stealth SSE

Government procurement portals frequently gate search filters, session cookies, or linked ATC downloads behind dynamic JavaScript state transitions that return bot_blocked, login_required, or empty_content errors in standard HTTP fetching. When TinyFetch returns one of these specific error codes in its errors[] array, TenderLens triggers Stage 3: TinyAgent (POST https://agent.tinyfish.ai/v1/automation/run-sse). Achieving 89.9% overall accuracy on the Online-Mind2Web benchmark—and 81.9% on hard tasks, outperforming OpenAI Operator (43.2%) and Anthropic Claude (32.4%)—TinyAgent translates natural-language goals into live browser interactions.   

TinyFish API Component	Production Endpoint & Method	Key Request Parameters Utilized by TenderLens	Rate Limits (Default vs. Startup Tiers)	Billing & Cost Structure
TinySearch	

GET https://api.search.tinyfish.ai

	

query, location="IN", language="en", include_domains, purpose, recency_minutes or after_date

	

30 req/min (Default)




120 req/min (Startup Tier 1 & 2)

	

$0.00 / call up to 12,000 req/day; positive wallet balance required beyond cap


TinyFetch	

POST https://api.fetch.tinyfish.ai

	

urls (max 10/call), format="markdown", purpose, iframe_links=true, include_etag_and_last_modified=true, if_none_match

	

150 URLs/min (Default)




600 URLs/min (Startup Tier 1 & 2)

	

$0.00 / call for all standard extractions


TinyAgent (SSE / Async)	

POST https://agent.tinyfish.ai/v1/automation/run-sse (or /run-async)

	

url, goal, output_schema, browser_profile="stealth", proxy_config={"enabled": true, "type": "tinyfish", "country_code": "IN"}, agent_config={"mode": "strict", "max_steps": 15}

	

50 concurrent runs (Startup Tier 1 & 2)

	

$0.016 / step ($0.048–$0.080 per 3–5 step run); 50% off for 24 mos on Startup Tier 2


TinyMonitor	

POST /v1/monitors & POST /v1/monitors/{id}/runs

	

Target URL or topic query, plain-language alert condition, schedule frequency, webhook_url

	

Up to 50 active monitors per account

	

$0.005 / completed check (includes LLM change judgment + webhook; failed checks unbilled)

  

To prevent runaway credit consumption when navigating complex government portals, TenderLens must enforce strict execution guardrails in the TinyAgent request payload. By default, TinyFish's EVA agent permits up to 150 steps per run—which, if caught in a portal redirect loop, would consume $2.40 for a single tender. TenderLens should explicitly configure agent_config.mode: "strict", which instructs the agent to fail fast when blocked rather than exploring costly workarounds, and set agent_config.max_steps: 10 alongside agent_config.max_duration_seconds: 60, capping worst-case agent expenditure at $0.16 per fallback invocation. Because many Indian PSU and NIC-hosted portals block or throttle foreign IP ranges, passing browser_profile: "stealth" with proxy_config: {"enabled": true, "type": "tinyfish", "country_code": "IN"} routes the cloud browser session through Indian exit nodes.   

When invoked via /v1/automation/run-sse, TinyAgent emits Server-Sent Events in the sequence STARTED 
→
→ STREAMING_URL 
→
→ PROGRESS 
→
→ COMPLETE, where streaming_url provides a live browser preview valid for 24 hours. If a portal presents a hard CAPTCHA or requires a physical Class-III Digital Signature Certificate (DSC) token that cannot be automated, strict mode terminates the run cleanly, and TenderLens surfaces the streaming_url or transitions the user to the manual PDF upload fallback exactly as specified in TenderLens's risk controls. Furthermore, to power the MSME Pro subscription tier's "Delta Alerts: Corrigenda Watch" feature without engineering a bespoke cron-scraping loop, TenderLens can programmatically provision a TinyMonitor (POST /v1/monitors) on each shortlisted tender URL with a natural-language trigger condition such as "Alert me when a new Corrigendum PDF link, Addendum, or bid submission date extension is added to this tender page". At $0.005 per completed check—which includes LLM change judgment and webhook delivery, while failed checks remain unbilled—checking an active tender twice daily for 10 days prior to bid closure costs just $0.10 (~₹8.40) and automatically initiates a Celery delta-reverification workflow whenever an amendment is published.   

Document Intelligence Pipeline: Hybrid PyMuPDF and Docling Extraction

While TinyFetch extracts raw text from simple PDFs, Indian tender documents present severe layout challenges that destroy structural context when flattened into plain text. Main GeM bid PDFs are formatted as dense two-column key-value grids (often bilingual in Hindi and English), while linked ATCs and PSU specifications contain multi-page financial matrices, nested technical compliance tables, and scanned stamp-paper annexures. TenderLens resolves this by pairing PyMuPDF (fitz) with IBM Docling (v2) inside its Document Intelligence layer, balancing computational throughput against structural fidelity to meet the < 5 minutes average processing time target per tender.   

Page-Level Triage and Hybrid Routing Mechanics

Running a deep neural layout and table-structure model across a 300-page PSU tender specification on standard CPU workers can consume several minutes per document, threatening the < 5 minutes end-to-end service-level objective. Conversely, C-based MuPDF bindings (pymupdf and pymupdf4llm-c) process 250 to 300 pages per second on CPU, extracting raw text spans, font sizes, style flags (bold, italic, monospace), embedded URI hyperlinks, and [x0, y0, x1, y1] bounding boxes almost instantaneously. However, when evaluated as a standalone parser on complex document layouts, the PyMuPDF baseline achieves only a 70.2 F1 score (72.4 precision and 68.1 recall), frequently interleaving multi-column clauses or failing silently when tables and figures are rendered as vector drawing operations rather than standard text blocks.   

To capture both the speed of MuPDF and the structural accuracy of Docling, TenderLens should implement a two-tier page router inside its Celery document worker. Upon downloading the Main Tender PDF and any linked files, the Tier 1 Fast Pass (parsing_method = "fitz") opens the document via pymupdf.open() and iterates across all pages in under a second. During this initial sweep, PyMuPDF performs hyperlink extraction critical to hitting the 90%+ Linked ATC Capture Rate target. Because GeM PDFs embed the target URL for "Buyer uploaded ATC document Click here to view the file" inside the PDF annotation and span dictionary (span.uri) rather than printing the raw URL string in visible text, plain Markdown extractors strip the link entirely; PyMuPDF inspects every page's link dictionary and pushes discovered ATC and corrigendum URIs directly into the Stage 2 ingestion queue. Simultaneously, PyMuPDF applies spatial rectangle clipping (page.get_text("dict", sort=True, clip=rect)) to separate bilingual Hindi left-hand columns from English right-hand columns in standard GeM templates, while evaluating each page's vector drawing density, character count, and tabular alignment.   

Standard prose pages—such as boilerplate GeM General Terms and Conditions—are retained directly from the fast fitz pass, whereas pages containing eligibility summary grids, technical specification tables, or low character counts indicative of scanned image annexures are routed to the Tier 2 Structural Pass (parsing_method = "docling"). In Tier 2, IBM Docling's DocumentConverter runs a specialized layout segmentation model trained on DocLayNet to classify visual regions into Text, Tables, Pictures, Section_Header, List, and page furniture (Headers and Footers), followed by TableFormer for cell-level table reconstruction and Tesseract OCR for scanned pixels. Unlike heuristic text extractors that collapse multi-line table cells, TableFormer recovers exact grid coordinates (cell.start_row_offset_idx, cell.start_col_offset_idx, num_rows, num_cols), preserving column headers alongside their corresponding financial or technical requirement thresholds. Post-processing via docling-hierarchical-pdf (ResultPostprocessor) reconstructs the flat blocks into a valid DoclingDocument hierarchy (section 
→
→ sub_section 
→
→ elements with start_page and end_page), stripping repetitive headers while preserving each item's prov (provenance) page number and bbox bounding box. Persisting both fitz and docling outputs in a unified relational table tagged by parsing_method enables downstream verification modules to weight extraction confidence and render precise visual highlights in the user interface.   

Hybrid Qualification and Verification Engine

The core intellectual property of TenderLens resides in Step 04 (Hybrid Verification Engine), which adheres to the architectural principle of "Deterministic Gates" (use code for explicit numerical rules) combined with "Safe Uncertainty" (unknown or conflicting evidence goes to human review). Large Language Models are prone to error when prompted to perform simultaneous multi-variable arithmetic, unit conversion (such as comparing ₹12 Crore against ₹1,000 Lakhs or ₹100 Million), date-window filtering, and exemption conditional branching inside a single generative pass. TenderLens eliminates mathematical hallucination by decoupling structured parameter extraction from rule evaluation.   

Canonical Pydantic Schema and Two-Stage Evaluation

In the first sub-stage of verification, the LLM processes the hierarchically resolved clauses and tables from Step 03 using strict structured output schemas enforced via Pydantic to populate a canonical TenderRequirements object. Every extracted parameter is encapsulated inside an EvidenceField[T] container that binds the extracted value to its exact provenance:   

EvidenceField
[
𝑇
]
=
{
value
:
𝑇
,
doc_id
:
str
,
page
:
int
,
clause
:
str
,
bbox
:
[
float
]
4
,
verbatim_quote
:
str
,
confidence
:
float
}
EvidenceField[T]={value:T,doc_id:str,page:int,clause:str,bbox:[float]
4
,verbatim_quote:str,confidence:float}

Once the LLM extracts the raw parameters and their verbatim citations, deterministic Python business rules execute the qualification logic against the structured BidderProfile created in Step 01.   

Verification Gate Category	Extracted Tender Parameters (EvidenceField)	Bidder Profile Inputs (Step 01)	Deterministic Python Evaluation Logic & Exemption Branching
Bidder & OEM Financial Turnover	

min_annual_turnover_inr, oem_min_turnover_inr, turnover_window_years (typically 3), msme_turnover_exemption, atc_revokes_exemption

	

annual_turnover_3yr (e.g., ₹12 Crore), entity_type, is_msme, is_startup

	

Evaluates 
𝑇
bidder
≥
𝑇
req
T
bidder
	​

≥T
req
	​

 (e.g., ₹12 Cr >= ₹10 Cr 
→
→ MEETS on Pg 8, Cl 4.1). If 
𝑇
bidder
<
𝑇
req
T
bidder
	​

<T
req
	​

, checks if is_msme == True and msme_turnover_exemption == True without ATC revocation (MEETS_VIA_EXEMPTION); if Main PDF and ATC conflict on exemption, flags AMBIGUOUS_CONFLICT for human review.


Past Project Experience & Capacity	

min_experience_years, estimated_bid_value (
𝑉
est
V
est
	​

), similar_work_definition

	

years_of_experience, past_projects[] (completion date, contract value, scope)

	

Filters past_projects within the valid date window where LLM semantic similarity matches similar_work_definition; deterministically checks standard CPWD/GeM thresholds (
1
 project
≥
0.80
𝑉
est
1 project≥0.80V
est
	​

, 
2
≥
0.50
𝑉
est
2≥0.50V
est
	​

, or 
3
≥
0.40
𝑉
est
3≥0.40V
est
	​

).


Entity Role & OEM Authorization (MAF)	

allowed_entity_types, oem_authorization_required (MAF mandatory flag)

	

entity_type (OEM / Manufacturer / Trader / Reseller), held_maf_authorizations[]

	

If entity_type == "OEM", satisfies OEM gate directly; if Trader/Reseller/System Integrator and oem_authorization_required == True, verifies active MAF or flags as a curable pre-bid action item.


Mandatory Certifications (BIS / ISO)	

required_certifications[] (e.g., ISO 9001, BIS, domain-specific test certs)

	

certifications[] (active standard code, validity date, issuing body)

	

Computes set difference 
𝐶
missing
=
𝐶
req
∖
𝐶
bidder
C
missing
	​

=C
req
	​

∖C
bidder
	​

; any non-empty missing set triggers NOT_FOUND anchored to the mandatory ATC/bid clause.


MII Local Content & EMD Exposure	

mii_class_allowed (Class-I >= 50%, Class-II >= 20%), emd_amount_inr, msme_emd_exemption

	

local_content_percentage, emd_liquidity_limit_inr, is_msme

	

Verifies local_content_percentage against MII threshold and compares emd_amount_inr against bidder working-capital cap unless exempted via valid Udyam/MSME status.

  
Composite Qualification Scorecard Formulation

In Step 05, TenderLens aggregates individual criterion evaluations into a 0.0 to 5.0 Qualification Scorecard—illustrated in the system blueprint by a 4.2/5.0 score—and categorizes the opportunity into one of three actionable decision states. A tender is designated as a Strong Bid when all hard numerical and documentary gates evaluate to MEETS or MEETS_VIA_EXEMPTION, no mandatory certifications are absent, and zero unresolved cross-document conflicts exist. Conversely, the engine assigns a Conditional Bid verdict when core financial and experience thresholds are satisfied, but either a curable compliance gap exists—such as a reseller needing to request a bid-specific OEM Authorization Letter before bid closure—or an ambiguous exemption conflict between the Main PDF and a linked ATC requires human clarification during the pre-bid query window. Finally, a Red Flag designation warns of a high probability of technical disqualification due to a failed deterministic gate, such as bidder turnover falling below the required threshold without valid exemption, an ineligible entity type, or an uncurable missing BIS license or EMD capacity shortfall.   

Full-Stack Engineering Blueprint: Async Orchestration and Evidence-Linked UI

To deliver a responsive user experience while executing multi-document fetching, OCR and table parsing, and hybrid verification in under 5 minutes, TenderLens separates synchronous API handling from asynchronous background processing using FastAPI, Pydantic, Celery, Redis, PostgreSQL, S3 Object Storage, and Next.js.   

Asynchronous Pipeline Orchestration with Real-Time SSE Progress

When a user initiates a tender audit in the Next.js frontend, waiting synchronously on a blocking HTTP request for several minutes would trigger browser and load-balancer timeouts. Instead, TenderLens implements an event-driven FastAPI, Celery, and Redis Server-Sent Events (SSE) architecture. Upon receiving a POST /api/v1/audits request, the FastAPI backend validates the input payload via Pydantic, creates an AuditJob record in PostgreSQL, enqueues a Celery task chain (discover_task.s() | fetch_recursive_task.s() | hybrid_parse_task.s() | verify_scorecard_task.s()) via the Redis broker, and immediately returns {"task_id": "...", "status": "in_progress"} within milliseconds.   

The Next.js client then establishes a persistent SSE connection (GET /api/v1/audits/{task_id}/stream) to FastAPI. As Celery worker processes complete each phase of ingestion and verification, they publish structured JSON progress updates to a Redis Pub/Sub channel that FastAPI streams directly to the browser. Crucially, if Stage 3 (TinyAgent) is invoked to navigate a gated GeM or PSU filter page, the Celery worker consumes TinyFish's /v1/automation/run-sse stream (STARTED 
→
→ STREAMING_URL 
→
→ PROGRESS 
→
→ COMPLETE) and relays the streaming_url over the FastAPI SSE channel to the Next.js interface. This integration enables the MSME owner or bid consultant to watch the live cloud browser navigate the government portal in real time inside the TenderLens dashboard.   

Frontend Evidence Viewer: Coordinate-Scaled Bounding Box Highlighting

A defining operational requirement of TenderLens is traceable, evidence-first recommendations: when the Qualification Scorecard reports "Meets (Pg 8, Cl 4.1): The bidder shall have an annual turnover of minimum 10 Crore in the last 3 financial years" or "EMD Requirement: Not satisfied (Pg 7, Cl 2.3)", clicking that citation must navigate the user directly to the exact paragraph or table cell inside the source PDF.   

Implementing this capability in the Next.js, TypeScript, and Tailwind CSS frontend requires a split-pane document verification workspace powered by react-pdf (built on Mozilla's pdf.js) or react-pdf-highlighter paired with an SVG coordinate overlay layer. Versioned PDFs—spanning the Main Bid, Linked ATC, and Corrigenda—are stored in S3 Object Storage and streamed to the Next.js client via short-lived presigned URLs (AWS4-HMAC-SHA256). Because backend bounding boxes extracted by PyMuPDF and Docling ([x0, y0, x1, y1]) are recorded in native PDF points (typically 72 DPI), the frontend dynamically normalizes coordinates to match the responsive HTML5 <canvas> width using the viewport scaling ratio:   

scale_ratio
=
𝑊
canvas
𝑊
pdf_native
scale_ratio=
W
pdf_native
	​

W
canvas
	​

	​


Using this ratio, an absolute SVG overlay layer renders a translucent, status-colored highlight rectangle (x = x0 * scale_ratio, y = y0 * scale_ratio, width = (x1 - x0) * scale_ratio, height = (y1 - y0) * scale_ratio) directly over the rendered text layer, executing element.scrollIntoView() to center the exact clause whenever a user selects a row on the Qualification Scorecard.   

Architectural Layer	Core Technologies	Primary Responsibilities in TenderLens	Reliability & Scaling Controls
Frontend UX	

Next.js, TypeScript, Tailwind CSS, react-pdf + SVG Overlay

	

Bidder profile builder, live SSE progress monitor, split-pane Qualification Scorecard, and bounding-box PDF evidence viewer.

	

Client-side page virtualization (react-pdf lazy page loading) to render 200+ page tender PDFs without browser memory leaks.


API & Orchestration	

FastAPI, Pydantic, Celery, Redis (Broker + Pub/Sub)

	

REST endpoints, schema validation, async task chaining, SSE progress streaming, and portal rate-limit throttling.

	

Separate Celery queues for fast I/O (tinyfish_io) vs. CPU-heavy layout parsing (docling_cpu) to prevent worker starvation.


Web Intelligence	

TinySearch, TinyFetch, TinyAgent, TinyMonitor, SerpAPI, HTTPX

	

Geo-targeted discovery (location="IN"), batch Markdown/PDF fetching, stealth browser fallback, and corrigenda delta webhooks.

	

include_etag_and_last_modified HTTP caching; agent_config.mode="strict" and max_steps=10 cost circuit breakers.


Document Intelligence	

PyMuPDF (fitz), IBM Docling (v2), TableFormer

	

Sub-second URI/text extraction, bilingual column clipping, neural table cell recovery, and hierarchical clause tree reconstruction.

	

Two-tier page router: PyMuPDF parses prose pages at ~250 pages/sec; Docling runs selectively on complex table and scanned pages.


Data & Storage	

PostgreSQL, S3 Object Storage, Redis Cache, Docker

	

Relational storage of versioned clause DAGs, bounding-box provenance, immutable PDF artifacts, and TTL cache.

	

Content-addressable SHA-256 hashing of downloaded PDFs in S3 so multiple MSMEs auditing the same GeM tender share one parsed artifact.

  
Competitive Landscape and Go-To-Market Strategy

To evaluate TenderLens's commercial viability and pricing architecture, its capabilities must be benchmarked against both domestic Indian tender aggregators (BidAssist and TrackTender) and enterprise global capture platforms (Procurement Sciences' Awarded AI).   

Structural Gap in the Indian Procurement Tech Market

The Indian tender discovery market is dominated by high-volume listing aggregators, led by BidAssist (owned by the OfBusiness Group). BidAssist has achieved massive distribution—serving 1.7 million users (with over 60% located in Tier-II and Tier-III cities) and tracking 50,000+ live tenders daily across 2,000+ sources (3 Lakh+ active tenders and 4 Crore+ historical tender results). Its business model relies on a "free-forever" search funnel coupled with a 3-day free trial, monetized via gated document downloads (₹299 per tender after a 2-document monthly free cap) or annual subscriptions starting at ₹3,000/year (~₹250/month billed annually for a single-state Basic/Solo plan, plus ₹1,000 per additional state up to 5 states, and GeM or Bid Advisory plans starting from ₹499). Crucially, BidAssist's subscription revenue exceeds its operating costs, allowing it to function as a self-funded customer acquisition engine for OfBusiness's core B2B raw-material commerce and working-capital lending businesses.   

Meanwhile, newer challengers such as TrackTender attack dashboard fatigue by offering a chat-first (Telegram and WhatsApp) alert pipeline priced at ₹30 for the first month (~₹1/day) and a flat ₹300/month (₹255/month billed yearly) for 3 states and 3 categories, delivering pre-parsed bid documents directly into chat without per-download gating. At the opposite end of the global spectrum, US federal capture platforms like Procurement Sciences (Awarded AI) provide FedRAMP Moderate-authorized enterprise workflows—including Probability of Win (PWIN) scoring, compliance matrices, and proposal drafting—at enterprise license tiers benchmarked around $40,000+/year.   

Neither BidAssist nor TrackTender resolves the cross-document qualification verification problem. BidAssist provides high-level summary cards inside its mobile and web apps, and TrackTender extracts headline metadata such as EMD and submission deadline into Telegram messages, but both leave the bidder to manually cross-reference 50-page uploaded ATCs and sequential corrigenda against their own balance sheets and ISO or BIS certificates.   

Unit Economics, Beachhead Execution, and Second-Order Monetization

TenderLens's go-to-market rollout is anchored in a disciplined three-milestone validation sequence starting with a Phase 1 geographical beachhead in Haryana (6,155 tenders) focused on Electrical and IT MSMEs. In Milestone 01 (50-Tender Benchmark), the engineering team constructs a ground-truth labeled evaluation dataset of 50 GeM tenders—complete with linked ATCs and corrigenda—to verify that the hybrid pipeline meets its 85%+ Disqualifier Precision, 80%+ Disqualifier Recall, and 90%+ Linked ATC Capture Rate targets. Following benchmark validation, Milestone 02 (Head-to-Head ATC Audit) pairs TenderLens against manual review by human bid consultants to quantify error reduction, caught exemption traps, and time saved relative to the < 5 mins processing target. In Milestone 03 (MSME Pilot), electrical and IT contractors are onboarded onto a Freemium tier offering 3 tender audits per month, converting into an MSME Pro monthly SaaS subscription (featuring high-volume audits and TinyMonitor Corrigenda Delta Alerts) and Enterprise Consultant API seats designed for bid advisory agencies managing multiple client profiles.   

Pipeline Cost Component	API / Compute Resource	Unit Cost Basis	Estimated Usage per Audit	Marginal Cost per Tender Audit
Stage 1: Discovery	

TinySearch API

	

$0.00 / call (up to 12,000/day; 120 rpm on Startup Tier)

	

1–3 search queries per discovery run

	

$0.000 (₹0.00)


Stage 2: Document Fetch	

TinyFetch Batch API

	

$0.00 / call (600 URLs/min on Startup Tier)

	

1 Main PDF + 2–4 linked ATC/Corrigenda URLs

	

$0.000 (₹0.00)


Stage 3: Stealth Fallback	

TinyAgent SSE (strict mode)

	

$0.016 / step (50% off on Startup Tier 2)

	

Triggered on ~15–20% of gated tenders (~4 steps/run)

	

~$0.010–$0.013 (~₹0.85–₹1.10)


Stage 4: Hybrid Parse & LLM	

PyMuPDF + Docling CPU + Structured LLM

	

Local CPU worker + LLM token inference

	~8K–15K input tokens on triaged eligibility pages	~$0.015–$0.040 (~₹1.25–₹3.35)
Corrigenda Delta Watch	

TinyMonitor API (Pro Tier)

	

$0.005 / completed check

	

Optional (2 checks/day for 10 days on shortlisted bids)

	

$0.100 (~₹8.40 per watched bid)

  

Because TenderLens caches parsed tender documents across users via S3 and Redis TTL caching, the total marginal cost per uncached tender audit is approximately $0.03 to $0.05 (₹2.50 to ₹4.25), and drops below ₹0.50 when a cached tender is re-evaluated against a second MSME's profile using deterministic Python gates. Serving the Freemium allowance of 3 audits per month costs less than ₹13 per user, enabling highly profitable conversion into an MSME Pro tier priced between ₹499/month and ₹1,499/month.   

Beyond direct SaaS subscriptions, OfBusiness's monetization of BidAssist demonstrates the strategic power of pairing tender intelligence with B2B working-capital credit. TenderLens possesses an even stronger underwriting signal than a discovery portal: verified technical and financial pre-qualification. When an Indian MSME receives a Strong Bid scorecard on TenderLens, it immediately faces capital requirements for Earnest Money Deposit (EMD) bid security prior to submission and Performance Bank Guarantees (ePBG) or invoice discounting upon contract award. Embedding a one-click EMD Surety Bond and working-capital financing workflow directly into the Qualification Scorecard allows TenderLens to pass cryptographically auditable compliance reports to partner lenders, capturing high-margin fintech origination fees alongside recurring software revenue.   

Risk Matrix and Actionable Implementation Roadmap

To transition TenderLens from its hackathon proposal architecture to a production-hardened system capable of auditing thousands of Haryana, GeM, and PSU tenders daily, TenderLens must address six primary operational and legal risk vectors.   

Architectural Risk Vector	Root Technical Cause	Production Mitigation Strategy
Missed External ATC Files (< 90% Capture)	

GeM PDFs embed "Click here to view the file" ATC links inside PDF URI dictionaries rather than visible text, and TinyFetch is a single-hop extractor.

	

Extract all span.uri and /Annots link objects via PyMuPDF during the Tier 1 pass and feed discovered URLs into a Celery recursive fetch queue (depth limit 
𝑑
max
⁡
=
2
d
max
	​

=2).


Hallucinated Eligibility via Superseded Clauses	

Corrigenda override baseline bid and ATC clauses using natural-language supersession declarations.

	

Enforce a strict Precedence DAG (
Corr
𝑁
>
Corr
𝑁
−
1
>
Uploaded ATC
>
Text ATC
>
Main PDF
Corr
N
	​

>Corr
N−1
	​

>Uploaded ATC>Text ATC>Main PDF) in Python before evaluating thresholds.


CPU Bottlenecks Violating < 5 Min SLA	

Running Docling + TableFormer + OCR across every page of a 250-page PSU tender on CPU workers takes several minutes.

	

Implement two-tier page triage: parse all pages in < 1 sec with PyMuPDF (fitz) and route only table-dense or low-character (scanned) pages to DocumentConverter.


TinyAgent Wallet Drain on Broken Portals	

Default EVA max_steps is 150 ($2.40/run), which can exhaust wallet funds if a portal enters an infinite redirect or CAPTCHA loop.

	

Pass agent_config={"mode": "strict", "max_steps": 10, "max_duration_seconds": 60} and route hard CAPTCHA/DSC failures to the Manual Upload fallback.


TinySearch Query Rejection or Low Precision	

Combining recency_minutes with after_date throws a validation error; site: operators in query are deprecated.

	

Use include_domains for portal scoping, pass bidder profile context via the purpose parameter (up to 2,000 chars), and separate recency from calendar date filters.


MuPDF / PyMuPDF AGPLv3 Licensing Exposure	

PyMuPDF (fitz) is licensed under GNU AGPLv3, which can trigger source-code disclosure obligations depending on network service distribution.

	

Isolate PDF parsing inside an internal microservice or evaluate Docling's native docling-parse / pypdfium backends (MIT/Apache-2.0) if commercial MuPDF licensing is not acquired.

  
Immediate Engineering Sequence for Milestone 01 to Milestone 03

Executing this roadmap begins with enrolling TenderLens in the TinyFish for Startups program (tinyfish.ai/startups) under Tier 1 (for independent pre-production teams, providing up to $7,000 in value, $100/month in wallet credits for 6 months, and 50 concurrent TinyAgent runs) or Tier 2 (for accelerator or investor-backed teams, providing up to $12,000 in value, $500 initial wallet credits, and 50% off TinyAgent for 24 months). Both tiers immediately quadrupled standard rate limits to 120 TinySearch requests per minute and 600 TinyFetch URLs per minute, enabling TenderLens to ingest the 6,155-tender Haryana beachhead and construct the 50-tender GeM benchmark dataset at zero infrastructure cost.   

In parallel with API provisioning, the engineering team should assemble the 50-tender GeM evaluation harness by curating a stratified sample across Haryana electrical and IT categories—combining straightforward single-PDF bids, tenders with hyperlinked multi-page buyer ATCs, and complex solicitations featuring multiple superseding corrigenda and MSME or MII exemption overrides. Validating the two-tier PyMuPDF and Docling router alongside the deterministic Python rules engine against this golden dataset will empirically establish the 85%+ precision and 80%+ recall baselines prior to onboarding pilot MSMEs. Finally, wiring TinyMonitor (POST /v1/monitors) into the FastAPI backend will operationalize automated corrigenda monitoring at $0.005 per check, ensuring that whenever an MSME shortlists a Strong Bid or Conditional Bid, any subsequent portal amendment automatically triggers a delta re-verification before bid submission.   

Report unsafe content
Opens in a new window
Sign in