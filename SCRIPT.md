# TRACE.ai — D5 Pitch Video Script (~5 minutes)

**Format:** Screen share of https://trace-ai-4xnj5ovp4a-uc.a.run.app + voiceover
**Upload:** YouTube Unlisted
**Portal structure (exact):** problem (30s) → solution + how it works (2 min) → demo walkthrough (1:30) → built vs. planned (30s) → team (30s)

---

## [0:00–0:30] PROBLEM

Show landing page. Pause on the stats bar.

> "Indian banks lost Rs. 71,543 crore to fraud in FY 2024-25. Rule-based systems generate
> 95% false positives — investigators spend the day dismissing noise. The median detection
> gap is 277 days. And the fraud that escapes entirely? Multi-hop fund flows through
> 8 intermediate accounts — invisible to any single-transaction rule."

---

## [0:30–2:30] SOLUTION + HOW IT WORKS

Show architecture section on landing page briefly.

> "TRACE.ai models every bank account as a node and every transaction as a directed edge.
> The entire bank becomes a graph. Fraud rings that are invisible transaction-by-transaction
> become visible structural patterns at the network level."

> "Four detection engines run in parallel. A graph pattern matcher covers all five PMLA
> typologies — circular flows, layering chains, structuring, mule fan-in/out, dormant burst.
> An XGBoost classifier on 11 graph-structural features — betweenness centrality, PageRank,
> transaction velocity, KYC risk score, dormancy delta — achieves AUC above 0.99 on the
> IBM AMLSim benchmark. A streaming per-account anomaly scorer using Half-Space Trees
> updates on every transaction with zero batch retraining. And a YAML compliance engine
> hot-reloads new RBI circulars in 5 seconds — no deployment, no ticket."

> "All four signals fuse into one composite risk score. SHAP TreeExplainer surfaces the
> top contributing features per alert. Gemini 2.5 Flash writes a plain-English explanation
> grounded in actual transaction evidence — not a template, the specific counterparties
> and amounts from the graph. One click generates an 8-section FIU-IND compliant
> Suspicious Transaction Report."

Cut to dashboard.

---

## [2:30–4:00] DEMO WALKTHROUGH

Navigate to `/dashboard`. Let the 3D graph load.

> "This is live on Google Cloud Run. 542 accounts, 5,049 transactions. Five fraud rings
> seeded — the orange clusters are active detections."

Click a CRITICAL alert.

> "SHAP attribution shows exactly which graph features drove the score and by how much.
> Gemini narrates the specific transaction evidence. One click — the STR PDF generates
> in under 5 seconds. This used to take 4 to 6 hours per case."

Click Investigation Copilot. Type: `Show circular flows above 5 lakhs in the last 7 days`

> "Officers ask in plain English. No SQL. No Cypher. The system maps the intent to a
> live graph query and returns the matching subgraph."

---

## [4:00–4:30] BUILT VS. PLANNED

Show the live URL or a feature list on screen.

> "What is live and running today: the graph engine, all five pattern detectors, the
> XGBoost classifier, the River streaming anomaly scorer, YAML compliance rules, SHAP
> explainability, Gemini narrative, the NL copilot, the STR PDF generator, and the 3D
> dashboard — all deployed in one container on Google Cloud Run."

> "Phase 3: CBS live API integration, Neo4j production graph at scale, real-bank
> retraining on actual transaction feeds, and RBAC access control with MLRO audit trails."

---

## [4:30–5:00] TEAM

Show landing page footer or team slide.

> "Team NamoFans from IIT Kharagpur: Animesh Raj, Devansh Gupta, Prem Agarwal, Faizan
> Khan. The system is live at trace-ai-4xnj5ovp4a-uc.a.run.app. All code is in the
> public GitHub repo. Thank you."

Show live URL in the browser address bar as the final frame.

---

## After Recording

1. Upload to YouTube as **Unlisted**
2. Test the link in an incognito window before submitting
3. Paste the link in both the **D5 Pitch Video** portal field and the end slide of your pitch deck
4. Update `README.md` under `## Live Demo` with this link

---

## Pre-Recording Checklist

```bash
# Verify deployment is up
curl https://trace-ai-4xnj5ovp4a-uc.a.run.app/api/health

# Open in browser and confirm before recording:
# - Landing page stats bar loads
# - 3D graph shows orange fraud clusters
# - Clicking a CRITICAL alert shows SHAP card + Gemini explanation
# - STR Download produces an 8-section PDF
# - Copilot responds to a natural language query
```
