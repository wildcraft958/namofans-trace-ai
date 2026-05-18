# TRACE.ai — Deliverables & Demo Script

## What's done vs what's left

| Deliverable | Status |
|---|---|
| D1 — Problem + Solution Brief | Done (`docs/D1_Problem_Solution_Brief.md`) |
| D3 — Technical Architecture | Done (`docs/D3_Technical_Architecture.md`) |
| D4 — GitHub repo + README | Done (pushed, live) |
| D2 — Technical Demo Video | Needs recording |
| D5 — Pitch Video + Slide Deck | Needs recording |
| Deploy | Build df333d56 running now |

---

## D2 — Technical Demo Video Script (5-7 min)

**Setup before recording:** Open three tabs — Landing page, Dashboard, GitHub repo. Have the
deployed URL ready. Seed is already in the container.

---

### [0:00-0:30] — Hook

> "India loses over 71,000 crore rupees annually to bank fraud. Today's AML systems flag
> everything — 95% of alerts are false positives. Investigators drown in noise. TRACE.ai
> fixes that."

Show the landing page. Scroll slowly through stats bar.

---

### [0:30-1:30] — The problem is structural

> "Rule-based systems see transactions one at a time. They miss money mule rings, layering
> chains that span 8 hops, and structuring patterns that stay individually below threshold.
> These aren't anomalies in isolation — they're only visible as a graph."

Show the "The Problem" section on the landing page. Let it breathe.

> "TRACE.ai models the entire bank as a temporal graph — every account a node, every
> transaction a directed edge with timestamp, amount, and channel. Then we run five
> detection layers simultaneously."

---

### [1:30-3:00] — Live dashboard walkthrough

Navigate to `/dashboard`. Let the 3D graph load.

> "This is a live deployment on Google Cloud Run. 20,000 accounts, 120,000 transactions
> from IBM's AMLSim benchmark — the regulator-recognized synthetic AML dataset."

Point to the 3D graph.

> "Each orange cluster is a detected fraud ring. The graph updates in real time — new
> transactions arrive every 1.5 seconds via WebSocket."

Point to the alert stream on the right.

> "High-risk alerts surface here automatically. Let me click one."

Click a CRITICAL alert. ExplainabilityCard opens.

> "SHAP breaks down why this account was flagged — what fraction of the risk score comes
> from the pattern detector, from the Temporal GNN, from the anomaly scorer, and from the
> compliance engine. A single number is a black box. Four numbers with weights are
> explainable."

Point to the SHAP bars. Then point to the LLM text.

> "Gemini 2.5 Flash generates a plain-English narrative grounded in the actual transaction
> evidence — not hallucinated accounts, real ones from the graph."

---

### [3:00-4:00] — The differentiator: STR in 5 minutes

> "Here's what actually matters to a compliance officer. Right now, filing a Suspicious
> Transaction Report takes 4 to 6 hours — manual write-up, regulatory formatting, evidence
> compilation. Watch this."

Click STR Download button.

> "That's an 8-section FIU-IND compliant PDF. Cover, subject account, transaction table,
> fund trail diagram, risk score breakdown, AI narrative, recommended action, evidence
> metadata. Generated in under 5 seconds. This is the only team you'll see today with a
> regulator-shaped artifact."

---

### [4:00-5:00] — NL Copilot + Live Inject

> "Investigators don't think in SQL. They think in questions."

Click the Investigation Copilot. Type: `Show me all circular flows above 5 lakhs in the last 7 days`

> "Gemini parses the intent, generates NetworkX traversal code, executes it against the
> live graph, and returns the result nodes. No SQL, no Cypher — natural language directly
> to graph query."

Click "Inject Pattern" button.

> "I'm now injecting a new fraud ring into the live graph. Watch the drift timeline."

Point to DriftTimeline — drift events should appear within 1-2 seconds.

> "ADWIN detected the distribution shift in real time. The compliance engine hot-reloads
> rules from a YAML file — no restart. That's operational sophistication."

---

### [5:00-5:45] — Architecture + numbers

> "Under the hood: IBM AMLSim 20,000-node graph, Temporal Graph Network trained on real
> data — AUC 0.72. Five AML typologies: circular flows, layering chains, structuring
> patterns, money mule clusters, dormant burst accounts. Four detection signals fused with
> calibrated weights. Entity resolution via rapidfuzz catches alias accounts that
> launderers use to split exposure."

Briefly show the Architecture section on the landing page.

---

### [5:45-6:15] — Close

> "TRACE.ai is designed for Union Bank's operational environment — FIU-IND compliance built
> in, Account Aggregator ecosystem compatible, hot-reloadable rules so compliance teams
> don't need engineers. The system is live now at trace-ai-4xnj5ovp4a-uc.a.run.app."

Show the URL in the browser.

> "GitHub repo, deployed URL, technical docs — all in the submission. Thank you."

---

## D5 — Pitch Video (5 min, non-technical)

Simpler version. Same structure but no code, no terminals. Just:

1. The 71,543 Cr problem (30s)
2. Show the dashboard + STR button (2 min, let the UI do the talking)
3. "Why TRACE.ai wins" — 3 slides: Regulatory artifact (STR), Explainability (SHAP), Operational maturity (hot-reload + NL copilot)
4. Team + ask (30s)

**Slide deck:** Pull the Architecture diagram from `docs/D3_Technical_Architecture.md` and the
tech stack table. 6-8 slides max. Judges read slides between sessions — keep them dense
with numbers, not fluffy.

---

## End-to-end verification (after build deploys)

```bash
curl https://trace-ai-4xnj5ovp4a-uc.a.run.app/api/health
# Open /dashboard in browser — graph should load
# Click an alert — SHAP + LLM text should appear
# Click STR Download — PDF should download
```
