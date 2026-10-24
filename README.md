# TenderLens

TenderLens is a Team Traxo hackathon project for making public tender requirements easier to review. It brings the main tender, extra buyer terms and official updates into one place, with findings linked to their source.

## What works today

- The website has a fictional sample report, sample tender search and filters, a document-order explorer, a local bidder profile draft, and an evidence checklist.
- The website can run optional live tender search through the FastAPI backend when a TinyFish API key is configured.
- The Strategy tools page sends bidder and tender values you enter to FastAPI to create a temporary review preview: clarification prompts, capability-gap notes, a compliance checklist and CSV, an EMD cash scenario, and optional public-source search. It does not upload tender files or store the preview.
- The backend includes endpoints for finding tenders, fetching linked documents, building a qualification scorecard, and the Strategy tools preview.
- Account pages support Supabase email/password and Google sign-in, a cross-device bidder profile, and saved live tender links when configured. `signin.html`, `signup.html`, `account.html` and `saved-tenders.html` are separate pages.
- The website does not upload files or save audit history. Fictional sample tenders, checklist selections and sample saves stay in the browser. The fetch and scorecard endpoints are not connected to a website form.

This is an experimental hackathon project. Sample tenders and report results are fictional. Check official documents and ask the buyer before acting on any tender.

## Run the website

The sample website works without a backend or API key. From the project folder, run:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open <http://127.0.0.1:4177>. Sample searches, filters, saved examples and the checklist run in your browser and reset when you reload. A signed-out bidder profile draft and theme choice stay in this browser. Account sign-in needs the FastAPI service and the Supabase setup below.

## Turn on live search

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and sync the locked Python dependencies:

```powershell
uv sync --locked
Copy-Item .env.example .env
```

Open `.env` and add your TinyFish key to `TINYFISH_API_KEY`. Keep this file private; it is ignored by Git. Do not put API secrets in the website code. `GEMINI_API_KEY` enables the backend's clause/conflict analysis, and `TAVILY_API_KEY` enables its web-search fallback. Those two are optional unless you use those backend features. `GEMINI_MODEL` defaults to `gemini-3.8-flash`.

Start the API in one terminal:

```powershell
uv run uvicorn backend.main:app --reload
```

Start the website in a second terminal:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open <http://127.0.0.1:4177> and expand “Search current tender notices.” The page checks that the service and API key are ready before it sends the search words and selected portal. The interactive API reference is at <http://127.0.0.1:8000/docs>.

Open <http://127.0.0.1:4177/strategy.html> to enter tender and bidder values and create a review preview. The request goes to POST /api/v1/strategy/preview; the route does not fetch tender files or persist the submitted form. Public-source search is a separate action at GET /api/v1/strategy/forensics and runs only after you choose its button. It sends the tender title and portal to the configured public-search provider and returns unverified links for manual review.

## Technology stack

- Website: responsive HTML, CSS and JavaScript, with the existing local Lenis scroll library.
- API: Python 3.12, FastAPI, Pydantic and Uvicorn.
- Search and document review: the existing TinyFish integration, PyMuPDF, and optional Gemini/Tavily provider adapters.
- Accounts and cross-device saved data: Supabase Auth and Postgres with row-level security.

The strategy modules use the Python and Pydantic dependencies already in pyproject.toml and uv.lock, so this integration adds no new package requirement. Use uv sync --locked to install the full locked project environment. Live public-source search requires TINYFISH_API_KEY or TAVILY_API_KEY in the private backend environment.

By default, the API allows the local website ports 3000 and 4177. If you serve the website from another address, add that exact origin to `CORS_ORIGINS` in `.env` and restart the API.

## Enable accounts and cross-device profile data

1. Create a Supabase project. Copy the Project URL and the **publishable key** from its Connect dialog into `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `.env`. The publishable key is designed for browser clients. Never use a Supabase secret/service-role key in the website or this endpoint.
2. Run [`supabase/setup.sql`](supabase/setup.sql) once in Supabase Dashboard → SQL Editor. It creates profile and saved-tender tables with row-level security policies tied to `auth.uid()`.
3. Enable Email and Google providers in Supabase Authentication. For Google, create an OAuth web client, copy its client ID and secret into Supabase's Google provider settings, and use the callback URL shown in Supabase as Google's authorized redirect URI.
4. Add `http://127.0.0.1:4177/**` and `http://localhost:4177/**` to Supabase Authentication → URL Configuration → Redirect URLs. Set the local Site URL to the address used in your browser.
5. Restart FastAPI. The public endpoint `/api/v1/auth/config` returns only the Supabase project URL and publishable key. Supabase Auth handles credentials; Postgres Data API requests use the signed-in session and the database policies.
6. Create an account at `/signup.html`. Save a profile from the home page or account page. When live search is enabled, save an official notice from a search result to see it at `/saved-tenders.html` on other devices.

The sign-in page includes a shared demo email shortcut; enter the password privately. The demo account must first be created and verified in Supabase. Everyone using a shared demo account can see the profile and saved notices attached to it, so do not store private information there.

For production, set each page's `meta[name="tenderlens-api"]` to the deployed FastAPI base URL, allow the deployed website origin in `CORS_ORIGINS`, and add the deployed site URL to Supabase's redirect allowlist. Configure a trusted SMTP sender in Supabase before relying on confirmation and password-reset emails. Google OAuth client secrets and SMTP credentials stay in the Supabase Dashboard; do not send them in chat or commit them.

## Privacy and data

The sample interface does not send sample tender filters, sample saves or checklist selections to a service. A bidder profile is synced only after a signed-in user chooses to save it; a live notice is stored only after a user explicitly chooses “Save to account.” See [the privacy notice](privacy.html), [terms and conditions](terms.html) and [easy guide](guide.html).

## Repository guide

- strategy.html, strategy.js — entered-value preview, checklist export and explicit public-source search controls.
- backend/engine/ — deterministic gates plus clarification prompts, consortium gap notes, compliance checklist, EMD scenario and public-record search helpers.

- `index.html`, `styles.css`, `app.js`, `auth.js`, `theme.js` — website, local sample interactions, Supabase account flows, live-search connection and theme support.
- `signin.html`, `signup.html`, `account.html`, `saved-tenders.html` — sign-in, registration, bidder profile and saved live notice pages.
- `supabase/setup.sql` — account tables and owner-only row-level security policies.
- `guide.html`, `privacy.html`, `terms.html` — plain-language help and website notices.
- `backend/` — FastAPI routes, tender search and fetch services, document processing and scorecard logic.
- `contracts/schema.py` — shared Python data models.
- `tests/` — backend test suite.
- `vendor/` — pinned Lenis distribution and its MIT license.
- `FINAL_IMPLEMENTATION_PLAN.md`, `research/` — product and procurement research.
- `arshit-agents.md`, `MOhit-Agents.md` — frontend and backend project trackers.

## Project direction

Next steps include configuring the team's Supabase project and Google OAuth credentials, verifying sign-up/sign-in and row policies against that project, reviewing backend behavior against real tender documents, and connecting verified file and scorecard workflows. This repository is not a production procurement service.
