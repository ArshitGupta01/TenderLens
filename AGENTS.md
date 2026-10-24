# Repository instructions

- Read `README.md`, `FINAL_IMPLEMENTATION_PLAN.md`, the relevant team tracker, and any related contracts or research before making project changes.
- Treat the report and sample tender explorer as illustrative; do not describe fictional workflows as real. Account features may persist only the signed-in bidder profile and live notice links that the user explicitly saves.
- Keep sample searches, filters, checklist selections and sample saves local. Live search submits only after a person chooses Search; saving a real result requires an explicit “Save to account” action.
- Account data must use Supabase Auth and the Supabase Postgres policies in `supabase/setup.sql`. Never bypass row-level security or put a Supabase secret/service-role key in browser code.
- Preserve the project's core principles: tender document precedence, source-linked evidence, deterministic checks for explicit values, and human review for ambiguity.
- Keep credentials and private bidder or tender data out of source control.
- After completing project work, update the relevant progress tracker (`arshit-agents.md` for frontend and project presentation work, `MOhit-Agents.md` for backend work) with completed items and the next outstanding milestone. Do not mark planned features complete based on mockups.
