# TRACE.ai — Transaction Risk Analysis & Compliance Engine

> **iDEA Hackathon 2.0 (PSBs Hackathon Series 2026) · PS3 — Tracking of Funds within Bank for Fraud Detection**
> Team **NamoFans** · IIT Kharagpur · Phase 1 **Shortlisted** ✓ · Phase 2 **Submitted**

**Live demo:** https://trace-ai-4xnj5ovp4a-uc.a.run.app

Graph-powered fund flow intelligence for AML and compliance. Models every banking transaction as an edge in a dynamic temporal directed graph, runs four detection engines in parallel, and auto-generates FIU-IND compliant Suspicious Transaction Reports in under 5 minutes.

---

## Phase 2 Deliverables

| ID | Deliverable | Link / Status |
|---|---|---|
| D1 | Problem + Solution Brief (2-page) | [`docs/D1_Problem_Solution_Brief.md`](docs/D1_Problem_Solution_Brief.md) |
| D2 | Technical Demo Video (5-10 min) | **TODO: upload to YouTube (unlisted) and add link** |
| D3 | Technical Architecture (1-2 page) | [`docs/D3_Technical_Architecture.md`](docs/D3_Technical_Architecture.md) |
| D4 | GitHub Repo + README | This file |
| D5 | Pitch Video (5 min) + Slide Deck | **TODO: upload pitch video and slide deck PDF and add links** |

**Deployed URL:** https://trace-ai-4xnj5ovp4a-uc.a.run.app
**Health check:** https://trace-ai-4xnj5ovp4a-uc.a.run.app/api/health

---

## Why this matters

- Indian banks lost **₹71,543 Cr** to fraud in FY 2024-25 (RBI Annual Report)
- Rule-based AML systems generate **95%+ false positives**, causing investigator fatigue
- Sophisticated layering, round-tripping, and structuring **evade transaction-level rules entirely**
- Manual STR preparation takes **4-6 hours per case**; TRACE.ai does it in under 5 minutes

---

## What TRACE.ai does

1. **Graph Pattern Matcher** — five AML typologies: circular flow, layering chains, structuring, mule fan-in/fan-out, dormant burst
2. **Graph Classifier** — XGBoost on 11 graph-structural features (PageRank, betweenness, velocity, KYC risk); AUC > 0.99 on synthetic data
3. **Online Anomaly Scorer** — River HalfSpaceTrees + ADWIN drift per account; streaming baselines, zero batch retraining
4. **YAML Compliance Engine** — hot-reloadable RBI / PMLA / FIU-IND rules; new circulars take effect without restarts
5. **Risk Fusion** — composite score: pattern(30%) + classifier(30%) + anomaly(20%) + compliance(20%)
6. **SHAP Explainability** — TreeExplainer attribution on every flag; no black-box alerts
7. **Gemini LLM Explainer** — grounded evidence block → plain-English explanation per alert
8. **NL Investigation Copilot** — ask in English; six pattern-specific graph query dispatchers + Gemini for freeform
9. **Auto-STR Generator** — one click → FIU-IND 8-section A4 PDF: fund trail, risk breakdown, AI narrative, recommended action
10. **3D React Dashboard** — live force-graph + alert stream + drift timeline + copilot panel

---

## Quick Start

```bash
# Prerequisites: Python 3.10+, Node.js 18+, Rust (for River)

# 1. Install backend
pip install -e ".[dev]"

# 2. Generate demo data (runs once, ~2 min)
python scripts/seed_demo.py

# 3. Start backend
uvicorn trace.api.main:app --reload --port 8000

# 4. Start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (dev proxy forwards `/api` to backend).

### Run tests

```bash
pytest -q           # 42 tests, all passing
ruff check src tests
cd frontend && npm run typecheck
```

### Redeploy to GCP Cloud Run

```bash
# Requires gcloud CLI authenticated as animeshraj958@gmail.com
gcloud builds submit --config cloudbuild.yaml . --project agrowise-192e3
# Build time: ~11 min (Rust compilation + npm build + data seeding)
```

---

## Architecture

```
CBS / NEFT / RTGS / UPI / IMPS
        |
        v
  NetworkX MultiDiGraph
  (accounts=nodes, txns=edges)
        |
        +---> Pattern Matcher (5 AML typologies)  --+
        +---> XGBoost Classifier (11 graph features) +---> Risk Fusion ---> Alert
        +---> River Anomaly Scorer (HST + ADWIN)    --+  (CRITICAL/HIGH/
        +---> YAML Compliance Engine (hot-reload)   --+   MEDIUM/LOW)
                                                              |
                              +-------------------------------+
                              |                               |
                     SHAP Explainability            NL Investigation Copilot
                     Gemini LLM Explainer           Auto-STR Generator (PDF)
                              |
                              v
                    FastAPI (REST + WebSocket)
                              |
                              v
                    React 3D Dashboard
        (force-graph · alert queue · copilot · drift timeline)
```

See [`docs/D3_Technical_Architecture.md`](docs/D3_Technical_Architecture.md) for the full breakdown.

---

## Repository Layout

```
src/trace/
  data/             generator · ingestion · feature_engineering
  graph/            builder (NetworkX MultiDiGraph)
  detection/
    patterns/       circular_flow · layering · structuring · mule · dormant_burst
    pattern_matcher · gnn_classifier · anomaly_scorer · compliance_engine · risk_fusion
  intelligence/     str_generator · explainer · copilot · drift_dashboard
  explainability/   shap_wrapper · calibration
  api/              main · routes (graph, alerts, investigate, reports, ws) · dependencies
frontend/src/
  components/       GraphVisualization · AlertPanel · ExplainabilityCard
                    InvestigationPanel · DriftTimeline · KPICards · STRDownload
  hooks/            useGraphData · useWebSocket
scripts/            seed_demo.py · run_demo.py · generate_data.py
tests/              unit (41 tests) · integration (1 smoke test)
docs/               D1_Problem_Solution_Brief · D3_Technical_Architecture
                    Idea2.0_PS3_NamoFans.pdf (Phase 1 PPT)
compliance_rules.yaml   hot-reloadable RBI/PMLA/FIU-IND rules
Dockerfile              single-container build (Python + Node.js + Rust)
cloudbuild.yaml         GCP Cloud Build pipeline
```

---

## Key Technical Choices

| Decision | Choice | Reason |
|---|---|---|
| ML model | XGBoost (not TGN/GNN) | Validated POC approach per hackathon sample doc; GNN needs 10x more data |
| Graph DB | NetworkX (not Neo4j) | Sufficient for 500-5000 accounts; Neo4j targeted for v2 production |
| LLM | Gemini 2.5 Flash (Vertex AI) | GCP credits; fast structured output; responses pre-cached for demo |
| Deployment | GCP Cloud Run (single container) | One URL, no CORS, no separate frontend hosting needed |
| Online ML | River 0.23.0 (Rust build) | Real streaming baselines; ADWIN drift; no batch retraining downtime |

**Honest limitations** (see `MODEL_CARD.md`): prototype trained on synthetic AMLSim data; real CBS integration is v2; XGBoost used instead of full TGN as disclosed.

---

## Hackathon Status

| Phase | Status |
|---|---|
| Phase 1 — PPT + Video | Submitted, **Shortlisted** |
| Phase 2 — Prototype | **Submitted** |
| Phase 3 — Mentorship | TBA |
| Phase 4 — Grand Finale | TBA |

---

## Team

| Member | Expertise |
|---|---|
| Animesh Raj | ML/AI, Graph Neural Networks |
| Devansh Gupta | Backend Engineering, System Design |
| Prem Agarwal | Full-Stack, Data Visualization |
| MD. Faizan Khan | NLP, LLMs, Compliance |

---

## License

MIT. Do not redistribute Union Bank or FIU-IND material without authorization.
