# TenderLens Agent Handoff

Updated: 2026-10-24

## Project state

- `main` contains the merged `Mohit-Backend` implementation and a static website for Team Traxo's TenderLens hackathon prototype.
- The website includes a fictional report, sample tender explorer, document-order guide, bidder profile, optional live tender search, light/dark theme, easy guide, privacy notice, terms and conditions, quick answers, and separate sign-in, registration, account and saved-tenders pages.
- Supabase email/password and Google auth, cross-device basic profiles, and explicitly saved live tender links are implemented in the client. External setup remains pending: Supabase project values, Google OAuth provider, account SQL, and end-to-end verification against the owner's project.
- Sample data and checklist changes stay in the browser. Fictional samples cannot be stored as account tenders. Live search sends a phrase and selected portal only after the visitor submits. A profile is synced only after an authenticated save; a live tender is stored only after “Save to account.”
- The backend uses `CORS_ORIGINS` for its local allowlist. Keep credentials and private bidder or tender data out of Git.

## Working rules

- Read `AGENTS.md`, `README.md`, `FINAL_IMPLEMENTATION_PLAN.md`, and the relevant team tracker before changing the project.
- Keep the website clear that sample tenders and results are fictional. Describe a feature as working only when it is connected in the code.
- Preserve source-linked evidence, document update order, fixed checks for clear numbers, and human review for unclear or conflicting wording.
- After each meaningful implementation task, update this handoff and the relevant tracker (`arshit-agents.md` for the website or `MOhit-Agents.md` for backend work) with completed work, verification actually performed, and the next open milestone.
- Never record credentials, private profiles, or private tender documents in this file.

## Latest work — 2026-10-24

- Added Supabase account pages for email/password and Google sign-in, confirmation and reset links, profile editing, sign-out, and a dedicated saved-live-tenders page.
- Added a FastAPI public config route that exposes only the Supabase project URL and browser-safe publishable key; no secret key or database password is exposed.
- Added `supabase/setup.sql` with profile/saved-tender tables, ownership constraints and explicit owner-scoped RLS policies. Live tender save controls appear only for real search results; sample bookmarks stay visit-only.
- Added account setup instructions to the easy guide and README, updated privacy/terms, and marked provider credential setup and account verification as the next milestone. No account credentials have been configured or tested against a Supabase project.
- Added a subtle scroll parallax ornament and responsive account screens with larger touch-friendly controls and shared dark theme.
- Next: apply `supabase/setup.sql` in the chosen Supabase project, configure `.env` and the Google/SMTP providers, then verify email confirmation, Google redirect, profile sync and cross-account RLS isolation.

- Added a tablet breakpoint for 851–1100px screens after reviewing the supplied layout screenshot. The header now uses the compact menu and the hero stacks into a readable full-width column at those sizes.
- Checked the live local preview at its available narrow viewport and reviewed the breakpoint rules against the 1056px screenshot dimensions. A dedicated 1056px browser viewport was not available in the embedded preview.
- Fixed the dark-theme closing banner, which used the theme's foreground color as its background, improved the small caption contrast and tablet spacing, and hid the floating top button while it would cover the footer.
- Added an editable bidder profile draft for organization name, bidder type, years in business and region. It saves only to browser storage, has a clear action, and is not sent with live search. Updated the privacy and terms notices, README and easy guide to explain this.
- Checked the profile and checklist UI in the preview. JavaScript syntax and whitespace checks passed; no backend or live-search tests were run.
- Merged `origin/Mohit-Backend` into `main`.
- Published the merged backend and finished website update in commit `518191e` on `origin/main`.
- Increased text sizes and simplified visible report language; added a plain-language guide, glossary, quick answers, dark mode, and terms page.
- Connected optional live search to the backend health check and search endpoint, with local-only defaults for preview and safe rendering of result links.
- Tightened backend CORS defaults to local preview origins and disabled credentialed requests.
- Reviewed the desktop and narrow browser layouts, confirmed the guide, terms page and interactive report controls load, and fixed small-screen horizontal overflow.
- Checked JavaScript syntax and whitespace; the backend test suite and external provider were not run for this update.
- Next: verify the backend suite and provider behavior when ready, then connect file review and scorecard flows only after their data and privacy behavior are ready.
