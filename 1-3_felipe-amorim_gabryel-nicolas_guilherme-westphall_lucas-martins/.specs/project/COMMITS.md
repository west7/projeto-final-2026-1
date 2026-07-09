# Commit Plan

**Convention:** Conventional Commits.

## Format

```text
<type>(<scope>): <summary>
```

Common types for this project:

- `docs`: specs, README, report and planning.
- `chore`: folder structure, metadata, non-product maintenance.
- `feat`: user-facing behavior or API capability.
- `test`: automated tests and fixtures.
- `fix`: bug fixes.

## Prepared Atomic Commits

### Commit 1 - created

```text
chore(project): rename delivery folder to submission format
```

Include:

- Rename tracked frontend files from `previsao-atraso/frontend/` to `1-3_felipe-amorim_gabryel-nicolas_guilherme-westphall_lucas-martins/frontend/`.
- Follow-up correction moves all project-owned docs/specs under `1-3_felipe-amorim_gabryel-nicolas_guilherme-westphall_lucas-martins/`.

Actual commit:

```text
dccb5a6 chore(project): rename delivery folder to submission format
```

### Commit 2 - ready

```text
docs(specs): add SDD planning for delay prediction agent
```

Include:

- `.specs/project/PROJECT.md`
- `.specs/project/ROADMAP.md`
- `.specs/project/STATE.md`
- `.specs/codebase/*.md`
- `.specs/features/agente-previsao-atraso/*.md`

### Commit 3 - ready

```text
docs(project): catalog superseded planning documents
```

Include:

- `.specs/project/DOCUMENTS.md`
- `.specs/project/COMMITS.md`
- State updates about folder naming and document cleanup.

### Optional Commit 4 - requires group decision

```text
chore(data): add Olist source dataset
```

Include:

- `dataset/*.csv`

Note: the dataset is about 123 MB total, with the largest file around 61 MB. It is below the common 100 MB per-file GitHub limit, but still large enough to be a deliberate repository decision.

### Optional Commit 5 - only if the group wants the draft kept

```text
docs(project): add initial problem statement draft
```

Include:

- `README-projeto.md`
- `projeto_agente_atraso_visao_geral.html`

Alternative: commit only `README-projeto.md` and remove/ignore the HTML after review, since the HTML is superseded by the specs.

## Future Implementation Commits

- `feat(backend): add delay prediction API foundation`
- `feat(agent): estimate delay risk from Olist history`
- `feat(frontend): connect dashboard to delay prediction API`
- `test(agent): cover risk fallback hierarchy`
- `docs(report): describe evaluation and ethical considerations`
