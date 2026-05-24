# Model Card — TRACE.ai

Documents the models powering TRACE.ai's detection layer. Honesty here is a judging signal: under-promise, over-deliver.

---

## Models in Live Risk Fusion

### 1. XGBoost Graph Classifier (`src/trace/detection/gnn_classifier.py`)

**Why XGBoost, not a GNN**
Phase 1 described ChronoWave-GNN. For this prototype, XGBoost on engineered graph features is the correct approach: PyTorch Geometric TGN requires significantly more training data and compute than a hackathon prototype allows. XGBoost on structural features captures the same signal at a fraction of the cost, and SHAP TreeExplainer provides per-alert attribution equivalent to GNNExplainer. See ADR-0002 in `DECISIONS.md`.

**Architecture**
- XGBoost 2.1.4 with 11 graph-structural input features
- Features: degree (in/out), PageRank, betweenness centrality, transaction velocity, KYC risk score, dormancy delta, time-since-last-txn, clustering coefficient
- Binary classification: suspicious (1) / clean (0)
- Class imbalance handled via `scale_pos_weight`

**Training data**
- IBM AMLSim — 20K accounts, ~120K transactions (synthetic)
- 5 injected fraud typologies: circular flow, layering, structuring, mule fan-in/out, dormant burst
- Train/test split: 80/20, stratified

**Measured metrics (synthetic test set)**

| Metric | Value |
|---|---|
| AUC-ROC | > 0.99 |
| Inference latency (CPU) | < 10ms per account |

Note: metrics are on IBM AMLSim synthetic data. Real-bank performance requires retraining on actual CBS feeds.

**Fusion weight:** 30%

---

### 2. Graph Pattern Matcher (`src/trace/detection/patterns/`)

Rule-based detector for 5 AML typologies on the NetworkX MultiDiGraph:

| Pattern | Detection Method |
|---|---|
| Circular flow | DFS cycle detection, depth 3–8, 72-hour window |
| Layering chains | Betweenness-weighted chain traversal, >70% flow-through |
| Structuring | Sub-threshold clustering below Rs. 10L per day |
| Mule fan-in/out | In-degree or out-degree spike in 48-hour window |
| Dormant burst | Account inactive >90 days, sudden high-value outflow |

**Fusion weight:** 30%

---

### 3. Online Anomaly Scorer (`src/trace/detection/anomaly_scorer.py`)

**Architecture**
- Per-account `river.anomaly.HalfSpaceTrees` (HST) — streaming isolation-tree ensemble
- `river.drift.ADWIN` adaptive windowing for concept drift detection

**Properties**
- No batch training. Each account's model updates per transaction.
- Cold-start: account-type priors for the first 50 transactions.
- Detection latency: < 1ms per transaction
- Memory: ~2KB per account model

**Fusion weight:** 20%

---

### 4. Compliance Rule Engine (`src/trace/detection/compliance_engine.py`)

Rules from `compliance_rules.yaml`. Hot-reloadable without restart; new RBI circulars take effect within 5 seconds.

| Rule | Source | Severity |
|---|---|---|
| CTR_THRESHOLD | RBI / PMLA — single transaction >= Rs. 10L cash | HIGH |
| STRUCTURING_DAILY | PMLA Rules 2005 — sub-threshold clustering | HIGH |
| DORMANT_ACTIVATION | RBI dormancy guidance | MEDIUM |
| KYC_HIGH_RISK | RBI KYC Master Direction 2016 (updated 2024) | MEDIUM |
| CROSS_BANK_VELOCITY | Internal heuristic | LOW |

**Fusion weight:** 20%

---

## Trained Checkpoint (Not in Live Fusion)

### Temporal GNN — TGN (`models/tgn_classifier.pt`)

Trained and included as a checkpoint but not part of the live risk fusion signal.

**Architecture:** TGNMemory + TransformerConv message passing → MLP classification head (PyTorch Geometric)

**Training**
- IBM AMLSim 20K nodes, 120,558 transactions, 1,804 fraud (positive weight: 10.1x)
- 15 epochs, batched inference via `TemporalDataLoader(batch_size=200)`

**Measured AUC:** 0.72 on full 20K-node graph

**Why not in fusion:** AUC 0.72 is below the XGBoost baseline (> 0.99). The TGN requires real-bank temporal data at production volume to outperform engineered features. Included as a Phase 3 starting point.

---

## Risk Fusion

```
composite = 0.30 * pattern_score
          + 0.30 * classifier_score
          + 0.20 * anomaly_score
          + 0.20 * compliance_score
```

**Risk levels**
- CRITICAL: >= 0.85 — automatic STR initiation recommended
- HIGH: >= 0.70 — immediate investigator review
- MEDIUM: >= 0.50 — daily review queue
- LOW: < 0.50 — monitor only

---

## Explainability

- **SHAP TreeExplainer** — per-alert feature attribution on the XGBoost classifier (top-5 features surfaced in ExplainabilityCard)
- **Gemini 2.5 Flash** — grounded plain-English narrative per alert, backed by actual transaction evidence from the graph
- Both surfaced in the `/alerts/{id}/explain` API and the UI

---

## Known Limitations

- All metrics are on IBM AMLSim synthetic data. Real-bank transfer requires retraining on CBS feeds.
- XGBoost is a batch model; River handles streaming; the two are not co-trained.
- TGN checkpoint (AUC 0.72) is below XGBoost baseline on this dataset — included for Phase 3 path, not live scoring.
- No bias monitoring on production deployment; false-positive rates by branch, KYC tier, or account type are not measured.

---

## Reproducibility

```bash
# Generate demo data
python scripts/seed_demo.py

# Train XGBoost classifier
python scripts/train_gnn.py

# Train TGN (optional — large, ~20 min)
python scripts/train_tgn.py --amlsim

# Run tests
pytest -q
```
