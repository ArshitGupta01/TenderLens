# TenderLens

TenderLens is a Team Traxo hackathon project for making public tender requirements easier to review. It brings the main tender, extra buyer terms and official updates into one place, with findings linked to their source.

## What works today

- The website has a fictional sample report, sample tender search and filters, a document-order explorer, a local bidder profile draft, and an evidence checklist.
- The website can run optional live tender search through the FastAPI backend when a TinyFish API key is configured.
- The backend includes early endpoints for finding tenders, fetching linked documents and building a sample qualification scorecard.
- The website does not upload files, keep cloud company accounts or save audit history. A short organization profile can be saved in the browser on this device only. The fetch and scorecard endpoints are not connected to a website form.

This is an experimental hackathon project. Sample tenders and report results are fictional. Check official documents and ask the buyer before acting on any tender.

## Run the website

The sample website works without a backend or API key. From the project folder, run:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open <http://127.0.0.1:4177>. Sample searches, filters, saved examples and the checklist run in your browser and reset when you reload. The theme choice and optional basic bidder profile stay in this browser; clear the profile in the page or remove the site's data in browser settings.

## Turn on live search

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and sync the Python dependencies:

```powershell
uv sync
Copy-Item .env.example .env
```

Open `.env` and add your TinyFish key to `TINYFISH_API_KEY`. Keep this file private; it is ignored by Git. Do not put API keys in the website code.

Start the API in one terminal:

```powershell
uv run uvicorn backend.main:app --reload
```

Start the website in a second terminal:

```powershell
python -m http.server 4177 --bind 127.0.0.1
```

Open <http://127.0.0.1:4177> and expand “Search current tender notices.” The page checks that the service and API key are ready before it sends the search words and selected portal. The interactive API reference is at <http://127.0.0.1:8000/docs>.

By default, the API allows the local website ports 3000 and 4177. If you serve the website from another address, add that exact origin to `CORS_ORIGINS` in `.env` and restart the API.

## Privacy and data

The sample interface does not send tender filters, saved examples, checklist selections or the local bidder profile to a service. Live search sends only the search phrase and portal, after you press the search button. The local profile avoids registration IDs, financial figures and files. See [the privacy notice](privacy.html), [terms and conditions](terms.html) and [easy guide](guide.html).

## Repository guide

- `index.html`, `styles.css`, `app.js`, `theme.js` — website, local sample interactions, live-search connection and theme support.
- `guide.html`, `privacy.html`, `terms.html` — plain-language help and website notices.
- `backend/` — FastAPI routes, tender search and fetch services, document processing and scorecard logic.
- `contracts/schema.py` — shared Python data models.
- `tests/` — backend test suite.
- `vendor/` — pinned Lenis distribution and its MIT license.
- `FINAL_IMPLEMENTATION_PLAN.md`, `research/` — product and procurement research.
- `arshit-agents.md`, `MOhit-Agents.md` — frontend and backend project trackers.

## Project direction

Next steps include reviewing backend behavior against real tender documents, connecting verified file and scorecard workflows to the website, and deciding what data storage and security are required before any production use. This repository is not a production procurement service.
