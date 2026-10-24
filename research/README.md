# Research & Benchmark Workspace (Argon)

Welcome Argon! This directory is your dedicated workspace. All research, benchmark datasets, prompt tests, and competitor notes belong here.

## Directory Structure
- `evals/`: Labeled GeM/CPPP evaluation tenders (the 50-tender benchmark mentioned in Slide 9).
- `prompts/`: Prompt iterations and clause extraction experiments.
- `competitors/`: Deep-dive teardowns and comparison notes (BidAssist, Loopio, etc.).
- `samples/`: Sample tender text snippets, tricky ATCs, and corrigenda.

## Shared Data Contract
To ensure your benchmark results and prompt outputs plug directly into the backend engine and frontend scorecard without merge conflicts, please follow the schema defined in [`contracts/schema.py`](file:///d:/softwares/Tenderlens/TenderLens/contracts/schema.py):
- `BidderProfile`
- `ClauseCitation`
- `GateResult`
- `QualificationScorecard`

## Git Workflow
1. Work in this directory on branch `feat/argon-research`.
2. Push your changes freely without affecting `backend/` or `frontend/`.
3. When ready, create a PR or merge into `main`.
