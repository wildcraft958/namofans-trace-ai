# SECURITY.md

## Threat model

TRACE.ai handles sensitive transaction graphs. Even on synthetic data, treat the system as if real banking data flows through it.

## Privacy / data hygiene

- Account numbers are masked in all logs, dashboards, and STR PDFs (last 4 digits only).
- LLM prompts are template-constrained; full account details are never sent to the LLM provider — only deterministic summaries.
- AMLSim output is synthetic, but follow real-data rules anyway: no commits of `data/raw/`, no copy/paste into chat tools.

## Authentication

- Phase 2 prototype: no auth — for demo only. Document this clearly in the README and demo narration.
- v2 (post-hackathon): RBAC with roles (analyst, supervisor, MLRO, admin). All actions audited to `audit.db`.

## Audit trail

- Every alert acknowledgement, STR generation, and copilot query writes to a SQLite audit log (`audit.db`).
- Audit log is append-only; rotated daily in production.

## Encryption

- Phase 2: at-rest encryption deferred. Demo only.
- v2: AES-256 at rest, TLS 1.3 in transit, per RBI Master Direction on Information Security.

## Secrets

- LLM API keys live in `.env` (gitignored). Never commit.
- Use `.env.example` to document new env vars.
- If a key is ever committed, rotate immediately and remove from git history with explicit team lead approval.

## Reporting

If a teammate finds a security issue, ping the team lead privately first. Do not file public issues with reproducer details.
