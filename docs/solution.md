
# TRACE.ai — Transaction Risk Analysis & Compliance Engine
## Detailed Project Solution

**Hackathon:** iDEA 2.0 (Union Bank of India / IBA / DFS)
**Problem Statement:** PS3 — Tracking of Funds within Bank for Fraud Detection
**Submission Deadline:** March 29, 2026

---

## 1. PROBLEM STATEMENT

Indian banks lost **₹71,543 Cr** to fraud in FY 2024-25 (RBI Annual Report). Despite this, over **95% of banks rely on rule-based AML systems** that:

- Generate **95%+ false positive rates**, creating investigator fatigue
- Cannot detect **multi-hop laundering** — layering funds through 4-8 intermediary accounts
- Miss **circular round-tripping** — funds cycling through shell entities back to origin
- Fail on **structuring** — splitting ₹10L+ amounts into dozens of sub-threshold transactions
- Cannot correlate **dormant account activations** for high-value transfers
- Take investigators **4–6 hours per STR** with manual fund-flow tracing

The core failure: rule-based systems look at transactions in isolation. Sophisticated AML requires seeing the **graph** — the network of accounts, relationships, and temporal patterns that rules cannot model.

---

## 2. SOLUTION OVERVIEW

**TRACE.ai** (Transaction Risk Analysis & Compliance Engine) is an intelligent fund flow tracking platform that:

1. Models every banking transaction as an **edge in a dynamic temporal directed graph**
2. Runs **three detection engines in parallel** (pattern matching, temporal GNN, online anomaly)
3. Fuses signals with a **compliance rule engine** into a weighted risk score
4. Provides an **LLM-powered investigation copilot** for natural language querying
5. **Auto-generates FIU-IND compliant STR evidence packages** in one click
6. Delivers everything through a **React dashboard with 3D graph visualization**

---

## 3. ARCHITECTURE — FIVE LAYERS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRACE.ai ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 0: DATA INGESTION                                                   │
│  AMLSim (synthetic) · CBS Feeds · NEFT/RTGS/UPI/IMPS                      │
│  → Parse to (sender, receiver, amount, timestamp, channel)                 │
│                          │                                                 │
│                          ▼                                                 │
│  LAYER 1: GRAPH ENGINE                                                     │
│  NetworkX MultiDiGraph (prototype) │ Neo4j GDS (production scale)         │
│  Nodes = Accounts (type, KYC risk, age, balance, dormancy status)         │
│  Edges = Transactions (amount, timestamp, channel, fraud_label)           │
│                          │                                                 │
│                          ▼                                                 │
│  LAYER 2: DETECTION ENGINE (4 parallel modules + fusion)                  │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ ┌──────────────┐  │
│  │ A: Pattern   │ │ B: Temporal  │ │ C: Online      │ │ D: Compliance│  │
│  │  Matcher     │ │    GNN       │ │   Anomaly      │ │   Rules      │  │
│  │ (NetworkX)   │ │ (PyG TGN +  │ │  Scorer        │ │ (YAML hot-  │  │
│  │ cycles,      │ │  ChronoWave  │ │ (River HST +   │ │  reload)     │  │
│  │ paths,       │ │  + THG-OAFN  │ │  ADWIN drift)  │ │ CTR, KYC,   │  │
│  │ centrality,  │ │  attention)  │ │  Per-account   │ │ RBI rules)  │  │
│  │ community)   │ │              │ │  streaming     │ │              │  │
│  └──────┬───────┘ └──────┬───────┘ └───────┬────────┘ └──────┬───────┘  │
│         └───────────────┬┘────────────────┘└──────────────────┘          │
│                          ▼                                                 │
│         E: Risk Fusion (weighted composite score)                         │
│         pattern(0.30) + GNN(0.30) + anomaly(0.20) + compliance(0.20)     │
│                          │                                                 │
│                          ▼                                                 │
│  LAYER 3: INTELLIGENCE                                                     │
│  F: LLM Alert Explainer │ G: NL Investigation Copilot │ H: Auto-STR Gen  │
│                          │                                                 │
│                          ▼                                                 │
│  LAYER 4: DELIVERY                                                         │
│  FastAPI (REST + WebSocket) │ React Dashboard                              │
│  3D Force Graph · Alert Stream · Copilot Chat · STR Download              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. DETECTION ENGINE — MODULE-BY-MODULE

### Module A: Graph Pattern Matcher
**Technology:** NetworkX algorithms on MultiDiGraph

Detects the structural signatures of five core AML typologies:

| Typology | Algorithm | Detection Criteria |
|---|---|---|
| **Circular Flow / Round-Tripping** | `simple_cycles()` | Cycles ≥ 3 nodes, within 72-hour window, cumulative amount > ₹1L |
| **Layering** | Temporal path analysis | Transaction chains ≥ 4 hops, funds forward >70%, within 48-hour window |
| **Structuring** | Amount-threshold clustering | ≥3 transactions from same account summing ₹9L–9.99L within 24 hours |
| **Mule Account / Fan-In-Out** | In-degree/out-degree centrality + community detection | High in-degree from disparate communities + immediate high out-degree |
| **Dormant Account Burst** | Temporal burst analysis | Account inactive >90 days → >3 high-value transactions within 48 hours |

**Scoring output:** `pattern_score ∈ [0,1]` with matched typology flags.

**Research basis:** PPATK "Money Laundering Typology Detection Using Graph Analytics and Neural Networks" (2025); Elliptic2 "Shape of Money Laundering" subgraph motifs (2024).

---

### Module B: Temporal Graph Neural Network (TGN)
**Technology:** PyTorch Geometric TGN + ChronoWave-GNN-inspired edge encoding + THG-OAFN attention fusion

**Architecture:**
```
Transaction Stream
       │
       ▼
Line-Graph Encoder (edge-centric: transactions as nodes, adjacency via shared accounts)
       │
       ▼
Multi-scale Temporal Features
  ├── Short window (1h): recent burst detection
  ├── Medium window (24h): daily pattern baseline
  └── Long window (7d): weekly behavioral drift
       │
       ▼
TGN Memory Module (per-account temporal state)
  ├── Memory: compressed historical embedding per account
  ├── Message passing: graph attention over temporal neighbors
  └── Memory updater: GRU-based incremental update
       │
       ▼
Attention Fusion Layer (THG-OAFN-inspired)
  ├── Structural features (degree, centrality, community)
  └── Temporal features (recency, frequency, velocity)
       │
       ▼
Node Classifier: suspicious / clean (per account)
Edge Classifier: suspicious / clean (per transaction)
Link Predictor: fraud ring formation probability
```

**Handling class imbalance:** GraphSMOTE-based oversampling (THG-OAFN pattern). Fraud = <1% of transactions; oversampling in the graph structure rather than feature space.

**Training data:** IBM AMLSim synthetic dataset — 100K+ labeled transactions with 6+ injected AML typologies. Validated on Elliptic dataset structure.

**Scoring output:** `gnn_score ∈ [0,1]` per account and transaction.

**Research basis:**
- Rossi et al., "Temporal Graph Networks" (arXiv:2006.10637, 2020)
- ChronoWave-GNN wavelet-temporal graph network (PMC, 2026)
- THG-OAFN — AUC 96.56%, recall 95%+ on fraud benchmarks (PLOS ONE, 2025)
- "Real-time Cross-border Payment Fraud Detection Using TGNN" — 37% FP reduction (2025)

---

### Module C: Online Anomaly Scorer
**Technology:** River library — HalfSpaceTrees + ADWIN

**Design:**
- **Per-account behavioral baseline:** Each account develops its own streaming anomaly model through incremental online learning — updates per transaction, no batch retraining
- **Features:** {transaction amount, velocity (txns/hour), amount variance, channel change frequency, time-of-day deviation, counterparty diversity}
- **Cold-start handling:** New accounts use account-type priors (savings/current/salary profiles) until sufficient history accumulates
- **Concept drift:** ADWIN (Adaptive Windowing) detects when fraud patterns shift and automatically adapts the model window

**Scoring output:** `anomaly_score ∈ [0,1]` — deviation from learned behavioral baseline.

**Research basis:** BIS Working Paper "ML Anomaly Detection for Large-Value Payment Systems" — two-layer supervised filter + unsupervised anomaly design; >90% detection rate (2023).

---

### Module D: Compliance Rule Engine
**Technology:** YAML-defined rules with hot-reload (watchdog file watcher)

**Rules implemented:**
```yaml
rules:
  - id: CTR_THRESHOLD
    description: Cash Transaction Report — ₹10L+ cash
    condition: amount >= 1000000 AND channel IN [BRANCH, ATM]
    action: FLAG_CTR
    severity: HIGH

  - id: STRUCTURING_DAILY
    description: Multiple sub-threshold transactions same day
    condition: daily_sum_same_sender >= 900000 AND daily_sum_same_sender < 1000000
    action: FLAG_STRUCTURING
    severity: HIGH

  - id: DORMANT_ACTIVATION
    description: Dormant account high-value activation
    condition: account_dormant_days >= 90 AND amount >= 500000
    action: FLAG_DORMANT
    severity: MEDIUM

  - id: KYC_HIGH_RISK
    description: High-risk KYC customer large transfer
    condition: kyc_risk_category == HIGH AND amount >= 200000
    action: FLAG_KYC_REVIEW
    severity: MEDIUM

  - id: CROSS_BORDER_NEFT
    description: Unusual cross-bank large transfer
    condition: sender_bank != receiver_bank AND amount >= 500000 AND velocity_24h >= 5
    action: FLAG_CROSS_BORDER
    severity: LOW
```

**Hot-reload:** YAML file is watched; rule changes take effect within 5 seconds without system restart. Supports first-match-wins evaluation, wildcard conditions, and AND/OR operators.

---

### Module E: Risk Fusion Engine
**Technology:** Weighted composite scoring with calibrated thresholds

```
composite_score = (
    0.30 × pattern_score     # Structural typology match
  + 0.30 × gnn_score         # Learned temporal-structural anomaly
  + 0.20 × anomaly_score     # Per-account behavioral deviation
  + 0.20 × compliance_score  # Regulatory rule match
)

Risk Levels:
  CRITICAL  (≥0.85): Automatic STR initiation recommended
  HIGH      (≥0.70): Immediate investigator review required
  MEDIUM    (≥0.50): Queue for daily investigation review
  LOW       (<0.50): Monitor, no immediate action
```

---

## 5. INTELLIGENCE LAYER

### Module F: LLM Alert Explainer
Every alert is accompanied by a natural language explanation generated by an LLM:

> *"This alert was triggered because Account ACC-4821 (UBIN, current account, high KYC risk) transferred ₹9.7L to 3 different accounts within 18 hours — matching structuring criteria. The GNN model also assigns this account a 0.87 suspicious probability due to its position as a hub in a 7-node community that received funds from dormant accounts in the past 72 hours."*

**Technology:** GPT-4o-mini / Claude Haiku via LiteLLM, with template-constrained generation grounded in factual graph evidence. Human review required before STR filing.

### Module G: Investigation Copilot (NL → Graph Query)
Compliance officers query the graph in plain English:

| Natural Language Query | System Action |
|---|---|
| "Show all circular flows above ₹5L in the last 7 days" | NL → Cypher → graph subview with highlighted cycles |
| "Which accounts sent funds to dormant accounts yesterday?" | NL → NetworkX query → account list with risk scores |
| "Give me the full fund trail for ACC-4821" | Multi-hop path traversal → visual fund flow diagram |
| "Flag all accounts with high KYC risk that transferred above ₹2L to the same beneficiary" | Rule → query execution → filtered alert list |

**Technology:** Vanna.ai-inspired NL-to-query pipeline. LLM translates intent to NetworkX API calls (prototype) or Cypher (production). Results returned as graph subviews + tabular data.

### Module H: Auto-STR Generator (FIU-IND Compliant)
One-click generation of regulatory-compliant Suspicious Transaction Report:

**STR Package Contents:**
1. **Cover page:** Alert ID, generation timestamp, risk level
2. **Subject account details:** Account number (masked), type, branch, KYC category
3. **Suspicious transaction table:** All flagged transactions with amounts, timestamps, counterparties, channels
4. **Complete fund trail diagram:** Visual graph showing full money flow path
5. **Risk score breakdown:** Pattern score, GNN score, anomaly score, compliance flags — each explained
6. **AI-generated analysis narrative:** LLM-written description of the suspicious behavior pattern
7. **Recommended action:** STR filing, account freeze, further investigation
8. **Evidence metadata:** Pattern IDs, algorithm versions, timestamp

**Technology:** ReportLab PDF generation. Format compliant with FIU-IND reporting requirements under PMLA 2002.

**Impact:** STR preparation time reduced from **4–6 hours → under 5 minutes**.

---

## 6. DATA LAYER

### Synthetic Data Generation
**Source:** IBM AMLSim (primary) + custom IndianBankingDataGenerator

**Generated dataset:**
- **5,000 accounts** with realistic Indian banking profiles (account types, IFSC codes, KYC categories, cities)
- **100,000+ transactions** across NEFT, RTGS, UPI, IMPS, BRANCH, ATM, MOBILE channels
- **6 injected fraud typologies** with labeled ground truth:
  - Layering (multi-hop chains, ≥4 hops)
  - Round-tripping (circular flows, ≥3 nodes)
  - Structuring (sub-threshold clustering)
  - Mule account networks (fan-in / fan-out)
  - Dormant account bursts
  - Fan-out disbursement

**Indian banking context:** ₹ amounts, IFSC codes (UBIN/SBIN/HDFC/ICIC/PUNB/BKID/CNRB), CTR threshold at ₹10L, RBI-compliant date ranges.

---

## 7. DELIVERY LAYER

### Backend: FastAPI
```
REST API endpoints:
  GET  /graph                    → Full transaction graph (paginated)
  GET  /graph/{account_id}       → Subgraph centered on account
  GET  /alerts                   → Active alerts with risk scores
  POST /alerts/{id}/acknowledge  → Mark alert as reviewed
  POST /investigate              → Copilot NL query
  GET  /reports/str/{alert_id}   → Download STR PDF
  POST /transactions             → Ingest new transaction

WebSocket:
  WS  /ws/alerts                 → Real-time alert stream
```

### Frontend: React Dashboard
- **3D Force Graph** (react-force-graph-3d / Three.js / WebGL) — accounts as nodes colored by risk level, transactions as edges with thickness proportional to amount
- **Alert Panel** — real-time WebSocket stream of new alerts with risk scores and typology tags
- **Investigation Panel** — copilot chat interface + graph explorer
- **KPI Cards** — alerts today, high-risk accounts, false positive rate, STRs generated
- **Account Detail** — click any node for full account profile + transaction history + risk breakdown
- **STR Download** — one-click evidence package download for any alert

---

## 8. TECHNOLOGY STACK

| Layer | Technology | Purpose |
|---|---|---|
| Data Generation | IBM AMLSim, Faker (en_IN) | Synthetic labeled AML transactions |
| Graph Engine | NetworkX MultiDiGraph | Pattern detection, graph algorithms |
| Graph Scale | Neo4j Community + APOC + GDS | Production-scale graph storage and queries |
| GNN Framework | PyTorch Geometric (TGN) | Temporal graph neural network |
| GNN Architecture | ChronoWave-GNN inspired, THG-OAFN inspired | Edge-centric temporal encoding, attention fusion |
| Imbalance Handling | GraphSMOTE (THG-OAFN pattern) | Rare fraud class oversampling in graph space |
| Online ML | River (HalfSpaceTrees, ADWIN) | Per-account streaming anomaly baseline |
| Compliance Rules | YAML + watchdog (hot-reload) | Regulatory rule evaluation |
| LLM | GPT-4o-mini / Claude Haiku via LiteLLM | Alert explanations, NL queries, STR narratives |
| NL-to-Query | Vanna.ai-inspired pipeline | NL → Cypher / NetworkX |
| PDF Generation | ReportLab | FIU-IND compliant STR packages |
| Backend | FastAPI + WebSocket + Uvicorn | REST API + real-time alert streaming |
| Database | SQLite (audit log + alert store) | Decision audit trail |
| Frontend | React + TypeScript | Investigator dashboard |
| Visualization | react-force-graph-3d (Three.js/WebGL) | 3D transaction network |
| Containerization | Docker + Docker Compose | Reproducible deployment |
| Training | Kaggle/Colab T4 GPU | GNN training (CPU inference) |

---

## 9. KEY INNOVATIONS

1. **Temporal GNN with edge-centric modeling** — Not a static graph snapshot. TGN with line-graph encoder captures evolving fraud ring formation over days, detecting patterns invisible to node-level or rule-based systems.

2. **Online ML baselines — zero batch retraining** — River HalfSpaceTrees build per-account behavioral models through streaming learning. ADWIN detects and adapts to concept drift. No scheduled retraining jobs, no model staleness.

3. **Natural language investigation copilot** — Compliance officers ask questions in English. No Cypher, no SQL, no technical skills required. Instant graph subviews with risk highlights.

4. **Automated FIU-IND STR generation** — Complete regulatory artifact in one click: fund trail, risk breakdown, AI narrative, evidence package. 4 hours → 5 minutes.

5. **Hot-reloadable YAML compliance rules** — When RBI issues a new circular, rules update in seconds without code changes or system restart. AML policy changes deploy at the speed of YAML editing.

---

## 10. WHAT WE ARE NOT BUILDING

- We are **not** building a traditional rule-based AML system (those already exist and fail)
- We are **not** replacing human compliance officers (TRACE.ai augments their judgment)
- We are **not** using a black-box approach (every alert comes with a full explanation)
- We are **not** requiring real bank data for development (IBM AMLSim + synthetic generator)

---

## 11. EXPECTED OUTCOMES

| Metric | Current Baseline | TRACE.ai Target | Source |
|---|---|---|---|
| False positive rate | 95%+ (rule-based) | <15% (multi-signal fusion) | THG-OAFN benchmarks + multi-model fusion |
| AUC on fraud detection | ~0.70 (static ML) | >0.95 (temporal GNN) | ChronoWave-GNN / THG-OAFN benchmarks |
| STR preparation time | 4–6 hours (manual) | <5 minutes (automated) | Auto-STR generation module |
| Fraud detection latency | 277 days avg (IBM 2024) | Real-time (per transaction) | Online ML + streaming detection |
| FP reduction vs static GNN | baseline | ~37% improvement | Real-time TGNN for Payments (2025) |

---

## 12. RESEARCH FOUNDATION

| Paper | Relevance |
|---|---|
| Rossi et al., "Temporal Graph Networks" (arXiv:2006.10637, 2020) | Core TGN architecture |
| "Graph Neural Networks for Financial Fraud Detection: A Review" (arXiv 2024) | Justification for GNN approach |
| Wei & Lee, "THG-OAFN" (PLOS ONE, 2025) | Imbalance handling + attention fusion architecture |
| "ChronoWave-GNN" (PMC, 2026) | Edge-centric temporal modeling, wavelet features |
| "Shape of Money Laundering / Elliptic2" (2024) | Subgraph typology motifs |
| BIS WP: "ML Anomaly Detection for LVPS" (2023) | Two-layer anomaly framework |
| "Real-time TGNN for Cross-border Payments" (2025) | 37% FP reduction benchmark |
| "Money Laundering Typology Detection" PPATK (2025) | Graph metric-based pattern detection |
| Weber et al., "GNNs for Bitcoin AML / Elliptic" (arXiv:1908.02591, 2019) | AML GNN benchmark baseline |

---

## 13. FEASIBILITY

**Why this is buildable in a hackathon timeframe:**
- All components are proven open-source libraries with good documentation
- No real bank data required — IBM AMLSim provides realistic labeled synthetic data
- GNN training runs on free Kaggle T4 GPUs; inference runs on CPU
- Modular architecture — each module (A–H) is independently developed and tested
- 4-member team maps directly to 4 architecture layers (ML/GNN, Backend, Frontend, LLM/Compliance)

**Biggest risk and mitigation:**
- **GNN class imbalance** (fraud <1%): Mitigated by GraphSMOTE + focal loss + stratified temporal batching
- **False positives**: Multi-signal fusion (3 independent modules) reduces FP vs any single model
- **Scale**: NetworkX for prototype → Neo4j GDS for production, graph queries scoped to temporal windows

---

## 14. DEPLOYMENT PATH

```
Phase 1 (Hackathon — current):
  → Fully functional on IBM AMLSim synthetic data
  → All 5 detection modules + copilot + auto-STR
  → React dashboard + FastAPI backend
  → Docker Compose deployment

Phase 2 (Post-hackathon pilot — Union Bank):
  → API integration with CBS transaction feeds
  → Neo4j for production graph storage
  → GNN fine-tuned on bank's anonymized data
  → Compliance rules tuned to Union Bank's policies

Phase 3 (Production — multi-bank):
  → Multi-branch deployment
  → Federated model updates (privacy-preserving)
  → Real-time WebSocket alerting at scale
  → FIU-IND direct STR submission integration
  → IBA/DFS recommendation for PSB rollout
```

---

## 15. REPO STRUCTURE

```
trace-ai/
├── data/
│   ├── raw/                    # AMLSim output (generated)
│   ├── processed/              # Feature-engineered data
│   └── amlsim_config/          # AMLSim configuration (fraud_patterns.yaml)
├── src/trace/
│   ├── data/
│   │   ├── generator.py        # Synthetic Indian banking data generator
│   │   ├── ingestion.py        # CSV/stream → internal format
│   │   └── feature_engineering.py
│   ├── graph/
│   │   ├── builder.py          # NetworkX DiGraph construction
│   │   ├── temporal.py         # Temporal windowing + snapshots
│   │   └── export.py           # → PyG format, Neo4j, JSON (viz)
│   ├── detection/
│   │   ├── pattern_matcher.py  # Module A: Graph pattern detection
│   │   ├── gnn_classifier.py   # Module B: TGN-based classification
│   │   ├── anomaly_scorer.py   # Module C: River HalfSpaceTrees
│   │   ├── compliance_engine.py # Module D: YAML rule engine
│   │   ├── risk_fusion.py      # Module E: Composite risk scoring
│   │   └── patterns/           # circular_flow.py, layering.py, etc.
│   ├── intelligence/
│   │   ├── explainer.py        # Module F: LLM alert explanation
│   │   ├── copilot.py          # Module G: NL investigation copilot
│   │   └── str_generator.py    # Module H: FIU-IND STR generation
│   └── api/
│       ├── main.py             # FastAPI app
│       ├── routes/             # graph.py, alerts.py, investigate.py, reports.py, ws.py
│       └── dependencies.py
├── frontend/src/
│   ├── components/
│   │   ├── GraphVisualization.tsx  # 3D Force Graph
│   │   ├── AlertPanel.tsx
│   │   ├── InvestigationPanel.tsx  # Copilot chat
│   │   ├── KPICards.tsx
│   │   └── STRDownload.tsx
│   └── hooks/
│       ├── useWebSocket.ts
│       └── useGraphData.ts
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_graph_analysis.ipynb
│   ├── 03_gnn_training.ipynb
│   └── 04_evaluation.ipynb
├── scripts/
│   ├── generate_data.py
│   ├── train_gnn.py
│   ├── seed_demo.py
│   └── run_demo.py
├── compliance_rules.yaml       # Module D regulatory rules
├── docker-compose.yml
└── pyproject.toml
```

---

*Solution finalized: March 29, 2026. iDEA Hackathon 2.0 — PS3.*
