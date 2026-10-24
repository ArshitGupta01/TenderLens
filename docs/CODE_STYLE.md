# TenderLens Code Style Guide
==============================

## 1. Purpose
This document establishes the official coding standards, formatting conventions, and architectural principles for the TenderLens project. All human developers and AI assistants must follow these guidelines.

## 2. Technology Stack
- **Frontend**: Semantic HTML5, Modern CSS3 with CSS Custom Properties, Vanilla ES6+ JavaScript.
- **Backend API**: Python 3.12, FastAPI, Pydantic v2, Uvicorn, `sse-starlette`.
- **Package & Virtualenv Management**: `uv` (Astral) with pinned `pyproject.toml` and `uv.lock`.
- **Database & Auth**: Supabase PostgreSQL with Row-Level Security (RLS) and Supabase Auth.
- **Testing**: `pytest`, `pytest-asyncio`, FastAPI `TestClient`, `node --check`.

## 3. General Principles
- **Clarity Over Cleverness**: Code must be explicit, easy to follow, and self-documenting.
- **Separation of Concerns**: Keep deterministic gatekeeping logic (`backend/engine/deterministic_gatekeeper.py`) completely separate from semantic LLM auditing (`backend/engine/qualification_engine.py`) and API routes (`backend/main.py`).
- **Zero Hallucination in Math**: Always use pure-Python arithmetic for financial and statutory gates (e.g. 3-year average turnover, CPWD 80/50/40 similar-work ratios, Make in India local content percentages).
- **Graceful Degradation**: Frontend features must remain functional even if backend services or optional third-party providers (TinyFish, Gemini, Tavily) are temporarily offline or unconfigured.

## 4. Naming Conventions
- **Python**:
  - Modules & files: `snake_case` (e.g., `precedence_rag_engine.py`, `tinyfish_service.py`)
  - Classes & Pydantic Models: `PascalCase` (e.g., `BidderProfile`, `QualificationScorecard`, `PrecedenceDAGGraph`)
  - Functions & methods: `snake_case` (e.g., `evaluate_capital_risk`, `extract_criteria_from_chunks`)
  - Constants & Config: `UPPER_SNAKE_CASE` (e.g., `MAX_CRAWL_DEPTH`, `ALLOWED_DOMAINS`)
- **JavaScript & Frontend**:
  - Files: `kebab-case` or `lowercase` (e.g., `strategy.js`, `auth.js`, `theme.js`)
  - Variables & functions: `camelCase` (e.g., `renderToolkit`, `applyPreset`, `initDemoLogin`)
  - HTML Data Attributes: `kebab-case` prefixed with `data-` (e.g., `data-auth-signin`, `data-strategy-preset`)
  - CSS Classes: `kebab-case` with functional or BEM-style names (e.g., `strategy-gate-card`, `top-menu-banner`, `is-active`)

## 5. Frontend & UI Conventions
- **Accessible HTML**: Always include `<label for="...">` with matching `<input id="...">`, `aria-live="polite"` on status fields, `role="status"` or `role="tab"`, and `<a class="skip-link">`.
- **Responsive Mobile-First CSS**: Use `clamp()`, `minmax()`, flexbox, and grid layouts. Touch targets must be at least 44x44px. Prevent horizontal scrolling on mobile viewports.
- **Theme Variables**: All colors must use CSS custom properties (`var(--surface)`, `var(--ink)`, `var(--green)`, `var(--paper-deep)`) supporting both Light and Dark modes.

## 6. Error Handling & Security
- Never expose stack traces, database credentials, or secret API keys in client-facing error responses.
- Always provide user-friendly, actionable error messages with guidance.
- Validate all incoming JSON requests with Pydantic v2 schemas and HTTP status codes (`200`, `201`, `400`, `401`, `403`, `404`, `429`, `500`).
