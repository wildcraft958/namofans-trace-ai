# TRACE.ai: Problem and Solution Brief

**iDEA Hackathon 2.0 | PSBs Hackathon Series 2026**
**Team NamoFans | IIT Kharagpur | PS3 - Tracking of Funds within Bank for Fraud Detection**
**Members:** Animesh Raj · Devansh Gupta · Prem Agarwal · MD. Faizan Khan

---

## The Problem

Indian banks are losing the war against financial crime - not because of a lack of effort, but because of fundamentally inadequate tooling.

**The scale is alarming.** The RBI Annual Report (FY 2024-25) documents ₹71,543 Cr in bank fraud losses in a single year. Every rupee of that represents a failure in detection, prevention, or reporting.

**Rule-based systems are broken by design.** The AML infrastructure deployed at most Indian PSBs today operates on fixed thresholds: flag any single transaction above ₹10 lakh, flag accounts with unusual channel mixes, block remittances that match a known mule account list. These rules generate 95%+ false positive rates. Compliance officers spend most of their day dismissing false alerts rather than investigating real threats. Investigator fatigue causes genuine fraud rings to be dismissed as noise.

**The patterns that matter evade rules entirely.** Sophisticated money laundering does not involve single large transactions - it involves coordinated multi-hop movement across accounts. Three specific patterns dominate AML casework but are invisible to rule engines:

- **Layering chains:** Funds move through 4-8 intermediate accounts, each forwarding more than 70% of received value within 48 hours, disguising origin.
- **Round-tripping (circular flow):** Money exits Account A, travels through a ring of 3-6 accounts, and returns - all within 72 hours. The net fund movement is zero; the purpose is to create a false paper trail of legitimate transactions.
- **Structuring:** Multiple transactions just below ₹10 lakh are split across several beneficiaries on the same day, evading CTR thresholds.

**Reporting is a manual ordeal.** When a compliance officer does identify a suspicious case, filing a Suspicious Transaction Report (STR) with FIU-IND requires manually compiling transaction histories, fund trail diagrams, risk narratives, and recommended actions into a structured A4 PDF. This takes 4-6 hours per case. STR quality varies enormously across officers, and FIU-IND receives incomplete evidence packages that reduce the intelligence value of every filing.

**The time-to-detection gap compounds losses.** IBM's 2024 Financial Services benchmark finds a median of 277 days between fraud initiation and detection. By then, funds have been layered multiple times, accounts have been closed, and recovery is effectively impossible.

---

## The Solution: TRACE.ai

TRACE.ai is a graph-native, AI-powered AML intelligence platform built specifically for Indian PSBs. It treats every banking transaction as a directed edge in a dynamic temporal graph, enabling detection of multi-hop fraud patterns that are structurally impossible to identify at the single-transaction level.

### How it works

**Layer 1 - Graph Engine.** CBS transaction feeds (NEFT/RTGS/UPI/IMPS) are ingested and modeled as a NetworkX MultiDiGraph where nodes are accounts and edges are transactions carrying amount, timestamp, and channel. Every account carries KYC risk category and dormancy status as node features.

**Layer 2 - Detection Engine (four parallel signals).**

- *Pattern Matcher:* Five AML typology detectors run concurrently on the graph. Circular flow detection uses cycle enumeration with temporal windowing. Layering detection traces BFS paths up to depth 6, flagging chains where forwarding ratio exceeds 70%. Structuring detection identifies same-day transaction clusters from a single source that aggregate into the ₹8-10 lakh range. Mule detection flags high in-degree and out-degree accounts within 24-hour windows. Dormant burst detection catches accounts inactive 90+ days that suddenly execute high-value transfers.

- *Graph Classifier:* An XGBoost model trained on 11 graph-structural features (degree centrality, PageRank, betweenness, transaction velocity, counterparty uniqueness, KYC risk score) assigns a continuous fraud probability to every account. At prototype scale with synthetic data, the classifier achieves AUC > 0.99.

- *Online Anomaly Scorer:* River HalfSpaceTrees build individual behavioral baselines per account using streaming updates with sub-millisecond latency. ADWIN drift detection identifies accounts whose behavior has shifted significantly from their own established baseline, catching emerging fraud rings without batch retraining.

- *Compliance Rule Engine:* A YAML-defined rule set encoding RBI Master Directions, PMLA 2002 requirements, and FIU-IND STR triggers evaluates each account's transaction attributes. Rules hot-reload without system restarts - a new RBI circular becomes effective in the running system within seconds.

**Risk Fusion.** The four signals are combined into a single composite score (pattern 30%, classifier 30%, anomaly 20%, compliance 20%). Accounts scoring above 0.85 are flagged CRITICAL, above 0.70 HIGH, above 0.50 MEDIUM.

**Layer 3 - Intelligence.**

- *SHAP Explainability:* Every alert includes a SHAP TreeExplainer breakdown showing which graph features drove the suspicion score, in plain-language format. No black-box flags.
- *Gemini LLM Explainer:* A grounded evidence block is assembled from the alert data and sent to Gemini 2.5 Flash to produce a 2-3 sentence plain English explanation of why the account is flagged.
- *NL Investigation Copilot:* Compliance officers ask questions in plain English - "Show circular flows above ₹5 lakh in the last 7 days," "Find dormant accounts with recent high-value activity." The system dispatches to six pattern-specific graph query handlers or falls back to Gemini for intent parsing.
- *Auto-STR Generator:* One click produces a FIU-IND-compliant 8-section A4 PDF: cover, subject account, suspicious transactions table, fund trail flowchart, risk score breakdown, AI narrative, recommended action, and evidence metadata. What took 4-6 hours now takes under 5 minutes.

**Layer 4 - Delivery.** A 3D interactive dashboard built with React and react-force-graph-3d renders the transaction graph in real time. Nodes glow red/orange/yellow based on risk level. WebSocket alerts stream as new patterns emerge. The drift timeline shows River ADWIN events live - compliance officers can watch the ML adapt to a new pattern without system downtime.

### Impact

| Metric | Before TRACE.ai | With TRACE.ai |
|---|---|---|
| False positive rate | 95%+ (rule-only) | Target <15% |
| STR preparation time | 4-6 hours | <5 minutes |
| Pattern detection | Single-transaction rules | Multi-hop graph analysis |
| ML adaptation | Quarterly batch retraining | Real-time, zero downtime |
| Investigator interface | Manual query building | Ask in plain English |

### Deployment path

Phase 2 (this submission) is a working prototype on IBM AMLSim-generated synthetic data with realistic Indian banking parameters. Phase 3 targets API integration with Union Bank CBS feeds and Neo4j for production-scale graph storage. Phase 4 extends to 3-5 additional PSBs through the IBA/DFS endorsement channel that this hackathon provides.

**Live prototype:** https://trace-ai-4xnj5ovp4a-uc.a.run.app
**Repository:** https://github.com/wildcraft958/namofans-trace-ai
