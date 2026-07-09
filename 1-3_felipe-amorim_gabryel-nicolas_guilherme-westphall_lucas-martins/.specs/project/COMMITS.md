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

### Commit 2 - created

```text
docs(specs): add SDD planning for delay prediction agent
```

Include:

- `.specs/project/PROJECT.md`
- `.specs/project/ROADMAP.md`
- `.specs/project/STATE.md`
- `.specs/codebase/*.md`
- `.specs/features/agente-previsao-atraso/*.md`
- `.specs/project/DOCUMENTS.md`
- `.specs/project/COMMITS.md`

Actual commit:

```text
be1030f docs(specs): add SDD planning for delay prediction agent
```

### Commit 3 - created

```text
docs(project): add initial delay prediction report draft
```

Include:

- `README.md`
- Any small metadata update needed after commit creation.

Actual commit: see `git log --oneline`.

### Commit 4 - created

```text
chore(data): add Olist source dataset
```

Include:

- `dataset/*.csv`

Actual commit:

```text
ecbd0fe chore(data): add Olist source dataset
```

Note: the dataset is about 123 MB total, with the largest file around 61 MB. It is below the common 100 MB per-file GitHub limit, but still large enough to keep as an intentional repository decision.

### Optional Commit 5 - only if a new draft is promoted

```text
docs(project): add supplementary planning draft
```

Include:

- Any supplementary draft that the group explicitly wants in version control.

Rule: committed docs must not mention untracked drafts.

## Future Implementation Commits

- `feat(backend): add delay prediction API foundation`
- `feat(agent): estimate delay risk from Olist history`
- `feat(frontend): connect dashboard to delay prediction API`
- `test(agent): cover risk fallback hierarchy`
- `docs(report): describe evaluation and ethical considerations`
