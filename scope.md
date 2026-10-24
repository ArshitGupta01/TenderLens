# TenderLens — Final Development Scope and Delivery Plan

**Updated:** 2026-10-24
**Status:** implementation plan for the next product phase
**Decision:** retain the current static prototype as a clearly labelled demo while the verified tender-review workflow is built and validated.

## 1. Evidence used for this update

This plan reconciles the repository snapshot in `single.xml` (an earlier, read-only Repomix export), the current source tree, the shared contract in `contracts/schema.py`, the backend trackers, and the current public website.

The snapshot documents the original intended architecture. The current tree shows that the FastAPI routes, deterministic gatekeeper, PDF processor, qualification engine, and demo website have since been added. It also shows that only live search is connected to the website; fetching, document review, and the scorecard are not yet an end-to-end product workflow.

## 2. Current baseline

### Available now

- Static, accessible website with fictional examples, a document-order explainer, a local-only basic profile, and an optional live tender-search form.
- FastAPI health, search, fetch, audit-evaluation, and SSE endpoints.
- A Pydantic contract for bidder profiles, gate results, citations, and qualification scorecards.
- Deterministic checks for turnover, experience, EMD, Make in India, OEM authorization, and mandatory certifications.
- PyMuPDF extraction of text blocks, page coordinates, PDF links, and an initial document-rank heuristic.
- Ten repository tests covering selected gates, endpoint shape, PDF-link extraction, and basic rank inference.

### Not ready to claim

- A real eligibility decision, production audit, or legally complete procurement interpretation.
- A browser workflow for tender fetching, source review, or scorecard evaluation.
- Durable accounts, cloud bidder profiles, document storage, audit history, or monitoring.
- Verified behaviour against a representative corpus of live tender documents.
- Live provider reliability or a passing local test run in this checkout. `uv` and `pytest` are not installed in the available runtime, so the existing tests were not rerun for this update.

## 3. Product outcome

Deliver a human-in-the-loop tender-review workflow that lets a bidder:

1. Find a public tender.
2. Review every relevant tender document and later update in a visible precedence order.
3. Compare evidenced requirements with a deliberately supplied bidder profile.
4. Receive a source-linked **review recommendation**, with uncertainty and missing evidence made explicit.
5. Export or save the review only after privacy, security, and retention requirements are agreed.

The product must never present an automated result as legal advice or a guarantee of bid eligibility. A buyer's official documents and clarifications remain authoritative.

## 4. Scope boundaries

### In scope for the next release sequence

- Verified tender discovery and document ingestion from an approved portal allowlist.
- Source-preserving PDF and document processing, including linked ATCs and corrigenda.
- Deterministic evaluation of clearly extracted numerical and boolean requirements.
- Evidence-first scorecards with citations, source URLs, page coordinates, extraction confidence, and manual-review states.
- A frontend workflow for search, review progress, evidence inspection, and scorecard display.
- Automated tests, golden-document evaluation, operational logging, and a privacy/security baseline.

### Explicitly out of scope until a later decision

- Filing or submitting bids; making legal determinations; automated buyer communication.
- Silent web crawling outside approved procurement portals.
- Uploading or retaining sensitive company records before an approved data model, access control, retention policy, and deletion workflow exist.
- Billing, multi-tenant administration, and enterprise integrations.
- Treating an LLM extraction as authoritative when source text, ranking, or interpretation is uncertain.

## 5. Delivery plan

| Phase | Outcome | Work | Exit criteria |
| --- | --- | --- | --- |
| 0. Stabilize contracts and safety | A trustworthy development baseline | Version the API contract; document request/response examples; validate portal and fetch URLs against an allowlist; apply request limits, timeouts, structured errors, and correlation IDs; replace simulated SSE with actual job state or label it demo-only. | Contract tests pass; unsafe or unsupported URLs are rejected; every API failure reaches the user as a clear non-decision. |
| 1. Verify ingestion | Reproducible source collection | Download and fingerprint source documents; store source URL, retrieval time, content hash, document type, publication time, and portal metadata; follow linked files only within the approved policy; use the PDF processor rather than paragraph-splitting fetched markdown. | A curated set of multi-document tenders is ingested repeatably, with original-source links and hashes. |
| 2. Make precedence auditable | Correct, explainable document order | Replace filename-only rank inference with metadata plus document dates; distinguish latest from earlier corrigenda; record why each document has a rank; detect unresolved conflicts and route them to manual review. | Every extracted requirement can show its effective source, superseded source(s), and reason for its status. |
| 3. Harden requirement extraction | Reliable, limited automation | Define a canonical criterion schema with units, normalized amounts, confidence, and citation; add parsers for turnover, experience, EMD, MII, MAF, and certificates; use structural/table parsing only where the fast pass cannot preserve the evidence. | Extraction accuracy and source-citation completeness meet agreed thresholds on the golden set; low-confidence results are not auto-decided. |
| 4. Validate the decision engine | Safe recommendations | Separate statutory-policy assumptions from tender-specific rules; require evidence for overrides; return `MANUAL_REVIEW` for ambiguity, absent documents, failed retrieval, or incompatible terms; make score logic explainable and tested. | No `STRONG_BID` result is possible after a retrieval, parse, or evidence failure; unit, contract, and negative-path tests pass. |
| 5. Build the review experience | A usable human review flow | Add a real profile form only after consent and data handling are approved; connect search to tender selection, ingestion status, evidence viewer, and scorecard; provide accessible loading/error/retry states; keep the current fictional demo separate. | A user can review one audited tender end to end and inspect each result's source without reading raw JSON. |
| 6. Establish persistence and operations | Controlled pilot readiness | Decide the data architecture; add authentication/authorization, encryption, secret management, retention/deletion, audit logging, backups, monitoring, and rate/cost controls; add background jobs only when real workloads require them. | Threat model and data-retention policy are approved; an authorized user can access only their records; operational alerts cover failed ingestion and provider spend. |
| 7. Evaluate and pilot | Evidence for a limited release | Build a stratified, labelled 50-tender benchmark; measure discovery, linked-document capture, rule extraction, citation completeness, recommendation precision/recall, latency, and cost; conduct human review of failures. | Pre-agreed quality targets are met, including 100% source links for displayed decisive findings, before a pilot claim is made. |

## 6. Priority technical corrections

These items precede a real scorecard UI because they can otherwise produce an overconfident result.

1. **Fail closed on ingestion errors.** The fetch service currently represents provider errors as documents and evaluation can continue. A failed fetch, empty evidence set, or unsupported document must produce a non-decision/manual-review result.
2. **Use the document processor in the audit pipeline.** The evaluation route currently turns fetched markdown paragraphs into chunks. It must process retained source documents to preserve page numbers, links, and coordinates.
3. **Make precedence data-driven.** Filename matching cannot reliably identify the latest corrigendum. Use portal/document metadata, dates, version identifiers, and explicit conflict detection.
4. **Protect the fetch and search surfaces.** Validate schemes, hostnames, redirects, file size, content type, and depth; do not allow a caller to choose arbitrary domains through the `portal` field.
5. **Replace simulated progress.** Progress events must correspond to an observable background job and a stable task identifier, or the endpoint remains a demo-only UI aid.
6. **Test offline with provider mocks.** Endpoint tests should not depend on a live TinyFish call or credentials. Add fixtures for successful, blocked, malformed, empty, and conflicting source documents.
7. **Align documentation and contracts.** Maintain one versioned API description and update website language only after the connected behavior is verified.

## 7. Quality gates and measures

Before any pilot, track these measures by portal, tender type, and document count:

- Discovery relevance and completeness.
- Linked ATC/corrigendum capture rate.
- Requirement extraction precision and recall.
- Citation completeness: every displayed decisive requirement links to a source document and page or a clearly stated limitation.
- Precedence-resolution accuracy against labelled examples.
- False-positive `STRONG_BID` rate, targeted at zero for known retrieval, parsing, or conflict failures.
- Median and 95th-percentile review latency, provider cost per review, and failed-job rate.
- Accessibility checks for the review flow and error states.

Initial numerical targets for precision and recall should be agreed only after the benchmark labels and review rubric are completed. The historic 85%/80% aspiration is not evidence of achieved quality.

## 8. Ownership and sequencing

| Workstream | Primary ownership | Dependencies |
| --- | --- | --- |
| Contracts, ingestion, parsing, gates, API, test harness | Backend / intelligence | Source corpus and policy review |
| Review flow, evidence viewer, accessibility, UX copy | Frontend | Stable versioned API and realistic fixtures |
| Benchmark labels, procurement-rule review, failure analysis | Research / domain review | Collected source documents and canonical criteria |
| Data model, storage, auth, retention, operations | Platform / product owner | Explicit decision to persist sensitive data |

Sequence backend contract and ingestion validation before attaching financial or registration data to the browser workflow. Build the scorecard UI against fixtures in parallel only after its states are agreed; connect it to live evaluations after Phase 4's safety gates pass.

## 9. Immediate next actions

1. Install/sync the declared development environment and rerun the existing suite; record actual results.
2. Freeze `contracts/schema.py` behind a versioned API description and add representative request/response fixtures.
3. Implement URL/domain validation and explicit fail-closed outcomes for discovery, fetch, and evaluation.
4. Assemble and label the first 10 multi-document tenders for ingestion and precedence testing.
5. Refactor the audit flow to process downloaded source documents and emit evidence-bearing chunks.
6. Add mocked provider, failure-path, precedence-conflict, and end-to-end API tests before connecting scorecard evaluation to the website.

## 10. Release decision

The current website may continue to be shown as an experimental, fictional demonstration with optional live discovery. Do not market or deploy it as a qualification engine until the ingestion, evidence, security, and benchmark gates in this document have been completed and independently reviewed.
