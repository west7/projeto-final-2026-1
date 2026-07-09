# Code Conventions

## Naming Conventions

**Files:**

- React entry files use standard Vite names: `main.jsx`, `App.jsx`.
- CSS uses a single global stylesheet: `styles.css`.
- Dataset files keep original Olist names, such as `olist_orders_dataset.csv`.

**Functions/Components:**

- React component names use PascalCase, example: `App`.
- No helper functions are present yet.

**Variables:**

- JavaScript constants use camelCase, example: `orders`.
- Object properties use camelCase, examples: `promisedDate`, `risk`, `status`.

**Constants:**

- Static UI data is declared as `const` near the top of `App.jsx`.

## Code Organization

**Import/Dependency Declaration:**

- `main.jsx` imports React, ReactDOM, `App.jsx`, then CSS.
- `vite.config.js` imports `defineConfig` and plugin, then exports config.

**File Structure:**

- `App.jsx` currently combines static data and all UI markup in one file.
- `styles.css` defines global reset first, then page, components, table and responsive rules.

## Type Safety/Documentation

**Approach:** No TypeScript, JSDoc or runtime schemas in the current frontend.

## Error Handling

**Pattern:** Not implemented yet. Buttons and forms have no event handlers.

## Comments/Documentation

**Style:** Current code has no inline comments. Project context is documented in Markdown and static HTML.

## Implications for New Work

- Keep React components simple and local unless repeated UI patterns emerge.
- Prefer extracting API/client logic only when a real API is added.
- Introduce backend validation through explicit schemas rather than ad hoc checks.
- Keep dataset-derived artifacts separate from raw CSV files.
