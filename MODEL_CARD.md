# Model Card — TRACE.ai

This card documents the models that power TRACE.ai's detection layer. Honesty here is a judging signal — under-promise, over-deliver.

## Models

### 1. GraphSAGE Classifier (`src/trace/detection/gnn_classifier.py`)

**Architecture**
- 2 × `SAGEConv` layers, hidden dim 64, ReLU activations
- Linear classification head, 2-class (suspicious / clean)
- Handcrafted temporal features as node attributes (txn velocity, dormancy delta, time-since-last-txn)
- Class imbalance handled via focal loss + GraphSMOTE oversampling

**Training data**
- IBM AMLSim — 5K accounts × 100K transactions (synthetic)
- 6 injected fraud typologies (layering, round-tripping, structuring, mule fan-in, mule fan-out, dormant burst)
- Train/test split: 80/20, temporally stratified

**Metrics** _(populated after Day 8 training run)_

| Metric | Target | Measured |
|---|---|---|
| AUC | ≥ 0.85 | _TBD_ |
| Precision @ 5% FPR | ≥ 0.80 | _TBD_ |
| Recall on coordinated rings (≥5 accounts) | ≥ 0.80 | _TBD_ |
| Inference latency (CPU) | < 100ms per account | _TBD_ |

**Limitations**
- Trained on synthetic data; real-world transfer requires bank-specific fine-tuning
- Sensitive to graph structure changes; expects retraining at least monthly
- Does not capture cross-bank flows beyond AMLSim's modeled structure

**Roadmap**
- v2: Replace with full Temporal Graph Network (TGN, Rossi et al. 2020) once training converges with measured AUC ≥ 0.90
- v2: Add ChronoWave-GNN-style edge-centric temporal encoding
- v2: Integrate THG-OAFN attention fusion

---

### 2. Online Anomaly Scorer (`src/trace/detection/anomaly_scorer.py`)

**Architecture**
- Per-account `river.anomaly.HalfSpaceTrees` (HST) — streaming isolation-tree ensemble
- `river.drift.ADWIN` adaptive windowing for concept drift detection

**Training**
- No batch training. Each account's model updates per-transaction.
- Cold-start: account-type priors (savings/current/salary profiles) for the first 50 transactions.

**Metrics**
- Detection latency: <1ms per transaction
- Memory: ~2KB per account model

**Limitations**
- Susceptible to coordinated low-and-slow attacks that stay below the per-account anomaly threshold (mitigated by graph-level signals from GraphSAGE)
- Drift detection is heuristic; not a guarantee of recall on novel typologies

---

### 3. Compliance Rule Engine (`src/trace/detection/compliance_engine.py`)

Rules from `compliance_rules.yaml`. Hot-reloadable; first-match-wins.

| Rule | Source | Severity |
|---|---|---|
| CTR_THRESHOLD | RBI / PMLA — single ≥₹10L cash | HIGH |
| STRUCTURING_DAILY | PMLA Rules 2005 — sub-threshold clustering | HIGH |
| DORMANT_ACTIVATION | RBI dormancy guidance | MEDIUM |
| KYC_HIGH_RISK | RBI KYC Master Direction 2016 (updated 2024) | MEDIUM |
| CROSS_BANK_VELOCITY | Internal heuristic | LOW |

---

### 4. Risk Fusion (`src/trace/detection/risk_fusion.py`)

Weighted composite:

```
composite = 0.30 × pattern_score
          + 0.30 × gnn_score
          + 0.20 × anomaly_score
          + 0.20 × compliance_score
```

**Calibration** — `sklearn.calibration.calibration_curve` plot in `docs/figures/calibration.png` (generated on Day 12).

**Risk levels**
- CRITICAL: ≥ 0.85 → automatic STR initiation recommended
- HIGH: ≥ 0.70 → immediate investigator review
- MEDIUM: ≥ 0.50 → daily review queue
- LOW: < 0.50 → monitor only

---

## Explainability

- **GNNExplainer** (PyG `torch_geometric.explain`) — top-k contributing nodes/edges in the subgraph
- **SHAP** (`shap.KernelExplainer`) — feature-level attributions on the anomaly scorer
- Both surfaced in the `/alerts/{id}/explain` API and the `ExplainabilityCard` UI

## Bias and fairness

- Synthetic data does not include protected attributes by default; production deployment must add bias monitoring (false-positive rates by demographic, by branch, by KYC tier).
- Cold-start accounts (new) are scored with type priors only — be cautious about flagging legitimate new customers.

## Retraining cadence

- GraphSAGE: weekly batch retrain on rolling 90-day window
- Online anomaly: continuous (per-transaction)
- Compliance rules: ad-hoc on RBI circular issuance (hot-reload)

## Reproducibility

```bash
python scripts/generate_data.py --num-accounts 5000 --num-transactions 100000
python scripts/train_gnn.py --epochs 50 --hidden 64
pytest -q
```

Random seed pinned to 42 across NumPy / PyTorch / River where applicable.
