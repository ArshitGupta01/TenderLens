# TenderLens Agent Handoff

Updated: 2026-10-24

## Project state

- `main` contains the merged `Mohit-Backend` implementation and a static website for Team Traxo's TenderLens hackathon prototype.
- The website includes a fictional report, sample tender explorer, document-order guide, local bidder checklist, optional live tender search, light/dark theme, easy guide, privacy notice, terms and conditions, and quick answers.
- Only live tender search is connected to the API. The page does not upload tender files or company profiles, run eligibility reviews, create accounts, or save audit history.
- Search sends the visitor's phrase and selected portal only after they submit. Sample data and checklist changes stay in the browser.
- The backend uses `CORS_ORIGINS` for its local allowlist. Keep credentials and private bidder or tender data out of Git.

## Working rules

- Read `AGENTS.md`, `README.md`, `FINAL_IMPLEMENTATION_PLAN.md`, and the relevant team tracker before changing the project.
- Keep the website clear that sample tenders and results are fictional. Describe a feature as working only when it is connected in the code.
- Preserve source-linked evidence, document update order, fixed checks for clear numbers, and human review for unclear or conflicting wording.
- After each meaningful implementation task, update this handoff and the relevant tracker (`arshit-agents.md` for the website or `MOhit-Agents.md` for backend work) with completed work, verification actually performed, and the next open milestone.
- Never record credentials, private profiles, or private tender documents in this file.

## Latest work — 2026-10-24

- Added a tablet breakpoint for 851–1100px screens after reviewing the supplied layout screenshot. The header now uses the compact menu and the hero stacks into a readable full-width column at those sizes.
- Checked the live local preview at its available narrow viewport and reviewed the breakpoint rules against the 1056px screenshot dimensions. A dedicated 1056px browser viewport was not available in the embedded preview.
- Merged `origin/Mohit-Backend` into `main`.
- Published the merged backend and finished website update in commit `518191e` on `origin/main`.
- Increased text sizes and simplified visible report language; added a plain-language guide, glossary, quick answers, dark mode, and terms page.
- Connected optional live search to the backend health check and search endpoint, with local-only defaults for preview and safe rendering of result links.
- Tightened backend CORS defaults to local preview origins and disabled credentialed requests.
- Reviewed the desktop and narrow browser layouts, confirmed the guide, terms page and interactive report controls load, and fixed small-screen horizontal overflow.
- Checked JavaScript syntax and whitespace; the backend test suite and external provider were not run for this update.
- Next: verify the backend suite and provider behavior when ready, then connect file review and scorecard flows only after their data and privacy behavior are ready.
