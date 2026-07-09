# Agente de Previsao de Atraso Tasks

**Design:** `.specs/features/agente-previsao-atraso/design.md`
**Status:** Executing

---

## Execution Plan

### Phase 1: Backend Foundation

```text
T1 -> T2 -> T3
```

### Phase 2: Agent Core and Evaluation

```text
T3 -> T4 -> T5 -> T6
             \-> T7
```

### Phase 3: API and Product Integration

```text
T6 -> T8 -> T9 -> T10
T7 --------^
```

### Phase 4: Deploy and Report

```text
T10 -> T11 -> T12
```

---

## Task Breakdown

### T1: Create backend project foundation

**What:** Add backend folder with app package, dependency manifest and initial test setup.
**Where:** `backend`
**Depends on:** None
**Reuses:** Existing project layout under this delivery folder.
**Requirement:** DELAY-03, DELAY-08

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] Backend has a reproducible way to install/run.
- [x] Test command is documented.
- [x] Health or smoke module can be imported.

**Tests:** setup/build
**Gate:** planned backend gate

---

### T2: Define schemas and guardrail errors

**What:** Create request/response schemas and friendly validation error structures.
**Where:** `backend/app/schemas.py`
**Depends on:** T1
**Reuses:** Data models from design.
**Requirement:** DELAY-01, DELAY-03, DELAY-06

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] Required fields and optional fields are explicit.
- [x] Invalid UF, missing identifiers and impossible numeric values are handled.
- [x] Unit tests cover valid and invalid inputs.

**Tests:** unit
**Gate:** backend quick gate

---

### T3: Build order-level feature preparation

**What:** Implement raw CSV to prepared order-level feature artifact.
**Where:** `backend/app/data_prep.py`
**Depends on:** T2
**Reuses:** Raw CSVs in `dataset`.
**Requirement:** DELAY-01, DELAY-09

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] Delivered orders receive `delayed` target.
- [x] Leakage fields are excluded from feature output.
- [x] Item, product, seller, customer and payment aggregates are generated.
- [x] Small fixture tests verify target and aggregates.

**Tests:** unit/integration
**Gate:** backend quick gate

---

### T4: Implement historical risk tool

**What:** Estimate delay risk from prepared features using fallback hierarchy.
**Where:** `backend/app/risk_tool.py`
**Depends on:** T3
**Reuses:** Prepared feature artifact and fallback hierarchy in design.
**Requirement:** DELAY-01, DELAY-02

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] Risk score is computed from delayed rate in selected segment.
- [x] Risk level maps score to low/medium/high.
- [x] Confidence reflects sample size and fallback depth.
- [x] Tests cover specific match, fallback and global baseline.

**Tests:** unit
**Gate:** backend quick gate

---

### T5: Implement explanation and action policy

**What:** Generate deterministic explanation and recommended action from risk evidence.
**Where:** `backend/app/explanation.py`
**Depends on:** T4
**Reuses:** Risk evidence factors.
**Requirement:** DELAY-04, DELAY-05, DELAY-06

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] Explanation cites evidence fields and sample size.
- [x] Action differs by risk level and confidence.
- [x] Low-confidence cases recommend human review.
- [x] Output guardrail rejects missing evidence.

**Tests:** unit
**Gate:** backend quick gate

---

### T6: Implement delay agent service

**What:** Orchestrate schemas, risk tool, explanation, guardrails and telemetry fields.
**Where:** `backend/app/agent.py`
**Depends on:** T5
**Reuses:** Schemas, risk tool and explanation policy.
**Requirement:** DELAY-01, DELAY-04, DELAY-05, DELAY-06, DELAY-08

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [x] `classify_order` returns complete prediction response.
- [x] Fallback and guardrail events are represented in output.
- [x] LLM primary path falls back to deterministic text when unconfigured or unavailable.
- [x] Tests cover normal, fallback and guardrail scenarios.

**Tests:** unit/integration
**Gate:** backend quick gate

---

### T7: Add offline evaluation script

**What:** Evaluate the baseline over historical delivered orders and output metrics.
**Where:** `backend/app/evaluate.py`
**Depends on:** T4
**Reuses:** Prepared feature artifact and risk tool.
**Requirement:** DELAY-09

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] Script reports delayed recall, precision or confusion by risk band.
- [ ] Script reports fallback rate.
- [ ] Script can group metrics by state/region when data exists.

**Tests:** integration/smoke
**Gate:** backend quick gate

---

### T8: Expose API endpoints

**What:** Add HTTP API for health and delay prediction.
**Where:** `backend/app/api.py`
**Depends on:** T6
**Reuses:** Agent service.
**Requirement:** DELAY-01, DELAY-03, DELAY-08

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] `GET /health` returns service status.
- [ ] `POST /predict-delay` returns agent prediction.
- [ ] Validation errors are friendly.
- [ ] Logs include latency and event type.

**Tests:** integration
**Gate:** backend full gate

---

### T9: Add frontend API client and state

**What:** Create frontend client and connect classify action to API.
**Where:** `frontend/src/api.js`, `frontend/src/App.jsx`
**Depends on:** T8
**Reuses:** Existing dashboard layout.
**Requirement:** DELAY-07

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] Form adds orders to local queue.
- [ ] Selected orders call API.
- [ ] Loading, success and error states are visible.
- [ ] Existing build gate passes.

**Tests:** build/smoke
**Gate:** frontend build gate

---

### T10: Display explanation, confidence and fallback in UI

**What:** Extend dashboard table/panel to show prediction details.
**Where:** `frontend/src/App.jsx`, `frontend/src/styles.css`
**Depends on:** T9
**Reuses:** Existing table, cards and button styles.
**Requirement:** DELAY-04, DELAY-05, DELAY-07

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] Risk badges distinguish low/medium/high.
- [ ] Explanation and recommended action are visible for selected result.
- [ ] Fallback/low-confidence response is understandable.
- [ ] Mobile layout remains usable.

**Tests:** build/smoke + manual UAT
**Gate:** frontend build gate

---

### T11: Add Docker and run instructions

**What:** Package backend and frontend for reproducible execution.
**Where:** `Dockerfile*`, `docker-compose.yml`, docs
**Depends on:** T10
**Reuses:** Existing frontend build and backend run command.
**Requirement:** DELAY-07, DELAY-08

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] One command starts API and frontend or documented equivalent.
- [ ] Environment variables are documented.
- [ ] Health check works after startup.

**Tests:** deploy smoke
**Gate:** full gate

---

### T12: Complete report/demo documentation

**What:** Update project report with problem, architecture, data, guardrails, evaluation, ethics and demo script.
**Where:** `README.md` or final report file
**Depends on:** T11
**Reuses:** `.specs`, `README.md`, dataset analysis.
**Requirement:** DELAY-08, DELAY-09

**Tools:**

- MCP: NONE
- Skill: `tlc-spec-driven`

**Done when:**

- [ ] Report includes app/repo links placeholders or final URLs.
- [ ] Data source/license and known biases are documented.
- [ ] Metrics, latency, fallback and guardrail behavior are documented.
- [ ] Demo script covers normal, high-risk and fallback cases.

**Tests:** documentation review
**Gate:** manual review

---

## Parallel Execution Map

```text
Phase 1:
  T1 -> T2 -> T3

Phase 2:
  T3 -> T4
        ├── T5 -> T6
        └── T7

Phase 3:
  T6 -> T8 -> T9 -> T10
  T7 --------^

Phase 4:
  T10 -> T11 -> T12
```

**Parallelism constraint:** No task is marked `[P]` yet because backend test isolation is not established. After T1 defines isolated test fixtures, T7 can potentially run in parallel with T5/T6.

---

## Pre-Approval Checks

### Check 1: Task Granularity

| Task | Atomic? | Notes |
| --- | --- | --- |
| T1 | Pass | One backend foundation deliverable. |
| T2 | Pass | One schema/guardrail deliverable. |
| T3 | Pass | One data prep deliverable. |
| T4 | Pass | One risk tool deliverable. |
| T5 | Pass | One explanation/action deliverable. |
| T6 | Pass | One agent orchestration deliverable. |
| T7 | Pass | One evaluation script deliverable. |
| T8 | Pass | One API endpoint layer deliverable. |
| T9 | Pass | One frontend API/state deliverable. |
| T10 | Pass | One UI display deliverable. |
| T11 | Pass | One deployment packaging deliverable. |
| T12 | Pass | One report/demo documentation deliverable. |

### Check 2: Diagram-Definition Cross-Check

| Dependency in diagram | Task `Depends on` match | Status |
| --- | --- | --- |
| T1 -> T2 | T2 depends on T1 | Pass |
| T2 -> T3 | T3 depends on T2 | Pass |
| T3 -> T4 | T4 depends on T3 | Pass |
| T4 -> T5 | T5 depends on T4 | Pass |
| T5 -> T6 | T6 depends on T5 | Pass |
| T4 -> T7 | T7 depends on T4 | Pass |
| T6 -> T8 | T8 depends on T6 | Pass |
| T8 -> T9 | T9 depends on T8 | Pass |
| T9 -> T10 | T10 depends on T9 | Pass |
| T10 -> T11 | T11 depends on T10 | Pass |
| T11 -> T12 | T12 depends on T11 | Pass |

### Check 3: Test Co-location Validation

| Task | Tests field | Matches TESTING.md? | Status |
| --- | --- | --- | --- |
| T1 | setup/build | Yes, foundation defines gates | Pass |
| T2 | unit | Yes, schema layer needs unit tests | Pass |
| T3 | unit/integration | Yes, data prep needs fixture integration | Pass |
| T4 | unit | Yes, risk tool is deterministic | Pass |
| T5 | unit | Yes, explanation policy is deterministic | Pass |
| T6 | unit/integration | Yes, agent crosses components | Pass |
| T7 | integration/smoke | Yes, evaluation uses prepared data/tool | Pass |
| T8 | integration | Yes, API layer needs request tests | Pass |
| T9 | build/smoke | Yes, frontend has build gate only | Pass |
| T10 | build/smoke + manual UAT | Yes, user-facing UI needs UAT | Pass |
| T11 | deploy smoke | Yes, Docker/deploy is not parallel-safe | Pass |
| T12 | documentation review | Yes, report is manual review | Pass |

---

## Tools for Execution

Available skills in this session:

- `tlc-spec-driven`
- `imagegen`
- `openai-docs`
- `plugin-creator`
- `skill-creator`
- `skill-installer`

Recommended execution tools:

- Filesystem/editing tools for all tasks.
- Web access only when confirming official dataset license, deployment docs or current external service documentation.
- No extra MCPs are currently available for code navigation or Mermaid rendering.
