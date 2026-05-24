# TRACE.ai — D5 Pitch Video Script (5 minutes)

**Format:** Screen share of https://trace-ai-4xnj5ovp4a-uc.a.run.app + voiceover
**Upload:** YouTube Unlisted
**Structure (portal requirement):** problem → solution → demo → team

---

## [0:00–0:45] PROBLEM

> "Indian banks lost Rs. 71,543 crore to fraud in FY 2024-25. The systems designed to catch
> this generate 95% false positives — investigators spend their entire day dismissing noise.
> The median gap between fraud starting and detection is 277 days. By then, recovery is
> impossible. And the fraud that escapes detection entirely? Multi-hop fund flows: money
> that moves through 8 intermediate accounts before disappearing. No single transaction is
> suspicious. Only the chain is — and today's rules cannot see chains."

Show landing page. Scroll slowly through the stats bar.

---

## [0:45–1:30] SOLUTION

> "TRACE.ai models every bank account as a node and every transaction as a directed edge.
> The entire bank becomes a graph. Fraud rings become structural patterns that emerge only
> at the network level. Four detection engines run in parallel: a graph pattern matcher,
> an XGBoost classifier on 11 graph features, a per-account streaming anomaly scorer with
> zero batch retraining, and a YAML compliance engine that hot-reloads new RBI circulars
> in 5 seconds. Their signals are fused into one composite risk score."

Show architecture section on landing page briefly, then cut to dashboard.

---

## [1:30–3:30] LIVE DEMO

Navigate to `/dashboard`. Let the 3D graph load.

> "This is live on Google Cloud Run. 542 accounts, 5,049 transactions. Five fraud rings
> seeded — the orange clusters are active detections."

Click a CRITICAL alert.

> "Every alert comes with SHAP attribution — which graph features drove the score and by
> how much. Gemini 2.5 Flash writes a plain-English explanation grounded in the actual
> transaction evidence from the graph. No hallucination. No black box."

Click STR Download.

> "One click. An 8-section FIU-IND compliant PDF — cover, subject account, fund trail,
> risk breakdown, AI narrative, recommended action. Generated in under 5 seconds.
> This used to take 4 to 6 hours per case."

Click Investigation Copilot. Type: `Show circular flows above 5 lakhs in the last 7 days`

> "Officers ask in plain English. The system maps the intent to a graph query and runs it
> live. No SQL, no Cypher."

---

## [3:30–4:30] ARCHITECTURE + IMPACT

Show architecture section or D3 diagram briefly.

> "XGBoost AUC above 0.99 on synthetic test data. Compliance rules are YAML — a new RBI
> circular takes effect in 5 seconds without a deployment. The entire system runs in one
> Docker container on Cloud Run."

Pause on impact numbers:
- False positives: 95%+ rule-only → target below 15%
- STR prep time: 4–6 hours → under 5 minutes
- Detection scope: single-transaction → multi-hop depth 6

---

## [4:30–5:00] TEAM + CLOSE

> "Team NamoFans from IIT Kharagpur: Animesh Raj, Devansh Gupta, Prem Agarwal, Faizan Khan.
> The system is live at trace-ai-4xnj5ovp4a-uc.a.run.app. All code and docs are in the
> public GitHub repo. Thank you."

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
```
