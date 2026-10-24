# TenderLens

TenderLens is a Team Traxo hackathon project exploring evidence-backed qualification reviews for Indian public tenders. Its goal is to help bidders read the full opportunity set—including the main bid, buyer-added terms and later corrigenda—before making a bid/no-bid decision.

## Project status

The website in this repository is a static presentation prototype. Its interactive report uses illustrative data; it does not search live portals, accept uploads, run an audit or save bidder profiles. The Python entry point is still a scaffold. API routes and the qualification workflow described in the engineering plan are planned work, not a deployed service.

Treat the sample as a product concept only. It is not a legal opinion or an eligibility determination.

## Preview the website

The site has no build step or package installation. From the repository root, run:

```powershell
python -m http.server 8000
```

Then open <http://localhost:8000> in a browser. The interactive sample report runs locally in the browser.

## Product direction

The proposed workflow is to:

1. Capture a bidder profile with financial, experience, certification and MSME details.
2. Discover the main tender and retrieve linked ATCs and later amendments where accessible.
3. Apply document precedence, keeping the latest corrigenda and source references attached to extracted clauses.
4. Check explicit values with deterministic rules and use clause analysis for less structured requirements.
5. Show an evidence-backed scorecard and send ambiguous or conflicting clauses for human review.

The system is intended as decision support. People must verify tender terms with the procuring authority before acting.

## Repository guide

- `index.html`, `styles.css`, `app.js` — static website and illustrative report.
- `privacy.html`, `terms.html`, `404.html` — prototype notices and not-found page.
- `contracts/schema.py` — shared data contract definitions.
- `FINAL_IMPLEMENTATION_PLAN.md` — proposed production architecture and delivery phases.
- `argon.md`, `research/` — domain research and procurement analysis.
- `arshit-agents.md`, `MOhit-Agents.md` — team responsibilities and progress notes.
- `main.py` — current Python package scaffold.

For current technical direction, see [the final implementation plan](FINAL_IMPLEMENTATION_PLAN.md) and [the research overview](research/README.md).
