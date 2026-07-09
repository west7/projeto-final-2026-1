# Architecture

**Pattern:** Early-stage single frontend app plus local dataset and planning documents.

## High-Level Structure

```mermaid
graph TD
    A[README/project docs] --> B[SDD specs]
    C[Olist CSV dataset] --> D[planned data prep]
    D --> E[planned agent/API]
    E --> F[React dashboard]
    G[Project README] --> B
```

## Identified Patterns

### Static React Dashboard

**Location:** `frontend/src/App.jsx`
**Purpose:** Represent the future operational product as a tower-of-control dashboard.
**Implementation:** A single `App` component renders topbar metrics, an order entry form and a table populated from a static `orders` array.
**Example:** The `orders` constant contains route, category, promised date, freight, status and risk placeholders.

### CSS-Only Design System

**Location:** `frontend/src/styles.css`
**Purpose:** Define spacing, typography, buttons, cards, tables and responsive behavior without a component library.
**Implementation:** CSS classes such as `.app-shell`, `.topbar`, `.summary-grid`, `.workspace`, `.button`, `.metric-card`.
**Example:** The layout switches from sidebar/table grid to single-column under `920px`.

### Project Direction Document

**Location:** `README.md`
**Purpose:** Seed the final project report and explain the initial problem framing.
**Implementation:** Markdown document with problem, stakeholders, business metrics, technical metric and MVP scope.
**Example:** The document states the MVP should classify whether an order is likely to delay and return a simple explanation.

## Data Flow

### Current UI Flow

```mermaid
graph LR
    A[Static order array] --> B[App.jsx]
    B --> C[Rendered dashboard]
    D[Form fields] --> E[No submit behavior yet]
    F[Classificar button] --> G[No API call yet]
```

### Planned Agent Flow

```mermaid
graph LR
    A[Operator enters/imports order] --> B[Frontend validation]
    B --> C[POST /predict-delay]
    C --> D[Input guardrails]
    D --> E[Agent]
    E --> F[Historical statistics tool]
    F --> G[Risk score + evidence]
    G --> H[Output guardrails]
    H --> I[Dashboard result]
    C --> J[Logs: latency/fallback/errors]
```

## Code Organization

**Approach:** Project folder by deliverable.

**Structure:**

- `readme.md`: course-level final project instructions.
- `trilhas.md`: available tracks.
- `README.md`: problem definition for Trilha 1.3.
- `dataset/`: Olist CSV files.
- `frontend/`: Vite React dashboard.
- `.specs/`: SDD documentation introduced for planning.

**Module boundaries:**

- Frontend is isolated under `frontend`.
- Dataset is read-only source material under `dataset`.
- Backend/agent modules are not present yet and should be added under `backend` or similarly scoped path.
