# Modelo ML + MLflow Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user — do not proceed without it.**

---

**Design**: `.specs/features/modelo-ml-mlflow/design.md`
**Status**: In Progress — Batch 1 (T1–T7) dispatched

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec — confirm before Execute. Guidelines found: none (global CLAUDE.md: minimal comments) — strong defaults applied. Sampled: `backend/tests/test_risk_tool.py`, `test_agent.py`, `test_api.py`, `test_evaluate.py`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Domain logic (`feature_encoding`, `model_risk_tool`, `mlflow_tracking`, `evaluate` extension) | unit | All branches; 1:1 to spec ACs; every listed edge case | `backend/tests/test_*.py` | `cd backend && ./.venv/bin/python -m pytest -q` |
| Training script (`train_model`) | unit | Pipeline builds; trains on fixture → loadable model, proba ∈ [0,1] | `backend/tests/test_train_model.py` | `cd backend && ./.venv/bin/python -m pytest -q` |
| API composition (`api._build_default_agent`) | integration | Model-mode + fallback-mode selection, happy + degradation | `backend/tests/test_api.py` | `cd backend && ./.venv/bin/python -m pytest -q` |
| Real-data evidence (train + eval run) | none (evidence gate) | Real numbers recorded; recall > 5.5% + bands ordered asserted on 96k | — | manual run, numbers captured in artifact |
| Config (`requirements-ml.txt`, `docker-compose.yml`, README) | none | build gate only | — | build gate only |

## Gate Check Commands

> Generated from codebase — confirm before Execute.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests | `cd backend && ./.venv/bin/python -m pytest -q` |
| Full | After tasks touching API/eval | `cd backend && ./.venv/bin/python -m pytest -q` |
| Build | After config/compose tasks | `cd backend && ./.venv/bin/python -m pytest -q` + `python -m app.train_model --help` / `docker compose config` |

Baseline: **68 tests** currently pass — no task may reduce this count.

---

## Execution Plan

### Phase 1: Foundation (deps + shared encoding)

```
T1 → T2
```

### Phase 2: Model core (train + risk tool)

```
T2 → T3 → T4
```

### Phase 3: Eval, MLflow, API wiring

```
T4 → T5 → T6 → T7
```

### Phase 4: Evidence + packaging

```
T3,T6 → T8
T4,T7 → T9 → T10
```

---

## Task Breakdown

### T1: Isolate ML dependencies ✅ DONE

**What**: Add `requirements-ml.txt` with pinned `scikit-learn`, `joblib`, `mlflow`; install into the venv so ML modules import.
**Where**: `backend/requirements-ml.txt` (new)
**Depends on**: None
**Reuses**: `backend/requirements.txt` format
**Requirement**: ML-04 (dep isolation)

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [x] `requirements-ml.txt` pins exact `scikit-learn==1.9.0` (for joblib load stability), `joblib`, `mlflow`.
- [x] API `requirements.txt` is unchanged (no sklearn/mlflow leak).
- [x] `./.venv/bin/pip install -r requirements-ml.txt` succeeds; `python -c "import sklearn, joblib, mlflow"` works.
- [x] Gate passes: `cd backend && ./.venv/bin/python -m pytest -q` (68 tests, unchanged).

**Tests**: none (config) · **Gate**: build

---

### T2: Shared train/serve feature encoding ✅ DONE

**What**: One module mapping both `OrderFeature` and `OrderInput` to the identical feature vector, `sellers_count` excluded.
**Where**: `backend/app/feature_encoding.py` (new) + `backend/tests/test_feature_encoding.py`
**Depends on**: None
**Reuses**: derivation logic mirrored from `data_prep.build_order_features`; `schemas.OrderInput`, `data_prep.OrderFeature`
**Requirement**: ML-02

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [x] `FEATURE_COLUMNS`, `CATEGORICAL_COLUMNS`, `features_from_order_feature`, `features_from_order_input` implemented.
- [x] Test: a matched `OrderFeature`/`OrderInput` pair encodes to an equal vector (ML-02 AC-1).
- [x] Test: `sellers_count` never appears in the vector (ML-02 AC-2).
- [x] Test: missing `OrderInput` fields (no timestamp/dates/money) → `None`, no exception; `promised_days` absent when dates missing.
- [x] Gate passes; test count increases (no deletions). 71 pass.

**Tests**: unit · **Gate**: quick

---

### T3: Model training script ✅ DONE

**What**: Build the calibrated pipeline and a `train()` that persists `model.joblib`, with optional MLflow model registration.
**Where**: `backend/app/train_model.py` (new) + `backend/tests/test_train_model.py`
**Depends on**: T2
**Reuses**: `feature_encoding`, `data_prep.load_prepared_features`, `mlflow_tracking` (T5 optional hook — guarded, no hard dep)
**Requirement**: ML-03, ML-07, MLF-02

**Tools**: MCP: NONE · Skill: `tlc-spec-driven` · (Context7 optional: sklearn `HistGradientBoostingClassifier`/`CalibratedClassifierCV` API)

**Done when**:

- [x] `build_pipeline()` returns `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-2)` on categoricals → `CalibratedClassifierCV(HistGradientBoostingClassifier(categorical_features=…), method="isotonic", cv=5)`.
- [x] `train(prepared_path, model_path)` fits on features/target and `joblib.dump`s the pipeline.
- [x] Runnable as `python -m app.train_model`.
- [x] Test: trains on a small in-memory fixture → dumped model loads and `predict_proba` returns values ∈ [0,1].
- [x] Test: MLflow registration is skipped cleanly when `mlflow_tracking.enabled()` is false.
- [x] Gate passes; test count increases. 73 pass.

**Tests**: unit · **Gate**: quick

---

### T4: ModelRiskTool (compose + graceful fallback)

**What**: Risk tool that takes the number from the model and evidence from the historical tool; degrades to historical on any model failure.
**Where**: `backend/app/model_risk_tool.py` (new) + `backend/tests/test_model_risk_tool.py`
**Depends on**: T2
**Reuses**: `HistoricalRiskTool`, `risk_tool._risk_level`, `schemas.RiskEvidence.model_copy`, `feature_encoding.features_from_order_input`
**Requirement**: ML-01, ML-04, ML-05

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [ ] `estimate_delay_risk(order)`: `ev = historical.estimate`; if model present, override `risk_score`/`risk_level` (via `_risk_level(p)`) and prepend a "score do modelo calibrado: …" factor; else return `ev` unchanged.
- [ ] `from_paths(prepared_path, model_path)`: guarded import — missing sklearn/joblib **or** missing/corrupt model file → `model=None` (never raises).
- [ ] Test: with a model, score comes from the model and `risk_level` matches `_risk_level(p)` (ML-01).
- [ ] Test: `factors`/`segment_used`/`sample_size` preserved from historical so the output guardrail passes (ML-05).
- [ ] Test: `model=None`, missing file, and corrupt file each fall back to historical output (ML-04).
- [ ] Test: order missing optional fields still returns a model score (no fallback from missing fields alone).
- [ ] Gate passes; test count increases.

**Tests**: unit · **Gate**: quick

---

### T5: MLflow tracking wrapper (optional/no-op)

**What**: Guarded MLflow wrapper that logs eval runs when configured and no-ops otherwise.
**Where**: `backend/app/mlflow_tracking.py` (new) + `backend/tests/test_mlflow_tracking.py`
**Depends on**: T1
**Reuses**: `evaluate.EvalReport`
**Requirement**: MLF-01

**Tools**: MCP: NONE · Skill: `tlc-spec-driven` · (Context7 optional: mlflow tracking API)

**Done when**:

- [ ] `enabled()` returns true only if `MLFLOW_TRACKING_URI` set **and** `mlflow` importable.
- [ ] `log_eval_run(report, params)` logs metrics+params when enabled; no-op when disabled.
- [ ] Test: `enabled()` false when env unset (MLF-01 AC-3); `log_eval_run` no-ops without error.
- [ ] Test: with a temp `file:` tracking URI, a run is recorded (metric readable back).
- [ ] Gate passes; test count increases.

**Tests**: unit · **Gate**: quick

---

### T6: evaluate.py — model scorer + JSON artifact + per-state

**What**: Add `--scorer model` (out-of-fold predictions), `--json-out`, per-state reuse, and MLflow hook.
**Where**: `backend/app/evaluate.py` (modify) + `backend/tests/test_evaluate.py`
**Depends on**: T3, T5
**Reuses**: `compute_report`, `render_report`, per-state aggregation; `feature_encoding`; `sklearn.model_selection.cross_val_predict`; `mlflow_tracking`
**Requirement**: ML-06, ML-08, MLF-01

**Tools**: MCP: NONE · Skill: `tlc-spec-driven` · (Context7 optional: `cross_val_predict`)

**Done when**:

- [ ] `--scorer {historical,model}` (default historical); model path uses `cross_val_predict(cv=5, method="predict_proba")` for out-of-fold probs → `_risk_level` → existing `compute_report`.
- [ ] `--json-out` dumps the full `EvalReport` (overall + per-band + per-state + alarm TP/FP/FN) to JSON.
- [ ] Model report includes the per-customer-state breakdown (ML-08 AC-1).
- [ ] Test: model scorer on a fixture produces an `EvalReport` with per-state entries and a written JSON artifact (ML-08 AC-1/AC-2).
- [ ] Test: a bands-ordered helper (high > medium > low observed rate) exists and is asserted (ML-06 AC-3 mechanics).
- [ ] Test: `log_eval_run` invoked (no-op when disabled) without breaking the run.
- [ ] Gate passes; test count increases.

**Tests**: unit · **Gate**: full

---

### T7: Wire model into the API composition root

**What**: `_build_default_agent` selects `ModelRiskTool` when `MODEL_PATH` is set and loadable; else `HistoricalRiskTool`. `agent.py` untouched.
**Where**: `backend/app/api.py` (modify) + `backend/tests/test_api.py`
**Depends on**: T4
**Reuses**: `_build_default_agent`, `ModelRiskTool.from_paths`
**Requirement**: ML-01, ML-04

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [ ] `MODEL_PATH` set + loadable → agent uses `ModelRiskTool`; unset/unloadable → `HistoricalRiskTool`; API contract unchanged.
- [ ] Test: with a tiny trained model on disk + `MODEL_PATH`, `/predict-delay` returns a model-sourced score with non-empty evidence factors.
- [ ] Test: `MODEL_PATH` unset → historical path, endpoint still 200.
- [ ] Gate passes; test count increases (≥68 + all new).

**Tests**: integration · **Gate**: full

---

### T8: Generate real report evidence (train + both evals)

**What**: Build prepared data if absent, train the real model, run both scorers, capture the committed comparison artifacts.
**Where**: `backend/data/model.joblib` (gitignored), `backend/data/eval_historical.json` + `eval_model.json` (committed), evidence note
**Depends on**: T3, T6
**Reuses**: `prepare_data`, `train_model`, `evaluate --scorer … --json-out`
**Requirement**: ML-06 (AC-2 real outcome), ML-08 (AC-3 committed artifacts)

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [ ] `prepared_orders.jsonl` exists (built if missing) and model trained on real data.
- [ ] `eval_historical.json` and `eval_model.json` produced and committed.
- [ ] Recorded: model high-alarm recall **> 5.5%** and bands ordered (high > medium > low). **If the bar is not met, STOP and escalate** (tune within reason, or record as an honest documented limitation) — never silently pass.
- [ ] Per-state comparison (baseline vs model) captured for the ethics section.

**Tests**: none (evidence gate) · **Gate**: build (real-run numbers recorded)

---

### T9: Optional MLflow service in Docker Compose

**What**: Add an `mlflow` service under `profiles: [mlflow]`; API/frontend start without it.
**Where**: `backend/../docker-compose.yml` (modify)
**Depends on**: T4, T7
**Reuses**: existing compose services
**Requirement**: MLF-03

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [ ] `docker compose config` valid; `mlflow` service gated behind `profiles: [mlflow]`.
- [ ] Without the profile, no mlflow container is created and the API serves predictions.
- [ ] With the profile, the mlflow server is reachable and eval can point at it.

**Tests**: none (config) · **Gate**: build (`docker compose config`)

---

### T10: Document train/eval/MLflow usage + deployment modes

**What**: Update backend README with train/eval/MLflow commands and the model-enabled vs fallback deployment modes (Render reality).
**Where**: `backend/README.md` (modify)
**Depends on**: T9
**Reuses**: existing README structure
**Requirement**: ML-07, ML-04 (deployment doc)

**Tools**: MCP: NONE · Skill: `tlc-spec-driven`

**Done when**:

- [ ] Documented: `python -m app.train_model`, `evaluate --scorer model --json-out`, enabling MLflow, and the two deploy modes (with/without sklearn+model).
- [ ] Reproducible retrain command documented (ML-07).

**Tests**: none (docs) · **Gate**: build

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 1:  T1 ──→ T2
Phase 2:  T2 ──→ T3 ──→ T4
Phase 3:  T4 ──→ T5 ──→ T6 ──→ T7
Phase 4:  (T3,T6) ──→ T8 ;  (T4,T7) ──→ T9 ──→ T10
```

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1: requirements-ml.txt | 1 config file | ✅ Granular |
| T2: feature_encoding | 1 module | ✅ Granular |
| T3: train_model | 1 script | ✅ Granular |
| T4: model_risk_tool | 1 module | ✅ Granular |
| T5: mlflow_tracking | 1 module | ✅ Granular |
| T6: evaluate extension | 1 file (modify) | ✅ Granular |
| T7: api composition | 1 function (modify) | ✅ Granular |
| T8: real evidence run | run + 2 artifacts | ✅ Cohesive (one evidence deliverable) |
| T9: compose mlflow | 1 file (modify) | ✅ Granular |
| T10: README | 1 file (modify) | ✅ Granular |

## Diagram-Definition Cross-Check

| Task | Depends On (body) | Diagram Shows | Status |
| ---- | ----------------- | ------------- | ------ |
| T1 | None | — | ✅ |
| T2 | None | — | ✅ |
| T3 | T2 | T2→T3 | ✅ |
| T4 | T2 | T2→T4 | ✅ |
| T5 | T1 | (Phase 3 start, needs deps from T1) | ✅ |
| T6 | T3, T5 | T5→T6 (and T3 via Phase 2) | ✅ |
| T7 | T4 | T6→T7 chain; T7 needs T4 | ✅ |
| T8 | T3, T6 | (T3,T6)→T8 | ✅ |
| T9 | T4, T7 | (T4,T7)→T9 | ✅ |
| T10 | T9 | T9→T10 | ✅ |

> Note: T5 depends on T1 (deps) not T4; it is placed in Phase 3 for cohesion but has no backward-crossing violation (T1 is Phase 1). T7 depends on T4 (Phase 2), consumed after T6 — backward/within-phase only. No forward dependencies.

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| ---- | ---------- | --------------- | --------- | ------ |
| T1 | config | none | none | ✅ |
| T2 | domain logic | unit | unit | ✅ |
| T3 | training script | unit | unit | ✅ |
| T4 | domain logic | unit | unit | ✅ |
| T5 | domain logic | unit | unit | ✅ |
| T6 | domain logic | unit | unit | ✅ |
| T7 | API composition | integration | integration | ✅ |
| T8 | evidence run | none (evidence gate) | none | ✅ |
| T9 | config | none | none | ✅ |
| T10 | docs | none | none | ✅ |

---

## Requirement Coverage

| Requirement | Task(s) |
| ----------- | ------- |
| ML-01 | T4, T7 |
| ML-02 | T2 |
| ML-03 | T3 |
| ML-04 | T1, T4, T7 |
| ML-05 | T4 |
| ML-06 | T6, T8 |
| ML-07 | T3, T10 |
| ML-08 | T6, T8 |
| MLF-01 | T5, T6 |
| MLF-02 | T3 |
| MLF-03 | T9 |

All 11 requirements mapped. No unmapped requirements.
