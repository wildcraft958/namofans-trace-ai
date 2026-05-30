# TRACE.ai — D5 Pitch Deck Outline (Google Slides)

**Platform:** Google Slides
**Sharing:** Anyone with the link can view
**Mandatory:** Final slide must list links to ALL deliverables D1–D5

---

## Slide 1 — Title

**Headline:** TRACE.ai
**Subheading:** Graph-Native AML Detection for Indian Banks
**Bottom line:** Team NamoFans · IIT Kharagpur · PS3 — Fund Flow Tracking
**Badge:** iDEA 2.0, PSBs Hackathon Series 2026 · Union Bank of India

---

## Slide 2 — The Problem

**Headline:** Indian Banks Are Losing — Systematically

Three stat blocks (large numbers, one per column):
- **Rs. 71,543 Cr** — Bank fraud losses, FY 2024-25
- **95%** — False positive rate in rule-based AML systems
- **277 days** — Median gap from fraud start to detection

**Body:** Today's systems flag individual transactions. Fraud doesn't work that way.
Layering and circular flows move money through 8–12 intermediate accounts —
each hop below the reporting threshold. No single transaction triggers a rule.
Only the chain is suspicious. And today's rules cannot see chains.

---

## Slide 3 — Why Current Systems Fail

**Headline:** Four Failure Modes, One Root Cause

Table (2 columns: Failure / Impact):

| Failure | Impact |
|---|---|
| Threshold-only rules (Rs. 10L CTR) | Multi-hop flows below threshold escape detection |
| No structural analysis | Circular flows and layering invisible at transaction level |
| Manual STR preparation | 4–6 hours per case; investigators overloaded |
| 95% false positive rate | Real threats buried in noise; 277-day detection lag |

**Root cause:** Rule engines see transactions. They cannot see networks.

---

## Slide 4 — Our Solution

**Headline:** TRACE.ai — The Entire Bank as a Graph

**Diagram (simple):** Nodes = Accounts → Edges = Transactions → Graph → Risk Score → Alert + STR

**Three pillars:**
1. Graph-native detection — structural patterns across the entire transaction network
2. Four-signal fusion — pattern matching + ML classifier + streaming anomaly + compliance rules
3. Explainable output — SHAP attribution + Gemini narrative + one-click FIU-IND STR

---

## Slide 5 — How It Works

**Headline:** Four Engines, One Risk Score

Four engine boxes (2x2 grid):

| Engine | Method | Fusion Weight |
|---|---|---|
| Graph Pattern Matcher | DFS cycle detection, betweenness traversal, degree spikes — 5 PMLA typologies | 30% |
| XGBoost Classifier | 11 graph features (PageRank, velocity, KYC score, dormancy) — AUC > 0.99 | 30% |
| River Anomaly Scorer | Per-account HalfSpaceTrees, updates per transaction, < 1ms latency | 20% |
| YAML Compliance Engine | Hot-reloadable RBI rules — new circular live in 5 seconds | 20% |

**Formula (small, bottom):** composite = 0.30 × pattern + 0.30 × classifier + 0.20 × anomaly + 0.20 × compliance

---

## Slide 6 — Live Demo

**Headline:** Everything You Just Heard Is Running Right Now

Two-column layout:

Left — screenshot of 3D graph with orange fraud clusters (from dashboard)
Right — screenshot of an alert card with SHAP attribution + Gemini explanation

Below: Screenshot of STR PDF (cover page visible) + Copilot interface with a NL query

**Caption:** Live at trace-ai-4xnj5ovp4a-uc.a.run.app · 542 accounts · 5,049 transactions · 5 fraud rings detected

---

## Slide 7 — Built vs. Planned

**Headline:** Honest Assessment — What Is Live Today

Two-column table:

| LIVE IN POC | PLANNED (Phase 3) |
|---|---|
| NetworkX graph engine | Neo4j production graph |
| 5 AML pattern detectors | CBS live API integration |
| XGBoost classifier (AUC > 0.99) | Real-bank retraining on CBS feeds |
| River streaming anomaly scorer | RBAC with MLRO audit trails |
| YAML compliance engine (hot-reload) | Multi-branch deployment |
| SHAP TreeExplainer attribution | Automated regulatory reporting |
| Gemini 2.5 Flash narrative | |
| NL Investigation Copilot | |
| FIU-IND STR PDF generator | |
| 3D dashboard + WebSocket alerts | |
| Google Cloud Run deployment | |

---

## Slide 8 — Impact

**Headline:** The Numbers That Matter to a Compliance Officer

Three before/after blocks:

- **False Positives:** 95% (rule-only) → Target < 15% (four-signal fusion)
- **STR Prep Time:** 4–6 hours (manual) → Under 5 minutes (one click)
- **Detection Depth:** Single transaction → Multi-hop chains at depth 6

**PS3 minimum met:** Graph of fund flows + flagged patterns + ML-flagged subgraphs — all three running live.

---

## Slide 9 — Team

**Headline:** Team NamoFans · IIT Kharagpur

Four member blocks:
- **Animesh Raj** — Lead, Backend + ML
- **Devansh Gupta** — Member
- **Prem Agarwal** — Member
- **Faizan Khan** — Member

**Hackathon:** iDEA 2.0 (PSBs Hackathon Series 2026) · Problem Statement 3: Fund Flow Tracking
**Institute:** IIT Kharagpur

---

## Slide 10 — MANDATORY END SLIDE: All Deliverables

**Headline:** All Deliverables — iDEA 2.0 Round 2

> This slide is required by the portal. List every D1–D5 link.

| ID | Deliverable | Link |
|---|---|---|
| D1 | Problem + Solution Brief | [Google Drive link — paste after upload] |
| D2 | Live Deployed URL | https://trace-ai-4xnj5ovp4a-uc.a.run.app |
| D2 | Frontend-Backend Demo Video | [YouTube Unlisted link — paste after recording] |
| D3 | Technical Architecture | [Google Drive link — paste after upload] |
| D4 | GitHub Repository | https://github.com/wildcraft958/namofans-trace-ai |
| D5 | Pitch Deck (this deck) | [Google Slides link — paste after sharing] |
| D5 | Pitch Video | [YouTube Unlisted link — paste after recording] |

**Contact:** animeshraj958@gmail.com · ideahackathon.com

---

## Notes for Building the Deck

- Use the same template format as your Round 1 PPT (same branding, colors, font)
- Brand colors: orange (#F97316) primary, dark background for contrast
- Keep each slide to one idea — max 5 bullet points per slide
- Slide 6 (Demo) should use actual screenshots from the live system
- Slide 10 links: fill in after each deliverable is finalized and shared
- Set sharing: Anyone with the link → Viewer before submitting
- Test the link in incognito before pasting in portal
