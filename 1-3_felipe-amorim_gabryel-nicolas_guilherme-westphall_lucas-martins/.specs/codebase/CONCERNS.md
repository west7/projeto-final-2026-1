# Concerns

**Analyzed:** 2026-07-13

## Active Concerns

### C-001: Regional performance remains uneven

The calibrated model improves high-risk recall over the historical baseline, but committed per-state evaluation still varies materially by region.

**Evidence:** `backend/data/eval_model.json` and `assets/eval-by-state.png`.

**Mitigation:** Keep per-state evaluation visible, expose confidence/evidence to operators and avoid fully automated adverse decisions.

### C-002: No automated frontend or end-to-end tests

The frontend has a production build gate but no component assertions or automated browser flow.

**Evidence:** `frontend/package.json` defines only dev/build/preview scripts; `.specs/codebase/TESTING.md` records zero frontend tests.

**Mitigation:** Preserve manual UAT for delivery; add focused component/API-state tests if the dashboard evolves.

### C-003: No CI pipeline

Backend tests and frontend builds depend on local execution before delivery.

**Evidence:** no workflow/pipeline configuration is versioned; the limitation is disclosed in `README.md`.

**Mitigation:** Run both documented gates before each push; add CI if development continues beyond the academic delivery.

### C-004: Dependency resolution is only partially pinned

scikit-learn and frontend packages are reproducible at the lock level, but several Python dependencies use open lower bounds. A fresh install can select newer transitive versions and currently emits Joblib/NumPy deprecation warnings.

**Evidence:** `backend/requirements.txt`, `requirements-ml.txt`; the verified suite passes despite the warnings.

**Mitigation:** Produce a tested constraints/lock file for future maintenance while retaining the exact scikit-learn version required by serialized models.

### C-005: Free-tier cold start and resource limits

The Render backend can sleep after inactivity and has constrained CPU/memory. Public health validation on 2026-07-13 observed a cold start of approximately 42 seconds.

**Evidence:** `render.yaml`, frontend warm-up logic and deployment notes in `README.md`.

**Mitigation:** Poll health with an explicit warming state, classify sequentially and use a paid instance for a time-critical demo if necessary.

### C-006: Build cost and artifact freshness are coupled

Prepared data and the calibrated model are generated during the Docker build. Changes to code, dependencies or dataset can invalidate the relevant layers and retrain the model; unchanged inputs may reuse Docker cache.

**Evidence:** `backend/Dockerfile`; no backend runtime volume exists in `docker-compose.yml`.

**Mitigation:** Keep preparation/training reproducible, review build logs and force a clean rebuild when deliberately validating artifact freshness.

## Mitigated Historical Concerns

- Temporal leakage: delivery/review/final-status fields are excluded from model inputs and tested.
- Sparse groups: the historical hierarchy exposes fallback/sample/confidence; the model removes segment-size fallback from the score.
- Class imbalance: reports prioritize recall/precision rather than accuracy.
- Static frontend/no backend/no tests: superseded by the implemented dashboard, FastAPI service and 101-test backend suite.
- LLM unreliability: strict structured output, intent matching and deterministic fallback cover provider and quota failures.
- Dataset license: source and CC BY-NC-SA 4.0 license are declared in the project report.
