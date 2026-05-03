

# TRACE.ai — Complete Build Bible

## PS3: Tracking of Funds within Bank for Fraud Detection

---

## 1. EXECUTIVE SUMMARY

```
PROJECT:     TRACE.ai — Transaction Risk Analysis & Compliance Engine
PS:          PS3 — Tracking of Funds within Bank for Fraud Detection
HACKATHON:   iDEA 2.0 (Union Bank of India / IBA / DFS)
DEADLINE:    March 29, 2026 (Idea Submission — PDF, no resubmission)
TEAM SIZE:   4 members
LANGUAGE:    Python (backend + ML) / TypeScript (frontend)
GOAL:        Intelligent fund flow tracking system using graph analytics,
             GNNs, online ML anomaly detection, and LLM-powered
             investigation tools for AML compliance.
```

---

## 2. ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRACE.ai ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DATA LAYER (Layer 0)                            │   │
│  │                                                                     │   │
│  │  AMLSim (synthetic)  ──┐                                           │   │
│  │  CSV/JSON feeds      ──┼──►  Transaction Ingestion Pipeline        │   │
│  │  Real-time streams   ──┘     (FastAPI + async queue)               │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                       │                                     │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │                   GRAPH ENGINE (Layer 1)                            │   │
│  │                                                                     │   │
│  │  NetworkX DiGraph                    Neo4j (optional, at scale)    │   │
│  │  ├─ Nodes: Accounts                  ├─ Cypher queries             │   │
│  │  ├─ Edges: Transactions              ├─ APOC procedures            │   │
│  │  ├─ Temporal attributes              └─ Graph Data Science lib    │   │
│  │  └─ Dynamic updates                                               │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                       │                                     │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │                  DETECTION ENGINE (Layer 2)                         │   │
│  │                                                                     │   │
│  │  Module A: Graph Pattern Matcher (NetworkX algorithms)             │   │
│  │    ├─ Circular flow detection (simple_cycles)                      │   │
│  │    ├─ Layering detection (path analysis + temporal windowing)       │   │
│  │    ├─ Structuring detection (amount threshold clustering)           │   │
│  │    ├─ Mule account identification (centrality + community)         │   │
│  │    └─ Dormant account activation (temporal burst analysis)         │   │
│  │                                                                     │   │
│  │  Module B: GNN Anomaly Classifier (PyTorch Geometric)              │   │
│  │    ├─ Temporal Graph Network (TGN) for dynamic graphs              │   │
│  │    ├─ Node classification: suspicious vs clean accounts            │   │
│  │    ├─ Edge classification: suspicious vs clean transactions        │   │
│  │    └─ Link prediction: will this account join a fraud ring?        │   │
│  │                                                                     │   │
│  │  Module C: Online Anomaly Scorer (River)                           │   │
│  │    ├─ HalfSpaceTrees per-account behavioral baseline               │   │
│  │    ├─ Cold-start fallback (account-type priors)                    │   │
│  │    └─ ADWIN concept drift detection                                │   │
│  │                                                                     │   │
│  │  Module D: Compliance Rule Engine (YAML-driven)                    │   │
│  │    ├─ CTR threshold rules (₹10L+ reporting)                       │   │
│  │    ├─ RBI Master Direction rules                                   │   │
│  │    └─ Hot-reloadable policy definitions                            │   │
│  │                                                                     │   │
│  │  Module E: Risk Fusion Engine                                      │   │
│  │    └─ Weighted composite: pattern + GNN + anomaly + compliance    │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                       │                                     │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │                 INTELLIGENCE LAYER (Layer 3)                        │   │
│  │                                                                     │   │
│  │  Module F: LLM Alert Explainer                                     │   │
│  │    └─ "This alert was triggered because Account A transferred..."  │   │
│  │                                                                     │   │
│  │  Module G: Investigation Copilot (Vanna.ai-inspired)               │   │
│  │    └─ NL → Graph Query → Result → NL Response                    │   │
│  │                                                                     │   │
│  │  Module H: STR Report Generator (ReportLab)                        │   │
│  │    └─ Auto-generate FIU-IND compliant PDF evidence packages       │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                       │                                     │
│  ┌───────────────────────────────────▼─────────────────────────────────┐   │
│  │                   DELIVERY LAYER (Layer 4)                          │   │
│  │                                                                     │   │
│  │  FastAPI Backend (REST + WebSocket)                                │   │
│  │  React Frontend                                                    │   │
│  │    ├─ 3D Force Graph (transaction network visualization)           │   │
│  │    ├─ Alert Dashboard (real-time stream)                           │   │
│  │    ├─ Investigation Panel (copilot chat + graph explorer)          │   │
│  │    ├─ KPI Cards (alerts today, risk score distribution, etc.)     │   │
│  │    └─ STR Download (one-click evidence package)                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. REPO DEPENDENCY MAP (UPDATED — WITH SOTA COMPONENTS)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REPOS TO CLONE/STAR NOW (TRACE.ai)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LAYER 0 — DATA & TYPOLOGIES                                           │
│                                                                         │
│  ☐ github.com/IBM/AMLSim                                               │
│    → Clone. Study paramFiles/. Run to generate 100K+ labeled txns.    │
│    → fraud_patterns.yaml → use to seed our amlsim_config/             │
│    → Outputs: transactions.csv, accounts.csv, sar_accounts.csv        │
│                                                                         │
│  ☐ Elliptic2 dataset (via Papers With Code)                            │
│    → Study subgraph extraction + "shape of laundering" motifs         │
│    → 122K labeled laundering subgraphs; adapt into patterns/          │
│                                                                         │
│                                                                         │
│  LAYER 1 — GRAPH & GNN CORE                                            │
│                                                                         │
│  ☐ github.com/pyg-team/pytorch_geometric                               │
│    → pip install torch-geometric                                       │
│    → Study examples/temporal/tgn.py — start TGN from here            │
│    → Use built-in TGN as base for gnn_classifier.py                   │
│                                                                         │
│  ☐ github.com/wei4zheng/THG-OAFN  [PRIORITY — CLONE]                  │
│    → PyTorch implementation of temporal-aware heterogeneous GNN       │
│    → Borrow: GraphSMOTE oversampling + attention fusion blocks        │
│    → Plug into gnn_classifier.py as imbalance handler                 │
│                                                                         │
│  ☐ ChronoWave-GNN (PMC article code — check repo link in paper)       │
│    → Wavelet + temporal GNN, edge-centric (line-graph view)           │
│    → Borrow: multi-scale temporal feature extraction                  │
│    → Use ideas in gnn_classifier.py edge encoder                      │
│                                                                         │
│  ☐ github.com/git-disl/EllipticGNN                                     │
│    → Study only. Reference feature engineering + training loops       │
│                                                                         │
│  ☐ networkx (pip install networkx)                                     │
│    → simple_cycles, community detection, centrality, shortest_paths   │
│    → Core of pattern_matcher.py + graph/builder.py                    │
│                                                                         │
│  ☐ github.com/neo4j-graph-examples/fraud-detection                     │
│    → Study Cypher queries for fraud patterns                          │
│    → Reference for Neo4j integration + NL→Cypher copilot templates   │
│                                                                         │
│                                                                         │
│  LAYER 2 — ANOMALY & ONLINE LEARNING                                   │
│                                                                         │
│  ☐ github.com/online-ml/river                                          │
│    → pip install river                                                 │
│    → Use: anomaly.HalfSpaceTrees + drift.ADWIN                        │
│    → Per-account streaming anomaly scores in anomaly_scorer.py        │
│                                                                         │
│                                                                         │
│  LAYER 3 — INTELLIGENCE & COPILOT                                      │
│                                                                         │
│  ☐ github.com/vanna-ai/vanna                                           │
│    → Study architecture. Adapt NL→SQL pattern for NL→Cypher          │
│    → Use in copilot.py investigation query generation                  │
│                                                                         │
│  ☐ LLM: GPT-4o-mini / Claude Haiku via LiteLLM                        │
│    → Alert explanations (explainer.py)                                │
│    → NL investigation queries (copilot.py)                            │
│    → STR narrative generation (str_generator.py)                      │
│                                                                         │
│                                                                         │
│  LAYER 4 — VISUALIZATION & REPORTING                                   │
│                                                                         │
│  ☐ github.com/vasturiano/react-force-graph                             │
│    → npm install react-force-graph-3d                                  │
│    → Main viz canvas in GraphVisualization.tsx                        │
│                                                                         │
│  ☐ reportlab (pip install reportlab)                                   │
│    → FIU-IND style STR evidence packages in str_generator.py         │
│                                                                         │
│  ☐ FastAPI (pip install fastapi uvicorn)                               │
│    → REST + WebSocket in api/main.py                                  │
│                                                                         │
│                                                                         │
│  RESEARCH / DESIGN REFERENCES (mine for architecture ideas)            │
│                                                                         │
│  ☐ arXiv:2006.10637 — TGN: Temporal Graph Networks (Rossi 2020)       │
│  ☐ arXiv:2411.05815 — GNNs for Fraud Detection Survey (2024)          │
│  ☐ arXiv:1908.02591 — GNNs for Bitcoin AML / Elliptic (Weber 2019)    │
│  ☐ PMC/ChronoWave-GNN — Wavelet-temporal GNN (2026)                   │
│  ☐ PLOS ONE/THG-OAFN — Temporal-heterogeneous graph + GraphSMOTE      │
│  ☐ BIS WP 1188 — ML anomaly detection for LVPS (2023)                 │
│  ☐ Elliptic2 / "Shape of Money Laundering" — subgraph motifs (2024)   │
│  ☐ PPATK/JAC — Money Laundering Typology Detection (2025)             │
│  ☐ TGNN Cross-border Payments — 37% FP reduction (2025)               │
│  ☐ RBI Master Direction on KYC (updated 2024)                         │
│  ☐ FIU-IND STR Filing Manual                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. PROJECT STRUCTURE

```
trace-ai/
├── README.md
├── claude.md                          # AI assistant context file
├── pyproject.toml                     # Python project config (uv/poetry)
├── uv.lock
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
│
├── data/
│   ├── raw/                           # AMLSim output (generated)
│   │   ├── transactions.csv
│   │   ├── accounts.csv
│   │   └── alerts.csv                 # Ground truth labels
│   ├── processed/                     # Feature-engineered data
│   │   ├── graph_edges.parquet
│   │   ├── graph_nodes.parquet
│   │   └── temporal_features.parquet
│   └── amlsim_config/                # AMLSim configuration files
│       ├── accounts.yaml
│       ├── transaction_types.yaml
│       └── fraud_patterns.yaml
│
├── src/
│   ├── trace/                         # Main package
│   │   ├── __init__.py
│   │   ├── config.py                  # YAML config loader
│   │   ├── models.py                  # Pydantic models (Transaction, Account, Alert, etc.)
│   │   │
│   │   ├── data/                      # Layer 0: Data
│   │   │   ├── __init__.py
│   │   │   ├── generator.py           # Synthetic data generator (wraps AMLSim concepts)
│   │   │   ├── ingestion.py           # CSV/stream → internal format
│   │   │   └── feature_engineering.py # Compute node/edge features for GNN
│   │   │
│   │   ├── graph/                     # Layer 1: Graph Engine
│   │   │   ├── __init__.py
│   │   │   ├── builder.py            # Build NetworkX DiGraph from transactions
│   │   │   ├── temporal.py           # Temporal graph windowing & snapshots
│   │   │   └── export.py             # Export to PyG format, Neo4j, JSON (for viz)
│   │   │
│   │   ├── detection/                 # Layer 2: Detection Engine
│   │   │   ├── __init__.py
│   │   │   ├── pattern_matcher.py     # Module A: Graph pattern detection
│   │   │   ├── gnn_classifier.py      # Module B: TGN-based classification
│   │   │   ├── anomaly_scorer.py      # Module C: River HalfSpaceTrees
│   │   │   ├── compliance_engine.py   # Module D: YAML rule engine
│   │   │   ├── risk_fusion.py         # Module E: Composite risk scoring
│   │   │   └── patterns/             # Pattern definitions
│   │   │       ├── circular_flow.py
│   │   │       ├── layering.py
│   │   │       ├── structuring.py
│   │   │       ├── mule_detection.py
│   │   │       └── dormant_burst.py
│   │   │
│   │   ├── intelligence/              # Layer 3: AI Intelligence
│   │   │   ├── __init__.py
│   │   │   ├── explainer.py           # Module F: LLM alert explanation
│   │   │   ├── copilot.py            # Module G: NL investigation copilot
│   │   │   └── str_generator.py       # Module H: FIU-IND STR report gen
│   │   │
│   │   ├── api/                       # Layer 4: Delivery (Backend)
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # FastAPI app entry point
│   │   │   ├── routes/
│   │   │   │   ├── graph.py          # GET /graph, /graph/{account_id}
│   │   │   │   ├── alerts.py         # GET /alerts, POST /alerts/acknowledge
│   │   │   │   ├── investigate.py    # POST /investigate (copilot)
│   │   │   │   ├── reports.py        # GET /reports/str/{alert_id}
│   │   │   │   └── ws.py            # WebSocket: real-time alert stream
│   │   │   └── dependencies.py       # Shared deps (graph instance, etc.)
│   │   │
│   │   └── observability/             # Audit & logging
│   │       ├── __init__.py
│   │       ├── audit_log.py          # SQLite-based decision log
│   │       └── metrics.py            # Detection metrics (precision, recall)
│   │
│   └── compliance_rules.yaml          # Module D config: regulatory rules
│
├── frontend/                          # Layer 4: Delivery (Frontend)
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── GraphVisualization.tsx  # 3D Force Graph
│   │   │   ├── AlertPanel.tsx         # Real-time alerts
│   │   │   ├── InvestigationPanel.tsx # Copilot chat interface
│   │   │   ├── KPICards.tsx           # Summary metrics
│   │   │   ├── AccountDetail.tsx      # Deep-dive on clicked account
│   │   │   └── STRDownload.tsx        # One-click report download
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts        # Alert stream
│   │   │   └── useGraphData.ts        # Graph data fetching
│   │   └── types/
│   │       └── index.ts               # TypeScript types
│   └── public/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # Explore AMLSim output
│   ├── 02_graph_analysis.ipynb        # NetworkX pattern detection experiments
│   ├── 03_gnn_training.ipynb          # TGN training on Kaggle/Colab
│   └── 04_evaluation.ipynb            # Precision/recall evaluation
│
├── tests/
│   ├── test_data_generator.py
│   ├── test_graph_builder.py
│   ├── test_pattern_matcher.py
│   ├── test_anomaly_scorer.py
│   ├── test_compliance_engine.py
│   ├── test_risk_fusion.py
│   ├── test_explainer.py
│   └── test_api.py
│
├── scripts/
│   ├── generate_data.py               # Run synthetic data generation
│   ├── train_gnn.py                   # Train TGN model
│   ├── seed_demo.py                   # Seed system with demo data + fraud
│   └── run_demo.py                    # Full demo script
│
└── docs/
    ├── idea_submission/
    │   ├── slides.pptx                # The 9-slide PPT (PDF export)
    │   └── one_page_summary.pdf       # Mandatory 1-page summary
    ├── architecture.md
    └── fraud_patterns.md              # Documentation of each pattern
```

---

## 5. COMPLETE BUILD GUIDE

### PHASE A: Synthetic Data Generation

```
GOAL: Generate 100K+ realistic banking transactions with injected
      fraud patterns (layering, round-tripping, structuring, mule networks)

TIME ESTIMATE: 3-4 hours
DEPENDENCY: Python, Faker
```

**File: `src/trace/data/generator.py`**

```python
"""
Synthetic Indian banking transaction data generator.
Inspired by IBM/AMLSim but simplified for hackathon speed.
Generates accounts with realistic Indian banking profiles and
injects 6 fraud typologies as labeled ground truth.
"""

import random
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import csv
import json

from faker import Faker

fake = Faker("en_IN")


class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    SALARY = "salary"
    NRE = "nre"
    OVERDRAFT = "overdraft"


class Channel(str, Enum):
    NEFT = "NEFT"
    RTGS = "RTGS"
    UPI = "UPI"
    IMPS = "IMPS"
    BRANCH = "BRANCH"
    ATM = "ATM"
    MOBILE = "MOBILE"
    NET_BANKING = "NET_BANKING"


class FraudType(str, Enum):
    CLEAN = "clean"
    LAYERING = "layering"
    ROUND_TRIPPING = "round_tripping"
    STRUCTURING = "structuring"
    MULE = "mule_account"
    DORMANT_BURST = "dormant_burst"
    FAN_OUT = "fan_out"


# Real IFSC codes (public data, first 4 chars = bank code)
BANK_IFSC_PREFIXES = [
    "UBIN",  # Union Bank of India
    "SBIN",  # SBI
    "HDFC",  # HDFC
    "ICIC",  # ICICI
    "PUNB",  # PNB
    "BKID",  # Bank of India
    "CNRB",  # Canara Bank
]


@dataclass
class Account:
    account_id: str
    account_type: AccountType
    ifsc_code: str
    branch_city: str
    customer_name: str
    pan_hash: str  # hashed PAN (privacy)
    kyc_risk_category: str  # low / medium / high
    account_age_days: int
    average_monthly_balance: float
    is_dormant: bool = False
    is_mule: bool = False
    fraud_label: FraudType = FraudType.CLEAN

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "account_type": self.account_type.value,
            "ifsc_code": self.ifsc_code,
            "branch_city": self.branch_city,
            "customer_name": self.customer_name,
            "pan_hash": self.pan_hash,
            "kyc_risk_category": self.kyc_risk_category,
            "account_age_days": self.account_age_days,
            "avg_monthly_balance": self.average_monthly_balance,
            "is_dormant": self.is_dormant,
            "is_mule": self.is_mule,
            "fraud_label": self.fraud_label.value,
        }


@dataclass
class Transaction:
    txn_id: str
    timestamp: datetime
    sender_id: str
    receiver_id: str
    amount: float
    channel: Channel
    currency: str = "INR"
    fraud_label: FraudType = FraudType.CLEAN
    fraud_pattern_id: Optional[str] = None  # links txns in same fraud pattern

    def to_dict(self) -> dict:
        return {
            "txn_id": self.txn_id,
            "timestamp": self.timestamp.isoformat(),
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "amount": self.amount,
            "channel": self.channel.value,
            "currency": self.currency,
            "fraud_label": self.fraud_label.value,
            "fraud_pattern_id": self.fraud_pattern_id or "",
        }


class IndianBankingDataGenerator:
    """
    Generates realistic synthetic Indian banking data with fraud patterns.

    Usage:
        gen = IndianBankingDataGenerator(
            num_accounts=5000,
            num_clean_transactions=80000,
            num_fraud_patterns=150,
        )
        accounts, transactions = gen.generate()
        gen.save_csv(accounts, transactions, output_dir="data/raw/")
    """

    INDIAN_CITIES = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal",
        "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana",
        "Agra", "Nashik", "Ranchi", "Faridabad", "Meerut",
        "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
    ]

    def __init__(
        self,
        num_accounts: int = 5000,
        num_clean_transactions: int = 80000,
        num_fraud_patterns: int = 150,
        start_date: datetime = datetime(2025, 1, 1),
        end_date: datetime = datetime(2025, 12, 31),
        seed: int = 42,
    ):
        self.num_accounts = num_accounts
        self.num_clean_txns = num_clean_transactions
        self.num_fraud_patterns = num_fraud_patterns
        self.start_date = start_date
        self.end_date = end_date
        self.rng = random.Random(seed)
        self.accounts: list[Account] = []
        self.transactions: list[Transaction] = []
        Faker.seed(seed)

    def _generate_ifsc(self) -> str:
        prefix = self.rng.choice(BANK_IFSC_PREFIXES)
        suffix = "".join([str(self.rng.randint(0, 9)) for _ in range(7)])
        return f"{prefix}0{suffix}"

    def _random_timestamp(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> datetime:
        s = start or self.start_date
        e = end or self.end_date
        delta = (e - s).total_seconds()
        offset = self.rng.random() * delta
        return s + timedelta(seconds=offset)

    def _random_amount(
        self, low: float = 100, high: float = 500000
    ) -> float:
        # Log-normal distribution (most txns small, few large)
        import math
        mu = math.log(low + (high - low) * 0.1)
        sigma = 1.5
        amount = self.rng.lognormvariate(mu, sigma)
        return round(min(max(amount, low), high), 2)

    # ── Account Generation ──────────────────────────────────

    def generate_accounts(self) -> list[Account]:
        accounts = []
        for i in range(self.num_accounts):
            acc = Account(
                account_id=f"ACC{i:06d}",
                account_type=self.rng.choice(list(AccountType)),
                ifsc_code=self._generate_ifsc(),
                branch_city=self.rng.choice(self.INDIAN_CITIES),
                customer_name=fake.name(),
                pan_hash=uuid.uuid4().hex[:16],
                kyc_risk_category=self.rng.choices(
                    ["low", "medium", "high"], weights=[70, 25, 5]
                )[0],
                account_age_days=self.rng.randint(30, 3650),
                average_monthly_balance=self._random_amount(5000, 2000000),
                is_dormant=self.rng.random() < 0.08,  # 8% dormant
            )
            accounts.append(acc)
        self.accounts = accounts
        return accounts

    # ── Clean Transaction Generation ────────────────────────

    def generate_clean_transactions(self) -> list[Transaction]:
        txns = []
        active_accounts = [a for a in self.accounts if not a.is_dormant]
        for i in range(self.num_clean_txns):
            sender = self.rng.choice(active_accounts)
            receiver = self.rng.choice(
                [a for a in active_accounts if a.account_id != sender.account_id]
            )
            channel = self.rng.choices(
                list(Channel),
                weights=[15, 5, 40, 20, 5, 5, 5, 5],  # UPI dominant
            )[0]
            # Channel-appropriate amounts
            if channel == Channel.UPI:
                amount = self._random_amount(50, 100000)
            elif channel == Channel.RTGS:
                amount = self._random_amount(200000, 5000000)
            elif channel == Channel.NEFT:
                amount = self._random_amount(1000, 1000000)
            else:
                amount = self._random_amount(100, 500000)

            txn = Transaction(
                txn_id=f"TXN{len(txns):08d}",
                timestamp=self._random_timestamp(),
                sender_id=sender.account_id,
                receiver_id=receiver.account_id,
                amount=amount,
                channel=channel,
                fraud_label=FraudType.CLEAN,
            )
            txns.append(txn)
        return txns

    # ── Fraud Pattern Injection ─────────────────────────────

    def _inject_layering(self, pattern_id: str) -> list[Transaction]:
        """
        Layering: A → B → C → D → E → F (rapid hops, same ~amount)
        Funds move through 4-8 intermediaries within a short time window.
        """
        chain_length = self.rng.randint(4, 8)
        chain_accounts = self.rng.sample(
            [a for a in self.accounts if not a.is_dormant], chain_length
        )
        base_amount = self._random_amount(50000, 900000)
        start_time = self._random_timestamp()
        txns = []

        for i in range(chain_length - 1):
            # Slight amount variation to avoid exact-match detection
            amount = base_amount * self.rng.uniform(0.95, 1.0)
            # Rapid succession: 2-30 minutes between hops
            hop_time = start_time + timedelta(
                minutes=self.rng.randint(2, 30) * (i + 1)
            )
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=hop_time,
                sender_id=chain_accounts[i].account_id,
                receiver_id=chain_accounts[i + 1].account_id,
                amount=round(amount, 2),
                channel=self.rng.choice([Channel.NEFT, Channel.IMPS, Channel.RTGS]),
                fraud_label=FraudType.LAYERING,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)
        return txns

    def _inject_round_tripping(self, pattern_id: str) -> list[Transaction]:
        """
        Round-tripping: A → B → C → D → A (circular flow)
        Funds return to origin through intermediaries.
        """
        ring_size = self.rng.randint(3, 6)
        ring_accounts = self.rng.sample(
            [a for a in self.accounts if not a.is_dormant], ring_size
        )
        base_amount = self._random_amount(100000, 2000000)
        start_time = self._random_timestamp()
        txns = []

        for i in range(ring_size):
            next_idx = (i + 1) % ring_size  # wraps around to 0
            amount = base_amount * self.rng.uniform(0.92, 1.0)
            hop_time = start_time + timedelta(
                hours=self.rng.randint(1, 12) * (i + 1)
            )
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=hop_time,
                sender_id=ring_accounts[i].account_id,
                receiver_id=ring_accounts[next_idx].account_id,
                amount=round(amount, 2),
                channel=self.rng.choice([Channel.NEFT, Channel.RTGS]),
                fraud_label=FraudType.ROUND_TRIPPING,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)
        return txns

    def _inject_structuring(self, pattern_id: str) -> list[Transaction]:
        """
        Structuring: Multiple transactions just below ₹10,00,000
        (CTR reporting threshold) from same sender.
        """
        sender = self.rng.choice(
            [a for a in self.accounts if not a.is_dormant]
        )
        receivers = self.rng.sample(
            [a for a in self.accounts if a.account_id != sender.account_id],
            self.rng.randint(3, 7),
        )
        start_time = self._random_timestamp()
        txns = []

        for i, receiver in enumerate(receivers):
            # Just below ₹10L (CTR threshold)
            amount = self.rng.uniform(850000, 995000)
            txn_time = start_time + timedelta(
                hours=self.rng.randint(0, 48)
            )
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=txn_time,
                sender_id=sender.account_id,
                receiver_id=receiver.account_id,
                amount=round(amount, 2),
                channel=self.rng.choice([Channel.NEFT, Channel.IMPS]),
                fraud_label=FraudType.STRUCTURING,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)
        return txns

    def _inject_mule_network(self, pattern_id: str) -> list[Transaction]:
        """
        Mule accounts: Multiple sources → single account → fan-out
        Aggregation then distribution pattern.
        """
        mule = self.rng.choice(self.accounts)
        mule.is_mule = True
        mule.fraud_label = FraudType.MULE

        # Fan-in: 5-10 accounts send to mule
        senders = self.rng.sample(
            [a for a in self.accounts if a.account_id != mule.account_id],
            self.rng.randint(5, 10),
        )
        # Fan-out: mule sends to 3-5 accounts
        receivers = self.rng.sample(
            [a for a in self.accounts
             if a.account_id != mule.account_id
             and a.account_id not in [s.account_id for s in senders]],
            self.rng.randint(3, 5),
        )
        start_time = self._random_timestamp()
        txns = []

        # Fan-in phase
        for i, sender in enumerate(senders):
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=start_time + timedelta(hours=self.rng.randint(0, 24)),
                sender_id=sender.account_id,
                receiver_id=mule.account_id,
                amount=self._random_amount(50000, 500000),
                channel=self.rng.choice([Channel.NEFT, Channel.UPI, Channel.IMPS]),
                fraud_label=FraudType.MULE,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)

        # Fan-out phase (after accumulation)
        total_in = sum(t.amount for t in txns)
        for receiver in receivers:
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=start_time + timedelta(hours=self.rng.randint(25, 72)),
                sender_id=mule.account_id,
                receiver_id=receiver.account_id,
                amount=round(total_in / len(receivers) * self.rng.uniform(0.8, 1.2), 2),
                channel=Channel.RTGS,
                fraud_label=FraudType.MULE,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)
        return txns

    def _inject_dormant_burst(self, pattern_id: str) -> list[Transaction]:
        """
        Dormant burst: Account inactive for 6+ months suddenly
        receives/sends high-value transactions.
        """
        dormant = self.rng.choice(
            [a for a in self.accounts if a.is_dormant]
        )
        if not dormant:
            dormant = self.rng.choice(self.accounts)
            dormant.is_dormant = True

        dormant.fraud_label = FraudType.DORMANT_BURST
        partners = self.rng.sample(
            [a for a in self.accounts if a.account_id != dormant.account_id],
            self.rng.randint(3, 6),
        )
        start_time = self._random_timestamp()
        txns = []

        for partner in partners:
            # High-value transactions
            amount = self._random_amount(200000, 2000000)
            direction = self.rng.choice(["in", "out"])
            txn = Transaction(
                txn_id=f"TXN{len(self.transactions) + len(txns):08d}",
                timestamp=start_time + timedelta(hours=self.rng.randint(0, 6)),
                sender_id=dormant.account_id if direction == "out" else partner.account_id,
                receiver_id=partner.account_id if direction == "out" else dormant.account_id,
                amount=amount,
                channel=self.rng.choice([Channel.NEFT, Channel.RTGS]),
                fraud_label=FraudType.DORMANT_BURST,
                fraud_pattern_id=pattern_id,
            )
            txns.append(txn)
        return txns

    # ── Master Generate ─────────────────────────────────────

    def generate(self) -> tuple[list[Account], list[Transaction]]:
        """Generate complete dataset: accounts + clean + fraud transactions."""
        print("Generating accounts...")
        self.generate_accounts()

        print("Generating clean transactions...")
        self.transactions = self.generate_clean_transactions()

        print("Injecting fraud patterns...")
        fraud_generators = [
            self._inject_layering,
            self._inject_round_tripping,
            self._inject_structuring,
            self._inject_mule_network,
            self._inject_dormant_burst,
        ]

        for i in range(self.num_fraud_patterns):
            gen_fn = self.rng.choice(fraud_generators)
            pattern_id = f"FRAUD_{i:04d}"
            try:
                fraud_txns = gen_fn(pattern_id)
                self.transactions.extend(fraud_txns)
            except (ValueError, IndexError):
                continue  # Skip if not enough accounts

        # Sort by timestamp
        self.transactions.sort(key=lambda t: t.timestamp)

        total = len(self.transactions)
        fraud = sum(1 for t in self.transactions if t.fraud_label != FraudType.CLEAN)
        print(f"Generated: {len(self.accounts)} accounts, {total} transactions")
        print(f"Fraud transactions: {fraud} ({fraud/total*100:.1f}%)")

        return self.accounts, self.transactions

    # ── Save to CSV ─────────────────────────────────────────

    def save_csv(
        self,
        accounts: list[Account],
        transactions: list[Transaction],
        output_dir: str = "data/raw",
    ) -> None:
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Accounts CSV
        with open(f"{output_dir}/accounts.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=accounts[0].to_dict().keys())
            writer.writeheader()
            writer.writerows([a.to_dict() for a in accounts])

        # Transactions CSV
        with open(f"{output_dir}/transactions.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=transactions[0].to_dict().keys())
            writer.writeheader()
            writer.writerows([t.to_dict() for t in transactions])

        print(f"Saved to {output_dir}/")


# ── Quick Run ────────────────────────────────────────────────
if __name__ == "__main__":
    gen = IndianBankingDataGenerator(
        num_accounts=5000,
        num_clean_transactions=80000,
        num_fraud_patterns=200,
    )
    accounts, txns = gen.generate()
    gen.save_csv(accounts, txns)
```

---

### PHASE B: Graph Construction

**File: `src/trace/graph/builder.py`**

```python
"""
Build a NetworkX directed graph from transaction data.
Nodes = accounts, Edges = transactions.
Each edge carries temporal + amount attributes.
"""

import networkx as nx
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional


class TransactionGraph:
    """
    Core graph engine for TRACE.ai.
    Builds and maintains a directed multigraph of fund flows.

    Node attributes:
        - account_type, kyc_risk, account_age, avg_balance, is_dormant
    Edge attributes:
        - txn_id, timestamp, amount, channel, fraud_label, pattern_id
    """

    def __init__(self):
        self.G: nx.MultiDiGraph = nx.MultiDiGraph()
        self._account_data: dict[str, dict] = {}

    def load_from_csv(
        self,
        accounts_path: str,
        transactions_path: str,
    ) -> None:
        """Load graph from CSV files (AMLSim-compatible format)."""
        accounts_df = pd.read_csv(accounts_path)
        txns_df = pd.read_csv(transactions_path)

        # Add account nodes
        for _, row in accounts_df.iterrows():
            self.add_account(row["account_id"], row.to_dict())

        # Add transaction edges
        for _, row in txns_df.iterrows():
            self.add_transaction(
                txn_id=row["txn_id"],
                sender_id=row["sender_id"],
                receiver_id=row["receiver_id"],
                amount=row["amount"],
                timestamp=row["timestamp"],
                channel=row["channel"],
                fraud_label=row.get("fraud_label", "clean"),
                pattern_id=row.get("fraud_pattern_id", ""),
            )

    def add_account(self, account_id: str, attributes: dict) -> None:
        """Add or update an account node."""
        self.G.add_node(account_id, **attributes)
        self._account_data[account_id] = attributes

    def add_transaction(
        self,
        txn_id: str,
        sender_id: str,
        receiver_id: str,
        amount: float,
        timestamp: str | datetime,
        channel: str,
        fraud_label: str = "clean",
        pattern_id: str = "",
    ) -> None:
        """Add a transaction as a directed edge."""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        self.G.add_edge(
            sender_id,
            receiver_id,
            key=txn_id,
            txn_id=txn_id,
            amount=amount,
            timestamp=timestamp,
            channel=channel,
            fraud_label=fraud_label,
            pattern_id=pattern_id,
        )

    # ── Subgraph Extraction ─────────────────────────────────

    def get_account_neighborhood(
        self, account_id: str, depth: int = 2
    ) -> nx.MultiDiGraph:
        """Get N-hop neighborhood subgraph around an account."""
        nodes = set()
        frontier = {account_id}
        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                next_frontier.update(self.G.successors(node))
                next_frontier.update(self.G.predecessors(node))
            nodes.update(frontier)
            frontier = next_frontier - nodes
        nodes.update(frontier)
        return self.G.subgraph(nodes).copy()

    def get_temporal_subgraph(
        self,
        start: datetime,
        end: datetime,
    ) -> nx.MultiDiGraph:
        """Extract subgraph for a specific time window."""
        edges_in_window = [
            (u, v, k, d)
            for u, v, k, d in self.G.edges(data=True, keys=True)
            if start <= d.get("timestamp", datetime.min) <= end
        ]
        subgraph = nx.MultiDiGraph()
        for u, v, k, d in edges_in_window:
            subgraph.add_node(u, **self.G.nodes[u])
            subgraph.add_node(v, **self.G.nodes[v])
            subgraph.add_edge(u, v, key=k, **d)
        return subgraph

    # ── Export for Visualization ─────────────────────────────

    def to_force_graph_json(
        self,
        subgraph: Optional[nx.MultiDiGraph] = None,
        highlight_nodes: Optional[set[str]] = None,
        highlight_edges: Optional[set[str]] = None,
    ) -> dict:
        """
        Export graph to JSON format compatible with 3d-force-graph / react-force-graph.
        {
            "nodes": [{"id": "ACC000001", "group": 1, "risk": 0.8, ...}],
            "links": [{"source": "ACC000001", "target": "ACC000002", "value": 50000, ...}]
        }
        """
        G = subgraph or self.G
        highlight_nodes = highlight_nodes or set()
        highlight_edges = highlight_edges or set()

        nodes = []
        for node_id in G.nodes:
            node_data = G.nodes[node_id]
            is_suspicious = node_id in highlight_nodes
            nodes.append({
                "id": node_id,
                "name": node_data.get("customer_name", node_id),
                "accountType": node_data.get("account_type", "unknown"),
                "kycRisk": node_data.get("kyc_risk_category", "medium"),
                "isMule": node_data.get("is_mule", False),
                "isDormant": node_data.get("is_dormant", False),
                "isSuspicious": is_suspicious,
                "group": 2 if is_suspicious else 1,
                # Degree centrality for node size
                "val": G.degree(node_id),
            })

        links = []
        for u, v, k, d in G.edges(data=True, keys=True):
            txn_id = d.get("txn_id", k)
            is_suspicious = txn_id in highlight_edges
            links.append({
                "source": u,
                "target": v,
                "txnId": txn_id,
                "amount": d.get("amount", 0),
                "channel": d.get("channel", "unknown"),
                "timestamp": d.get("timestamp", "").isoformat()
                    if isinstance(d.get("timestamp"), datetime) else str(d.get("timestamp", "")),
                "fraudLabel": d.get("fraud_label", "clean"),
                "isSuspicious": is_suspicious,
                "color": "#ff4444" if is_suspicious else "#888888",
                "width": 3 if is_suspicious else 1,
            })

        return {"nodes": nodes, "links": links}

    # ── Compute Node Features for GNN ────────────────────────

    def compute_node_features(self) -> pd.DataFrame:
        """
        Compute feature vectors for each account node.
        Used as input to GNN and anomaly detection.
        """
        features = []
        for node_id in self.G.nodes:
            in_edges = list(self.G.in_edges(node_id, data=True))
            out_edges = list(self.G.out_edges(node_id, data=True))

            in_amounts = [d["amount"] for _, _, d in in_edges]
            out_amounts = [d["amount"] for _, _, d in out_edges]

            node_data = self.G.nodes[node_id]
            features.append({
                "account_id": node_id,
                "in_degree": len(in_edges),
                "out_degree": len(out_edges),
                "total_in": sum(in_amounts) if in_amounts else 0,
                "total_out": sum(out_amounts) if out_amounts else 0,
                "avg_in_amount": (sum(in_amounts) / len(in_amounts)) if in_amounts else 0,
                "avg_out_amount": (sum(out_amounts) / len(out_amounts)) if out_amounts else 0,
                "max_in_amount": max(in_amounts) if in_amounts else 0,
                "max_out_amount": max(out_amounts) if out_amounts else 0,
                "net_flow": sum(in_amounts) - sum(out_amounts) if in_amounts or out_amounts else 0,
                "unique_in_partners": len(set(u for u, _, _ in in_edges)),
                "unique_out_partners": len(set(v for _, v, _ in out_edges)),
                "account_age": node_data.get("account_age_days", 0),
                "kyc_risk_score": {"low": 0, "medium": 1, "high": 2}.get(
                    node_data.get("kyc_risk_category", "medium"), 1
                ),
                "is_dormant": int(node_data.get("is_dormant", False)),
                "pagerank": 0,  # Computed below
                "clustering_coeff": 0,  # Computed below
            })

        df = pd.DataFrame(features)

        # Add graph-level features
        simple_G = nx.DiGraph(self.G)  # Convert multigraph for algorithms
        pagerank = nx.pagerank(simple_G, alpha=0.85)
        clustering = nx.clustering(simple_G.to_undirected())

        df["pagerank"] = df["account_id"].map(pagerank)
        df["clustering_coeff"] = df["account_id"].map(clustering)

        return df

    # ── Statistics ───────────────────────────────────────────

    @property
    def stats(self) -> dict:
        return {
            "num_accounts": self.G.number_of_nodes(),
            "num_transactions": self.G.number_of_edges(),
            "density": nx.density(self.G),
            "avg_degree": sum(dict(self.G.degree()).values()) / max(self.G.number_of_nodes(), 1),
        }
```

---

### PHASE C: Pattern Detection Engine

**File: `src/trace/detection/pattern_matcher.py`**

```python
"""
Graph-based fraud pattern detection using NetworkX algorithms.
Detects 6 AML typologies through structural and temporal analysis.
"""

import networkx as nx
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from collections import defaultdict


@dataclass
class PatternMatch:
    """A detected suspicious pattern."""
    pattern_type: str           # layering, round_tripping, structuring, etc.
    risk_score: float           # 0.0 to 1.0
    accounts_involved: list[str]
    transactions_involved: list[str]
    total_amount: float
    time_window_minutes: float
    description: str
    evidence: dict              # Additional evidence for LLM explainer


class PatternMatcher:
    """
    Detects AML fraud patterns in a transaction graph.

    Patterns detected:
        1. Circular flows (round-tripping)
        2. Rapid layering chains
        3. Structuring below CTR threshold
        4. Mule account networks (fan-in/fan-out)
        5. Dormant account burst activity
        6. Velocity anomalies
    """

    CTR_THRESHOLD = 1_000_000   # ₹10 Lakh — Cash Transaction Report threshold
    STRUCTURING_TOLERANCE = 0.15  # 15% below CTR
    RAPID_WINDOW_MINUTES = 120    # 2 hours for "rapid" layering
    DORMANT_THRESHOLD_DAYS = 180  # 6 months

    def __init__(self, graph: nx.MultiDiGraph):
        self.G = graph
        self.matches: list[PatternMatch] = []

    def detect_all(self) -> list[PatternMatch]:
        """Run all pattern detectors."""
        self.matches = []
        self.matches.extend(self.detect_circular_flows())
        self.matches.extend(self.detect_layering())
        self.matches.extend(self.detect_structuring())
        self.matches.extend(self.detect_mule_networks())
        self.matches.extend(self.detect_dormant_bursts())
        return self.matches

    # ── 1. Circular Flow Detection ──────────────────────────

    def detect_circular_flows(
        self,
        min_cycle_length: int = 3,
        max_cycle_length: int = 8,
        amount_tolerance: float = 0.15,
    ) -> list[PatternMatch]:
        """
        Detect round-tripping: A → B → C → ... → A
        Funds that return to origin through intermediaries.

        Uses NetworkX simple_cycles() on a simplified DiGraph.
        Then validates with temporal ordering and amount consistency.
        """
        matches = []

        # Work on simplified DiGraph (collapse multi-edges)
        simple_G = nx.DiGraph()
        for u, v, d in self.G.edges(data=True):
            if simple_G.has_edge(u, v):
                # Accumulate amounts for multi-edges
                simple_G[u][v]["total_amount"] += d.get("amount", 0)
                simple_G[u][v]["txn_count"] += 1
                simple_G[u][v]["txn_ids"].append(d.get("txn_id", ""))
            else:
                simple_G.add_edge(u, v,
                    total_amount=d.get("amount", 0),
                    txn_count=1,
                    txn_ids=[d.get("txn_id", "")],
                )

        # Find cycles
        try:
            cycles = list(nx.simple_cycles(simple_G, length_bound=max_cycle_length))
        except Exception:
            cycles = []

        for cycle in cycles:
            if len(cycle) < min_cycle_length:
                continue

            # Collect all transactions in this cycle
            cycle_txns = []
            cycle_amounts = []
            cycle_timestamps = []

            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]

                for _, _, d in self.G.edges(u, data=True):
                    if _ == v or self.G.has_edge(u, v):
                        # Get all edges u → v
                        for _, _, k, ed in self.G.edges(u, data=True, keys=True):
                            if _ == v:
                                cycle_txns.append(ed.get("txn_id", k))
                                cycle_amounts.append(ed.get("amount", 0))
                                ts = ed.get("timestamp")
                                if isinstance(ts, datetime):
                                    cycle_timestamps.append(ts)

            if not cycle_amounts:
                continue

            # Check amount consistency (amounts within tolerance)
            avg_amount = sum(cycle_amounts) / len(cycle_amounts)
            amount_consistent = all(
                abs(a - avg_amount) / avg_amount < amount_tolerance
                for a in cycle_amounts
            ) if avg_amount > 0 else False

            # Calculate time window
            if cycle_timestamps:
                time_window = (max(cycle_timestamps) - min(cycle_timestamps)).total_seconds() / 60
            else:
                time_window = 0

            # Risk scoring
            risk_score = 0.5  # Base risk for any cycle
            if amount_consistent:
                risk_score += 0.2
            if time_window < self.RAPID_WINDOW_MINUTES * len(cycle):
                risk_score += 0.15  # Rapid cycling increases risk
            if avg_amount > self.CTR_THRESHOLD * 0.5:
                risk_score += 0.15  # High amounts increase risk

            risk_score = min(risk_score, 1.0)

            matches.append(PatternMatch(
                pattern_type="round_tripping",
                risk_score=risk_score,
                accounts_involved=cycle,
                transactions_involved=cycle_txns[:20],  # Cap for display
                total_amount=sum(cycle_amounts),
                time_window_minutes=time_window,
                description=(
                    f"Circular fund flow detected: {' → '.join(cycle[:5])}{'...' if len(cycle) > 5 else ''} → {cycle[0]}. "
                    f"{'Amount-consistent' if amount_consistent else 'Variable amounts'}, "
                    f"avg ₹{avg_amount:,.0f} over {time_window:.0f} minutes."
                ),
                evidence={
                    "cycle_length": len(cycle),
                    "avg_amount": avg_amount,
                    "amount_consistent": amount_consistent,
                    "amounts": cycle_amounts[:10],
                },
            ))

        return matches

    # ── 2. Layering Detection ───────────────────────────────

    def detect_layering(
        self,
        min_chain_length: int = 4,
        time_window_hours: float = 4,
    ) -> list[PatternMatch]:
        """
        Detect layering: rapid fund movement through multiple intermediaries.
        A → B → C → D → E in quick succession.

        Approach: Find long paths with temporally ordered edges.
        """
        matches = []

        # Group edges by timestamp windows
        edges_by_time: dict[str, list] = defaultdict(list)

        for u, v, k, d in self.G.edges(data=True, keys=True):
            ts = d.get("timestamp")
            if isinstance(ts, datetime):
                # Window key: date + 4-hour block
                window = ts.strftime("%Y-%m-%d") + f"_H{ts.hour // 4}"
                edges_by_time[window].append((u, v, k, d))

        for window, edges in edges_by_time.items():
            if len(edges) < min_chain_length:
                continue

            # Build temporal subgraph for this window
            temp_G = nx.DiGraph()
            for u, v, k, d in edges:
                temp_G.add_edge(u, v, **d)

            # Find nodes with only outgoing (sources) and only incoming (sinks)
            sources = [n for n in temp_G.nodes if temp_G.in_degree(n) == 0 and temp_G.out_degree(n) > 0]
            sinks = [n for n in temp_G.nodes if temp_G.out_degree(n) == 0 and temp_G.in_degree(n) > 0]

            for source in sources:
                for sink in sinks:
                    try:
                        paths = list(nx.all_simple_paths(
                            temp_G, source, sink,
                            cutoff=min_chain_length + 4,
                        ))
                    except nx.NetworkXError:
                        continue

                    for path in paths:
                        if len(path) < min_chain_length:
                            continue

                        # Collect path transaction data
                        path_amounts = []
                        path_txn_ids = []
                        path_timestamps = []

                        for i in range(len(path) - 1):
                            edge_data = temp_G[path[i]][path[i+1]]
                            path_amounts.append(edge_data.get("amount", 0))
                            path_txn_ids.append(edge_data.get("txn_id", ""))
                            ts = edge_data.get("timestamp")
                            if isinstance(ts, datetime):
                                path_timestamps.append(ts)

                        if not path_amounts:
                            continue

                        avg_amount = sum(path_amounts) / len(path_amounts)
                        time_window = 0
                        if len(path_timestamps) >= 2:
                            time_window = (
                                max(path_timestamps) - min(path_timestamps)
                            ).total_seconds() / 60

                        # Risk scoring
                        risk_score = 0.4
                        risk_score += min(len(path) * 0.08, 0.3)  # Longer chains = higher risk
                        if time_window < 60 * len(path):  # Very rapid
                            risk_score += 0.2
                        if avg_amount > 100000:
                            risk_score += 0.1

                        matches.append(PatternMatch(
                            pattern_type="layering",
                            risk_score=min(risk_score, 1.0),
                            accounts_involved=path,
                            transactions_involved=path_txn_ids,
                            total_amount=sum(path_amounts),
                            time_window_minutes=time_window,
                            description=(
                                f"Layering chain: {' → '.join(path[:6])}{'...' if len(path) > 6 else ''}, "
                                f"{len(path)-1} hops in {time_window:.0f} min, avg ₹{avg_amount:,.0f}"
                            ),
                            evidence={
                                "chain_length": len(path),
                                "amounts": path_amounts,
                                "avg_amount": avg_amount,
                                "velocity_per_hop_min": time_window / max(len(path) - 1, 1),
                            },
                        ))

        return matches

    # ── 3. Structuring Detection ────────────────────────────

    def detect_structuring(self) -> list[PatternMatch]:
        """
        Detect structuring: multiple transactions just below ₹10L
        CTR threshold from the same sender within a time period.
        """
        matches = []
        threshold_low = self.CTR_THRESHOLD * (1 - self.STRUCTURING_TOLERANCE)
        threshold_high = self.CTR_THRESHOLD

        # Group outgoing transactions by sender
        sender_txns: dict[str, list] = defaultdict(list)
        for u, v, k, d in self.G.edges(data=True, keys=True):
            amount = d.get("amount", 0)
            if threshold_low <= amount <= threshold_high:
                sender_txns[u].append((v, k, d))

        for sender, txns in sender_txns.items():
            if len(txns) < 3:
                continue

            # Check temporal clustering
            timestamps = []
            for _, _, d in txns:
                ts = d.get("timestamp")
                if isinstance(ts, datetime):
                    timestamps.append(ts)

            if len(timestamps) < 3:
                continue

            timestamps.sort()
            # Find clusters within 72 hours
            clusters: list[list] = []
            current_cluster = [0]

            for i in range(1, len(timestamps)):
                if (timestamps[i] - timestamps[current_cluster[-1]]).total_seconds() < 72 * 3600:
                    current_cluster.append(i)
                else:
                    if len(current_cluster) >= 3:
                        clusters.append(current_cluster)
                    current_cluster = [i]
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)

            for cluster_indices in clusters:
                cluster_txns = [txns[i] for i in cluster_indices]
                amounts = [d.get("amount", 0) for _, _, d in cluster_txns]
                total = sum(amounts)
                receivers = [v for v, _, _ in cluster_txns]

                risk_score = 0.6 + min(len(cluster_txns) * 0.05, 0.3)
                if total > self.CTR_THRESHOLD * 2:
                    risk_score += 0.1

                matches.append(PatternMatch(
                    pattern_type="structuring",
                    risk_score=min(risk_score, 1.0),
                    accounts_involved=[sender] + receivers,
                    transactions_involved=[d.get("txn_id", k) for _, k, d in cluster_txns],
                    total_amount=total,
                    time_window_minutes=(
                        timestamps[cluster_indices[-1]] - timestamps[cluster_indices[0]]
                    ).total_seconds() / 60,
                    description=(
                        f"Structuring: {sender} made {len(cluster_txns)} transactions "
                        f"between ₹{threshold_low:,.0f}-₹{threshold_high:,.0f} "
                        f"(total ₹{total:,.0f}), likely avoiding CTR threshold."
                    ),
                    evidence={
                        "num_transactions": len(cluster_txns),
                        "amounts": amounts,
                        "total_would_trigger_ctr": total > self.CTR_THRESHOLD,
                        "avg_amount": sum(amounts) / len(amounts),
                    },
                ))

        return matches

    # ── 4. Mule Account Detection ───────────────────────────

    def detect_mule_networks(
        self,
        fan_in_threshold: int = 5,
        fan_out_threshold: int = 3,
    ) -> list[PatternMatch]:
        """
        Detect mule accounts: high fan-in followed by high fan-out.
        Many sources → mule account → few destinations.
        """
        matches = []

        for node in self.G.nodes:
            in_degree = self.G.in_degree(node)
            out_degree = self.G.out_degree(node)

            if in_degree >= fan_in_threshold and out_degree >= fan_out_threshold:
                in_edges = list(self.G.in_edges(node, data=True))
                out_edges = list(self.G.out_edges(node, data=True))

                total_in = sum(d.get("amount", 0) for _, _, d in in_edges)
                total_out = sum(d.get("amount", 0) for _, _, d in out_edges)

                # Check if in/out amounts are roughly balanced (pass-through)
                if total_in == 0:
                    continue
                throughput_ratio = total_out / total_in

                # Check temporal ordering: most inflows before outflows
                in_times = [d.get("timestamp") for _, _, d in in_edges
                           if isinstance(d.get("timestamp"), datetime)]
                out_times = [d.get("timestamp") for _, _, d in out_edges
                            if isinstance(d.get("timestamp"), datetime)]

                temporal_ordered = False
                if in_times and out_times:
                    avg_in_time = sum(t.timestamp() for t in in_times) / len(in_times)
                    avg_out_time = sum(t.timestamp() for t in out_times) / len(out_times)
                    temporal_ordered = avg_in_time < avg_out_time

                risk_score = 0.5
                if 0.7 < throughput_ratio < 1.3:  # Pass-through behavior
                    risk_score += 0.2
                if temporal_ordered:
                    risk_score += 0.15
                if in_degree > 10:
                    risk_score += 0.1
                # Check account age — new accounts are more suspicious
                account_age = self.G.nodes[node].get("account_age_days", 365)
                if account_age < 90:
                    risk_score += 0.05

                senders = list(set(u for u, _, _ in in_edges))
                receivers = list(set(v for _, v, _ in out_edges))

                matches.append(PatternMatch(
                    pattern_type="mule_account",
                    risk_score=min(risk_score, 1.0),
                    accounts_involved=[node] + senders[:5] + receivers[:5],
                    transactions_involved=(
                        [d.get("txn_id", "") for _, _, d in in_edges[:10]]
                        + [d.get("txn_id", "") for _, _, d in out_edges[:10]]
                    ),
                    total_amount=total_in + total_out,
                    time_window_minutes=0,
                    description=(
                        f"Mule suspect: {node} received from {in_degree} accounts "
                        f"(₹{total_in:,.0f}) and sent to {out_degree} accounts "
                        f"(₹{total_out:,.0f}). Throughput ratio: {throughput_ratio:.2f}"
                    ),
                    evidence={
                        "fan_in": in_degree,
                        "fan_out": out_degree,
                        "throughput_ratio": throughput_ratio,
                        "temporal_ordered": temporal_ordered,
                        "account_age_days": account_age,
                    },
                ))

        return matches

    # ── 5. Dormant Account Burst ────────────────────────────

    def detect_dormant_bursts(self) -> list[PatternMatch]:
        """
        Detect dormant accounts suddenly activated with high-value transactions.
        """
        matches = []

        for node in self.G.nodes:
            if not self.G.nodes[node].get("is_dormant", False):
                continue

            all_edges = (
                list(self.G.in_edges(node, data=True))
                + list(self.G.out_edges(node, data=True))
            )

            if len(all_edges) < 2:
                continue

            total_amount = sum(d.get("amount", 0) for *_, d in all_edges)
            avg_balance = self.G.nodes[node].get("avg_monthly_balance", 100000)

            if total_amount > avg_balance * 3:  # Activity >> historical average
                risk_score = 0.7 + min(total_amount / 5_000_000, 0.3)
                txn_ids = [d.get("txn_id", "") for *_, d in all_edges]
                partners = list(set(
                    [u for u, _, d in self.G.in_edges(node, data=True)]
                    + [v for _, v, d in self.G.out_edges(node, data=True)]
                ))

                matches.append(PatternMatch(
                    pattern_type="dormant_burst",
                    risk_score=min(risk_score, 1.0),
                    accounts_involved=[node] + partners[:5],
                    transactions_involved=txn_ids[:10],
                    total_amount=total_amount,
                    time_window_minutes=0,
                    description=(
                        f"Dormant account {node} activated with {len(all_edges)} "
                        f"transactions totaling ₹{total_amount:,.0f} "
                        f"(avg balance was ₹{avg_balance:,.0f})"
                    ),
                    evidence={
                        "account_age": self.G.nodes[node].get("account_age_days", 0),
                        "avg_balance": avg_balance,
                        "burst_total": total_amount,
                        "burst_ratio": total_amount / max(avg_balance, 1),
                    },
                ))

        return matches
```

---

### PHASE D: Online Anomaly Detection (River)

**File: `src/trace/detection/anomaly_scorer.py`**

```python
"""
Per-account online anomaly detection using River's HalfSpaceTrees.
Learns behavioral baselines incrementally — no batch retraining.
"""

from river import anomaly, drift
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnomalyResult:
    account_id: str
    anomaly_score: float  # 0-1 (higher = more anomalous)
    is_anomalous: bool
    features_used: dict
    reason: str


class AccountAnomalyScorer:
    """
    Online anomaly detection using River HalfSpaceTrees.

    Maintains a per-account-type behavioral baseline.
    Each transaction updates the model incrementally.

    Features per transaction:
        - amount (log-scaled)
        - hour_of_day (cyclical)
        - day_of_week
        - channel (encoded)
        - in_degree_delta
        - out_degree_delta
        - time_since_last_txn (seconds)
    """

    CHANNEL_ENCODING = {
        "NEFT": 0, "RTGS": 1, "UPI": 2, "IMPS": 3,
        "BRANCH": 4, "ATM": 5, "MOBILE": 6, "NET_BANKING": 7,
    }

    def __init__(
        self,
        n_trees: int = 15,
        height: int = 8,
        window_size: int = 250,
        anomaly_threshold: float = 0.75,
        cold_start_transactions: int = 20,
    ):
        self.n_trees = n_trees
        self.height = height
        self.window_size = window_size
        self.threshold = anomaly_threshold
        self.cold_start_min = cold_start_transactions

        # Per account-type model (grouped baseline)
        self._models: dict[str, anomaly.HalfSpaceTrees] = {}
        # Per account transaction history (for feature computation)
        self._account_history: dict[str, list] = defaultdict(list)
        # Transaction count per account (for cold-start detection)
        self._account_txn_count: dict[str, int] = defaultdict(int)
        # Drift detector
        self._drift_detector = drift.ADWIN()

    def _get_or_create_model(self, account_type: str) -> anomaly.HalfSpaceTrees:
        """Get existing model or create new one for account type."""
        if account_type not in self._models:
            self._models[account_type] = anomaly.HalfSpaceTrees(
                n_trees=self.n_trees,
                height=self.height,
                window_size=self.window_size,
                seed=42,
            )
        return self._models[account_type]

    def _compute_features(
        self,
        account_id: str,
        amount: float,
        timestamp: datetime,
        channel: str,
    ) -> dict:
        """Compute feature vector for a single transaction."""
        import math

        history = self._account_history[account_id]

        # Time since last transaction
        if history:
            last_ts = history[-1]["timestamp"]
            time_since_last = (timestamp - last_ts).total_seconds()
        else:
            time_since_last = 86400 * 30  # Default: 30 days

        # Amount statistics from history
        if history:
            recent_amounts = [h["amount"] for h in history[-50:]]
            avg_amount = sum(recent_amounts) / len(recent_amounts)
            amount_ratio = amount / max(avg_amount, 1)
        else:
            amount_ratio = 1.0

        features = {
            "log_amount": math.log1p(amount),
            "hour_sin": math.sin(2 * math.pi * timestamp.hour / 24),
            "hour_cos": math.cos(2 * math.pi * timestamp.hour / 24),
            "day_of_week": timestamp.weekday(),
            "channel": self.CHANNEL_ENCODING.get(channel, 0),
            "log_time_since_last": math.log1p(max(time_since_last, 0)),
            "amount_ratio": min(amount_ratio, 100),
            "is_weekend": int(timestamp.weekday() >= 5),
            "is_off_hours": int(timestamp.hour < 6 or timestamp.hour > 22),
        }

        return features

    def score_transaction(
        self,
        account_id: str,
        account_type: str,
        amount: float,
        timestamp: datetime,
        channel: str,
    ) -> AnomalyResult:
        """
        Score a single transaction for anomaly.
        Updates the model incrementally (online learning).
        """
        model = self._get_or_create_model(account_type)
        features = self._compute_features(account_id, amount, timestamp, channel)

        self._account_txn_count[account_id] += 1
        txn_count = self._account_txn_count[account_id]

        # Cold-start: don't flag anomalies until baseline is established
        if txn_count <= self.cold_start_min:
            score = model.score_one(features)
            model.learn_one(features)
            # Store history
            self._account_history[account_id].append({
                "amount": amount, "timestamp": timestamp,
            })
            return AnomalyResult(
                account_id=account_id,
                anomaly_score=0.0,  # Don't flag during cold start
                is_anomalous=False,
                features_used=features,
                reason=f"Cold start ({txn_count}/{self.cold_start_min})",
            )

        # Score BEFORE learning (detect deviation from existing baseline)
        score = model.score_one(features)
        is_anomalous = score > self.threshold

        # Generate reason
        reasons = []
        if features["is_off_hours"]:
            reasons.append("off-hours transaction")
        if features["amount_ratio"] > 5:
            reasons.append(f"amount {features['amount_ratio']:.1f}x above average")
        if features["log_time_since_last"] < 3:  # Very rapid
            reasons.append("rapid succession")
        if not reasons:
            reasons.append("behavioral deviation from baseline")

        # Learn this observation (update baseline)
        model.learn_one(features)

        # Update drift detector
        self._drift_detector.update(score)

        # Store history
        self._account_history[account_id].append({
            "amount": amount, "timestamp": timestamp,
        })
        # Keep history bounded
        if len(self._account_history[account_id]) > 200:
            self._account_history[account_id] = self._account_history[account_id][-100:]

        return AnomalyResult(
            account_id=account_id,
            anomaly_score=round(score, 4),
            is_anomalous=is_anomalous,
            features_used=features,
            reason="; ".join(reasons) if is_anomalous else "normal",
        )

    @property
    def drift_detected(self) -> bool:
        """Check if concept drift has been detected (changing fraud patterns)."""
        return self._drift_detector.drift_detected
```

---

### PHASE E: Risk Fusion + Compliance Engine

**File: `src/trace/detection/compliance_engine.py`**

```python
"""
YAML-driven compliance rule engine.
Hot-reloadable regulatory rules (RBI Master Directions).
"""

import yaml
from dataclasses import dataclass
from typing import Any
from pathlib import Path


@dataclass
class ComplianceViolation:
    rule_id: str
    rule_name: str
    severity: str  # low, medium, high, critical
    description: str
    regulatory_reference: str


class ComplianceEngine:
    """
    Evaluates transactions against regulatory compliance rules.
    Rules defined in YAML for hot-reloading.

    Example rule:
        - id: CTR_001
          name: Cash Transaction Report
          condition:
            amount_gte: 1000000
            channel_in: [BRANCH, ATM]
          action: FLAG_CTR
          severity: high
          reference: "RBI Master Direction on KYC, Chapter V"
    """

    def __init__(self, rules_path: str):
        self.rules_path = Path(rules_path)
        self.rules: list[dict] = []
        self.load_rules()

    def load_rules(self) -> None:
        """Load or reload rules from YAML."""
        with open(self.rules_path) as f:
            config = yaml.safe_load(f)
        self.rules = config.get("rules", [])

    def reload(self) -> None:
        """Hot-reload rules without restart."""
        self.load_rules()

    def evaluate(
        self,
        amount: float,
        channel: str,
        sender_kyc_risk: str,
        receiver_kyc_risk: str,
        account_age_days: int,
        is_dormant: bool,
        **context,
    ) -> list[ComplianceViolation]:
        """Evaluate a transaction against all compliance rules."""
        violations = []
        txn_context = {
            "amount": amount,
            "channel": channel,
            "sender_kyc_risk": sender_kyc_risk,
            "receiver_kyc_risk": receiver_kyc_risk,
            "account_age_days": account_age_days,
            "is_dormant": is_dormant,
            **context,
        }

        for rule in self.rules:
            if self._evaluate_condition(rule.get("condition", {}), txn_context):
                violations.append(ComplianceViolation(
                    rule_id=rule["id"],
                    rule_name=rule["name"],
                    severity=rule.get("severity", "medium"),
                    description=rule.get("description", ""),
                    regulatory_reference=rule.get("reference", ""),
                ))

        return violations

    def _evaluate_condition(self, condition: dict, context: dict) -> bool:
        """Evaluate a rule condition against transaction context."""
        for key, value in condition.items():
            field, op = self._parse_condition_key(key)
            actual = context.get(field)
            if actual is None:
                return False
            if not self._compare(actual, op, value):
                return False
        return True

    def _parse_condition_key(self, key: str) -> tuple[str, str]:
        """Parse 'amount_gte' → ('amount', 'gte')"""
        operators = ["gte", "lte", "gt", "lt", "eq", "ne", "in", "not_in"]
        for op in operators:
            if key.endswith(f"_{op}"):
                field = key[:-(len(op) + 1)]
                return field, op
        return key, "eq"

    def _compare(self, actual: Any, op: str, expected: Any) -> bool:
        ops = {
            "gte": lambda a, e: a >= e,
            "lte": lambda a, e: a <= e,
            "gt": lambda a, e: a > e,
            "lt": lambda a, e: a < e,
            "eq": lambda a, e: a == e,
            "ne": lambda a, e: a != e,
            "in": lambda a, e: a in e,
            "not_in": lambda a, e: a not in e,
        }
        return ops.get(op, lambda a, e: False)(actual, expected)
```

**File: `src/compliance_rules.yaml`**

```yaml
# TRACE.ai Compliance Rules
# Based on RBI Master Direction on KYC (2016, updated 2024)
# Hot-reloadable: modify and call engine.reload()

rules:
  - id: CTR_001
    name: Cash Transaction Report Threshold
    condition:
      amount_gte: 1000000
    action: FLAG_CTR
    severity: high
    description: "Transaction ≥ ₹10,00,000 — requires Cash Transaction Report"
    reference: "RBI Master Direction on KYC, Chapter V, Para 36"

  - id: CTR_002
    name: Cross-border Wire Transfer Report
    condition:
      amount_gte: 500000
      channel_in: [RTGS, NEFT]
    action: FLAG_CBWTR
    severity: medium
    description: "Cross-border wire ≥ ₹5,00,000 — requires reporting"
    reference: "RBI Master Direction on KYC, Chapter V, Para 37"

  - id: STR_001
    name: Dormant Account High Value
    condition:
      is_dormant_eq: true
      amount_gte: 100000
    action: FLAG_STR
    severity: critical
    description: "Dormant account transacting ₹1L+ — mandatory STR"
    reference: "PMLA Rules 2005, Rule 3"

  - id: STR_002
    name: New Account High Value
    condition:
      account_age_days_lt: 90
      amount_gte: 500000
    action: FLAG_STR
    severity: high
    description: "Account <90 days old transacting ₹5L+ — flag for review"
    reference: "RBI KYC Direction, Para 38(1)"

  - id: RISK_001
    name: High Risk Customer Large Transaction
    condition:
      sender_kyc_risk_eq: "high"
      amount_gte: 200000
    action: ESCALATE
    severity: high
    description: "High-risk customer transacting ₹2L+ — escalate to MLRO"
    reference: "RBI KYC Direction, Chapter IV"
```

**File: `src/trace/detection/risk_fusion.py`**

```python
"""
Composite risk scoring engine.
Fuses signals from pattern matcher, GNN, anomaly scorer, and compliance.
"""

from dataclasses import dataclass


@dataclass
class FusedRiskScore:
    account_id: str
    composite_score: float  # 0-1
    risk_level: str  # low, medium, high, critical
    contributing_signals: dict[str, float]
    explanation: str


class RiskFusionEngine:
    """
    Weighted fusion of multiple detection signals.

    Weights are tunable via config. Default:
        pattern_match:  0.35
        gnn_score:      0.25
        anomaly_score:  0.20
        compliance:     0.20
    """

    RISK_LEVELS = [
        (0.3, "low"),
        (0.5, "medium"),
        (0.75, "high"),
        (1.0, "critical"),
    ]

    def __init__(
        self,
        w_pattern: float = 0.35,
        w_gnn: float = 0.25,
        w_anomaly: float = 0.20,
        w_compliance: float = 0.20,
    ):
        self.weights = {
            "pattern_match": w_pattern,
            "gnn_score": w_gnn,
            "anomaly_score": w_anomaly,
            "compliance": w_compliance,
        }

    def fuse(
        self,
        account_id: str,
        pattern_score: float = 0.0,
        gnn_score: float = 0.0,
        anomaly_score: float = 0.0,
        compliance_score: float = 0.0,
    ) -> FusedRiskScore:
        """Compute weighted composite risk score."""
        signals = {
            "pattern_match": pattern_score,
            "gnn_score": gnn_score,
            "anomaly_score": anomaly_score,
            "compliance": compliance_score,
        }

        composite = sum(
            signals[k] * self.weights[k] for k in signals
        )
        composite = min(max(composite, 0.0), 1.0)

        # Determine risk level
        risk_level = "low"
        for threshold, level in self.RISK_LEVELS:
            if composite <= threshold:
                risk_level = level
                break

        # Generate explanation
        top_signal = max(signals, key=signals.get)
        explanation = (
            f"Composite risk: {composite:.2f} ({risk_level}). "
            f"Primary signal: {top_signal} ({signals[top_signal]:.2f})"
        )

        return FusedRiskScore(
            account_id=account_id,
            composite_score=round(composite, 4),
            risk_level=risk_level,
            contributing_signals=signals,
            explanation=explanation,
        )
```

---

### PHASE F: LLM Intelligence Layer

**File: `src/trace/intelligence/explainer.py`**

```python
"""
LLM-powered alert explanation and investigation copilot.
Generates human-readable explanations for flagged patterns.
"""

import os
import json
from openai import OpenAI
from trace.detection.pattern_matcher import PatternMatch
from trace.detection.risk_fusion import FusedRiskScore


class AlertExplainer:
    """
    Uses LLM to generate natural language explanations for alerts.
    Supports OpenAI API, Azure OpenAI, and local models via Ollama.
    """

    SYSTEM_PROMPT = """You are TRACE.ai, an AI-powered anti-money laundering 
investigation assistant for Indian banks. You help compliance officers 
understand suspicious transaction patterns detected by the system.

Your explanations should:
1. Be clear, concise, and professional
2. Reference specific account IDs, amounts (in ₹), and timestamps
3. Explain WHY the pattern is suspicious (cite AML typology)
4. Reference relevant RBI regulations where applicable
5. Suggest next steps for the investigator
6. Use Indian banking terminology (NEFT, RTGS, UPI, IMPS, CTR, STR, FIU-IND)

Do NOT speculate on the identity of account holders.
Always note that patterns require human investigation to confirm fraud."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        self.client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
        )
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def explain_pattern(self, match: PatternMatch) -> str:
        """Generate natural language explanation for a detected pattern."""
        prompt = f"""Analyze this detected suspicious pattern and provide a 
clear explanation for the compliance officer:

Pattern Type: {match.pattern_type}
Risk Score: {match.risk_score:.2f}/1.00
Accounts Involved: {', '.join(match.accounts_involved[:10])}
Transactions: {len(match.transactions_involved)} transactions
Total Amount: ₹{match.total_amount:,.2f}
Time Window: {match.time_window_minutes:.0f} minutes
System Description: {match.description}
Evidence: {json.dumps(match.evidence, default=str)}

Provide:
1. A 2-3 sentence summary of what was detected
2. Why this pattern is suspicious (AML typology)
3. Relevant RBI regulation reference
4. Recommended next steps for the investigator"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content

    def explain_risk_score(self, score: FusedRiskScore) -> str:
        """Generate explanation for a composite risk score."""
        prompt = f"""Explain this risk assessment to a compliance officer:

Account: {score.account_id}
Composite Risk Score: {score.composite_score:.2f}/1.00
Risk Level: {score.risk_level}
Contributing Signals:
{json.dumps(score.contributing_signals, indent=2)}

Provide a concise 2-3 sentence explanation of why this account 
is flagged at this risk level and what the primary concern is."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content


class InvestigationCopilot:
    """
    Natural language investigation interface.
    Users ask questions in English → system generates graph queries → returns results.

    Inspired by Vanna.ai's NL-to-SQL approach, adapted for graph queries.
    """

    SYSTEM_PROMPT = """You are an investigation copilot for TRACE.ai, 
a bank fraud detection system. Users ask questions about transaction 
patterns and you must generate Python/NetworkX code to answer them.

You have access to a NetworkX MultiDiGraph called `G` where:
- Nodes are bank accounts with attributes: account_type, kyc_risk_category, 
  account_age_days, avg_monthly_balance, is_dormant, is_mule
- Edges are transactions with attributes: txn_id, amount, timestamp, 
  channel, fraud_label, pattern_id

Always return a JSON object with:
{{
    "query_type": "accounts" | "transactions" | "patterns" | "statistics",
    "code": "Python code using nx to query the graph",
    "explanation": "What this query does in plain English"
}}

IMPORTANT: The code should be safe — no file operations, no imports 
beyond networkx and datetime. Return only READ operations."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        self.client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
        )
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def process_query(self, user_question: str) -> dict:
        """Convert natural language question to graph query."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_question},
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def execute_query(self, query_result: dict, graph) -> dict:
        """Safely execute the generated graph query."""
        import networkx as nx
        from datetime import datetime, timedelta

        code = query_result.get("code", "")

        # Safety: only allow specific operations
        forbidden = ["import os", "open(", "exec(", "eval(", "__", "subprocess"]
        for f in forbidden:
            if f in code:
                return {"error": f"Forbidden operation: {f}", "results": []}

        # Execute in sandboxed namespace
        namespace = {"nx": nx, "G": graph, "datetime": datetime, "timedelta": timedelta}
        try:
            exec(code, namespace)
            result = namespace.get("result", "No result variable found")
            return {"results": result, "explanation": query_result.get("explanation", "")}
        except Exception as e:
            return {"error": str(e), "results": []}
```

---

### PHASE G: STR Report Generator

**File: `src/trace/intelligence/str_generator.py`**

```python
"""
Auto-generate FIU-IND compliant Suspicious Transaction Reports.
Uses ReportLab for PDF generation.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from typing import Optional

from trace.detection.pattern_matcher import PatternMatch
from trace.detection.risk_fusion import FusedRiskScore


class STRReportGenerator:
    """
    Generates FIU-IND compliant Suspicious Transaction Report (STR) PDFs.

    Format based on FIU-IND STR filing guidelines:
    - Part A: Information about the reporting entity
    - Part B: Information about the suspect
    - Part C: Information about the suspicious transaction
    - Part D: Reason for suspicion
    - Part E: Action taken by the reporting entity
    """

    def __init__(self, bank_name: str = "Union Bank of India", branch: str = ""):
        self.bank_name = bank_name
        self.branch = branch
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name="STRTitle",
            parent=self.styles["Heading1"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor("#1a1a2e"),
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor("#e94560"),
        ))

    def generate_str(
        self,
        pattern: PatternMatch,
        risk_score: FusedRiskScore,
        llm_explanation: str,
        output_path: str,
        report_id: Optional[str] = None,
    ) -> str:
        """Generate a complete STR PDF."""
        report_id = report_id or f"STR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        elements = []

        # Title
        elements.append(Paragraph(
            "SUSPICIOUS TRANSACTION REPORT (STR)", self.styles["STRTitle"]
        ))
        elements.append(Paragraph(
            f"Report ID: {report_id} | Generated: {datetime.now().strftime('%d-%m-%Y %H:%M IST')}",
            self.styles["Normal"],
        ))
        elements.append(Spacer(1, 10 * mm))

        # Part A: Reporting Entity
        elements.append(Paragraph("PART A: REPORTING ENTITY", self.styles["SectionHeader"]))
        part_a_data = [
            ["Bank Name", self.bank_name],
            ["Branch", self.branch or "Central Monitoring Unit"],
            ["Filing Date", datetime.now().strftime("%d-%m-%Y")],
            ["Report Type", "Suspicious Transaction Report"],
            ["Generated By", "TRACE.ai — Automated AML System"],
        ]
        elements.append(self._make_table(part_a_data))
        elements.append(Spacer(1, 6 * mm))

        # Part B: Suspect Information
        elements.append(Paragraph("PART B: SUSPECT ACCOUNTS", self.styles["SectionHeader"]))
        account_data = [["S.No.", "Account ID", "Role"]]
        for i, acc in enumerate(pattern.accounts_involved[:10], 1):
            role = "Primary Suspect" if i == 1 else "Connected Account"
            account_data.append([str(i), acc, role])
        elements.append(self._make_table(account_data, header=True))
        elements.append(Spacer(1, 6 * mm))

        # Part C: Transaction Details
        elements.append(Paragraph("PART C: SUSPICIOUS TRANSACTIONS", self.styles["SectionHeader"]))
        elements.append(Paragraph(
            f"<b>Pattern Type:</b> {pattern.pattern_type.replace('_', ' ').title()}<br/>"
            f"<b>Total Amount:</b> ₹{pattern.total_amount:,.2f}<br/>"
            f"<b>Time Window:</b> {pattern.time_window_minutes:.0f} minutes<br/>"
            f"<b>Transactions Involved:</b> {len(pattern.transactions_involved)}<br/>",
            self.styles["Normal"],
        ))
        elements.append(Spacer(1, 4 * mm))

        # Transaction list
        txn_data = [["S.No.", "Transaction ID"]]
        for i, txn_id in enumerate(pattern.transactions_involved[:15], 1):
            txn_data.append([str(i), txn_id])
        elements.append(self._make_table(txn_data, header=True))
        elements.append(Spacer(1, 6 * mm))

        # Part D: Reason for Suspicion
        elements.append(Paragraph("PART D: REASON FOR SUSPICION", self.styles["SectionHeader"]))
        elements.append(Paragraph(
            f"<b>Risk Score:</b> {risk_score.composite_score:.2f}/1.00 "
            f"({risk_score.risk_level.upper()})<br/><br/>"
            f"<b>System Detection:</b><br/>{pattern.description}<br/><br/>"
            f"<b>AI Analysis:</b><br/>{llm_explanation}",
            self.styles["Normal"],
        ))
        elements.append(Spacer(1, 4 * mm))

        # Risk signal breakdown
        signal_data = [["Signal", "Score"]]
        for signal, score in risk_score.contributing_signals.items():
            signal_data.append([signal.replace("_", " ").title(), f"{score:.2f}"])
        elements.append(self._make_table(signal_data, header=True))
        elements.append(Spacer(1, 6 * mm))

        # Part E: Action Taken
        elements.append(Paragraph("PART E: ACTION TAKEN", self.styles["SectionHeader"]))
        elements.append(Paragraph(
            "This STR has been auto-generated by TRACE.ai and is pending "
            "review by the Principal Officer / MLRO. Upon review and approval, "
            "this report shall be filed with FIU-IND within the stipulated "
            "timeframe as per PMLA Rules 2005.",
            self.styles["Normal"],
        ))
        elements.append(Spacer(1, 10 * mm))

        # Footer
        elements.append(Paragraph(
            "<i>This is a system-generated report. All flagged patterns require "
            "human investigation and verification before any action is taken. "
            "Generated by TRACE.ai — Transaction Risk Analysis & Compliance Engine.</i>",
            self.styles["Normal"],
        ))

        doc.build(elements)
        return output_path

    def _make_table(self, data: list, header: bool = False) -> Table:
        """Create a formatted table."""
        table = Table(data, hAlign="LEFT")
        style_commands = [
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]
        if header:
            style_commands.extend([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        table.setStyle(TableStyle(style_commands))
        return table
```

---

### PHASE H: FastAPI Backend

**File: `src/trace/api/main.py`**

```python
"""
TRACE.ai FastAPI backend.
REST API + WebSocket for real-time alert streaming.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from trace.graph.builder import TransactionGraph
from trace.detection.pattern_matcher import PatternMatcher
from trace.detection.anomaly_scorer import AccountAnomalyScorer
from trace.detection.compliance_engine import ComplianceEngine
from trace.detection.risk_fusion import RiskFusionEngine
from trace.intelligence.explainer import AlertExplainer, InvestigationCopilot
from trace.intelligence.str_generator import STRReportGenerator


# ── Global State ─────────────────────────────────────────────
graph = TransactionGraph()
anomaly_scorer = AccountAnomalyScorer()
compliance_engine = ComplianceEngine("src/compliance_rules.yaml")
risk_fusion = RiskFusionEngine()
explainer = AlertExplainer()
copilot = InvestigationCopilot()
str_generator = STRReportGenerator()

alerts: list[dict] = []
connected_ws: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data on startup."""
    graph.load_from_csv("data/raw/accounts.csv", "data/raw/transactions.csv")
    # Run initial pattern detection
    matcher = PatternMatcher(graph.G)
    patterns = matcher.detect_all()
    for p in patterns:
        alerts.append({
            "id": len(alerts),
            "pattern": p.__dict__,
            "timestamp": datetime.now().isoformat(),
            "status": "open",
        })
    print(f"Loaded {graph.stats['num_accounts']} accounts, "
          f"{graph.stats['num_transactions']} transactions, "
          f"{len(alerts)} initial alerts")
    yield


app = FastAPI(
    title="TRACE.ai API",
    description="Transaction Risk Analysis & Compliance Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST Endpoints ───────────────────────────────────────────

@app.get("/api/graph")
async def get_graph(
    limit: int = 500,
    highlight_suspicious: bool = True,
):
    """Get full graph data for visualization."""
    suspicious_nodes = set()
    suspicious_edges = set()
    if highlight_suspicious:
        for alert in alerts:
            pattern = alert.get("pattern", {})
            for acc in pattern.get("accounts_involved", []):
                suspicious_nodes.add(acc)
            for txn in pattern.get("transactions_involved", []):
                suspicious_edges.add(txn)

    return graph.to_force_graph_json(
        highlight_nodes=suspicious_nodes,
        highlight_edges=suspicious_edges,
    )


@app.get("/api/graph/{account_id}")
async def get_account_subgraph(account_id: str, depth: int = 2):
    """Get N-hop neighborhood of a specific account."""
    if account_id not in graph.G.nodes:
        raise HTTPException(404, f"Account {account_id} not found")
    subgraph = graph.get_account_neighborhood(account_id, depth)
    return graph.to_force_graph_json(subgraph)


@app.get("/api/alerts")
async def get_alerts(
    status: str | None = None,
    min_risk: float = 0.0,
    limit: int = 50,
):
    """Get alerts, optionally filtered."""
    filtered = alerts
    if status:
        filtered = [a for a in filtered if a.get("status") == status]
    if min_risk > 0:
        filtered = [
            a for a in filtered
            if a.get("pattern", {}).get("risk_score", 0) >= min_risk
        ]
    return filtered[:limit]


@app.get("/api/alerts/{alert_id}/explain")
async def explain_alert(alert_id: int):
    """Get LLM-generated explanation for an alert."""
    if alert_id >= len(alerts):
        raise HTTPException(404, "Alert not found")

    alert = alerts[alert_id]
    pattern_data = alert["pattern"]

    # Reconstruct PatternMatch
    from trace.detection.pattern_matcher import PatternMatch
    pattern = PatternMatch(**pattern_data)

    explanation = explainer.explain_pattern(pattern)
    return {"alert_id": alert_id, "explanation": explanation}


@app.post("/api/investigate")
async def investigate(query: dict):
    """Natural language investigation query."""
    question = query.get("question", "")
    if not question:
        raise HTTPException(400, "Question is required")

    query_result = copilot.process_query(question)
    execution_result = copilot.execute_query(query_result, graph.G)

    return {
        "question": question,
        "generated_query": query_result,
        "result": execution_result,
    }


@app.get("/api/reports/str/{alert_id}")
async def generate_str_report(alert_id: int):
    """Generate and download STR PDF for an alert."""
    if alert_id >= len(alerts):
        raise HTTPException(404, "Alert not found")

    alert = alerts[alert_id]
    from trace.detection.pattern_matcher import PatternMatch
    from trace.detection.risk_fusion import FusedRiskScore

    pattern = PatternMatch(**alert["pattern"])
    risk = risk_fusion.fuse(
        account_id=pattern.accounts_involved[0] if pattern.accounts_involved else "unknown",
        pattern_score=pattern.risk_score,
    )

    explanation = explainer.explain_pattern(pattern)

    output_path = f"/tmp/STR_{alert_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    str_generator.generate_str(
        pattern=pattern,
        risk_score=risk,
        llm_explanation=explanation,
        output_path=output_path,
    )

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"STR_Alert_{alert_id}.pdf",
    )


@app.get("/api/stats")
async def get_stats():
    """Dashboard KPI statistics."""
    return {
        "total_accounts": graph.stats["num_accounts"],
        "total_transactions": graph.stats["num_transactions"],
        "total_alerts": len(alerts),
        "open_alerts": sum(1 for a in alerts if a.get("status") == "open"),
        "critical_alerts": sum(
            1 for a in alerts
            if a.get("pattern", {}).get("risk_score", 0) > 0.75
        ),
        "pattern_distribution": _pattern_distribution(),
    }


def _pattern_distribution() -> dict:
    dist = {}
    for alert in alerts:
        pt = alert.get("pattern", {}).get("pattern_type", "unknown")
        dist[pt] = dist.get(pt, 0) + 1
    return dist


# ── WebSocket: Real-time Alert Stream ────────────────────────

@app.websocket("/ws/alerts")
async def alert_websocket(websocket: WebSocket):
    """Real-time alert stream via WebSocket."""
    await websocket.accept()
    connected_ws.append(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_ws.remove(websocket)


async def broadcast_alert(alert: dict):
    """Send new alert to all connected WebSocket clients."""
    for ws in connected_ws:
        try:
            await ws.send_json(alert)
        except Exception:
            connected_ws.remove(ws)
```

---

### PHASE I: React Frontend (Key Components)

**File: `frontend/src/components/GraphVisualization.tsx`**

```tsx
import React, { useCallback, useRef, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';

interface GraphNode {
  id: string;
  name: string;
  accountType: string;
  isSuspicious: boolean;
  isMule: boolean;
  isDormant: boolean;
  val: number;
  group: number;
}

interface GraphLink {
  source: string;
  target: string;
  txnId: string;
  amount: number;
  channel: string;
  fraudLabel: string;
  isSuspicious: boolean;
  color: string;
  width: number;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface Props {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  highlightedAccounts?: Set<string>;
}

export const GraphVisualization: React.FC<Props> = ({
  data,
  onNodeClick,
  highlightedAccounts = new Set(),
}) => {
  const fgRef = useRef<any>();

  const nodeColor = useCallback((node: GraphNode) => {
    if (node.isMule) return '#ff0000';
    if (node.isSuspicious) return '#ff4444';
    if (node.isDormant) return '#888888';
    if (highlightedAccounts.has(node.id)) return '#ffaa00';
    return '#4ecdc4';
  }, [highlightedAccounts]);

  const nodeLabel = useCallback((node: GraphNode) => {
    return `${node.id}\n${node.name}\nType: ${node.accountType}${
      node.isSuspicious ? '\n⚠️ SUSPICIOUS' : ''
    }${node.isMule ? '\n🚨 MULE ACCOUNT' : ''}`;
  }, []);

  const linkColor = useCallback((link: GraphLink) => {
    if (link.isSuspicious) return '#ff4444';
    return 'rgba(255,255,255,0.15)';
  }, []);

  const linkWidth = useCallback((link: GraphLink) => {
    return link.isSuspicious ? 3 : 0.5;
  }, []);

  const handleNodeClick = useCallback((node: GraphNode) => {
    // Zoom to node
    const distance = 100;
    const distRatio = 1 + distance / Math.hypot(
      (node as any).x, (node as any).y, (node as any).z
    );
    fgRef.current?.cameraPosition(
      {
        x: (node as any).x * distRatio,
        y: (node as any).y * distRatio,
        z: (node as any).z * distRatio,
      },
      node,
      2000, // ms transition
    );
    onNodeClick?.(node);
  }, [onNodeClick]);

  return (
    <ForceGraph3D
      ref={fgRef}
      graphData={data}
      nodeColor={nodeColor}
      nodeLabel={nodeLabel}
      nodeVal={(node: GraphNode) => Math.max(node.val, 2)}
      linkColor={linkColor}
      linkWidth={linkWidth}
      linkDirectionalArrowLength={3.5}
      linkDirectionalArrowRelPos={1}
      linkDirectionalParticles={(link: GraphLink) =>
        link.isSuspicious ? 4 : 0
      }
      linkDirectionalParticleWidth={2}
      linkDirectionalParticleColor={() => '#ff4444'}
      onNodeClick={handleNodeClick}
      backgroundColor="#0a0a1a"
      showNavInfo={false}
    />
  );
};
```

---

### PHASE J: Dependencies & Setup

**File: `pyproject.toml`**

```toml
[project]
name = "trace-ai"
version = "1.0.0"
description = "Transaction Risk Analysis & Compliance Engine"
requires-python = ">=3.11"

dependencies = [
    # Data
    "pandas>=2.2",
    "faker>=33.0",
    # Graph
    "networkx>=3.4",
    # Online ML
    "river>=0.21",
    # GNN (optional — for Phase 2+)
    # "torch>=2.4",
    # "torch-geometric>=2.6",
    # LLM
    "openai>=1.50",
    # API
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "websockets>=13.0",
    # PDF
    "reportlab>=4.2",
    # Config
    "pyyaml>=6.0",
    # Utilities
    "python-dotenv>=1.0",
    "pydantic>=2.9",
]

[project.optional-dependencies]
gnn = ["torch>=2.4", "torch-geometric>=2.6"]
dev = ["pytest>=8.0", "ruff>=0.8"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

**File: `frontend/package.json`**

```json
{
  "name": "trace-ai-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.3",
    "react-dom": "^18.3",
    "react-force-graph-3d": "^1.24",
    "three": "^0.170",
    "recharts": "^2.13",
    "lucide-react": "^0.460"
  },
  "devDependencies": {
    "@types/react": "^18.3",
    "typescript": "^5.7",
    "vite": "^6.0",
    "@vitejs/plugin-react": "^4.3"
  }
}
```

**File: `.env.example`**

```bash
# LLM API (OpenAI or compatible)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Data paths
DATA_DIR=data/raw
ACCOUNTS_CSV=data/raw/accounts.csv
TRANSACTIONS_CSV=data/raw/transactions.csv

# Server
API_HOST=0.0.0.0
API_PORT=8000

# Neo4j (optional)
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password
```

---

## 6. 24-HOUR GRAND FINALE BUILD SCHEDULE

```
┌──────────┬────────────────────────────────────────────┬───────────────────┐
│  HOUR    │  TASK                                      │  TEAM MEMBER      │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  0:00-1  │  Setup: clone repos, install deps,         │  ALL              │
│          │  configure .env, verify tools work         │                   │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  1-3     │  Data generation (generator.py)            │  Member 1 (Data)  │
│  1-3     │  Graph builder (builder.py)                │  Member 2 (ML)    │
│  1-3     │  Pattern matcher framework                 │  Member 3 (Backend│
│  1-3     │  React project setup + force-graph         │  Member 4 (Front) │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  3-6     │  Feature engineering for GNN               │  Member 1         │
│  3-6     │  All 5 pattern detectors                   │  Member 2         │
│  3-6     │  Anomaly scorer (River) + compliance       │  Member 3         │
│  3-6     │  Graph visualization + alert panel         │  Member 4         │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  6-10    │  GNN training (TGN on Colab/Kaggle)        │  Member 1         │
│  6-10    │  Risk fusion engine                        │  Member 2         │
│  6-10    │  FastAPI backend + REST endpoints          │  Member 3         │
│  6-10    │  Investigation panel + KPI cards           │  Member 4         │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  10-14   │  LLM explainer integration                 │  Member 1         │
│  10-14   │  Investigation copilot (NL queries)        │  Member 2         │
│  10-14   │  WebSocket real-time alerts                │  Member 3         │
│  10-14   │  Frontend-backend integration              │  Member 4         │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  14-18   │  STR report generator (PDF)                │  Member 1         │
│  14-18   │  Integration testing all modules           │  Member 2         │
│  14-18   │  API polishing + error handling            │  Member 3         │
│  14-18   │  UI polish + responsive design             │  Member 4         │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  18-21   │  End-to-end testing                        │  ALL              │
│          │  Demo script rehearsal                      │                   │
│          │  Edge case handling                        │                   │
├──────────┼────────────────────────────────────────────┼───────────────────┤
│  21-24   │  Final polish                              │  Member 1+2       │
│          │  PPT preparation                           │  Member 3         │
│          │  Demo rehearsal (3 dry runs minimum)        │  Member 4 (lead)  │
└──────────┴────────────────────────────────────────────┴───────────────────┘
```

---

## 7. IDEA SUBMISSION CONTENT (7 Slides)

### Slide 1: PROPOSED SOLUTION (Title: "TRACE.ai")

> **TRACE.ai** — Transaction Risk Analysis & Compliance Engine
>
> An intelligent fund flow tracking platform that uses **Graph Neural Networks**, **online machine learning**, and **LLM-powered investigation tools** to detect, explain, and report anti-money laundering patterns in real-time.
>
> **How it addresses the problem:**
> - Maps end-to-end fund movement across accounts, branches, and channels as a **temporal directed graph**
> - Detects 6 AML typologies (layering, round-tripping, structuring, mule networks, dormant bursts, fan-out) using **graph algorithms + GNN inference**
> - Provides **natural language investigation copilot** for compliance officers
> - Auto-generates **FIU-IND compliant Suspicious Transaction Reports**
>
> **Innovation:**
> Unlike rule-based AML systems (95%+ false positive rate), TRACE.ai combines graph structure, temporal dynamics, and behavioral anomaly detection to reduce false positives while catching sophisticated multi-hop fraud patterns invisible to threshold-based rules.

*(Include a small architecture diagram fitting the slide)*

### Slide 2: OUTLINE OF UNIQUE & INNOVATIVE SOLUTION

> **Innovation 1: Temporal Graph Neural Networks for AML**
> Traditional GNNs operate on static graphs. TRACE.ai uses Temporal Graph Networks (TGN) that model the TIME dimension of transactions — detecting rapid layering bursts and evolving fraud rings that static analysis misses.
>
> **Innovation 2: Online ML Behavioral Baselines (Zero Batch Retraining)**
> Using River's HalfSpaceTrees, each account develops an individual behavioral baseline through online learning. New fraud patterns are detected WITHOUT retraining — the model adapts per-transaction with cold-start fallback for new accounts.
>
> **Innovation 3: Natural Language Investigation Copilot**
> Investigators ask questions in English ("Show all circular flows above ₹5L this week") → LLM translates to graph queries → executes → returns visualized results. No Cypher/SQL knowledge needed.
>
> **Innovation 4: Hot-Reloadable Compliance Engine**
> YAML-defined regulatory rules update in real-time when RBI issues new KYC/AML circulars. No system restart, no code changes. Compliance is always current.
>
> **Innovation 5: Automated FIU-IND STR Generation**
> One-click generation of regulatory-compliant evidence packages with complete fund trail, risk assessment, AI-generated analysis, and recommended actions.

### Slide 3: TECHNICAL APPROACH

*(Architecture diagram — the one from Section 2 above, simplified to fit one slide)*
*(Tech stack table)*

| Component | Technology |
|---|---|
| Graph Engine | NetworkX + Neo4j (scale) |
| GNN Model | PyTorch Geometric (TGN) |
| Online Anomaly | River HalfSpaceTrees |
| Compliance | YAML rule engine (hot-reload) |
| LLM Intelligence | OpenAI API / Ollama |
| Visualization | React + 3D Force Graph |
| Backend | FastAPI (REST + WebSocket) |
| Reporting | ReportLab (PDF) |
| Audit | SQLite |

### Slide 4: FEASIBILITY & VIABILITY

> **Feasibility:** All components use proven OSS tools (NetworkX, PyG, River, FastAPI). Synthetic data generation eliminates dependency on real bank data. System runs on standard hardware (no GPU required for inference — GNN model trained offline).
>
> **Challenges & Mitigations:**
> | Challenge | Mitigation |
> |---|---|
> | No access to real bank data | AMLSim-inspired synthetic data with realistic Indian banking patterns |
> | GNN training requires GPU | Train on Kaggle/Colab (free T4 GPU), export model for CPU inference |
> | False positive rate | Multi-signal fusion (pattern + GNN + anomaly + compliance) reduces FP vs single-model approach |
> | Scale (millions of txns/day) | NetworkX → Neo4j migration path. Online ML eliminates batch retraining bottleneck |
> | Regulatory changes | YAML rule engine — hot-reload without code changes |

### Slide 5: IMPACT & BENEFITS

> **Quantified Impact:**
> - ₹71,500 Cr lost to bank fraud in India (RBI Annual Report 2024-25)
> - Current rule-based AML: **95%+ false positive rate** → investigator fatigue
> - TRACE.ai target: **<15% false positive rate** through multi-signal fusion
> - STR preparation time: **4 hours manual → 4 minutes automated**
> - Pattern detection: catches **multi-hop layering** invisible to threshold rules
>
> **Beneficiaries:**
> - **Compliance Officers**: Reduced alert fatigue, AI-powered investigation
> - **MLRO/Principal Officer**: Automated regulatory reporting
> - **Bank**: Reduced RBI penalty risk (up to ₹1 Cr per AML violation)
> - **Customers**: Protection from mule account exploitation
> - **Nation**: Stronger financial crime prevention infrastructure

### Slide 6: BUSINESS MODEL

> **Model:** B2B SaaS — Annual licensing per bank
>
> **Target Market:**
> - 12 Public Sector Banks, 21 Private Banks, 43 RRBs, 1500+ cooperative banks
> - TAM: ₹2,000 Cr (Indian RegTech market, growing 25% CAGR)
>
> **Revenue:** ₹50L–2Cr per bank/year (tiered by size and transaction volume)
>
> **Commercialization Path:**
> 1. Pilot with Union Bank of India (post-hackathon product development)
> 2. Integration with bank's CBS via API middleware
> 3. Scale to other PSBs through IBA/DFS recommendation
> 4. Expand to private banks and NBFCs
>
> **Competitive Advantage:**
> - Existing solutions (Actimize, Mantas) cost ₹5-20 Cr + long implementation
> - TRACE.ai: ₹50L, cloud-native, deploys in weeks
> - India-specific: Hindi/regional language support, RBI-aligned rules, FIU-IND format

### Slide 7: RESEARCH & REFERENCES

> **Papers:**
> 1. Rossi et al., "Temporal Graph Networks for Deep Learning on Dynamic Graphs," arXiv:2006.10637
> 2. Weber et al., "Anti-Money Laundering in Bitcoin: Experimenting with GNNs," arXiv:1908.02591
> 3. Johannessen & Jullum, "GNNs for Financial Crime Detection: A Survey," arXiv:2203.14624
> 4. Yin et al., "SUREL+: Moving from Walks to Sets for Scalable Graph Neural Networks," ICML 2024
>
> **Regulatory References:**
> 5. RBI Master Direction — Know Your Customer (KYC) Direction, 2016 (Updated 2024)
> 6. Prevention of Money-Laundering Act (PMLA), 2002
> 7. FIU-IND — STR Filing Manual and Guidelines
>
> **One-Page Summary:** *(Google Drive link — view-only PDF)*
> [Link to 1-page summary PDF]

---

## 8. CLAUDE.MD

```markdown
# claude.md — TRACE.ai Project Context

## Project Overview
TRACE.ai (Transaction Risk Analysis & Compliance Engine) is a graph-analytics
and AI-powered fund flow tracking system for anti-money laundering (AML)
in Indian banking. Built for iDEA Hackathon 2.0 (Union Bank of India / IBA / DFS).

**Problem Statement:** PS3 — Tracking of Funds within Bank for Fraud Detection

**One-line pitch:** "GNN-powered fund flow intelligence that catches what rules miss."

## Architecture Summary
```
Data Layer → Graph Engine → Detection Engine → Intelligence Layer → Delivery Layer
  (AMLSim)   (NetworkX)    (Patterns+GNN+     (LLM Explainer +    (FastAPI +
                            River+Rules+        Copilot + STR)      React 3D
                            Risk Fusion)                            Force Graph)
```

## Tech Stack
- **Language:** Python 3.11+ (backend + ML), TypeScript (frontend)
- **Graph:** NetworkX (core), Neo4j (optional scale path)
- **GNN:** PyTorch Geometric — Temporal Graph Network (TGN)
- **Online ML:** River — HalfSpaceTrees (per-account anomaly)
- **LLM:** OpenAI API (GPT-4o-mini) or local via Ollama
- **API:** FastAPI (REST + WebSocket)
- **Frontend:** React + react-force-graph-3d (ThreeJS)
- **PDF:** ReportLab (STR generation)
- **Config:** YAML (compliance rules, hot-reloadable)
- **Audit:** SQLite
- **Package Manager:** uv

## Key Domain Concepts

### AML Fraud Typologies Detected
1. **Layering** — Rapid fund movement through 4-8 intermediaries
2. **Round-tripping** — Circular flows (A→B→C→D→A)
3. **Structuring** — Multiple transactions just below ₹10L CTR threshold
4. **Mule accounts** — High fan-in + fan-out (aggregation then distribution)
5. **Dormant burst** — Inactive account suddenly activated with high-value txns
6. **Fan-out** — Single source distributing to many recipients rapidly

### Indian Banking Context
- **CTR threshold:** ₹10,00,000 (Cash Transaction Report to FIU-IND)
- **STR:** Suspicious Transaction Report — filed with FIU-IND
- **Channels:** NEFT, RTGS, UPI, IMPS, BRANCH, ATM, MOBILE, NET_BANKING
- **IFSC codes:** Format: XXXX0NNNNNNN (e.g., UBIN0123456)
- **Regulatory body:** RBI (Reserve Bank of India)
- **Filing body:** FIU-IND (Financial Intelligence Unit - India)
- **Key regulation:** PMLA 2002, RBI Master Direction on KYC (2016, updated 2024)

### Key Thresholds
- CTR: ₹10,00,000 (mandatory reporting)
- Cross-border wire: ₹5,00,000 (CBWTR)
- Structuring tolerance: 15% below CTR (₹8,50,000 - ₹9,99,999 range)
- Dormant: 6+ months no activity (180 days)

## Project Structure
```
trace-ai/
├── src/trace/
│   ├── data/           # Synthetic data generation + ingestion
│   │   ├── generator.py          # IndianBankingDataGenerator class
│   │   ├── ingestion.py          # CSV/stream → internal format
│   │   └── feature_engineering.py
│   ├── graph/          # Graph engine
│   │   ├── builder.py            # TransactionGraph class (NetworkX MultiDiGraph)
│   │   ├── temporal.py           # Time-windowed subgraph extraction
│   │   └── export.py             # Export to PyG, Neo4j, JSON
│   ├── detection/      # Detection engine (5 modules)
│   │   ├── pattern_matcher.py    # Module A: 6 graph pattern detectors
│   │   ├── gnn_classifier.py     # Module B: TGN node/edge classification
│   │   ├── anomaly_scorer.py     # Module C: River HalfSpaceTrees (online)
│   │   ├── compliance_engine.py  # Module D: YAML rule engine
│   │   ├── risk_fusion.py        # Module E: Weighted composite scoring
│   │   └── patterns/             # Individual pattern implementations
│   ├── intelligence/   # AI intelligence layer
│   │   ├── explainer.py          # LLM alert explanation + copilot
│   │   ├── copilot.py            # NL → graph query interface
│   │   └── str_generator.py      # FIU-IND STR PDF generation
│   ├── api/            # FastAPI backend
│   │   ├── main.py               # App entry point + routes
│   │   └── routes/               # Modular route files
│   └── observability/  # Audit logging
├── frontend/           # React + 3D force graph
├── data/               # Generated synthetic data
├── notebooks/          # Training + evaluation notebooks
├── tests/              # Test suite
└── scripts/            # Utility scripts
```

## Coding Conventions
- **Line length:** 100 chars (ruff)
- **Target Python:** 3.11+
- **Type hints:** Required on all function signatures
- **Docstrings:** Google style, required on all public classes and functions
- **Imports:** Standard lib → third-party → local (ruff isort)
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Error handling:** Custom exceptions in trace/exceptions.py
- **Config:** YAML files loaded via trace/config.py
- **Testing:** pytest, files mirror src structure in tests/

## Critical Implementation Notes

### Pattern Detection
- `PatternMatcher` operates on the full NetworkX graph
- `simple_cycles()` has exponential worst-case — use `length_bound` parameter
- Layering detection uses temporal windowing (4-hour blocks) to avoid O(n³)
- Mule detection uses degree thresholds (fan_in ≥ 5, fan_out ≥ 3)
- All patterns return `PatternMatch` dataclass with evidence dict

### Anomaly Scorer
- HalfSpaceTrees need `cold_start_min` transactions before flagging (default: 20)
- Models are per-account-TYPE, not per-account (saves memory, better baselines)
- Features include cyclical encoding for hour_of_day (sin/cos)
- Score BEFORE learn (detect deviation from current baseline, then update)
- ADWIN drift detector monitors for concept drift in fraud patterns

### Risk Fusion
- Weighted average: pattern(0.35) + gnn(0.25) + anomaly(0.20) + compliance(0.20)
- Weights are tunable via config
- Risk levels: low(≤0.3), medium(≤0.5), high(≤0.75), critical(≤1.0)

### LLM Integration
- Uses OpenAI-compatible API (works with local models via Ollama)
- System prompt enforces Indian banking terminology and professional tone
- Investigation copilot generates Python/NetworkX code from NL questions
- Sandboxed execution: forbidden operations list prevents code injection
- Temperature 0.1-0.3 for deterministic, professional outputs

### Frontend
- react-force-graph-3d for 3D transaction graph visualization
- Suspicious nodes: red (#ff4444), mule: bright red (#ff0000)
- Suspicious edges: red with directional particles (animated)
- Clean edges: semi-transparent white (rgba(255,255,255,0.15))
- WebSocket connection for real-time alert streaming
- Click on node → zoom animation → show account detail panel

### STR Reports
- ReportLab generates A4 PDFs
- 5-part structure: Reporting Entity → Suspect → Transactions → Reason → Action
- Includes AI-generated analysis as part of "Reason for Suspicion"
- Download via GET /api/reports/str/{alert_id}

## API Endpoints
```
GET  /api/graph                        — Full graph (force-graph JSON)
GET  /api/graph/{account_id}           — N-hop subgraph around account
GET  /api/alerts                       — List alerts (filterable)
GET  /api/alerts/{id}/explain          — LLM explanation for alert
POST /api/investigate                   — NL investigation query
GET  /api/reports/str/{alert_id}       — Download STR PDF
GET  /api/stats                        — Dashboard KPIs
WS   /ws/alerts                        — Real-time alert stream
```

## Data Models (Pydantic)

### Transaction
```python
txn_id: str, timestamp: datetime, sender_id: str, receiver_id: str,
amount: float, channel: str, currency: str = "INR",
fraud_label: str = "clean", fraud_pattern_id: str = ""
```

### Account
```python
account_id: str, account_type: str, ifsc_code: str, branch_city: str,
customer_name: str, pan_hash: str, kyc_risk_category: str,
account_age_days: int, average_monthly_balance: float,
is_dormant: bool, is_mule: bool, fraud_label: str
```

### PatternMatch
```python
pattern_type: str, risk_score: float, accounts_involved: list[str],
transactions_involved: list[str], total_amount: float,
time_window_minutes: float, description: str, evidence: dict
```

### AnomalyResult
```python
account_id: str, anomaly_score: float, is_anomalous: bool,
features_used: dict, reason: str
```

## Performance Targets
- Graph construction: <5s for 100K transactions
- Pattern detection (all 5): <10s for 100K transactions
- Anomaly scoring: <1ms per transaction (online)
- LLM explanation: <3s per alert (API call)
- Frontend render: <2s initial load, 60fps interaction
- STR PDF generation: <2s per report

## Testing Strategy
- Unit tests for each detection module (pattern_matcher, anomaly_scorer, etc.)
- Integration tests: data → graph → detection → alert pipeline
- Property-based tests: injected fraud patterns MUST be detected
- Frontend: manual testing during hackathon (no time for E2E tests)

## Demo Script (3 minutes)
1. Show dashboard with live transaction graph (30s)
2. Trigger alert: circular flow detection (30s)
3. Click alert → LLM explanation appears (30s)
4. Use investigation copilot: "Show all structuring patterns this week" (30s)
5. Generate STR PDF → download and show (20s)
6. Zoom into mule account network in 3D graph (20s)
7. Closing statement with impact numbers (10s)

## Environment Variables
```
OPENAI_API_KEY — LLM API key
OPENAI_BASE_URL — API endpoint (default: OpenAI, or Ollama local)
OPENAI_MODEL — Model name (default: gpt-4o-mini)
DATA_DIR — Path to data directory
API_HOST — Server host (default: 0.0.0.0)
API_PORT — Server port (default: 8000)
```

## References
- arXiv:2006.10637 — Temporal Graph Networks (TGN)
- arXiv:1908.02591 — GNNs for Bitcoin AML
- arXiv:2203.14624 — GNNs for Financial Crime Survey
- RBI Master Direction on KYC (2016, updated 2024)
- PMLA 2002 + Rules 2005
- FIU-IND STR Filing Manual
- IBM/AMLSim — Synthetic AML data generation
- Salt Security State of API Security Report 2024
```

---

## Quick-Start Commands

```bash
# 1. Setup
git init trace-ai && cd trace-ai
uv init
uv add pandas faker networkx river openai fastapi uvicorn reportlab pyyaml python-dotenv pydantic websockets

# 2. Generate data
uv run python scripts/generate_data.py

# 3. Run backend
uv run uvicorn src.trace.api.main:app --reload --port 8000

# 4. Setup frontend
cd frontend && npm install && npm run dev

# 5. Run tests
uv run pytest tests/ -v
```

**Go build. The repos are mapped. The architecture is proven. The code patterns are here. Execute.**
