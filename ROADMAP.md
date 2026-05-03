# ROADMAP.md — Phase 2 day-by-day

3-week pragmatic flagship build. Owners are role-tagged; map to TEAM.md once members claim.

Each item has an **owner role**, **deliverable**, and **DoD (definition of done)**.

---

## Week 1 — Foundation (Days 1–7)

### Day 1 (Mon)
- **Backend** — Pull AMLSim Kaggle dump → `data/raw/amlsim/`. Wire `data/ingestion.py::load_amlsim_csv`.
  - DoD: `pd.read_csv` returns ≥100K rows of labeled txns
- **Backend** — Build `graph/builder.py::build_graph`.
  - DoD: a NetworkX MultiDiGraph with ≥5K nodes is built and pickled to `data/processed/graph.pkl`
- **Frontend** — `npm install`, run `npm run dev`, blank shell renders.
  - DoD: <http://localhost:5173> loads without errors

### Day 2 (Tue)
- **Backend** — Implement 5 pattern detectors in `detection/patterns/*.py`.
  - DoD: each returns True on its seeded fraud, False on clean accounts (test in `tests/unit/`)
- **Frontend** — Wire `useGraphData` hook to a stub `/api/graph` returning a tiny graph
  - DoD: `react-force-graph-3d` renders ≥50 nodes

### Day 3 (Wed)
- **Backend** — Risk fusion module + tests (already partially scaffolded).
  - DoD: `pytest tests/unit/test_risk_fusion.py` passes
- **Backend** — YAML compliance engine with hot-reload.
  - DoD: edit `compliance_rules.yaml`; engine picks up change within 5s without restart
- **NLP** — Hardcoded happy-path STR PDF: 1 sample alert → 1-page PDF with all 8 sections.
  - DoD: a PDF opens cleanly in Acrobat

### Day 4 (Thu)
- **ML** — Online anomaly scorer (`detection/anomaly_scorer.py`) + ADWIN drift wired to a streaming feed.
  - DoD: drift event fires when synthetic distribution shift is injected
- **Backend** — FastAPI app + `/health` + `/graph` + `/alerts` returning real graph data.
  - DoD: `curl /health` → `{"status":"ok"}`; `curl /alerts` returns ≥1 mocked alert

### Day 5 (Fri)
- **Backend** — WebSocket `/ws/alerts` push pipeline.
  - DoD: a script that posts a new alert pushes via WebSocket; frontend receives and renders
- **Frontend** — Alert panel + KPI cards live on real data
  - DoD: opening dashboard shows ≥5 KPI tiles + ≥10 alerts

### Day 6 (Sat) — buffer / catch-up
- Resolve any Day 1–5 slip. Code review across backend modules.

### Day 7 (Sun) — buffer
- README hero update with first dashboard screenshot.

---

## Week 2 — Intelligence + Differentiators (Days 8–14)

### Day 8 (Mon)
- **ML** — GraphSAGE training on AMLSim. Run on Kaggle T4. Save checkpoint.
  - DoD: measured AUC ≥ 0.85 on held-out test set; saved `models/graphsage.pt`
- **NLP** — LLM Alert Explainer with LiteLLM. Template-constrained prompt.
  - DoD: a flagged account → English explanation grounded in real evidence (no hallucinated account IDs)

### Day 9 (Tue)
- **ML** — GNNExplainer wrapper on the trained model.
  - DoD: GET `/alerts/{id}/explain` returns subgraph + edge mask JSON
- **NLP** — NL Investigation Copilot. 6 canned queries pre-cached.
  - DoD: each canned query returns sub-graph in <2s

### Day 10 (Wed)
- **ML** — SHAP wrapper for the fusion pipeline.
  - DoD: per-feature attributions render in `/alerts/{id}/explain`
- **Frontend** — `ExplainabilityCard` component live; "Why?" button on each alert

### Day 11 (Thu)
- **NLP** — Auto-STR Generator full FIU-IND format (8 sections) with fund-trail diagram.
  - DoD: STR PDF for any alert generates in <5s
- **Backend** — Entity resolution (`data/entity_resolution.py`) wired into graph build.
  - DoD: alias accounts merge automatically; FP rate measurably lower

### Day 12 (Fri)
- **ML** — Calibration curve + `MODEL_CARD.md`.
  - DoD: calibration plot saved to `docs/figures/`; MODEL_CARD references it
- **Frontend** — Drift timeline component live; visualizes ADWIN events

### Day 13 (Sat)
- **All** — End-to-end demo scenario rehearsal (the 4-min sequence).
- **All** — File any P0 bugs found; fix.

### Day 14 (Sun) — buffer
- README + RESEARCH + DECISIONS pass.
- TGN swap-in window: if GraphSAGE AUC ≥ 0.90 AND TGN training converged, swap in.

---

## Week 3 — Polish, Deploy, Demo (Days 15–21)

### Day 15 (Mon)
- **Backend + ML** — Live retraining demo path. Inject pattern → River retrains → drift timeline lights up.
  - DoD: button click in dashboard triggers full sequence in <5s
- **Frontend** — Polish: loading states, error toasts, mobile breakpoints

### Day 16 (Tue)
- **All** — End-to-end rehearsal #1 of the 4-min demo.
- **All** — Pre-record fallback GIFs for every demo step.

### Day 17 (Wed)
- **Backend** — Deploy backend to Render or Railway free tier.
- **Frontend** — Deploy frontend to Vercel.
- **All** — Test deployed URL from incognito + mobile + slow network.

### Day 18 (Thu)
- **All** — Record 4-minute demo video. Use Loom or OBS. Upload to YouTube unlisted.
- **All** — End-to-end rehearsal #2.

### Day 19 (Fri)
- **All** — README final pass with hero GIF + deployed URL + video link.
- **All** — End-to-end rehearsal #3.

### Day 20 (Sat) — buffer
- Fix anything found in rehearsals.
- Backup laptop with full env loaded.

### Day 21 (Sun) — submission
- Final submission to dashboard: GitHub URL + deployed URL + YouTube link.
- Tag release `phase-2-submission`.

---

## Owner role legend

- **Backend** — FastAPI, NetworkX graph, pattern matchers, compliance engine, entity resolution
- **ML** — GraphSAGE, online anomaly, GNNExplainer, SHAP, calibration, MODEL_CARD
- **NLP** — LLM explainer, NL copilot, STR generator
- **Frontend** — React dashboard, 3D force graph, all components, hooks, deploy

A 4-person team can map 1:1 to these roles. See `TEAM.md` for the actual assignment.

---

## Risk-aware adjustments

- **Slipping behind by Day 5?** Cut Module M (drift dashboard) first. Drop entity resolution next.
- **GNN doesn't converge by Day 10?** Ship XGBoost on graph features as the GNN substitute. Disclose in MODEL_CARD.
- **LLM API rate limits during demo?** Switch to fully cached query responses for the 6 canned NL prompts.
- **Phase 2 deadline shrinks unexpectedly?** Minimum-viable submission = Day 1–6 work + STR PDF + dashboard. Submittable as a "1-week sprint" build.
