# Testing

**Analyzed:** 2026-07-13

## Current State

- Backend automated tests are configured with pytest.
- Frontend has a build gate: `npm run build` from `frontend`.
- Backend has a full gate with 93 collected tests. Because collection imports the ML modules, install both `requirements.txt` and `requirements-ml.txt`.

## Test Coverage Matrix

| Layer | Required Test Type | Current Command | Planned Command | Parallel-Safe |
| --- | --- | --- | --- | --- |
| Data prep | unit/integration | `./.venv/bin/pytest` | `python -m pytest` | Yes |
| Risk tool | unit | `./.venv/bin/pytest` | `python -m pytest` | Yes |
| Agent/API | unit/integration | `./.venv/bin/python -m pytest -q` | same | Yes (fixtures are isolated) |
| Frontend components | build/smoke | `npm run build` | `npm run build` | Yes |
| Docker/deploy | smoke | Not available | `docker compose up` smoke check | No |

## Gate Check Commands

**Current frontend build gate:**

```bash
cd frontend
npm run build
```

**Backend gate:**

```bash
cd backend
./.venv/bin/python -m pytest -q
```

**Full local gate:**

```bash
cd frontend
npm run build
cd ../backend
./.venv/bin/python -m pytest -q
```

## Test Strategy

- Data prep tests should verify target creation, leakage exclusion and aggregate feature correctness on small fixtures.
- Risk tool tests should verify fallback order, risk bands and confidence behavior for sparse groups.
- API tests should verify valid input, invalid input, fallback response and no raw stack traces.
- Frontend gate should verify the product builds after API integration.
- Manual UAT is required for the dashboard because explanation clarity and operator workflow are user-facing.

## Test Count Baseline

- Frontend automated tests: 0.
- Backend automated tests: 93 collected before the final refinements.
- Build gate exists but no test assertions yet.
