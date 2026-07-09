# Concerns

**Analyzed:** 2026-07-09

## Data Concerns

### C-001: Temporal leakage

Fields like `order_delivered_customer_date`, reviews and final status can leak future information.

**Mitigation:** Treat delivery date only as target; exclude reviews from MVP; avoid `order_status` as feature unless representing a runtime status captured at prediction time.

### C-002: Sparse historical groups

Highly specific combinations such as seller-state + customer-state + category may have too few examples.

**Mitigation:** Use fallback hierarchy and expose sample size/confidence.

### C-003: Class imbalance

Delivered orders inspected locally show about 8.1% late cases.

**Mitigation:** Prefer recall-oriented technical metrics for critical cases, report precision/recall/F1 or confusion by risk band, and avoid using accuracy alone.

### C-004: Regional bias

The HTML overview flags possible under-representation of Norte/Nordeste.

**Mitigation:** Report performance and fallback frequency by region/state where possible; avoid recommendations that punish customers in underrepresented regions.

### C-005: License confirmation

The HTML overview says the dataset license should be declared and confirmed.

**Mitigation:** Confirm official Kaggle license before final report and cite the source.

## Code Concerns

### C-006: Frontend is static

Buttons and form do not yet have state management or API calls.

**Mitigation:** Introduce minimal state, validation and service client in focused tasks.

### C-007: No backend/test setup

There is no API, agent implementation or automated test suite.

**Mitigation:** Add backend foundation with tests as part of the first implementation milestone.

### C-008: Generated data artifacts can become stale

Precomputed features may drift from raw CSVs.

**Mitigation:** Provide reproducible data prep command and document artifact generation.
