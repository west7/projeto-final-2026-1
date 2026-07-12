# Document Inventory

**Analyzed:** 2026-07-09

## Keep

| Document | Status | Reason |
| --- | --- | --- |
| `readme.md` | Keep | Enunciado oficial do projeto final, incluindo criterio de entrega e formato da pasta. |
| `trilhas.md` | Keep | Fonte da trilha/projeto escolhidos. |
| `README.md` | Keep and evolve | Seed do relatorio final; ainda deve receber arquitetura, avaliacao, demo, impacto e referencias. |
| `.specs/project/PROJECT.md` | Keep | Visao e escopo SDD. |
| `.specs/project/ROADMAP.md` | Keep | Planejamento por milestones. |
| `.specs/project/STATE.md` | Keep | Memoria persistente de decisoes, blockers e aprendizados. |
| `.specs/project/TOOLING_REVIEW.md` | Keep | Analise adiada de MLflow, LangChain e ferramentas relacionadas para revisao pos-MVP. |
| `.specs/codebase/*.md` | Keep | Mapeamento brownfield usado para proximas tarefas. |
| `.specs/features/agente-*.md` | Keep | Spec, design e tarefas da feature principal. |

## Superseded After Specs

| Document | Recommendation | Reason |
| --- | --- | --- |
| None | - | Superseded drafts should not be referenced by committed docs unless they are also committed. |

## Not Documentation

| Path | Status | Reason |
| --- | --- | --- |
| `frontend/index.html` | Keep | Arquivo tecnico necessario para o Vite renderizar a aplicacao. |

## Cleanup Rule

Do not reference untracked drafts from committed project documentation. If a draft becomes useful again, commit it explicitly first.
