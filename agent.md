# TenderLens Agent Handoff

Updated: 2026-10-24

## Current project state

- TenderLens is a static HTML/CSS/JavaScript website with a FastAPI backend. The main site includes a fictional sample report, tender search, document-order guide, theme toggle, account pages, saved live notice links, easy guide, privacy notice and terms.
- The Strategy tools page sends manually entered values to `POST /api/v1/strategy/preview`. It provides clarification prompts, capability-gap notes, a draft compliance checklist/CSV and an EMD cash scenario. It does not fetch documents or persist the request. Public-source search is a separate, explicit action through `GET /api/v1/strategy/forensics` and needs a configured provider.
- Five strategy helper modules exist on `main`, but they are a lighter implementation than the latest `Mohit-Backend` branch. The preview is not a source-grounded tender audit.
- Search is connected to the website when configured. Fetch and qualification-audit API routes exist, but there is no website workflow for document fetching, uploaded-source review or saved audit history.
- Supabase Auth and direct, signed-in client access support profile and saved-live-notice data under the SQL row-level security policies. Real email/Google sign-in and RLS isolation still need verification. The backend audit persistence service from the latest Mohit branch is not on `main`.
- The sign-in page may show the shared demo email shortcut, but no password belongs in public source. Keep credentials, provider keys and private bidder/tender data out of Git.
- Sample tender details, sample filters and checklist selections are illustrative and remain in the browser. Do not describe them as verified procurement findings.

## GitHub comparison — 2026-10-24

- `main` was published at `527bf0b11f238b05acc5e47e0a196fbff95c4aa3`.
- The remote `Mohit-Backend` head was `ed4cf8d9fa4351a0bbabf9395be25a07c6d9aa9d` when checked. The histories diverge: `main` has 11 commits and the Mohit branch has 4 commits beyond their common base.
- The Mohit branch contains fuller versions of the five strategy pillars, `backend/services/supabase_service.py`, audit/profile persistence routes, expanded Supabase schema and tests, and a Supabase Python dependency. These updates have not been integrated into `main`.
- Do not merge the persistence routes as-is. They accept caller-supplied `user_id` values, and the service can use a service-role key. Before porting them, verify the bearer token, bind every read/write to its authenticated subject, and preserve row-level security. Prefer user-scoped Supabase access over service-role access unless a reviewed server-only operation requires it.
- The comparison was read-only; no source changes were made during it.

## Verification recorded for the latest main update

- Python syntax compilation, FastAPI import/OpenAPI generation, a synthetic strategy-preview request, and strategy-page rendering passed.
- `node --check auth.js` and `git diff --cached --check` passed before publishing.
- The full backend test suite and live provider-backed search were not run in that update. A prior sample provider call returned HTTP 401 because the configured TinyFish value was a placeholder.

## Next milestones

1. Review and safely port any needed Mohit branch improvements, starting with authenticated Supabase persistence and ownership checks.
2. Run the backend suite against the current `main` source and test the strategy endpoints without external credentials.
3. Connect tender fetching and a source-grounded document review only after upload consent, source precedence, retention and access controls are defined.
4. Verify real Supabase sign-in, profile/save sync and RLS isolation; test the responsive pages on Android-sized and desktop viewports.

## Working rules

- Read `AGENTS.md`, `README.md`, `FINAL_IMPLEMENTATION_PLAN.md`, the relevant team tracker and contracts before project changes.
- Preserve document precedence, source-linked evidence, deterministic checks for explicit values, and human review for ambiguous rules.
- Keep fictional workflows local and label them clearly. Describe a feature as implemented only when its code path is connected and verified.
- Update this handoff and the relevant tracker (`MOhit-Agents.md` for backend work, `arshit-agents.md` for website work) with actual changes and the next open milestone.
- Never record passwords, API secrets, private profiles or private tender documents here.
