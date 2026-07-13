# Code Conventions

**Analyzed:** 2026-07-13

## Naming

- Python modules and functions use `snake_case`; classes and Pydantic models use `PascalCase`.
- Private Python helpers use a leading underscore, for example `_build_prompt` and `_safe_evidence`.
- React components use `PascalCase`; functions, hooks state and local constants use `camelCase`.
- API payload properties use `snake_case`, matching the backend contract and Olist terminology.
- Tests use `test_<behavior>` names under `backend/tests/test_<module>.py`.

## Backend Organization

- Each module owns one concern: schema, preparation, feature encoding, scoring, explanation policy, LLM boundary, orchestration or HTTP API.
- Imports follow standard library, third-party and local application groups.
- Pydantic models define public contracts and validation; frozen dataclasses represent internal results.
- Optional integrations are isolated behind narrow boundaries: MLflow calls no-op when disabled, and model/LLM failures have deterministic fallbacks.
- Errors returned by the API are friendly and do not expose raw stack traces; internal failures are logged with structured event metadata.

## Frontend Organization

- `App.jsx` owns the dashboard state and presentational helper components; `api.js` owns HTTP and warm-up behavior.
- Immutable state updates use functional `setState` calls and array mapping.
- Formatting and payload conversion remain small pure helpers near the bottom of `App.jsx`.
- Styling uses semantic class names in one global stylesheet and responsive media queries, without a component library.

## Tests and Documentation

- Backend tests rely on isolated fixtures, temporary paths and monkeypatching; provider calls are mocked.
- Test modules mirror application modules.
- Project decisions and task traceability live under `.specs`; operational/report documentation lives in the project `README.md` and `backend/README.md`.

## Known Variations

- Frontend source and deterministic Portuguese messages mostly omit accents, following the established project style.
- Python dependency files use a mix of exact and lower-bound versions; scikit-learn is exact because serialized models require version compatibility.
