# Contributing — TRACE.ai

Hackathon team rules. Keep it simple, ship fast, don't break the demo.

## Branching

- `main` is the deployable branch. All PRs go through CI.
- Feature branches: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
- Keep branches short-lived. Aim for <2 days from branch to merge.

## Commit messages

Conventional commit style:

- `feat: add NL copilot canned-query cache`
- `fix: handle empty subgraph in GNNExplainer`
- `docs: add MODEL_CARD calibration plot`
- `test: pattern detectors edge cases`
- `refactor: split risk fusion into pure function`

**Never add Claude as a co-author.**
**Never `git add -A`** — stage specific files. We have AMLSim data and `.env` floating around; an accidental `git add .` is a disaster.

## Pull requests

- Title: 1 line, imperative, plain language.
- Body: 1 paragraph "what + why" + a bulleted "how to test."
- Tag a reviewer (any teammate). PRs without review get blocked merging.
- Squash merge.

## Tests

- Add a unit test alongside any new detection logic in `tests/unit/`.
- API endpoints get a smoke test in `tests/integration/`.
- Run `pytest -q` locally before pushing.
- Frontend: run `npm run typecheck` before pushing.

## Lint

- Python: `ruff check src tests`. Auto-fix with `ruff check --fix`.
- TypeScript: `npm run lint`.
- Pre-commit hook recommended (`pip install pre-commit && pre-commit install` once we add a config).

## Out-of-scope reminders

Do not add (without an ADR in `DECISIONS.md`):
- Full TGN training
- Neo4j integration
- Federated / edge learning
- Adversarial robustness
- Real bank data feeds
- Multi-tenancy

If it didn't appear in the Phase 1 PPT, run it past the team before adding.

## Deploy

- Backend: Render or Railway free tier. URL goes in `README.md`.
- Frontend: Vercel. URL goes in `README.md`.
- Don't deploy from a feature branch — only from `main` after merge.

## Demo discipline

- **Do not refactor mid-week**. Stability beats elegance during demo prep.
- After Day 16 (rehearsal day), only bug fixes — no new features.
- Pre-record GIFs of every demo step. They are the safety net.

## Secrets

- All secrets in `.env` (gitignored).
- Use `.env.example` as the template — keep it up to date when adding new env vars.
- LLM API keys: ask the team lead. Never paste in chat or code.

## Data hygiene

- Never commit `data/raw/`, `data/processed/`, `data/checkpoints/`.
- `data/sample/` is for tiny fixtures used by tests only (≤100 rows).
- AMLSim output regenerates; treat it as ephemeral.

## Questions

Ping the team lead. If unsure about an out-of-scope item, default to **don't add it**.
