# TRACE.ai - Technical Architecture

**iDEA Hackathon 2.0 | PSBs Hackathon Series 2026**
**Team NamoFans | PS3 - Tracking of Funds within Bank for Fraud Detection**

---

## System Overview

TRACE.ai is structured as four independent layers. Each layer has a clean public interface; no layer imports internals of another. This lets each module be replaced or upgraded independently in production.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 0 - DATA INGESTION                                   │
│  CBS / NEFT / RTGS / UPI / IMPS feeds  →  Pandas DataFrame │
│  IBM AMLSim generator (synthetic data for prototype)        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  LAYER 1 - GRAPH ENGINE                                     │
│  NetworkX MultiDiGraph                                       │
│  Nodes: accounts (KYC risk, account type, dormant_days)     │
│  Edges: transactions (amount, timestamp, channel)            │
│  Feature engineering: PageRank, betweenness, degree,        │
│  velocity, counterparty uniqueness, KYC score               │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  LAYER 2 - DETECTION ENGINE (four parallel signals)         │
│                                                             │
│  A. Pattern Matcher     B. Graph Classifier                  │
│     5 AML typologies       XGBoost on 11 graph features     │
│     NetworkX algorithms     SHAP TreeExplainer per alert    │
│                                                             │
│  C. Online Anomaly Scorer  D. Compliance Rule Engine        │
│     River HalfSpaceTrees      YAML rules (hot-reload)       │
│     ADWIN drift detection     RBI/PMLA/FIU-IND encoding     │
│                                                             │
│  E. Risk Fusion                                             │
│     Composite score = pattern(0.30) + classifier(0.30)      │
│                      + anomaly(0.20) + compliance(0.20)     │
│     Thresholds: CRITICAL≥0.85, HIGH≥0.70, MEDIUM≥0.50      │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  LAYER 3 - INTELLIGENCE                                     │
│  F. SHAP Explainability    per-alert feature attributions   │
│  G. Gemini LLM Explainer   grounded evidence → English      │
│  H. NL Investigation Copilot  6 dispatchers + Gemini intent │
│  I. Auto-STR Generator     8-section FIU-IND PDF (ReportLab)│
│  J. Drift Dashboard        ADWIN event log + timeline       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│  LAYER 4 - DELIVERY                                         │
│  FastAPI (REST + WebSocket)  →  React 18 Dashboard          │
│  3D Force Graph (Three.js)      Alert Queue (live)          │
│  SHAP Explainability Card        NL Copilot Panel           │
│  KPI Cards                       Drift Timeline (recharts)  │
│  One-click STR PDF Download                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer / Component | Technology | Justification |
|---|---|---|
| Data | IBM AMLSim + Pandas + NumPy | Realistic synthetic Indian banking data; no real CBS required for prototype |
| Graph Engine | NetworkX MultiDiGraph | Sufficient for 500-5000 account prototype; Neo4j GDS targeted for production |
| Graph Features | scikit-learn (PageRank via NX) | 11 features: degree, PageRank, betweenness, clustering, velocity, KYC, dormancy |
| ML Classifier | XGBoost 2.1.4 | Validated POC approach for graph-feature classification; AUC > 0.99 on synthetic data |
| Explainability | SHAP 0.49 TreeExplainer | TreeExplainer on XGBoost is equivalent to GNNExplainer for feature-based models |
| Online Anomaly | River 0.23.0 (HalfSpaceTrees + ADWIN) | Streaming per-account baselines, sub-ms latency, no batch retraining |
| Compliance Engine | PyYAML + watchdog | Hot-reload YAML rules; new RBI circular effective without restart |
| LLM | Gemini 2.5 Flash (Vertex AI) | GCP credits available; fast, accurate for structured evidence prompts |
| STR PDF | ReportLab | FIU-IND compliant 8-section A4 PDF with tables, flowcharts, risk charts |
| Backend | FastAPI + Uvicorn + WebSocket | Async, production-grade; WebSocket for live alert streaming |
| Frontend | React 18 + TypeScript strict | Type-safe; hooks architecture |
| 3D Graph | react-force-graph-3d + Three.js 0.184.0 | GPU-accelerated 3D force-directed graph in browser |
| Charts | Recharts | Drift timeline AreaChart with ADWIN event markers |
| Deployment | GCP Cloud Run (Docker) | Single container serves backend + React SPA; no cold-start data seeding |

---

## Module Boundaries

```
src/trace/
  data/
    generator.py          Synthetic graph: 500 accounts, 5 fraud rings
    ingestion.py          CSV → DataFrame with canonical columns
    feature_engineering.py  extract_features(), build_feature_matrix()
  graph/
    builder.py            build_graph() → NetworkX MultiDiGraph
  detection/
    patterns/
      circular_flow.py    nx.simple_cycles + temporal window
      layering.py         BFS depth-6, forwarding ratio > 70%
      structuring.py      Same-day clustering ₹8-10L range
      mule_fanin_fanout.py  in_degree≥8 AND out_degree≥5 in 24h
      dormant_burst.py    dormant_days≥90 + burst ≥3 txns
    pattern_matcher.py    Orchestrates all 5 → score 0-1
    gnn_classifier.py     XGBoost train/score on graph features
    anomaly_scorer.py     River HST + ADWIN singleton
    compliance_engine.py  YAML rule eval + watchdog hot-reload
    risk_fusion.py        Weighted composite → RiskLevel enum
  intelligence/
    str_generator.py      ReportLab 8-section FIU-IND PDF
    explainer.py          Gemini evidence builder + cache
    copilot.py            6 regex dispatchers + Gemini fallback
    drift_dashboard.py    Event log + get_drift_events()
  explainability/
    shap_wrapper.py       batch_explain() → top-5 SHAP features
    calibration.py        sklearn calibration_curve + ECE metric
  api/
    main.py               FastAPI app; /api/* routes; SPA static files
    routes/
      graph.py            GET /api/graph, GET /api/graph/{id}
      alerts.py           GET/POST /api/alerts, drift-events, explain
      investigate.py      POST /api/investigate (NL copilot)
      reports.py          POST /api/reports/str/{id} → PDF
      ws.py               WebSocket /ws/alerts + /demo/inject-pattern
    dependencies.py       Graph/alerts/model singletons with RLock
```

---

## Key Architecture Decisions

**XGBoost instead of full GNN.** The Phase 1 PPT described a Temporal GNN (ChronoWave-GNN). For the prototype, XGBoost on graph-structural features is the correct approach - validated explicitly by the hackathon sample D3 document. PyTorch Geometric TGN requires significantly more training data and compute than a POC allows. SHAP TreeExplainer on XGBoost is functionally equivalent to GNNExplainer for the purposes of feature attribution. This is disclosed honestly in MODEL_CARD.md.

**NetworkX instead of Neo4j.** For 500-5000 accounts, NetworkX is adequate and eliminates an external database dependency. Neo4j GDS is the targeted v2 upgrade for production-scale (millions of accounts). This is documented in DECISIONS.md ADR-0003.

**Single-container deployment.** Backend and React frontend are served from the same Cloud Run container. FastAPI mounts the React `dist/` as StaticFiles with a catch-all SPA fallback. This simplifies the deployment to a single URL and eliminates CORS configuration.

**PYTHONPATH must be set.** Python's stdlib includes `trace.py` (for code tracing). Without `ENV PYTHONPATH=/app/src` in the Dockerfile, Cloud Run finds the stdlib module before our package. The editable install's `.pth` mechanism works locally but not in the Cloud Run runtime environment.

**Compliance rules as YAML, not code.** RBI Master Directions and FIU-IND thresholds change frequently. Hard-coding them in Python means every regulatory update requires a code deployment. The YAML hot-reload approach (watchdog file watcher, first-match-wins evaluation) lets compliance teams update rules without engineering involvement.

---

## Data Flow: Alert Generation

```
1. scripts/seed_demo.py runs once at Docker build time
2. generator.py creates 500 accounts + 5 seeded fraud rings
3. builder.py constructs NetworkX MultiDiGraph (542 nodes, 5049 edges)
4. feature_engineering.py extracts 11 features per account
5. gnn_classifier.py trains XGBoost → models/classifier.pkl
6. shap_wrapper.py batch_explain() → SHAP values cached in alerts.json
7. explainer.py precache_all() → Gemini explanations to data/processed/explanations/
8. alerts.json written with 8 flagged accounts (risk ≥ MEDIUM)

At runtime (FastAPI startup):
9. dependencies.py loads graph.pkl, alerts.json, classifier.pkl into memory
10. compliance_engine.py starts watchdog on compliance_rules.yaml
11. anomaly_scorer.py initializes River HST singleton
12. WebSocket ticks every 8s: score 10 random accounts → push drift events
```

---

## Test Coverage

| Suite | Tests | Coverage |
|---|---|---|
| Pattern detectors (5 typologies) | 18 | circular flow, layering, structuring, mule, dormant burst |
| Feature engineering | 10 | extract_features, build_feature_matrix, missing values |
| XGBoost classifier | 6 | train, score, AUC threshold, serialization |
| Compliance engine | 7 | rule eval, hot-reload, severity ordering |
| Risk fusion | 3 | composite score, threshold bins |
| API health | 1 | /api/health smoke test |
| **Total** | **42** | All passing |

---

## Deployment

| Component | Platform | URL |
|---|---|---|
| Full stack (API + Dashboard) | GCP Cloud Run (us-central1) | https://trace-ai-4xnj5ovp4a-uc.a.run.app |
| Container Registry | GCR (gcr.io/agrowise-192e3/trace-ai) | - |
| Rebuild | `gcloud builds submit --config cloudbuild.yaml .` | ~11 min (Rust + npm) |

**Resource allocation:** 2 vCPU, 2 GiB RAM, 300s request timeout, allow unauthenticated.
