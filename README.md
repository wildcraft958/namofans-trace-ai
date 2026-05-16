<![CDATA[<div align="center">

<img src="https://img.shields.io/badge/iDEA_2.0-PS3_Shortlisted-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOCA0IDQtMiA0IDItOC00eiIvPjwvc3ZnPg==" alt="iDEA 2.0"/>
<img src="https://img.shields.io/badge/GCP_Cloud_Run-LIVE-4CAF50?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Live"/>
<img src="https://img.shields.io/badge/Tests-42%20passing-success?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"/>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/>

# TRACE.ai
### Transaction Risk Analysis & Compliance Engine

*Graph-Powered Fund Flow Intelligence for Anti-Money Laundering*

**[🚀 Live Demo](https://trace-ai-4xnj5ovp4a-uc.a.run.app)** · **[📄 Problem Brief](docs/D1_Problem_Solution_Brief.md)** · **[🏗 Architecture](docs/D3_Technical_Architecture.md)**

---

**iDEA Hackathon 2.0 (PSBs Hackathon Series 2026) · Union Bank of India · PS3**
Team **NamoFans** · IIT Kharagpur · Animesh Raj · Devansh Gupta · Prem Agarwal · MD. Faizan Khan

</div>

---

## The Problem

```
₹71,543 Cr lost to bank fraud in India — FY 2024-25 (RBI Annual Report)

  Rule-based AML systems:          TRACE.ai:
  ┌─────────────────────┐          ┌─────────────────────────────────┐
  │  95%+ false          │   vs.   │  Target <15% false positives    │
  │  positives           │         │                                 │
  │  4-6 hrs per STR     │         │  <5 min per STR (auto-gen)      │
  │  277-day detection   │         │  Real-time detection            │
  │  Single-txn rules    │         │  Multi-hop graph analysis       │
  │  No explanation      │         │  SHAP + LLM per alert           │
  └─────────────────────┘         └─────────────────────────────────┘
```

Sophisticated money laundering — layering chains, circular round-trips, structured splits — is **invisible to transaction-level rules**. It only becomes visible on a graph.

---

## Architecture

```
 INPUT                  GRAPH ENGINE              DETECTION (4 signals)
 ──────                 ────────────              ─────────────────────
 CBS / NEFT             NetworkX                  ┌─ Pattern Matcher
 RTGS / UPI   ────────► MultiDiGraph   ──────────►├─ XGBoost Classifier  ──► RISK
 IMPS / ATM             Accts = Nodes             ├─ River Anomaly Scorer     FUSION
                        Txns  = Edges             └─ Compliance Engine
                                                                        │
                                       ┌────────────────────────────────┘
                                       │
                              INTELLIGENCE LAYER
                              ─────────────────
                              SHAP Explainability  (why this account?)
                              Gemini LLM Explainer  (plain English)
                              NL Investigation Copilot (ask in English)
                              Auto-STR Generator    (FIU-IND PDF, 8 sections)
                                       │
                              DELIVERY
                              ────────
                        FastAPI + WebSocket  +  React 3D Dashboard
                        (3D force-graph · alert queue · drift timeline)
```

---

## The 4 Differentiators

| # | Feature | What it does | Why it wins |
|---|---|---|---|
| 1 | **FIU-IND Auto-STR** | One click → 8-section A4 PDF with fund trail, AI narrative, risk breakdown | No other team ships regulatory artifacts |
| 2 | **SHAP Explainability** | TreeExplainer attribution on every flag + Gemini plain-English reason | Banking judges reject black boxes |
| 3 | **NL Investigation Copilot** | Ask in English → graph query results instantly | No Cypher, no SQL, no expertise needed |
| 4 | **Live Retraining Demo** | Inject fraud pattern → River ADWIN fires → drift dashboard reacts | Almost no team demos online learning |

---

## Detection Engine

```
Five AML Typologies (Pattern Matcher)
├── Circular Flow      → nx.simple_cycles + 72h temporal window
├── Layering Chain     → BFS depth-6, forwarding ratio > 70% within 48h
├── Structuring        → Same-day clusters ₹8–10L range (CTR evasion)
├── Mule Fan-in/out    → in_degree ≥ 8 AND out_degree ≥ 5 in 24h
└── Dormant Burst      → dormant_days ≥ 90 + burst ≥ 3 high-value txns

Risk Fusion Weights
├── Pattern score     30%
├── XGBoost score     30%   (11 graph features, AUC > 0.99 on synthetic data)
├── River anomaly     20%   (HalfSpaceTrees + ADWIN, per-account baseline)
└── Compliance rules  20%   (YAML hot-reload, RBI/PMLA/FIU-IND encoded)

Thresholds: CRITICAL ≥ 0.85 · HIGH ≥ 0.70 · MEDIUM ≥ 0.50
```

---

## Quick Start

```bash
# Prerequisites: Python 3.10+, Node.js 18+, Rust toolchain (for River)

# 1. Install
pip install -e ".[dev]"

# 2. Seed demo data (runs once, ~2 min — 500 accounts, 5 fraud rings)
python scripts/seed_demo.py

# 3. Backend
uvicorn trace.api.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. The Vite proxy forwards `/api` to `localhost:8000`.

```bash
# Tests
pytest -q                       # 42/42 passing
ruff check src tests            # lint
cd frontend && npm run typecheck # TypeScript strict
```

```bash
# Redeploy to GCP Cloud Run (requires gcloud auth)
gcloud builds submit --config cloudbuild.yaml . --project agrowise-192e3
# ~11 min first build (Rust + npm + seed_demo)
```

---

## Repository Layout

```
src/trace/
├── data/              generator · ingestion · feature_engineering
├── graph/             NetworkX MultiDiGraph builder
├── detection/
│   ├── patterns/      circular_flow · layering · structuring · mule · dormant_burst
│   ├── gnn_classifier.py    XGBoost + StandardScaler
│   ├── anomaly_scorer.py    River HalfSpaceTrees + ADWIN
│   ├── compliance_engine.py YAML rules + watchdog hot-reload
│   └── risk_fusion.py       Weighted composite → RiskLevel enum
├── intelligence/
│   ├── str_generator.py     ReportLab FIU-IND 8-section PDF
│   ├── explainer.py         Gemini 2.5 Flash + disk cache
│   ├── copilot.py           6 NL dispatchers + Gemini fallback
│   └── drift_dashboard.py   ADWIN event log
├── explainability/    shap_wrapper · calibration
└── api/               FastAPI · routes · WebSocket · dependencies

frontend/src/
├── components/
│   ├── GraphVisualization.tsx  react-force-graph-3d + THREE.js glow
│   ├── AlertPanel.tsx          WebSocket-merged alert queue
│   ├── ExplainabilityCard.tsx  SHAP bars + LLM text + STR download
│   ├── InvestigationPanel.tsx  NL copilot with suggested queries
│   ├── DriftTimeline.tsx       recharts AreaChart + inject button
│   └── KPICards.tsx            Live KPI grid
└── hooks/             useGraphData · useWebSocket (exponential backoff)

scripts/               seed_demo.py · run_demo.py
tests/                 42 tests (unit + integration)
docs/                  D1_Problem_Solution_Brief.md · D3_Technical_Architecture.md
compliance_rules.yaml  Hot-reloadable RBI/PMLA/FIU-IND rules
Dockerfile             Python + Node.js + Rust in one container
cloudbuild.yaml        GCP Cloud Build pipeline
```

---

## Phase 2 Deliverables

| ID | Deliverable | Status |
|---|---|---|
| D1 | Problem + Solution Brief | [`docs/D1_Problem_Solution_Brief.md`](docs/D1_Problem_Solution_Brief.md) |
| D2 | Technical Demo Video (5–10 min) | TODO — record and add YouTube link |
| D3 | Technical Architecture doc | [`docs/D3_Technical_Architecture.md`](docs/D3_Technical_Architecture.md) |
| D4 | GitHub Repo + README | This file |
| D5 | Pitch Video (5 min) + Slide Deck | TODO — record and add YouTube + PDF link |

**Live URL:** https://trace-ai-4xnj5ovp4a-uc.a.run.app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Graph | NetworkX MultiDiGraph (Neo4j GDS for v2 production) |
| ML | XGBoost 2.1.4 + SHAP TreeExplainer |
| Online ML | River 0.23.0 — HalfSpaceTrees + ADWIN |
| Compliance | YAML rule engine + watchdog hot-reload |
| LLM | Gemini 2.5 Flash (Vertex AI, GCP) |
| STR PDF | ReportLab (FIU-IND compliant) |
| Backend | FastAPI + Uvicorn + WebSocket |
| Frontend | React 18 + TypeScript strict + Vite |
| 3D Graph | react-force-graph-3d + Three.js 0.184 |
| Charts | Recharts |
| Deploy | GCP Cloud Run (single container, 2 vCPU / 2 GiB) |

---

## Honest Limitations

- Trained on IBM AMLSim synthetic data — real CBS integration is a Phase 3 deliverable
- XGBoost used instead of full Temporal GNN (ChronoWave-GNN as designed in Phase 1 PPT) — validated POC approach per hackathon sample D3; disclosed in `MODEL_CARD.md`
- Gemini explanations pre-cached at seed time; live LLM calls fall back to template if quota exceeded

---

## Hackathon Status

| Phase | Status |
|---|---|
| Phase 1 — PPT + Video | Submitted · **Shortlisted** |
| Phase 2 — Prototype | **Submitted** |
| Phase 3 — Mentorship | TBA |
| Phase 4 — Grand Finale | TBA |

---

## License

MIT. Do not redistribute Union Bank or FIU-IND material without authorization.
]]>