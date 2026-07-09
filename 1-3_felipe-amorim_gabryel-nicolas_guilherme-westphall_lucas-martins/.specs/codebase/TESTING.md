# Testing

**Analyzed:** 2026-07-09

## Current State

- No automated test framework is configured.
- Frontend has a build gate: `npm run build` from `frontend`.
- Backend does not exist yet, so backend tests and gates must be introduced with implementation.

## Test Coverage Matrix

| Layer | Required Test Type | Current Command | Planned Command | Parallel-Safe |
| --- | --- | --- | --- | --- |
| Data prep | unit/integration | Not available | `python -m pytest` | Yes, once pytest exists |
| Risk tool | unit | Not available | `python -m pytest` | Yes, once pytest exists |
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
python -m pytest
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
- Backend automated tests: 0.
- Build gate exists but no test assertions yet.
