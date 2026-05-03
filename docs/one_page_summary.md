
# TRACE.ai — Transaction Risk Analysis & Compliance Engine
**PS3: Tracking of Funds within Bank for Fraud Detection | iDEA Hackathon 2.0**

---

**PROBLEM**

Indian banks lost ₹71,543 Cr to fraud in FY 2024-25 (RBI). Over 95% of banks rely on rule-based AML systems generating 95%+ false positive rates. Sophisticated fraud — multi-hop layering, circular round-tripping, threshold structuring — goes undetected because rules cannot model complex transaction networks. Investigators manually trace fund flows, spending 4–6 hours per Suspicious Transaction Report (STR).

---

**SOLUTION**

TRACE.ai models every banking transaction as an **edge in a dynamic temporal directed graph** (accounts = nodes, transactions = directed edges with amounts and timestamps). Three detection engines run in parallel:

**(1) Graph Pattern Matcher** — NetworkX algorithms detect circular flows (`simple_cycles`), rapid layering chains (temporal path analysis), structuring clusters (amount-threshold analysis), money mule fan-in/fan-out (degree centrality + community detection), and dormant account bursts. Research basis: PPATK typology detection (2025); Elliptic2 subgraph motifs (2024).

**(2) Temporal Graph Neural Network** — PyG-based TGN with edge-centric temporal encoding (ChronoWave-GNN inspired) and attention fusion across structural + temporal features (THG-OAFN inspired). GraphSMOTE handles class imbalance (<1% fraud). Captures evolving fraud ring formation that static methods cannot see. Target: >0.95 AUC, 37% FP reduction vs static baselines.

**(3) Online Anomaly Scorer** — River HalfSpaceTrees build per-account behavioral baselines through streaming online learning — no batch retraining. ADWIN detects concept drift when fraud patterns shift.

All three signals plus a **YAML-driven compliance rule engine** (CTR thresholds, RBI Master Directions, hot-reloadable) are fused into a weighted composite risk score.

---

**INTELLIGENCE LAYER**

- **LLM Alert Explainer:** Every alert includes a natural language explanation grounded in graph evidence
- **NL Investigation Copilot:** Compliance officers query the graph in plain English → instant graph subviews ("Show all circular flows above ₹5L in the last 7 days")
- **Auto-STR Generator:** One-click FIU-IND compliant Suspicious Transaction Report — complete fund trail, risk breakdown, AI narrative. STR prep: 4–6 hours → under 5 minutes

---

**DELIVERY**

React dashboard with 3D force-directed graph visualization (react-force-graph-3d / WebGL), real-time alert streaming (WebSocket), investigator copilot chat, one-click STR download. FastAPI backend. Docker Compose deployment.

---

**KEY INNOVATIONS**

1. Temporal GNN with edge-centric modeling — not static snapshots
2. Online ML baselines — zero batch retraining, per-account streams
3. Natural language investigation — no technical skills required
4. Automated regulatory STR generation — 4 hours to 5 minutes
5. Hot-reloadable compliance rules — RBI circulars deploy in seconds

---

**IMPACT**

| Metric | Current | TRACE.ai Target |
|---|---|---|
| False positive rate | 95%+ | <15% |
| STR preparation time | 4–6 hours | <5 minutes |
| Fraud detection latency | 277 days avg | Real-time |
| AUC (fraud detection) | ~0.70 | >0.95 |

---

**TECH STACK**

Python 3.11 · PyTorch Geometric (TGN) · NetworkX · Neo4j · River · FastAPI · React · LiteLLM (GPT-4o-mini/Claude Haiku) · ReportLab · Docker

**Research basis:** Rossi et al. TGN (2020) · ChronoWave-GNN (2026) · THG-OAFN (PLOS ONE, 2025) · BIS LVPS Anomaly Framework (2023) · Elliptic2 Subgraph Learning (2024) · IBM AMLSim · PPATK Typology Detection (2025)

---

*iDEA Hackathon 2.0 | Union Bank of India / IBA / DFS | PS3 | Submission: March 29, 2026*
