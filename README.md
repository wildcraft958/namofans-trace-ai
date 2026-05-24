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

**Live App:** [https://trace-ai-4xnj5ovp4a-uc.a.run.app](https://trace-ai-4xnj5ovp4a-uc.a.run.app)

**Demo Video:** _Recording in progress — YouTube link will be added before May 31, 2026_

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

## Dataset Description

All data is **100% synthetic**. No real bank customer data is used anywhere in this prototype.

| Property | Value |
|---|---|
| Source | IBM AMLSim (open-source AML simulation) |
| Accounts (nodes) | 542 (demo graph); 20,000 (TGN training graph) |
| Transactions (edges) | 5,049 (demo); ~200,000 (TGN training) |
| Fraud rings seeded | 5 typologies: circular flow, layering, structuring, mule fan-in/out, dormant burst |
| Anomaly injection rate | ~5% of accounts (matches published insider-fraud base rates) |
| Indian banking parameters | NEFT/RTGS/UPI/IMPS channels; INR amounts; KYC tiers; RBI threshold at ₹10L |
| Reproducibility | `python scripts/seed_demo.py` regenerates the demo graph deterministically |

---

## Model Performance (on Synthetic Test Set)

These metrics are on synthetic AMLSim data. Real-bank data would require retraining with actual CBS feeds.

| Model | AUC-ROC | Notes |
|---|---|---|
| XGBoost Classifier | > 0.99 | 11 graph features; trained on AMLSim 20K split 80/20 |
| Temporal GNN (TGN) | 0.72 | Batched edge inference on 20K-node graph; `models/tgn_classifier.pt` |
| Pattern Matcher | N/A (rule-based) | 5 typologies; precision depends on graph structure |
| River Online Scorer | N/A (anomaly) | Per-account baseline; ADWIN drift detected in <1ms |

Risk fusion blends all four signals: pattern(30%) + classifier(30%) + anomaly(20%) + compliance(20%).

---

## What Is Built vs What Is Planned

| Capability | DEMONSTRABLE IN POC | PLANNED (NOT YET BUILT) |
|---|---|---|
| Graph engine | NetworkX MultiDiGraph (542 nodes, 5049 edges) | Neo4j GDS for millions of accounts |
| Pattern detection | 5 AML typologies, all running live | 15-20 additional typologies |
| ML classifier | XGBoost on 11 graph features (AUC > 0.99 synthetic) | Full TGN in production with real data |
| Online anomaly | River HalfSpaceTrees + ADWIN, per-account baselines | Kafka integration for real-time CBS stream |
| Compliance engine | YAML rules (RBI/PMLA/FIU-IND), hot-reload | Auto-update from RBI circular API |
| Explainability | SHAP TreeExplainer per alert | Counterfactual explanations |
| LLM explainer | Gemini 2.5 Flash (pre-cached + fallback) | Real-time Gemini calls at production quota |
| NL Copilot | 10 intents + Gemini intent parser | Full natural-language query over Neo4j |
| STR generator | 8-section FIU-IND PDF in <5 seconds | Legal sign-off integration, digital signature |
| Dashboard | React 3D force-graph, alert queue, drift timeline | Multi-branch, multi-bank view |
| Data source | IBM AMLSim synthetic data | Union Bank CBS API integration |
| Auth | None (POC) | LDAP/SSO for bank compliance teams |

---

## Team

| Name | Role |
|---|---|
| Animesh Raj | ML/AI & Graph Neural Networks |
| Devansh Gupta | Backend Engineering & System Design |
| Prem Agarwal | Full-Stack & Data Visualization |
| MD. Faizan Khan | NLP, LLMs & Compliance |

---

## Deliverables

| ID | Deliverable | Link |
|---|---|---|
| D1 | Problem + Solution Brief | [docs/D1_Problem_Solution_Brief.pdf](docs/D1_Problem_Solution_Brief.pdf) |
| D2 | Deployed URL | https://trace-ai-4xnj5ovp4a-uc.a.run.app |
| D3 | Technical Architecture | [docs/D3_Technical_Architecture.pdf](docs/D3_Technical_Architecture.pdf) |
| D4 | GitHub Repo + README | This file |
| D5 | Pitch Video | TODO |

**Live URL:** https://trace-ai-4xnj5ovp4a-uc.a.run.app

---

## Known Limitations

- **Synthetic data only.** Trained on IBM AMLSim; real CBS integration and retraining is a Phase 3 goal. Metrics (AUC > 0.99 XGBoost) are on synthetic test sets — real-bank performance would require revalidation.
- **XGBoost, not a full Temporal GNN.** Phase 1 PPT described ChronoWave-GNN; the POC uses XGBoost on graph-structural features because PyG TGN requires significantly more training data and compute than a prototype allows. See `MODEL_CARD.md` for the full rationale. The TGN checkpoint (`models/tgn_classifier.pt`) is trained but is not part of the live risk fusion.
- **Batch graph, not real-time stream.** The demo processes a pre-seeded CSV graph. Production would require Kafka for live CBS event ingestion.
- **No user authentication.** The dashboard is publicly accessible (POC only). Production requires LDAP/SSO.
- **Gemini explanations pre-cached.** Live LLM calls fall back to templates if Vertex AI quota is exceeded.
- **NetworkX for prototype scale.** Adequate for 500-5000 accounts; Neo4j GDS is the v2 upgrade for production-scale (millions of accounts).
- **FIU-IND STR format is simulated.** The PDF follows the 8-section structure but is not legally compliant — no digital signature or official submission channel.

---

## Contact

**Team:** NamoFans
**Institute:** IIT Kharagpur
**Email:** animeshraj958@gmail.com
**Hackathon:** iDEA 2.0 (PSBs Hackathon Series 2026) — PS3

---

## License

MIT. Do not redistribute Union Bank or FIU-IND material without authorization.
