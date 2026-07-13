# Modelo ML + MLflow Specification

## Problem Statement

The delivered agent scores delay risk with `HistoricalRiskTool` — a segment-average heuristic. Offline evaluation (T7, 96,470 real orders) shows good calibration but **weak discrimination**: high-alarm recall of only **5.5%**. A trained, calibrated classifier can raise recall without discarding the well-calibrated, interpretable behavior. Separately, the project has no experiment tracking or durable metrics store (telemetry is stdout-only), so runs cannot be compared. MLflow closes both gaps.

**Success metrics (report "Definição do problema"):**
- **Business metric:** share of orders that actually delayed which the system flags as high-risk *early* (so logistics/CS can act) — i.e. high-alarm recall, the operational lever for proactive intervention.
- **Technical metric:** high-alarm recall on the leave-one-out eval, subject to holding per-band calibration (observed rate ordered high > medium > low).

**Report fit (Trilha 1.3, official rubric `readme.md`):** classification of "vai atrasar?" is in-track; MLflow realizes the semester's *rastreamento de experimentos* competency; the heuristic→model progression is the rubric's required *baseline→final iteration* and *agent/model exploration* narrative; per-state metrics feed the required *Impactos e ética / viés regional* section.

## Goals

- [ ] Replace the risk-number source with a trained, calibrated classifier that **beats 5.5% high-alarm recall while holding per-band calibration** on the same leave-one-out eval.
- [ ] Produce **report-ready evidence**: baseline-vs-model comparison (metrics + per-state breakdown) as a durable artifact and as comparable MLflow runs.
- [ ] Keep every existing behavior intact: same API contract, same evidence factors, graceful degradation when the model or MLflow is absent.
- [ ] Track evaluation runs and register the model in **MLflow**, strictly optional — API and eval run with no MLflow server present.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Online/real-time model retraining | Batch-trained artifact is enough for the delivery; retrain is a manual script. |
| Deep models / XGBoost / LightGBM | sklearn `HistGradientBoostingClassifier` fits ~96k rows / ≤14 features; extra deps, no gain. |
| `sellers_count` as a model feature | Not reconstructable from `OrderInput` at request time; excluded to avoid train/serve skew. |
| LLM explanation changes | The LLM stage is untouched — it still only rewrites prose over the number. |
| Hyperparameter search / AutoML | One documented config; tuning is not required to clear the acceptance bar. |
| MLflow as a hard runtime dependency | Must degrade to no-op; the API image must build and serve without `mlflow` or a model file. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Scope of this delivery | Model **and** MLflow, both built | User decision | y |
| Feature set for the model | Only features reconstructable from `OrderInput` (drop `sellers_count`) | No train/serve skew; model always usable | y |
| Acceptance bar | high-alarm recall > 5.5% **and** per-band calibration holds, on `evaluate.py` leave-one-out | Tied to the real, honest weakness | y |
| Model class | sklearn `HistGradientBoostingClassifier` + isotonic `CalibratedClassifierCV` | Native NaN/categorical handling, calibrated probs, no pandas | y (design) |
| Evidence factors source | `HistoricalRiskTool` still supplies `factors`/`sample_size`/`segment_used` | Model has no human-readable "N of M" evidence; guardrail requires traceable factors | y |
| Missing request fields at serve time | Fed as NaN to the model (HGB handles natively); no fallback needed for missing fields | Model stays usable; fallback reserved for absent/broken model artifact | y |
| Branch | All work on `feat/modelo-ml-mlflow`, not `main` | User instruction (diverges from repo's commit-to-main convention) | y |
| Reverses `PROJECT.md` MVP out-of-scope ("no separate ML model in MVP") | Done deliberately, **post-MVP** | Rubric rewards baseline→final iteration + model exploration; MVP shipped first, model is the documented evolution | y |

**Open questions:** none — all resolved or logged above.

---

## User Stories

### P1: Trained model as the risk-number source ⭐ MVP

**User Story**: As the agent, I want the delay probability to come from a calibrated classifier so that high-risk orders are actually detected (recall rises above 5.5%).

**Why P1**: This is the headline result — it fixes the one honest weakness in the delivered system.

**Acceptance Criteria**:

1. WHEN training runs over `prepared_orders.jsonl` THEN the system SHALL produce a persisted calibrated model artifact using only features reconstructable from `OrderInput` (i.e. excluding `sellers_count`).
2. WHEN an order is scored and a valid model artifact is present THEN `ModelRiskTool.estimate_delay_risk(order)` SHALL return a `RiskEvidence` whose `risk_score` is the model's calibrated probability and whose `risk_level` uses the existing low/medium/high thresholds unchanged.
3. WHEN the model scores an order THEN the returned `RiskEvidence.factors`/`sample_size`/`segment_used` SHALL still be populated from `HistoricalRiskTool` so the output guardrail's traceable-evidence check passes.
4. WHEN request-time optional fields are absent THEN the system SHALL feed them to the model as missing values and still return a score (no error, no fallback triggered by missing fields alone).

**Independent Test**: Train on the prepared data, score a fixed order with and without the model artifact, assert the score comes from the model when present and that evidence factors are non-empty.

---

### P1: Feature derivation shared between train and serve ⭐ MVP

**User Story**: As a developer, I want one function that turns both an `OrderFeature` (training) and an `OrderInput` (serving) into the identical feature vector so that there is no train/serve skew.

**Why P1**: Skew silently destroys model quality; a single shared mapping is the guard.

**Acceptance Criteria**:

1. WHEN the same underlying order is expressed as an `OrderFeature` and as an `OrderInput` THEN the shared derivation SHALL produce the same feature vector (same keys, same values for shared fields; `price`→`total_price`, `freight_value`→`total_freight`, `same_state`/`purchase_month`/`purchase_weekday`/`promised_days`/`freight_ratio` derived identically).
2. WHEN the derivation runs THEN `sellers_count` SHALL NOT appear in the produced vector.

**Independent Test**: Construct a matched `OrderFeature`/`OrderInput` pair; assert both derive to an equal vector without `sellers_count`.

---

### P1: Offline eval proves the model beats the baseline ⭐ MVP

**User Story**: As an evaluator, I want `evaluate.py` to score the model on the same leave-one-out harness so that I can prove recall improved without losing calibration.

**Why P1**: The acceptance bar is only meaningful if measured the same way as the baseline.

**Acceptance Criteria**:

1. WHEN `evaluate.py --scorer model` runs THEN it SHALL report high-alarm recall, per-band calibration, precision, and fallback rate using the same report format as the baseline scorer.
2. WHEN the model eval completes THEN high-alarm recall SHALL be strictly greater than the baseline's 5.5%.
3. WHEN the model eval completes THEN each risk band's observed delay rate SHALL remain monotonically ordered (high > medium > low) — calibration is not inverted or collapsed.

**Independent Test**: Run both scorers; assert model recall > baseline recall and bands stay ordered.

---

### P1: Report-ready evidence (per-state bias + comparison artifact) ⭐ MVP

**User Story**: As the report author, I want the model eval to produce a per-state breakdown and a durable baseline-vs-model comparison so that the *Avaliação* and *Impactos e ética* sections cite real numbers.

**Why P1**: The rubric requires a test set with adequate metrics and a concrete regional-bias analysis; without these outputs the report has no evidence.

**Acceptance Criteria**:

1. WHEN `evaluate.py --scorer model` runs THEN it SHALL produce the same **per-customer-state** breakdown (orders, delay%, recall, fallback rate) the baseline scorer already produces, so regional bias is comparable across scorers.
2. WHEN an eval run completes THEN the system SHALL emit a machine-readable artifact (JSON) of the full `EvalReport` (overall + per-band + per-state + alarm TP/FP/FN) so exact figures are quotable in the report.
3. WHEN both scorers have been evaluated THEN the comparison SHALL be reproducible from committed artifacts (baseline JSON vs model JSON) without re-running training.

**Independent Test**: Run the model eval; assert the JSON artifact exists, contains per-state entries, and that a baseline JSON produced the same way is diff-able against it.

---

### P1: MLflow tracks eval runs and registers the model ⭐ MVP

**User Story**: As an evaluator, I want each evaluation logged to MLflow and the trained model registered so that runs are comparable and the model is versioned.

**Why P1**: Experiment tracking is the second half of the chosen scope.

**Acceptance Criteria**:

1. WHEN `MLFLOW_TRACKING_URI` is set and an eval runs THEN the system SHALL log the run's metrics (recall, precision, per-band rates, fallback rate) and params (scorer, min-segment-size) to MLflow.
2. WHEN training runs with MLflow configured THEN the calibrated model SHALL be logged/registered as an MLflow model artifact.
3. WHEN `MLFLOW_TRACKING_URI` is unset THEN training and eval SHALL complete normally with MLflow calls no-oped (no import error, no crash).

**Independent Test**: Run eval with the tracking URI unset (asserts no-op success) and with a local file-store URI (asserts a run is recorded).

---

### P2: MLflow runs as an optional Docker Compose service

**User Story**: As an evaluator, I want an MLflow server available via Docker Compose so that I can browse runs, without it being required to start the API.

**Acceptance Criteria**:

1. WHEN `docker compose up` runs without the mlflow profile THEN the API and frontend SHALL start with no MLflow container and serve predictions.
2. WHEN the mlflow profile is enabled THEN an MLflow server SHALL start and the eval SHALL be able to point at it.

**Independent Test**: Bring the stack up without the profile; hit `/predict-delay`; confirm no MLflow dependency. Enable the profile; confirm the server is reachable.

---

### P3: Retraining is reproducible

**User Story**: As a developer, I want a single documented command to regenerate the model so that the artifact is reproducible.

**Acceptance Criteria**:

1. WHEN the documented train command runs on the prepared data THEN it SHALL regenerate an equivalent model artifact (same features, same config).

---

## Edge Cases

- WHEN the model artifact file is absent THEN the agent SHALL fall back to `HistoricalRiskTool` and set `fallback_used` accordingly (API stays 200).
- WHEN the model artifact is present but fails to load/deserialize THEN the agent SHALL fall back to `HistoricalRiskTool` rather than error.
- WHEN `mlflow` (or `scikit-learn`) is not installed THEN the API SHALL still import and serve using the historical scorer (ML deps live in a separate `requirements-ml.txt`).
- WHEN both `customer_state` and `seller_state` are present but no dates THEN the model SHALL still score (dates→NaN), while `promised_days` is treated as missing.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| ML-01 | P1: Model as risk source | Design | Pending |
| ML-02 | P1: Shared feature derivation | Design | Pending |
| ML-03 | P1: Model training artifact | Design | Pending |
| ML-04 | P1: Graceful fallback (absent/broken model, missing deps) | Design | Pending |
| ML-05 | P1: Evidence factors preserved from historical tool | Design | Pending |
| ML-06 | P1: Offline eval `--scorer model` beats baseline recall + holds calibration | Design | Pending |
| ML-08 | P1: Per-state breakdown + JSON comparison artifact for the report | Design | Pending |
| MLF-01 | P1: MLflow logs eval runs (optional/no-op) | Design | Pending |
| MLF-02 | P1: MLflow registers the model (optional) | Design | Pending |
| MLF-03 | P2: Docker Compose mlflow profile, API independent | Design | Pending |
| ML-07 | P3: Reproducible retrain command | Design | Pending |

**ID format:** `ML-NN` (model), `MLF-NN` (MLflow).

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 11 total, 0 mapped to tasks yet.

---

## Report Mapping

Each output maps to a required section of the official report (`readme.md`) so nothing built here is un-reportable.

| Report section (rubric) | Evidence this feature produces | Requirement |
| ----------------------- | ------------------------------ | ----------- |
| Definição do problema — métrica de negócio & técnica | high-alarm recall as the operational lever; technical bar defined | ML-06 |
| Como o sistema é montado — model exploration | rejected alternatives (LogReg/XGBoost/LightGBM/NN) + chosen HGB, in design.md | (design) |
| Descrição do agente — ferramentas & iterações | `ModelRiskTool` behind the same seam; heuristic→model iteration story | ML-01, ML-04 |
| Avaliação — critérios, conjunto de teste, métricas | leave-one-out recall/precision/calibration, baseline vs model | ML-06, ML-08 |
| Impactos e ética — viés regional | per-state recall/fallback, baseline vs model | ML-08 |
| Monitore — traces, custo, latência, fallback | MLflow runs + existing JSON telemetry (recall/fallback/tokens/latency) | MLF-01, MLF-02 |
| Reflexão / próximos passos | honest comparison (even a small win) + calibration/interpretability trade-off | ML-06, ML-08 |
| Referências | scikit-learn, MLflow, Olist CC BY-NC-SA 4.0 | (design) |

---

## Success Criteria

- [ ] `evaluate.py --scorer model` high-alarm recall > 5.5% and bands stay ordered (high > medium > low).
- [ ] Per-state breakdown + a JSON comparison artifact exist and are committed as report evidence.
- [ ] `/predict-delay` returns model-sourced scores with non-empty evidence factors; identical API contract.
- [ ] API image builds and serves with no `mlflow`, no `scikit-learn` model file, no `MLFLOW_TRACKING_URI`.
- [ ] With MLflow configured, eval runs appear as comparable runs and the model is registered.
- [ ] Every requirement maps to a report section (see Report Mapping) — no un-reportable work.
