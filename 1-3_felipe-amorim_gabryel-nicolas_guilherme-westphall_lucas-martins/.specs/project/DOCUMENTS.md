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
| `.specs/codebase/*.md` | Keep | Mapeamento brownfield usado para proximas tarefas. |
| `.specs/features/agente-*.md` | Keep | Spec, design e tarefas da feature principal. |

## Superseded After Specs

| Document | Recommendation | Reason |
| --- | --- | --- |
| `projeto_agente_atraso_visao_geral.html` | Optional removal after review | Conteudo foi absorvido por `PROJECT.md`, `spec.md`, `design.md`, `tasks.md` e `STATE.md`. Hoje funciona apenas como rascunho visual/historico. |

## Not Documentation

| Path | Status | Reason |
| --- | --- | --- |
| `frontend/index.html` | Keep | Arquivo tecnico necessario para o Vite renderizar a aplicacao. |

## Cleanup Rule

Do not delete superseded files until the group confirms they are no longer useful for presentation or report writing. When removed, use a dedicated commit such as `chore(docs): remove superseded overview draft`.
