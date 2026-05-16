# TRACE.ai: Transaction Risk Analysis and Compliance Engine

[![Live Demo](https://img.shields.io/badge/Live_Demo-Cloud_Run-4CAF50?style=flat-square&logo=googlecloud)](https://trace-ai-4xnj5ovp4a-uc.a.run.app)
[![Tests](https://img.shields.io/badge/Tests-42_passing-brightgreen?style=flat-square&logo=pytest)](tests/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](pyproject.toml)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](frontend/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

> **iDEA Hackathon 2.0 (PSBs Hackathon Series 2026) · Union Bank of India · PS3 - Tracking of Funds within Bank for Fraud Detection**
> Team **NamoFans** · IIT Kharagpur · Phase 1 Shortlisted ✓

**Graph-powered fund flow intelligence for AML and compliance.** Models every banking transaction as an edge in a dynamic directed graph, runs four detection engines in parallel, and auto-generates FIU-IND compliant Suspicious Transaction Reports in under 5 minutes.

---

## The Problem

Indian banks lost **₹71,543 Cr** to fraud in FY 2024-25 (RBI Annual Report). Rule-based AML systems generate **95%+ false positives** - investigators spend their day dismissing noise instead of investigating real threats. Sophisticated fraud (multi-hop layering, circular round-trips, structuring) is **invisible to single-transaction rules**. Manual STR preparation takes **4-6 hours per case**.

---

## Live Demo

**[https://trace-ai-4xnj5ovp4a-uc.a.run.app](https://trace-ai-4xnj5ovp4a-uc.a.run.app)**

The dashboard loads with 8 pre-seeded alerts across a 542-node, 5049-edge transaction graph containing five fraud ring typologies.

---

## Features

| # | Feature | Description |
|---|---|---|
| 1 | **Graph Pattern Matcher** | 5 AML typologies: circular flow, layering chains, structuring, mule fan-in/out, dormant burst |
| 2 | **XGBoost Classifier** | 11 graph-structural features (PageRank, betweenness, velocity, KYC risk); AUC > 0.99 |
| 3 | **Online Anomaly Scorer** | River HalfSpaceTrees + ADWIN drift; per-account streaming baselines, zero batch retraining |
| 4 | **YAML Compliance Engine** | Hot-reloadable RBI/PMLA/FIU-IND rules; new circulars take effect without restarts |
| 5 | **SHAP Explainability** | TreeExplainer attribution on every flag - no black-box alerts |
| 6 | **Gemini LLM Explainer** | Grounded evidence → plain-English explanation per alert |
| 7 | **NL Investigation Copilot** | Ask in English → graph query results; six pattern dispatchers + Gemini for freeform |
| 8 | **Auto-STR Generator** | One click → FIU-IND 8-section A4 PDF: fund trail, risk breakdown, AI narrative |
| 9 | **3D React Dashboard** | Live force-graph, alert queue, drift timeline, copilot panel |

---

## Architecture

```
CBS / NEFT / RTGS / UPI / IMPS
           │
           ▼
   NetworkX MultiDiGraph
   (accounts = nodes, txns = edges)
           │
    ┌──────┴───────────────────────────┐
    │         Detection Engine         │
    │  Pattern Matcher  (30%)          │
    │  XGBoost Classifier (30%)        ├──► Risk Fusion ──► CRITICAL / HIGH / MEDIUM / LOW
    │  River Anomaly Scorer (20%)      │
    │  YAML Compliance Engine (20%)    │
    └──────────────────────────────────┘
           │
    ┌──────┴───────────────────────────┐
    │        Intelligence Layer        │
    │  SHAP Explainability             │
    │  Gemini LLM Explainer            │
    │  NL Investigation Copilot        │
    │  Auto-STR Generator (ReportLab)  │
    └──────────────────────────────────┘
           │
    FastAPI + WebSocket ──► React 3D Dashboard
```

Risk fusion weights: pattern(30%) + classifier(30%) + anomaly(20%) + compliance(20%)
Thresholds: CRITICAL ≥ 0.85 · HIGH ≥ 0.70 · MEDIUM ≥ 0.50

---

## Quick Start

**Prerequisites:** Python 3.10+, Node.js 18+, Rust (for River - `curl https://sh.rustup.rs -sSf | sh`)

```bash
# Install
pip install -e ".[dev]"

# Generate demo data (runs once, ~2 min)
python scripts/seed_demo.py

# Backend
PYTHONPATH=src uvicorn trace.api.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. The Vite proxy forwards `/api` and `/ws` to port 8000.

```bash
# Tests
pytest -q                        # 42/42 passing
ruff check src tests             # lint
cd frontend && npm run typecheck  # TypeScript strict
```

### Deploy to GCP Cloud Run

```bash
gcloud builds submit --config cloudbuild.yaml . --project agrowise-192e3
# ~11 min first build (Rust + npm + data seeding)
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
│   ├── compliance_engine.py YAML hot-reload + watchdog
│   └── risk_fusion.py       Weighted composite → RiskLevel enum
├── intelligence/
│   ├── str_generator.py     ReportLab FIU-IND 8-section PDF
│   ├── explainer.py         Gemini 2.5 Flash + disk cache
│   ├── copilot.py           NL dispatchers + Gemini fallback
│   └── drift_dashboard.py   ADWIN event log
├── explainability/    shap_wrapper · calibration
└── api/               FastAPI · routes · WebSocket · dependencies

frontend/src/
├── components/        GraphVisualization · AlertPanel · ExplainabilityCard
│                      InvestigationPanel · DriftTimeline · KPICards · STRDownload
└── hooks/             useGraphData · useWebSocket

scripts/               seed_demo.py · run_demo.py
tests/                 42 tests (unit + integration)
docs/                  D1_Problem_Solution_Brief · D3_Technical_Architecture
compliance_rules.yaml  Hot-reloadable RBI/PMLA/FIU-IND rules
Dockerfile             Single-container build (Python + Node.js + Rust)
cloudbuild.yaml        GCP Cloud Build pipeline
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Graph | NetworkX MultiDiGraph |
| ML | XGBoost 2.1.4 + SHAP TreeExplainer |
| Online ML | River 0.23.0 - HalfSpaceTrees + ADWIN |
| Compliance | YAML + watchdog hot-reload |
| LLM | Gemini 2.5 Flash via Vertex AI (GCP) |
| PDF | ReportLab (FIU-IND format) |
| Backend | FastAPI + Uvicorn + WebSocket |
| Frontend | React 18 + TypeScript strict + Vite |
| 3D Graph | react-force-graph-3d + Three.js |
| Deploy | GCP Cloud Run (2 vCPU / 2 GiB) |

---

## Deliverables

| ID | Deliverable | Link |
|---|---|---|
| D1 | Problem + Solution Brief | [docs/D1_Problem_Solution_Brief.md](docs/D1_Problem_Solution_Brief.md) |
| D2 | Technical Demo Video | TODO |
| D3 | Technical Architecture | [docs/D3_Technical_Architecture.md](docs/D3_Technical_Architecture.md) |
| D4 | GitHub Repo + README | This file |
| D5 | Pitch Video + Slide Deck | TODO |

**Live URL:** https://trace-ai-4xnj5ovp4a-uc.a.run.app

---

## Limitations

- Trained on IBM AMLSim synthetic data - real CBS integration is a Phase 3 goal
- XGBoost used instead of full Temporal GNN (ChronoWave-GNN as designed in Phase 1) - validated POC approach; see `MODEL_CARD.md`
- Gemini explanations are pre-cached at seed time; live LLM calls fall back to templates if quota is exceeded

---

## License

MIT. Do not redistribute Union Bank or FIU-IND material without authorization.
