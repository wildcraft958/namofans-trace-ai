# TRACE.ai — Transaction Risk Analysis & Compliance Engine

> **iDEA Hackathon 2.0 · PS3 — Tracking of Funds within Bank for Fraud Detection**
> Team **NamoFans** · IIT Kharagpur · Phase 1 **Shortlisted** ✓

Graph-powered fund flow intelligence for AML and compliance. Models every banking transaction as an edge in a dynamic temporal directed graph; runs three detection engines in parallel; auto-generates FIU-IND compliant Suspicious Transaction Reports.

## Why this matters

- Indian banks lost **₹71,543 Cr** to fraud in FY 2024-25 (RBI Annual Report)
- Rule-based AML systems generate **95%+ false positives**
- Investigators spend **4–6 hours per STR** manually tracing fund flows
- Sophisticated layering, round-tripping, and structuring **evade rules entirely**

## What TRACE.ai does

1. **Graph Pattern Matcher** — NetworkX detection of cycles, layering chains, structuring, mule fan-in/fan-out, dormant bursts
2. **GraphSAGE Classifier** — Trained on AMLSim with temporal features. Suspicious-account/transaction probability
3. **Online Anomaly Scorer** — River HalfSpaceTrees + ADWIN drift, per-account streaming baseline (no batch retraining)
4. **YAML Compliance Engine** — Hot-reloadable RBI / PMLA / FIU-IND rules
5. **Risk Fusion** — Weighted composite score (pattern · GNN · anomaly · compliance)
6. **LLM Investigation Copilot** — NL → graph queries, grounded explanations
7. **Auto-STR Generator** — One-click FIU-IND-format PDF with fund trail, risk breakdown, AI narrative
8. **Explainability Layer** — GNNExplainer subgraph + SHAP feature attributions on every flag
9. **3D React Dashboard** — Live force-graph + alert stream + copilot chat + drift timeline

## Architecture

```
Transactions → Graph Engine → ┌─ Pattern Matcher ─┐
                              ├─ GraphSAGE        ├→ Risk Fusion → Alert
                              ├─ Online Anomaly   │              ↓
                              └─ Compliance Rules ┘     ┌────────┴─────────┐
                                                       │ Explainability   │
                                                       │ NL Copilot       │
                                                       │ Auto-STR PDF     │
                                                       └──────────────────┘
                                                                ↓
                                                       3D React Dashboard
```

See `docs/solution.md` for the full spec, `docs/PLAN.md` for the build bible, `RESEARCH.md` for distilled research findings, `DECISIONS.md` for ADRs.

## Quickstart

```bash
# Backend (Python 3.11+)
pip install -e ".[dev]"
uvicorn trace.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Or everything via Docker
docker compose up --build
```

Then open <http://localhost:5173>.

## Repository Layout

```
src/trace/
  data/            ingestion · generator · feature engineering · entity resolution
  graph/           NetworkX builder · temporal windowing · PyG/Neo4j export
  detection/       pattern matcher · GraphSAGE · online anomaly · compliance · risk fusion
  intelligence/    LLM explainer · NL copilot · STR generator · drift dashboard
  explainability/  GNNExplainer · SHAP wrapper · calibration
  api/             FastAPI app · routes · WebSocket
frontend/src/
  components/      GraphVisualization · AlertPanel · InvestigationPanel · ExplainabilityCard · DriftTimeline
  hooks/           useGraphData · useWebSocket
  api/             axios client
notebooks/         01-data · 02-graph · 03-gnn · 04-evaluation
scripts/           generate_data · train_gnn · seed_demo · run_demo
tests/             unit · integration
docs/              PPT · PLAN · solution · one_page_summary · Phase 1 PDF
```

## Hackathon Status

| Phase | Status |
|---|---|
| Phase 1 — PPT + Video | ✅ Submitted, Shortlisted |
| Phase 2 — Prototype Round | 🚧 In progress (this repo) |
| Phase 3 — Mentorship | ⏳ TBA |
| Phase 4 — Grand Finale | ⏳ TBA |

## Team

See `TEAM.md` for module ownership.

## Documentation

| File | Purpose |
|---|---|
| `RESEARCH.md` | Distilled research — judging criteria, FIU-IND format, AMLSim, competitor analysis |
| `DECISIONS.md` | ADR-style architecture decisions |
| `ROADMAP.md` | Day-by-day Phase 2 plan |
| `MODEL_CARD.md` | Data, metrics, limitations, retraining cadence |
| `CONTRIBUTING.md` | Branching, commits, testing rules |
| `TEAM.md` | Members + module ownership |
| `CLAUDE.md` | Project-level Claude Code instructions |
| `docs/solution.md` | Definitive technical spec |
| `docs/PLAN.md` | Build bible with full code structure |
| `docs/PPT.md` | Phase 1 slide content + video script |

## License

MIT — see `LICENSE`. Do not redistribute Union Bank or FIU-IND material without authorization.
