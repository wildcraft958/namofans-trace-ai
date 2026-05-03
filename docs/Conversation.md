
# TRACE.ai — Planning Conversation Summary
## iDEA Hackathon 2.0 | PS3 | Archived: March 29, 2026

> This file is a cleaned-up summary of the planning conversation. The full solution is in `solution.md`.
> Slide content is in `PPT.md`. Build plan + repo map is in `PLAN.md`. One-page summary is in `one_page_summary.md`.

---

## KEY DECISIONS MADE

### Problem Statement
Selected **PS3 — Tracking of Funds within Bank for Fraud Detection**
- Assessed as top-3 contender among all PS tracks
- Estimated ~35–45% shortlist probability, ~5–9% win probability overall
- Stronger than PS4 (Churn) by 4–7x win probability

### Project Name & Positioning
**TRACE.ai — Transaction Risk Analysis & Compliance Engine**
Tagline: *Graph-Powered Fund Flow Intelligence for Anti-Money Laundering*

### Core Architecture Decision
Model every transaction as an **edge in a dynamic temporal directed graph** — not a static snapshot. Three detection modules in parallel: Pattern Matcher + Temporal GNN + Online Anomaly Scorer, fused with a Compliance Rule Engine.

### What Differentiates TRACE.ai (vs typical PS3 submissions)
Most teams: static graph + basic anomaly + dashboard.
TRACE.ai adds:
1. Temporal GNN with edge-centric modeling (ChronoWave-GNN inspired)
2. Online ML per-account streaming baselines (River — zero batch retraining)
3. Natural language investigation copilot (NL → graph query)
4. Automated FIU-IND STR generation (4 hrs → 5 min)
5. Hot-reloadable YAML compliance rule engine

---

## RESEARCH PAPERS IDENTIFIED (FINAL LIST)

| Paper | Use in TRACE.ai |
|---|---|
| Rossi et al., TGN (arXiv:2006.10637, 2020) | Core TGN architecture |
| GNN Fraud Detection Survey (arXiv 2024) | Justification for GNN approach |
| THG-OAFN, Wei & Lee (PLOS ONE, 2025) | GraphSMOTE + attention fusion, AUC 96.56% |
| ChronoWave-GNN (PMC, 2026) | Edge-centric temporal modeling, wavelet features |
| Elliptic2 / Shape of Money Laundering (2024) | Subgraph typology motifs |
| BIS WP 1188 — LVPS Anomaly (2023) | Two-layer anomaly framework |
| Real-time TGNN Cross-border Payments (2025) | 37% FP reduction stat (Slide 7) |
| PPATK Typology Detection (2025) | Module A graph metric justification |
| Weber et al., Elliptic GNN (arXiv:1908.02591, 2019) | AML GNN baseline |

---

## CRITICAL CITATIONS FOR SLIDES (GAPS FIXED)

Three citations were missing from initial PPT.md and were added:
1. Real-time TGNN (2025) — needed to cite the "37% FP reduction" stat on Slide 7
2. PPATK Typology Detection (2025) — justifies Module A (Pattern Matcher)
3. TigerGraph + Graphable blogs — "real banks use this" narrative

---

## RISK SCORE WEIGHTS (FINAL)
```
composite_score = 0.30 × pattern + 0.30 × gnn + 0.20 × anomaly + 0.20 × compliance
CRITICAL ≥ 0.85 | HIGH ≥ 0.70 | MEDIUM ≥ 0.50 | LOW < 0.50
```

---

## SUBMISSION CHECKLIST (from conversation)
- [ ] Google Slides deck — 9 slides, slide titles NOT changed, HEADER slide unmodified
- [ ] One-page summary PDF → Google Drive → "Anyone with link can view" → paste on Slide 9
- [ ] YouTube pitch video — 3–4 min, screen recording + voiceover (target 3:30)
- [ ] Registration form — Project Title, PS3, tech stack, PPT URL, Video URL
- [ ] All links tested in incognito window before submission
- [ ] Team member names match portal registration

---

## COMPETITIVE RISK ASSESSMENT (from conversation)
| Risk | Likelihood | Note |
|---|---|---|
| Banking insider team with operational language | Low-Medium | Write Slide 5 in both engineering + operational terms |
| Team that simplifies brilliantly — 1 clean idea | Medium | Counter with clear visual architecture diagram |
| Slide design quality | High | ASCII art → proper boxes/arrows in Google Slides |

---

## FILES IN THIS DIRECTORY
| File | Purpose |
|---|---|
| `solution.md` | **Definitive technical specification** — read this for what we're building |
| `PLAN.md` | Build bible: full architecture, code structure, implementation guide |
| `PPT.md` | Complete slide content + video script (ready to paste into Google Slides) |
| `one_page_summary.md` | Mandatory 1-page PDF content (copy to Google Doc → export PDF → Drive) |
| `Conversation.md` | This file — planning conversation summary |
| `1772011847095-lqibn.pptx` | Original hackathon slide template |
| `1772011847095-lqibn.pdf` | Original hackathon problem statement PDF |
