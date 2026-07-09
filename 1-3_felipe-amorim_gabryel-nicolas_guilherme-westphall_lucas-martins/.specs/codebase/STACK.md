# Tech Stack

**Analyzed:** 2026-07-09

## Core

- Framework: Vite 6.0.5 for frontend build.
- Language: JavaScript/JSX for current frontend; Python planned but not implemented.
- Runtime: Node.js for frontend scripts; browser runtime for product UI.
- Package manager: npm, evidenced by `package-lock.json`.

## Frontend

- UI Framework: React 19.0.0.
- Styling: Plain CSS in `frontend/src/styles.css`.
- State Management: Static local constants only; no state library yet.
- Form Handling: Native HTML inputs; no form library yet.

## Backend

- API Style: Not implemented.
- Database: Not implemented. Current data lives as local CSV files in `dataset`.
- Authentication: Not implemented.

## Testing

- Unit: Not configured.
- Integration: Not configured.
- E2E: Not configured.
- Current gate available: `npm run build` inside `frontend`.

## External Services

- Dataset: Olist Brazilian E-Commerce public dataset in local CSVs.
- LLM provider: OpenAI-compatible HTTP client scaffolded; concrete model/provider configured by `LLM_API_KEY`/`OPENAI_API_KEY`, `LLM_MODEL` and `LLM_BASE_URL`.
- Deployment: Not selected.

## Development Tools

- Build tool: Vite.
- React plugin: `@vitejs/plugin-react`.
- Documentation: Markdown specs and project README.
