# iDEA 2.0 Round 2 Submission Checklist

**Deadline: May 31, 2026** | Team NamoFans | IIT Kharagpur | PS3

---

## Portal Requirements vs. Our Status

| ID | Portal Says | Format | Our Status | Action |
|---|---|---|---|---|
| D1 | 1 page problem + 1 page solution | 2-page Google Doc | PDF ready: `docs/D1_Problem_Solution_Brief.pdf` | Upload to Google Drive, share "Anyone with link > Viewer", paste link |
| D2 | Live working prototype URL | URL | https://trace-ai-4xnj5ovp4a-uc.a.run.app | Paste as-is |
| D3 | 1-2 page doc with labelled diagram of all components | 1-2 page Google Doc | PDF ready: `docs/D3_Technical_Architecture.pdf` | Upload to Google Drive, share "Anyone with link > Viewer", paste link |
| D4 | Public repo, README covers: problem / how to run / dependencies / sample data / known limitations | Public GitHub | https://github.com/wildcraft958/namofans-trace-ai | Confirm repo is PUBLIC, paste link |
| D5 | 5-min YouTube Unlisted: problem → solution → demo → team | YouTube Unlisted | NOT DONE | Record, upload, paste link |

---

## D5 Pitch Video Script (5 minutes — portal structure: problem → solution → demo → team)

### [0:00-0:45] PROBLEM

> "Indian banks lost Rs. 71,543 crore to fraud in FY 2024-25. The systems designed to catch
> this generate 95% false positives — investigators spend their day dismissing noise.
> The median gap between fraud starting and detection is 277 days. By then, recovery is
> impossible. And the fraud that escapes detection entirely? Multi-hop fund flows: money
> that moves through 8 intermediate accounts. No single transaction is suspicious. Only
> the chain is — and today's rules cannot see chains."

*Show landing page. Scroll slowly through the stats bar.*

---

### [0:45-1:30] SOLUTION

> "TRACE.ai models every bank account as a node and every transaction as a directed edge.
> The entire bank becomes a graph. Fraud rings become structural patterns that emerge only
> at the network level. Four detection engines run in parallel: a graph pattern matcher,
> an XGBoost classifier on 11 graph features, a per-account streaming anomaly scorer with
> zero batch retraining, and a YAML compliance engine that hot-reloads new RBI circulars
> in 5 seconds. Their signals are fused into one composite risk score."

*Show architecture section on landing page briefly. Cut to dashboard.*

---

### [1:30-3:30] LIVE DEMO

Navigate to `/dashboard`. Let the 3D graph load.

> "This is live on Google Cloud Run. 542 accounts, 5,049 transactions. Five fraud rings
> seeded — the orange clusters are active detections."

Click a CRITICAL alert.

> "Every alert comes with SHAP attribution — which graph features drove the score and
> by how much. Gemini 2.5 Flash writes a plain-English explanation grounded in the actual
> transaction evidence. No hallucination. No black box."

Click STR Download.

> "One click. An 8-section FIU-IND compliant PDF — cover, subject account, fund trail,
> risk breakdown, AI narrative, recommended action. Generated in under 5 seconds.
> This used to take 4 to 6 hours per case."

Click Investigation Copilot. Type: `Show circular flows above 5 lakhs in the last 7 days`

> "Officers ask in plain English. The system maps the intent to a graph query and runs
> it live. No SQL, no Cypher."

---

### [3:30-4:30] ARCHITECTURE + IMPACT

> "XGBoost AUC above 0.99 on synthetic test data. Compliance rules are YAML — a new RBI
> circular takes effect in 5 seconds without a deployment. The entire system runs in one
> Docker container on Cloud Run."

Key metrics on screen (can show D1 impact table or landing stats):
- False positives: 95%+ rule-only → target below 15%
- STR prep time: 4-6 hours → under 5 minutes
- Detection scope: single-transaction rules → multi-hop depth 6

---

### [4:30-5:00] TEAM + CLOSE

> "Team NamoFans from IIT Kharagpur: Animesh Raj, Devansh Gupta, Prem Agarwal, Faizan Khan.
> The system is live at trace-ai-4xnj5ovp4a-uc.a.run.app. All code, docs, and the STR
> generator are in the public GitHub repo. Thank you."

**Record as:** screen share of https://trace-ai-4xnj5ovp4a-uc.a.run.app with voiceover.
**Upload to:** YouTube as Unlisted.
**After upload:** add the YouTube link to `README.md` under Live Demo and submit in portal.

---

## Google Drive Upload Steps (D1 and D3)

1. Open Google Drive
2. New > File Upload > select `docs/D1_Problem_Solution_Brief.pdf`
3. Right-click uploaded PDF > Open with > Google Docs
4. Review — check title block, tables, diagram are readable
5. Share > Anyone with the link > Viewer
6. Copy link, paste into D1 field in portal
7. Repeat for `docs/D3_Technical_Architecture.pdf`

---

## README Compliance Check (D4 — portal requires these 5 things)

| Portal Requires | Our README Section | Status |
|---|---|---|
| Problem | `## The Problem` | Done |
| How to run | `## Quick Start` | Done |
| Dependencies | Prerequisites in Quick Start + pyproject.toml | Done |
| Sample data | `## Dataset Description` | Done |
| Known limitations | `## Known Limitations` (7 bullets) | Done |

---

## D1 Compliance Check

| Sample Requires | Our D1 | Status |
|---|---|---|
| Problem in one sentence | Red box: Rs. 71,543 Cr, broken by design | Done |
| Who is affected and how severely | 4 bullets (direct/financial/operational/regulatory) | Done |
| Why current approaches fail | 4-row failure modes table | Done |
| What we are building | Solution paragraph + graph-native framing | Done |
| Core features of POC | 4-signal detection table with weights | Done |
| Built vs Planned table | 10-row table, green/orange columns | Done |
| Page 1 = problem, page 2 = solution | newpage between sections | Done |

---

## D3 Compliance Check

| Sample Requires | Our D3 | Status |
|---|---|---|
| System overview paragraph | Present (5 layers, clean interface description) | Done |
| Architecture diagram with labelled layers | TikZ 5-layer color-coded diagram, arrows | Done |
| Tech stack with WHY THIS CHOICE column | 12-row table with Layer / Technology / Why | Done |
| Key technical decisions | 4 bullets (XGBoost/GNN, NetworkX/Neo4j, YAML, single container) | Done |
| Known limitations | 6 bullets | Done |
