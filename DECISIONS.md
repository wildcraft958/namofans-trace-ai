# Architecture Decision Record

Lightweight ADRs. New decisions go at the bottom. Don't edit accepted ADRs in place — add a new one that supersedes.

---

## ADR-0001 — Pragmatic Flagship build strategy
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Phase 2 has ~3 weeks of build time. PS3 has ~32 shortlisted teams. We can either ship all 8 modules ambitiously (high risk of breakage) or trim hard (loses differentiation).

**Decision.** Pragmatic Flagship: ship 6 polished modules end-to-end + 4 magical differentiators (FIU-IND STR auto-gen, GNNExplainer + SHAP, NL Investigation Copilot, Live retraining demo). Defer full TGN training to v2; ship GraphSAGE + temporal features instead.

**Consequences.** Lower ML ceiling than a full TGN, but every claim is measurable. Demo story stays tight. Team can rehearse the 4-minute walkthrough.

---

## ADR-0002 — GraphSAGE for Phase 2, TGN deferred to v2
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Phase 1 PPT promised a Temporal Graph Network. TGN is non-trivial to train; if it doesn't converge in time, our strongest claim collapses.

**Decision.** Ship GraphSAGE + handcrafted temporal features (time-since-last-txn, txn velocity per account, dormancy delta). Disclose this honestly in `MODEL_CARD.md` and frame the full TGN as the v2 roadmap item.

**Consequences.** Less novel. But achievable AUC ≥ 0.85 measured on AMLSim is more credible than a target AUC ≥ 0.95 with no proof. Honest disclosure wins judge trust.

**Reversal trigger.** If TGN training converges by Day 12 with measured AUC ≥ 0.90, swap it in. Otherwise, ship GraphSAGE.

---

## ADR-0003 — NetworkX for prototype, Neo4j only as a roadmap line
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Production scale wants Neo4j + GDS. Hackathon scale (5K accounts, 100K txns) fits in NetworkX memory comfortably and is easier to build/test against.

**Decision.** All Phase 2 code uses NetworkX MultiDiGraph. Neo4j is named in slides and `solution.md` as the v2 deployment path. No Neo4j containers in `docker-compose.yml`.

**Consequences.** Faster builds, simpler deploys, no Neo4j licensing surface. We lose horizontal scale stories but gain demo reliability.

---

## ADR-0004 — IBM AMLSim as the only data source
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Real bank data is unavailable. Need labeled, realistic, regulator-recognized synthetic data.

**Decision.** Use IBM AMLSim (github.com/IBM/AMLSim) as the primary dataset, augmented with `Faker(en_IN)` for IFSC codes, account types, and KYC fields. Use the Kaggle pre-generated AMLSim dump (10K users × 1.32M txns) as a fallback if local generation is slow on Day 1. Do not blend with PaySim or Elliptic for Phase 2.

**Consequences.** Realistic Indian banking signals + zero privacy risk + reproducible benchmarks judges recognize.

---

## ADR-0005 — FIU-IND STR PDF as the headline differentiator
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** ~32 teams on PS3. Most will ship a graph + GNN + dashboard. Almost no one will build a real regulatory deliverable.

**Decision.** Auto-STR generation (Module H) is a P0 for Phase 2 — even if other ML modules slip. PDF must structurally match FIU-IND filing format (cover, masked subject, suspicious txns, fund trail, risk breakdown, AI narrative, recommended action, evidence metadata).

**Consequences.** This is the demo's most "this is real banking" moment. Templates referenced from RBI's e-filing manual (rbidocs.rbi.org.in/rdocs/content/Pdfs/68787.pdf).

---

## ADR-0006 — YAML hot-reloadable compliance rules over hardcoded checks
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** RBI updates KYC/AML circulars frequently. Hardcoded rules require redeploys.

**Decision.** Ship `compliance_rules.yaml` evaluated by a watchdog file watcher. Rule edits take effect within ~5 seconds without restart. First-match-wins evaluator with AND/OR operators.

**Consequences.** A small operational story that lands hard with banking judges. Cost: ~1 day of build.

---

## ADR-0007 — LiteLLM (GPT-4o-mini / Claude Haiku) for the LLM layer
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Need an LLM for alert explanation, NL→graph queries, and STR narratives. Local models too heavy for hackathon deploy.

**Decision.** LiteLLM as the unified client. Default model: GPT-4o-mini (cheap, low latency). Fallback: Claude Haiku. All prompts template-constrained and grounded in graph evidence — no free-form generation that could hallucinate accounts.

**Consequences.** External API dependency during demo. Mitigation: pre-cache 6 canned NL queries; deterministic fallback paths. Keep API keys out of git (`.env.example` only).

---

## ADR-0008 — Demo reliability over feature breadth
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Live demos fail. Judges remember crashes more than features.

**Decision.** Pre-record GIFs of every demo step. Deploy to two providers (Vercel for frontend, Render or Railway for backend). Have a backup laptop with the same env loaded. Rehearse the 4-min sequence ≥10 times before submission.

**Consequences.** A few hours of demo-rigging work. High EV vs the cost of a failed live demo.

---

## ADR-0009 — Out-of-scope items locked
**Date**: 2026-05-04 · **Status**: Accepted

**Context.** Scope creep is the #1 hackathon killer.

**Decision.** The following are explicitly out of scope for Phase 2 (re-stated in `CLAUDE.md`):
- Full TGN training
- Neo4j production integration
- Federated learning / edge deployment
- Adversarial robustness
- Real bank data integration
- Multi-tenant / multi-bank support

Any future Claude session or teammate proposing to add one of the above must open a new ADR overriding this one.

**Consequences.** Saved hours. Tighter narrative. Accepted opportunity cost on novelty axes others may chase (Kartavya = federated, RAW = adversarial). We win on regulatory IQ + demo polish instead.
