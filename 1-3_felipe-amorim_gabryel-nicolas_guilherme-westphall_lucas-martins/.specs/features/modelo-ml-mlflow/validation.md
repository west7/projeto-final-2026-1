# Modelo ML + MLflow Validation

**Date**: 2026-07-13 (re-verification after fix iteration)
**Spec**: `.specs/features/modelo-ml-mlflow/spec.md`
**Diff range**: `ee93340..HEAD` (branch `feat/modelo-ml-mlflow`)
**Verifier**: independent sub-agent (author ≠ verifier), read-only over the real tree; mutations applied in scratch and restored via `git checkout`.

---

## Verdict

**PASS ✅** — all three gaps from the prior FAIL are closed and independently re-confirmed.
The two positive-path gaps now have discriminating tests; the discrimination gap (ML-01/AC2 level) now dies under mutation. A latent production bug found while adding the registration test was also fixed (see below). Gate green at **89 passed, 0 failed**.

### Prior gaps — closure status (re-verified independently)

| Gap | Fix | Re-check (scratch mutant) | Closed? |
| --- | --- | ------------------------- | ------- |
| **ML-01/AC2** level override not discriminated | `test_model_overrides_risk_level_to_model_band` — `_StubModel(p=0.05)` in `low`, historical `high`; asserts model band wins | Removed `"risk_level": _risk_level(p)` override → test FAILS (`high != low`) | ✅ |
| **MLF-02/AC2** registration positive path untested | `test_mlflow_registration_logs_when_enabled` — sqlite tracking URI; asserts `mlflow_logged is True` AND `search_model_versions("name='delay-risk'") ≥ 1` | (a) forced `if False and _mlflow_enabled()` → FAILS on flag; (b) renamed registry to `delay-risk-NOPE` → FAILS on `search_model_versions` — so the test locks the actual registration, not just the flag | ✅ |
| **ML-04** missing-sklearn/joblib branch untested | `test_missing_joblib_dependency_falls_back` — `monkeypatch.setitem(sys.modules,"joblib",None)`; asserts `model is None` + historical output | Narrowed `except Exception` → `except FileNotFoundError` → test FAILS (`ModuleNotFoundError` propagates), confirming the broad `except` is genuinely exercised | ✅ |

### Production fix during the iteration

`app/train_model.py:100-105` — `mlflow.sklearn.log_model(..., serialization_format="cloudpickle")`. The default `skops` serializer rejects the pipeline's custom `FunctionTransformer` (`_records_to_frame`) as an untrusted type, so the registration path was a **latent crash** never hit until the positive-path test exercised it. With cloudpickle the model registers cleanly (verified: `Created version '1' of model 'delay-risk'`). This is the only production-code change in the fix iteration; the rest are test-only.

---

## Task Completion

All T1–T10 marked ✅ Done in tasks.md; confirmed present in the diff surface (feature_encoding, train_model, model_risk_tool, mlflow_tracking, evaluate, api; requirements-ml.txt; docker-compose mlflow profile; README; committed eval JSONs).

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN → THEN) | Spec-defined outcome | `file:line` + assertion | Result |
| ----------------------- | -------------------- | ----------------------- | ------ |
| **ML-01/AC1** train → persisted calibrated artifact, OrderInput-only features | model file exists, `predict_proba` ∈ [0,1] | `tests/test_train_model.py:48-54` — `model_path.is_file()`, `all(0.0<=p<=1.0 for p in proba)` | ✅ PASS |
| **ML-01/AC2** model present → `risk_score`=calibrated prob, `risk_level`=model band (existing thresholds) | `risk_score==round(p,4)`, `risk_level==_risk_level(p)` | `tests/test_model_risk_tool.py:72-73` (score+level); `:77-89` `test_model_overrides_risk_level_to_model_band` — `_StubModel(0.05)`→`low` while historical `high`, asserts model band wins | ✅ PASS (M2 now killed — override discriminated) |
| **ML-01/AC3** model scores → factors/sample_size/segment_used from historical | historical evidence preserved | `tests/test_model_risk_tool.py:72-75` — `ev.segment_used==hist.segment_used`, `ev.sample_size==hist… and >0`, `hist.factors[0] in ev.factors` | ✅ PASS |
| **ML-01/AC4** optional fields absent → still scores, no fallback | model score returned, no error | `tests/test_model_risk_tool.py:107-108` — sparse order → `factors[0].startswith("score do modelo calibrado")` | ✅ PASS |
| **ML-02/AC1** matched OrderFeature/OrderInput → equal vector (price→total_price, freight→total_freight, derived fields) | dicts equal | `tests/test_feature_encoding.py:47` — `features_from_order_feature(f) == features_from_order_input(o)` | ✅ PASS (M4 killed) |
| **ML-02/AC2** `sellers_count` absent from vector | not in FEATURE_COLUMNS nor either dict | `tests/test_feature_encoding.py:52-54` — `"sellers_count" not in …` | ✅ PASS (M3 killed) |
| **ML-03** training artifact persists & loads | dumped pipeline loads, proba valid | `tests/test_train_model.py:40-54` | ✅ PASS |
| **ML-04** absent model → historical, never raises | `model is None`, output == historical | `tests/test_model_risk_tool.py:78-83` (`model=None`) | ✅ PASS |
| **ML-04** missing file → historical | `tool.model is None`, output == historical | `tests/test_model_risk_tool.py:88-91` | ✅ PASS |
| **ML-04** corrupt file → historical | `tool.model is None`, output == historical | `tests/test_model_risk_tool.py:98-101` | ✅ PASS |
| **ML-04** missing sklearn/joblib → historical | import guarded, no crash | `tests/test_model_risk_tool.py:92-102` `test_missing_joblib_dependency_falls_back` — `sys.modules["joblib"]=None` → `model is None` + output == historical | ✅ PASS (dedicated ImportError test; narrowing `except` kills it) |
| **ML-05** evidence factors preserved so guardrail passes | segment/sample_size/factors from historical | `tests/test_model_risk_tool.py:72-75` | ✅ PASS (M1 killed) |
| **ML-06/AC1** `--scorer model` reports recall/calibration/precision/fallback, same format | report renders | `tests/test_evaluate.py:97-99` render smoke + `:121-132` model scorer report | ✅ PASS |
| **ML-06/AC2** model recall strictly > baseline 5.5% | real-data outcome | `data/eval_model.json` high recall **0.376** > `data/eval_historical.json` **0.0546** (n=96470 both) | ✅ PASS (evidence gate) |
| **ML-06/AC3** bands monotone high>medium>low | calibration held | `tests/test_evaluate.py:117-118` mechanics (M5 killed); `eval_model.json` `bands_ordered=true`, high 0.322 > med 0.143 > low 0.039 | ✅ PASS |
| **ML-08/AC1** per-customer-state breakdown | states present in report | `tests/test_evaluate.py:124-125,131` — `{"RJ","BA"} <= states`, `by_state` entry present | ✅ PASS |
| **ML-08/AC2** machine-readable full EvalReport JSON | overall+bands+state+alarm TP/FP/FN | `tests/test_evaluate.py:128-132` — writes JSON, asserts `n`, `by_state`, `alarms.high.recall`; `report_to_dict` includes all sections | ✅ PASS |
| **ML-08/AC3** comparison reproducible from committed artifacts | two diff-able JSONs committed | `data/eval_historical.json` + `data/eval_model.json` present & diff-able | ✅ PASS (evidence gate) |
| **MLF-01/AC1** URI set + eval → logs metrics+params | run recorded, readable back | `tests/test_mlflow_tracking.py:34-36` — `runs.iloc[0]["metrics.fallback_rate"]==0.25`, `params.scorer=="model"` | ✅ PASS |
| **MLF-01/AC3** URI unset → no-op, no crash | `enabled()==False`, `log_eval_run` returns None | `tests/test_mlflow_tracking.py:19-20` | ✅ PASS |
| **MLF-01** eval invokes `log_eval_run` | called with params | `tests/test_evaluate.py:139-141` — `calls == [{"scorer":"historical","min_segment_size":5}]` | ✅ PASS |
| **MLF-02/AC2** training with MLflow → model logged/registered | positive registration path | `tests/test_train_model.py:57-66` skip path (`mlflow_logged is False`); `:69-83` `test_mlflow_registration_logs_when_enabled` — sqlite URI, `mlflow_logged is True` AND `search_model_versions("name='delay-risk'") ≥ 1` | ✅ PASS (both branches; registration locked by name) |
| **MLF-03** compose `mlflow` profile; API independent | service gated behind `profiles:[mlflow]` | `docker-compose.yml:31` `profiles: [mlflow]`; config gate only (no automated test) | ✅ PASS (config gate) |
| **ML-07** reproducible retrain command | `python -m app.train_model` documented | `train_model.main()` runnable + README (T10); no test (docs) | ✅ PASS (evidence/docs gate) |

**Status**: ✅ All AC-checks match spec outcome — the 3 prior gaps are closed.

---

## Discrimination Sensor — re-check on the 3 previously-weak areas

Scratch method: edit in place → run targeted test → `git checkout -- <file>` (tracked tree was clean; all reverts confirmed). This pass re-injects the 3 mutations that map to the fixed gaps. The prior pass's 6 mutations (M1/M3/M4/M5/M6 killed) are unchanged and not re-run.

| # | File:line | Mutation | Test run | Killed? |
| - | --------- | -------- | -------- | ------- |
| R1 | `model_risk_tool.py:39` | Remove `"risk_level": _risk_level(p)` override (was M2, prior **survivor**) | test_model_overrides_risk_level_to_model_band | ✅ Killed (`AssertionError: 'high' == 'low'`) |
| R2a | `train_model.py:94` | `if _mlflow_enabled()` → `if False and …` (skip registration) | test_mlflow_registration_logs_when_enabled | ✅ Killed (`mlflow_logged` False) |
| R2b | `train_model.py:103` | `registered_model_name="delay-risk"` → `"delay-risk-NOPE"` (register under wrong name) | test_mlflow_registration_logs_when_enabled | ✅ Killed (`search_model_versions("name='delay-risk'")` empty) |
| R3 | `model_risk_tool.py:55` | `except Exception` → `except FileNotFoundError` (stop catching ImportError) | test_missing_joblib_dependency_falls_back | ✅ Killed (`ModuleNotFoundError` propagates) |

**Result**: 3 gaps re-checked, all mutants **die** (R2b is a bonus sharper mutant proving the registration is locked by name, not just the boolean flag). The previously-surviving M2 is now killed by R1. No survivors.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code / no scope creep | ✅ Compose pattern keeps agent.py untouched; one shared encoding module |
| Surgical changes, matches patterns | ✅ Reuses `_risk_level`, `HistoricalRiskTool`, `compute_report`, `model_copy` |
| Spec-anchored outcome check | ✅ ML-01/AC2 level + MLF-02 positive path + ML-04 missing-dep now locked by discriminating assertions |
| Every test maps to an AC / edge case | ✅ No unclaimed tests |
| Documented guidelines | none — global CLAUDE.md (minimal comments) honoured; strong defaults applied |

---

## Edge Cases

- [x] Model file absent → historical fallback, no raise (test_model_risk_tool.py:88-91)
- [x] Model present but corrupt → historical fallback (test_model_risk_tool.py:98-101)
- [x] `mlflow`/`sklearn`/`joblib` not installed → historical fallback — dedicated ImportError test (test_model_risk_tool.py:92-102), discriminating (narrowing `except` kills it)
- [x] `customer_state`+`seller_state` present, no dates → still scores, `promised_days` None (test_feature_encoding.py:57-67 + test_model_risk_tool.py:104-108)

---

## Gate Check

- **Command**: `cd backend && ./.venv/bin/python -m pytest -q`
- **Result**: **89 passed, 0 failed, 0 skipped** (exit 0)
- **Test count**: 86 (prior verifier pass) → **89** (+3: the three gap-closing tests)
- **No assertions weakened, no tests deleted.**
- mlflow test uses `monkeypatch.chdir(tmp_path)` + sqlite-in-tmp, so no stray `mlruns/`/`mlartifacts/` written to the tree; those paths are also gitignored.

---

## Fix Plans — all RESOLVED (re-verified this pass)

### Fix 1 — ML-01/AC2 risk_level override — ✅ RESOLVED
`test_model_overrides_risk_level_to_model_band` uses `_StubModel(0.05)` (→ `low`) against a historical estimate that resolves to `high`, with a guard asserting the two bands genuinely differ, then asserts the returned level follows the model. Removing the override now fails the test (`'high' == 'low'`).

### Fix 2 — MLF-02/AC2 registration positive path — ✅ RESOLVED
`test_mlflow_registration_logs_when_enabled` runs `train` under a sqlite `MLFLOW_TRACKING_URI` and asserts both `mlflow_logged is True` and `search_model_versions("name='delay-risk'") ≥ 1`. Adding this test surfaced a latent production crash (skops serializer); fixed with `serialization_format="cloudpickle"`.

### Fix 3 — ML-04 missing-sklearn/joblib — ✅ RESOLVED
`test_missing_joblib_dependency_falls_back` sets `sys.modules["joblib"]=None` and asserts `model is None` + historical output. Narrowing the `except` in `_load_model` fails the test, confirming the branch is exercised.

---

## Requirement Traceability Update

| Requirement | Previous | New |
| ----------- | -------- | --- |
| ML-01 | ⚠️ Needs Fix (AC2 level) | ✅ Verified (override discriminated) |
| ML-02 | ✅ Verified | ✅ Verified |
| ML-03 | ✅ Verified | ✅ Verified |
| ML-04 | ✅ Verified (⚠️ missing-dep gap) | ✅ Verified (dedicated ImportError test) |
| ML-05 | ✅ Verified | ✅ Verified |
| ML-06 | ✅ Verified | ✅ Verified (recall 37.6% > 5.5%, bands ordered) |
| ML-07 | ✅ Verified | ✅ Verified (docs/evidence) |
| ML-08 | ✅ Verified | ✅ Verified |
| MLF-01 | ✅ Verified | ✅ Verified |
| MLF-02 | ❌ Needs Fix (positive path) | ✅ Verified (both branches; cloudpickle fix) |
| MLF-03 | ✅ Verified (config gate) | ✅ Verified (config gate) |

---

## Lessons (no `scripts/lessons.py` present — recorded here per no-script fallback)

- **L1 (test discrimination)**: When a test asserts that field B is derived from source X, choose fixture data where source X's value differs from every other candidate source, otherwise the assertion passes even if the derivation is dropped. (Grounded in M2 survived / ML-01 AC2.)
- **L2 (coverage)**: An "optional/no-op integration" AC needs BOTH the no-op branch and the positive branch tested; testing only the disabled path leaves the actual side effect unverified. (Grounded in MLF-02 gap.)

---

## Summary

**Overall**: ✅ PASS — all 3 prior gaps closed and independently re-confirmed by mutation; gate green.

**Spec-anchored check**: 27/27 AC-checks match spec outcome.
**Sensor (re-check)**: 3 gaps re-injected, all killed (R1, R2a/R2b, R3); prior survivor M2 now dies.
**Gate**: 89 passed, 0 failed (86 → 89, +3 gap-closing tests).

**What works**: Model as risk source with historical evidence + graceful fallback (now incl. discriminated missing-dep branch); shared skew-free encoding; out-of-fold eval clearing recall 37.6% > 5.5% with monotone bands; committed baseline-vs-model JSONs; MLflow no-op **and** positive registration path (locked by model name); compose profile gating.

**Production fix this iteration**: `serialization_format="cloudpickle"` in `train_model.log_model` — resolves a latent skops-serializer crash on the custom `FunctionTransformer`, previously unreached because no test exercised the registration path.

**Next steps**: None blocking — feature is verified. Tree left as found (no tracked changes from this pass).
