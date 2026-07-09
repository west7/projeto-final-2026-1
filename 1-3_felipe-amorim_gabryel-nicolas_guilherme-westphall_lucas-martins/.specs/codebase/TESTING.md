# Testing

**Analyzed:** 2026-07-09

## Current State

- Backend automated tests are configured with pytest.
- Frontend has a build gate: `npm run build` from `frontend`.
- Backend has a quick/full gate: `./.venv/bin/pytest` or `python -m pytest` from `backend` after dependencies are installed.

## Test Coverage Matrix

| Layer | Required Test Type | Current Command | Planned Command | Parallel-Safe |
| --- | --- | --- | --- | --- |
| Data prep | unit/integration | `./.venv/bin/pytest` | `python -m pytest` | Yes |
| Risk tool | unit | `./.venv/bin/pytest` | `python -m pytest` | Yes |
| Agent/API | integration | Not available | `python -m pytest` plus API smoke test | No until API fixture is isolated |
| Frontend components | build/smoke | `npm run build` | `npm run build` | Yes |
| Docker/deploy | smoke | Not available | `docker compose up` smoke check | No |

## Gate Check Commands

**Current frontend build gate:**

```bash
cd frontend
npm run build
```

**Planned backend gate:**

```bash
cd backend
./.venv/bin/pytest
```

**Planned full gate:**

```bash
cd frontend
npm run build
cd ../backend
python -m pytest
```

## Test Strategy

- Data prep tests should verify target creation, leakage exclusion and aggregate feature correctness on small fixtures.
- Risk tool tests should verify fallback order, risk bands and confidence behavior for sparse groups.
- API tests should verify valid input, invalid input, fallback response and no raw stack traces.
- Frontend gate should verify the product builds after API integration.
- Manual UAT is required for the dashboard because explanation clarity and operator workflow are user-facing.

## Test Count Baseline

- Frontend automated tests: 0.
- Backend automated tests: 48.
- Build gate exists but no test assertions yet.
