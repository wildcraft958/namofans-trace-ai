# RESEARCH.md — Distilled findings

Compiled from three parallel research agents (web + repo). This is the cheat sheet for "what banking judges reward and how the field is positioned."

---

## 1. iDEA Hackathon 2.0 — judging signals

- **Mission theme**: AI-CSPARC — Customer Security, Privacy, Assurance, Reliance, Convenience. Compliance & trust > raw accuracy.
- **Phase 2 deliverables (per dashboard)**: GitHub repo + deployed URL + demo video.
- **Phase 2 deadline**: TBA officially. Realistic estimate from PSB Hackathon Series cadence: 4–8 weeks of build window. We plan for 3 weeks.
- **Judges**: Union Bank executives + technical jury + IBA / DFS observers.
- **Heuristic from prior edition**: Practical banking operations focus (loan defaulter tracking, transaction monitoring) won. Generic AI did not.
- **Submission depth expected**: Working demo > PowerPoint. Testable code/UI, not just algorithms.
- **Mandatory features**: AI implementation + explainability (banking judges reject black boxes).
- **Industry signal**: Winners showcase at Global Fintech Fest. Implies investor / enterprise visibility weighs into selection.

**Action items already encoded into our plan**:
- Measured numbers, not target numbers
- Explainability layer (GNNExplainer + SHAP)
- Auto-STR PDF (regulatory artifact)
- Pilot deployment narrative for Union Bank specifically

---

## 2. FIU-IND STR format — what the PDF must contain

Per RBI e-filing manual (rbidocs.rbi.org.in/rdocs/content/Pdfs/68787.pdf) and the FIU-IND filing manual, the electronic STR follows a 6-file dataset structure: accounts, transactions, parties, relationships, party attributes, transaction attributes.

For the prototype PDF we collapse this into 8 sections:

1. **Cover** — Alert ID, generation timestamp, risk level (CRITICAL/HIGH/MEDIUM/LOW), reporting entity (Union Bank), report type (STR)
2. **Subject account details** — Masked account number, type (SAVINGS/CURRENT/SALARY), branch, IFSC, KYC category
3. **Suspicious transaction table** — Each flagged txn: date, amount, channel, counterparty, reason
4. **Complete fund trail diagram** — Visual graph of money flow (rendered from NetworkX subgraph)
5. **Risk score breakdown** — Pattern, GNN, anomaly, compliance contributions; calibrated thresholds
6. **AI-generated analysis narrative** — Plain-English summary, grounded in evidence (no hallucinated accounts)
7. **Recommended action** — File STR / Freeze account / Further investigation
8. **Evidence metadata** — Algorithm versions, model checkpoint hash, generation timestamp

**Why this wins**: ~95% of teams will ship a dashboard. Almost none will produce a regulator-shaped artifact. The PDF is the demo moment that says "this is real banking."

---

## 3. AMLSim — practical setup

- **Repo**: github.com/IBM/AMLSim
- **Pre-generated Kaggle dump**: kaggle.com/datasets/anshankul/ibm-amlsim-example-dataset (10K users × 1.32M txns labeled). Use this on Day 1 to skip generation pipeline work.
- **Inject 6 typologies**: layering, round-tripping, structuring, mule fan-in, mule fan-out, dormant burst (config in `data/amlsim_config/fraud_patterns.yaml`).
- **Indian banking augmentation**: `Faker(en_IN)` for names + IFSC codes (UBIN/SBIN/HDFC/ICIC/PUNB/BKID/CNRB) + INR amounts + RBI-compliant date ranges.
- **Demo target**: 5K accounts × 100K transactions, fraud rate < 1%.
- **Why AMLSim and not Elliptic / PaySim**: AMLSim is the regulator-recognized synthetic AML benchmark. Elliptic is Bitcoin-centric. PaySim is mobile-money. AMLSim looks like an Indian PSB.

---

## 4. Differentiator details

### GNNExplainer + SHAP
- PyG `torch_geometric.explain.Explainer` with `GNNExplainer` algorithm. ~60 lines.
- Returns subgraph + edge mask explaining a single account's flag.
- SHAP via `shap.KernelExplainer` over the fusion pipeline → per-feature contributions for the anomaly scorer.
- Demo line: *"Why was this flagged?"* → 3 nodes + top SHAP features render in <2s.

### Online learning (River HST + ADWIN)
- `river.anomaly.HalfSpaceTrees` builds a per-account streaming baseline.
- `river.drift.ADWIN` flags concept drift when fraud patterns shift.
- Live retrain demo: inject a new pattern via UI button → ADWIN fires → drift timeline lights up. Almost no team will demo this.

### NL Investigation Copilot
- LLM via LiteLLM, prompt-grounded in graph schema.
- 6 canned queries pre-cached for demo reliability:
  1. "Show all circular flows above ₹X in the last N days"
  2. "Which accounts sent funds to dormant accounts yesterday?"
  3. "Give me the full fund trail for ACC-####"
  4. "Flag all high KYC risk accounts that transferred >₹X to the same beneficiary"
  5. "Top 10 highest-degree accounts in the last 7 days"
  6. "Accounts with sudden velocity change > 5x baseline"

### Hot-reloadable compliance rules
- `compliance_rules.yaml` watched by `watchdog`. Edits take effect within ~5s.
- Operational sophistication signal that banking judges score positively.

### Entity resolution
- `rapidfuzz` fuzzy match across (name, phone, address) tuples.
- Merges alias accounts before scoring. Reduces false positives ~15-30%.
- "Real-world messy data" signal.

### Calibration + Model Card
- `sklearn.calibration.calibration_curve` plot in `MODEL_CARD.md`.
- Honestly states data, metrics, limitations, retraining cadence.

---

## 5. Competitor analysis — PS3

PS3 has ~32 shortlisted teams (most contested track). We catalogued direct threats and inferred their strategies from project titles.

### Tier-S threats

| Team | Project | School | Threat signal |
|---|---|---|---|
| **Aryabhata** | Pay_Flow | IIT Bombay | Top ML talent, vague title may hide depth |
| **Bazooka** | Graph AI | IIT Roorkee | Direct naming clash; minimalist title |
| **SecureLedger** | Graph Intelligence Platform | IIT Kanpur | Mirrors our pitch language |
| **Coded Hearts** | STAR — Spatial Temporal Automated Risk | IIIT Nagpur | "Spatial Temporal" = TGN, our closest tech twin |
| **HackOverflow** | Financial Sentinel — Graph-Native AML | IIT Guwahati | Professional positioning |
| **syntax_error** | TraceX | IIT Bhilai | IIT brand, similar narrative |
| **Sus Slayers / Jai_Hind** | Fund tracking | IIT Patna | Two IIT Patna teams on PS3 |
| **Team Titans** | FundFlow Intelligence | IIIT Allahabad | Multi-hop graph fraud — close to ours |

### Tier-A — different angle

| Team | Project | Differentiator |
|---|---|---|
| **RAW (Parul)** | BLING with Adversarial Self-Evolution | Adversarial robustness |
| **Kartavya (KIET)** | GraphGuard: Hybrid Edge-to-Graph | Edge / federated computing |
| **DEMO BUDDIES (BIT Ranchi)** | GraphSentinel | Clean naming, strong PS3 fit |
| **Tri-Devi (DJ Sanghvi)** | FinTrace | Home-college advantage at KJ Somaiya |

### Inferred field distribution

- ~80% of PS3 teams: NetworkX/Neo4j + GraphSAGE/GCN + dashboard. Generic.
- ~15%: temporal modeling (TGN/T-GCN). Our tech tier.
- ~5%: regulatory artifacts / NL copilot / online ML. **Our blue ocean.**

### Counter-positioning

| Threat | Their likely move | Our counter |
|---|---|---|
| Coded Hearts (STAR) | Pure spatial-temporal GNN | Beat on regulatory artifacts (STR + compliance YAML) |
| Aryabhata (Pay_Flow) | Strong ML, brand | Beat on demo polish + explainability + STR |
| SecureLedger | Graph intelligence platform | Beat on live retraining + drift dashboard moment |
| HackOverflow | Graph-native AML | Beat on multi-signal fusion + NL copilot |
| RAW (BLING) | Adversarial self-evolution | Don't compete; emphasize compliance + measured AMLSim metrics |
| Kartavya (GraphGuard) | Edge / federated | Don't compete; emphasize centralized PSB-realistic deployment |

### Where TRACE.ai uniquely wins

The combined surface area of (FIU-IND STR + GNNExplainer + NL Copilot + Live Retraining + Drift Dashboard + Hot-Reload Compliance + Online ML) is broader than any single team will attempt. Most teams will pick 1–2. We ship all of them at hackathon-prototype quality.

---

## 6. What kills hackathon prototypes (avoid)

1. **Vague metrics** — "Detects fraud" doesn't win. Specific numbers do: "Catches 87% of coordinated rings (5+ accounts) at <3% FP on AMLSim."
2. **Non-demoable features** — If it can't be filmed in the 4-min demo, deprioritize it.
3. **No real data feel** — Synthetic data must look like banking. AMLSim + Indian banking augmentation = handles this.
4. **Skipped compliance context** — No FIU-IND, no RBI, no Account Aggregator mention = judges think you skipped regulatory research.
5. **Brittle live demo** — Pre-record fallback GIFs of every step.
6. **Scope creep beyond Phase 1 PPT** — Judges compare back to the idea you submitted. Sticking to your story raises trust.

---

## 7. Indian banking signals (bonus credibility)

- **Account Aggregator (Sahamati / ReBIT)** — Mention compatibility with AA ecosystem in slides; signals deep India-fintech understanding.
- **PMLA 2002 + PMLA Rules 2005** — STR filing legal basis.
- **RBI Master Direction on KYC, 2016 (updated 2024)** — KYC categories driving rule conditions.
- **CTR threshold ₹10L** — Cash Transaction Report regulatory line.
- **FATF Mutual Evaluation** — India's AML compliance benchmarking. Stronger STRs help India's score.

---

## 8. Sources

- [iDEA 2.0 official site](https://www.ideahackathon.com/)
- [iDEA 2.0 resources](https://www.ideahackathon.com/resources)
- [Union Bank press release on iDEA 1.0 conclusion](https://www.unionbankofindia.bank.in/pdf/press-release-union-bank-of-india-concludes-idea-hackathon.pdf)
- [PSB Hackathon Series portal (DFS)](https://financialservices.gov.in/beta/en/psb-hackathon)
- [iDEA 2.0 on Unstop](https://unstop.com/competitions/crp-idea-20-indias-most-premier-hackathon-k-j-somaiya-college-of-engineering-kjsce-vidyavihar-1656405)
- [IBM AMLSim GitHub](https://github.com/IBM/AMLSim/)
- [AMLSim Kaggle pre-generated dump](https://www.kaggle.com/datasets/anshankul/ibm-amlsim-example-dataset)
- [Elliptic Bitcoin Dataset on Kaggle](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set)
- [RBI FIU-IND STR template (PDF)](https://rbidocs.rbi.org.in/rdocs/content/Pdfs/68787.pdf)
- [Sahamati Account Aggregator](https://sahamati.org.in/)
- [PyTorch Geometric fraud tutorial](https://www.graphcore.ai/posts/fraud-detection-using-graph-neural-networks-with-pytorch-geometric)
- [NVIDIA GNN Fraud Detection blog](https://developer.nvidia.com/blog/supercharging-fraud-detection-in-financial-services-with-graph-neural-networks/)
- [Neo4j Fraud Detection blog](https://neo4j.com/blog/developer/detect-bank-fraud-neo4j-graph-database/)
- [Temporal GNN methods for AML (2025 survey)](https://arxiv.org/abs/2503.24259)
- [Heterogeneous GNN money laundering](https://www.sciencedirect.com/science/article/pii/S2405918825000273)
- [Explainable Fraud Detection with GNNExplainer + Shapley](https://arxiv.org/abs/2509.12262)
- [River concept drift docs](https://riverml.xyz/dev/introduction/getting-started/concept-drift-detection/)
