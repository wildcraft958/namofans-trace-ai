# TRACE.ai — D5 Pitch Video Script (5-7 minutes)

**Format:** Screen share of https://trace-ai-4xnj5ovp4a-uc.a.run.app + voiceover
**Upload:** YouTube Unlisted
**Structure (portal requirement):** problem → solution → demo → team

---

## [0:00–1:00] PROBLEM

> "Indian banks lost Rs. 71,543 crore to fraud in FY 2024-25. That number has grown every
> single year for the last decade. And yet the tools banks use today are the same rule-based
> systems from 2005 — if a single transaction crosses Rs. 10 lakh, flag it. If a dormant
> account wakes up, flag it. Simple thresholds."

Show landing page. Pause on the stats bar.

> "The problem with simple thresholds is this: sophisticated fraud does not look suspicious
> at the transaction level. Layering moves money through 8, 10, 12 intermediate accounts,
> each hop below the reporting threshold. Round-trip flows return funds to the origin
> after cycling through a network of mules. No single transaction in that chain triggers
> a rule. Only the structure of the chain is the signal — and today's systems are blind to
> structure."

Scroll slowly through the landing page problem section.

> "The result: 95% of the alerts generated are false positives. Investigators spend their
> entire day dismissing noise. The median gap between fraud starting and detection is
> 277 days. By then, the money is gone. Recovery is nearly impossible. And the compliance
> cost of filing a Suspicious Transaction Report manually is 4 to 6 hours per case.
> That is the problem TRACE.ai is built to solve."

---

## [1:00–2:15] SOLUTION

> "TRACE.ai models every bank account as a node and every transaction as a directed edge.
> The entire bank becomes a live graph. Fraud rings that are invisible at the transaction
> level become visible structural patterns at the network level."

Show architecture section on landing page briefly.

> "Four detection engines run in parallel. First: a graph pattern matcher that runs DFS
> cycle detection for circular flows, betweenness-weighted chain traversal for layering,
> and degree-spike analysis for mule fan-in and fan-out — all five AML typologies defined
> under PMLA 2005."

> "Second: an XGBoost classifier trained on 11 graph-structural features — PageRank,
> betweenness centrality, transaction velocity, dormancy delta, KYC risk score. AUC above
> 0.99 on the IBM AMLSim benchmark. Sub-10 millisecond inference per account."

> "Third: a per-account streaming anomaly scorer using Half-Space Trees. No batch
> retraining ever. Each account's model updates on every transaction. Detection latency
> under 1 millisecond."

> "Fourth: a YAML compliance engine. Rules are not hardcoded. A new RBI circular becomes
> active in 5 seconds without a deployment. The CTR threshold, structuring rules, dormancy
> guidance — all configurable."

> "These four signals fuse into one composite risk score. Pattern and classifier each
> carry 30%. Anomaly and compliance each carry 20%. One number per account. One decision
> surface for the investigator."

Cut to dashboard.

---

## [2:15–4:45] LIVE DEMO

Navigate to `/dashboard`. Let the 3D graph load.

> "This is live on Google Cloud Run right now. 542 accounts, 5,049 transactions. Five
> fraud rings were seeded — layering chains, circular flows, mule networks, structuring
> clusters, and dormant bursts. The orange clusters are the active detections."

Rotate the 3D graph slowly.

> "Every node is an account. Every edge is a transaction. The graph layout uses force
> simulation, so accounts that transact heavily with each other pull together. Fraud rings
> form visually distinct clusters. An investigator can see a circular flow in one glance."

Click a CRITICAL alert in the alerts panel.

> "This account has a composite risk score of 0.91 — CRITICAL threshold. Let me show you
> exactly why."

Point at the SHAP attribution card.

> "SHAP TreeExplainer computed feature attribution on the XGBoost classifier. The top
> drivers here are betweenness centrality — this account sits on the critical path of
> multiple transaction chains — and transaction velocity: 14 outgoing transactions in
> 48 hours. These are not guesses. These are mathematically derived contributions from the
> model, grounded in the actual graph structure."

Point at the LLM narrative.

> "Gemini 2.5 Flash writes a plain-English explanation of the alert, grounded in actual
> transaction evidence pulled from the graph. Not a generic summary. The specific
> counterparties, the specific timestamps, the specific amounts. No hallucination because
> the prompt is template-constrained — only deterministic evidence enters the LLM."

Click STR Download.

> "One click. An 8-section FIU-IND compliant Suspicious Transaction Report — cover page,
> subject account details, fund trail reconstruction, risk score breakdown, AI narrative,
> recommended action. Generated in under 5 seconds. This is the document that used to
> take an analyst 4 to 6 hours to produce manually."

Wait for the PDF to open or download.

> "Every field in this PDF maps to the FIU-IND STR format. The fund trail section shows
> the hop-by-hop transaction path. The risk breakdown section shows each engine's
> contribution. A compliance officer can file this directly."

Click Investigation Copilot. Type: `Show circular flows above 5 lakhs in the last 7 days`

> "Officers ask in plain English. The copilot maps the intent to a graph traversal query —
> 10 distinct intents are supported: circular flows, layering chains, dormant activations,
> high-velocity accounts, structuring clusters. No SQL. No Cypher. The query runs live
> against the NetworkX graph and returns the matching subgraph."

Pause on the copilot result.

> "This is the interface an investigator actually uses. Not a dashboard full of numbers.
> A question-and-answer loop that narrows the focus to the accounts that matter."

Navigate to the drift or alerts panel and click "Inject Pattern" if available, or show a HIGH alert.

> "The system is also streaming. New transactions arrive via WebSocket. The River anomaly
> scorer updates per account in real time. The compliance engine fires synchronously.
> If a new typology surfaces — say, a cross-border velocity spike — the YAML rule is
> updated and live in under 5 seconds."

---

## [4:45–6:15] ARCHITECTURE + IMPACT

Show architecture section or landing page tech diagram.

> "A few design decisions worth noting. XGBoost over a neural GNN for the classifier:
> XGBoost on engineered graph features achieves AUC above 0.99 on this dataset. A
> Temporal Graph Network trained on the same data achieves 0.72. Engineered features win
> on a hackathon prototype. The TGN checkpoint is included as the Phase 3 path when
> real-bank CBS feed volume makes temporal learning worthwhile."

> "NetworkX over Neo4j for the graph engine: NetworkX runs in-process, zero latency,
> no external dependency. The graph API and pattern matchers are already written in
> graph-native Python. Neo4j is the production path — the abstraction is already
> compatible."

> "YAML for compliance rules: every rule is declarative. The CTR threshold is a number
> in a file. When the RBI issues a revised Master Direction, the bank's compliance team
> edits one line. No engineering ticket. No deployment."

> "The entire system ships in one Docker container on Cloud Run. No Kubernetes. No
> microservice complexity. One container, one port, five features working end to end."

Pause on impact numbers:

> "In terms of impact: the false positive rate drops from 95% under pure rule-based
> systems to a target below 15% with four-signal fusion. STR preparation time drops
> from 4 to 6 hours to under 5 minutes. Detection scope expands from single-transaction
> thresholds to multi-hop chains at depth 6."

---

## [6:15–7:00] TEAM + CLOSE

> "Team NamoFans from IIT Kharagpur: Animesh Raj, Devansh Gupta, Prem Agarwal, Faizan
> Khan. The system is live right now at trace-ai-4xnj5ovp4a-uc.a.run.app. All code, the
> STR generator, the compliance engine, the copilot — everything is in the public GitHub
> repository. Thank you."

Show the live URL in the browser address bar as the final frame.

---

## After Recording

1. Upload to YouTube as **Unlisted**
2. Copy the YouTube link
3. Add it to `README.md` under `## Live Demo` (replace the "recording in progress" placeholder)
4. Paste the YouTube link in the D5 field of the submission portal before May 31, 2026

---

## Pre-Recording Checklist

```bash
# Verify deployment is up
curl https://trace-ai-4xnj5ovp4a-uc.a.run.app/api/health

# Open in browser and confirm:
# - 3D graph loads with orange fraud clusters
# - Clicking an alert shows SHAP card + LLM explanation
# - STR Download produces a PDF
# - Copilot responds to a natural language query
# - Alerts panel shows CRITICAL / HIGH alerts
```
