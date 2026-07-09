# Integrations

**Analyzed:** 2026-07-09

## Current Integrations

| System | Method | Status | Notes |
| --- | --- | --- | --- |
| Olist dataset | Local CSV files | Present | Raw source files in `dataset`. |
| React/Vite | npm dependencies | Present | Dashboard builds from frontend package. |

## Planned Integrations

| System | Method | Status | Notes |
| --- | --- | --- | --- |
| Agent API | REST over HTTP | Planned | Frontend will call endpoint to classify selected orders. |
| LLM provider | API call | Optional | Use only for controlled natural-language explanation if time and credentials allow. |
| Docker | Container runtime | Planned | Required for deployable/reproducible delivery. |
| Hosting | Public deployment | Planned | Target not selected. |

## Data Contracts

### Planned `POST /predict-delay`

Input should include route, timing, item/payment/product aggregates or enough raw fields to derive them.

Output should include:

- `risk_level`: low, medium, high.
- `risk_score`: numeric 0-1 or percentage.
- `confidence`: high, medium, low.
- `evidence`: historical segments used and sample sizes.
- `explanation`: short operator-readable reason.
- `recommended_action`: action for logistics/attendance.
- `fallback_used`: boolean.
- `latency_ms`: request duration.

## Security/Privacy Notes

- Olist IDs are pseudonymous, but project should avoid exposing raw customer identifiers unnecessarily.
- Inputs should reject abusive or unrelated text because the system is scoped to logistics delay prediction.
