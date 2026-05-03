# CLAUDE.md — TRACE.ai project instructions

This file is the project-level Claude Code guide. It overrides the global instructions for anything specific to this repo.

## Mission

TRACE.ai is the iDEA Hackathon 2.0 PS3 submission by Team NamoFans (IIT Kharagpur). Goal: ship a Phase 2 prototype that converts our shortlist into a finalist slot. We compete against ~32 other teams on PS3 — many from IITs — so polish, regulatory IQ, and demoability matter more than raw novelty.

## Key context

- **Hackathon**: iDEA 2.0 by Union Bank of India / IBA / DFS / KJ Somaiya
- **Problem Statement**: PS3 — Tracking of Funds within Bank for Fraud Detection
- **Theme**: AI-CSPARC (Customer Security, Privacy, Assurance, Reliance, Convenience)
- **Phase 2 deliverables**: GitHub repo + deployed URL + demo video
- **Build window**: ~3 weeks
- **Strategy**: Pragmatic Flagship — see `DECISIONS.md` ADR-0001
- **Magical differentiators**: FIU-IND STR auto-gen, GNNExplainer + SHAP, NL Investigation Copilot, Live retraining demo

## Out of Scope for Phase 2

These are explicitly **not** being built. Do not propose adding them unless the user opens the discussion.

- ❌ **Full TGN training** — defer to v2; we ship GraphSAGE + temporal features instead. Disclosed honestly in `MODEL_CARD.md`.
- ❌ **Neo4j production integration** — NetworkX is sufficient for the prototype scale. Neo4j is named only as a v2 path.
- ❌ **Federated / edge learning** — do not compete with Kartavya (KIET — GraphGuard) on this axis.
- ❌ **Adversarial robustness** — do not compete with RAW (Parul — BLING) on this axis.
- ❌ **Real bank data integration** — IBM AMLSim is the right call for the hackathon. CBS feeds are a v2 deployment milestone, not a build task.
- ❌ **Multi-tenant / multi-bank support** — Union Bank pilot only. No tenancy abstractions.

If a teammate (or a future Claude session) is tempted to add any of the above, the cost is high and the hackathon ROI is low. Document intent in `DECISIONS.md` first.

## Build / test / lint commands

```bash
# Python
pip install -e ".[dev]"
ruff check src tests          # lint
pytest -q                     # tests
uvicorn trace.api.main:app --reload   # dev server

# Frontend
cd frontend
npm install
npm run typecheck
npm run dev                    # Vite dev server on :5173
npm run build

# Full stack
docker compose up --build
```

## Conventions

- **Python**: 3.11, type hints everywhere, `from __future__ import annotations` at top of every module. Ruff + line length 100. No comments unless they explain WHY (per global CLAUDE.md).
- **TypeScript**: strict mode on. No `any` unless absolutely necessary. React 18 functional components only.
- **Imports**: absolute imports inside `trace.*`. Frontend uses relative imports inside `src/`.
- **Tests**: every detection module gets a unit test; API gets an integration smoke test. Tests use small synthetic graphs, not full AMLSim.
- **Commits**: small, atomic, conventional-commit style (`feat:`, `fix:`, `docs:`, `test:`). Per global rules: never add Claude as co-author. Never commit `.claude/`, `data/raw/`, secrets.
- **Branching**: `main` is protected (will require PR + green CI before merge once we set it up). Feature branches off `main`; small PRs.
- **Module boundaries**: detection/intelligence/explainability/api/data/graph are independent. Each ships with a clean public API; no cross-module imports of internals.

## Module ownership (proposed)

See `TEAM.md` for the locked-in version once the team agrees.

| Module | Default owner | Why |
|---|---|---|
| Data + Graph + Pattern Matcher | Backend | Tightly coupled |
| GraphSAGE + Online Anomaly + Explainability + Calibration | ML | Single ML mind |
| LLM Explainer + NL Copilot + STR Generator | NLP | LLM + text + PDF |
| Frontend (React, viz, copilot UI) | Full-stack | UI is the demo |

## Demo-day truth

The 4-minute demo MUST hit, in order:
1. Problem hook (₹71,543 Cr / 95% FP)
2. Live 3D graph with money laundering ring
3. Click flag → explainability card (GNNExplainer + SHAP)
4. NL copilot query → graph subview
5. One click → STR PDF auto-generates with FIU-IND fields
6. Live retraining: inject pattern → drift dashboard reacts
7. Closing metrics + Union Bank pilot path + GFF showcase ambition

This sequence is the source of truth. If a feature can't be filmed in this 4 minutes, it's a P3 not a P0.

## Data hygiene

- Never commit anything from `data/raw/` or `data/processed/`. Use `data/sample/` for tiny demo fixtures only.
- Never commit `.env` or any LLM API key.
- AMLSim output can be regenerated; do not store it in git.

## When in doubt

- Re-read `RESEARCH.md` for "what banking judges actually reward"
- Re-read `DECISIONS.md` for "why we're not doing X"
- Re-read `ROADMAP.md` for "what week is this task in"
- Don't ship something that wasn't pitched in Phase 1 — judges compare back to the PPT (`docs/PPT.md`)

## Forbidden

- Adding TGN, Neo4j, federated learning, or adversarial robustness to scope without an ADR
- Pushing data files
- Adding Claude as a commit co-author
- Touching `.claude/` or any global-config files
- Modifying `.gitignore` to allow `data/raw/`
- Skipping tests on the risk fusion module — it's the score everyone reads
