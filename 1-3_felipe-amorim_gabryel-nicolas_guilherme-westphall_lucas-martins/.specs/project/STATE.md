# State

**Last Updated:** 2026-07-09
**Current Work:** agente-previsao-atraso - executing (Phase 1 complete, Phase 2 next)

---

## Recent Decisions

### AD-001: MVP sem modelo supervisionado (2026-07-09)

**Decision:** O MVP usara um agente com ferramenta de consulta estatistica ao historico Olist, sem treinar um modelo de ML separado.
**Reason:** O enunciado valoriza agente, API, produto, guardrails, fallback, monitoramento e deploy; as specs consolidam essa direcao.
**Trade-off:** A acuracia pode ser menor que a de um modelo treinado, especialmente em combinacoes raras.
**Impact:** As tarefas priorizam preparo de dados, consulta historica explicavel, API e produto.

### AD-002: Previsao no momento de compra/aprovacao (2026-07-09)

**Decision:** As features do MVP devem representar informacoes disponiveis antes da entrega, idealmente logo apos compra/aprovacao.
**Reason:** O objetivo e identificar risco antes que o atraso se concretize.
**Trade-off:** Campos posteriores, como data de entrega e reviews, ficam fora das features.
**Impact:** `order_delivered_customer_date` define o alvo e nao entra como entrada; `order_delivered_carrier_date` nao entra no baseline.

### AD-003: Produto inicial como torre de controle (2026-07-09)

**Decision:** A interface existente em React sera evoluida como painel logistico, nao como landing page.
**Reason:** O frontend ja contem uma fila de pedidos e formulario de entrada.
**Trade-off:** Experiencia de chat pode ficar fora do MVP.
**Impact:** A API deve retornar dados estruturados que alimentem tabela, badges e painel de explicacao.

### AD-004: Pasta de entrega segue padrao do enunciado (2026-07-09)

**Decision:** A pasta do projeto foi renomeada para `1-3_felipe-amorim_gabryel-nicolas_guilherme-westphall_lucas-martins`.
**Reason:** O enunciado pede o formato `(X-Y_nome_integrantes)`, com X representando a trilha e Y o projeto.
**Trade-off:** O nome ficou longo, mas evita ambiguidade na submissao.
**Impact:** Specs, tarefas e comandos devem referenciar o novo caminho.

---

## Active Blockers

### B-001: Licenca oficial do dataset ainda precisa ser confirmada

**Discovered:** 2026-07-09
**Impact:** O relatorio exige origem e licenca claras.
**Workaround:** Documentar como pendente e manter uso academico/local.
**Resolution:** Confirmar na pagina oficial do dataset Olist no Kaggle antes da entrega.

### B-002: Backend ainda nao existe

**Discovered:** 2026-07-09
**Impact:** Fundacao, schemas/guardrails de entrada e preparo de dados prontos (T1-T3). Falta risk tool, agente, explicacao/acao, API, guardrails de saida e monitoramento.
**Workaround:** Backend isolado em `backend/` dentro desta pasta de entrega.
**Resolution:** Executar feature `agente-previsao-atraso` (Phase 2+) e depois API/produto.

---

## Lessons Learned

### L-001: Dataset tem alvo desbalanceado

**Context:** Inspecao local dos CSVs Olist.
**Problem:** Entre pedidos entregues, cerca de 8,1% atrasaram.
**Solution:** Priorizar recall para casos criticos e usar faixas de risco/confianca em vez de apenas classe binaria.
**Prevents:** Avaliar o sistema so por acuracia, que pode mascarar baixo desempenho em atrasos.

### L-002: Reviews sao vazamento temporal

**Context:** `olist_order_reviews_dataset.csv` contem avaliacao e comentarios apos a experiencia.
**Problem:** Usar reviews aumentaria artificialmente a qualidade da previsao.
**Solution:** Excluir reviews do baseline de features.
**Prevents:** Leakage no sistema de previsao antecipada.

---

## Quick Tasks Completed

| # | Description | Date | Commit | Status |
| --- | --- | --- | --- | --- |
| - | None yet | - | - | - |

---

## Deferred Ideas

- [ ] Treinar um modelo supervisionado para comparar com o agente - Captured during: planejamento.
- [ ] Usar reviews para analise pos-entrega e insights de satisfacao - Captured during: planejamento.
- [ ] Adicionar autenticacao e perfis de operador - Captured during: planejamento.

---

## Todos

- [ ] Confirmar licenca oficial do dataset na fonte.
- [ ] Decidir se o LLM sera usado ou se a explicacao sera totalmente templateada.
- [ ] Definir onde hospedar API e frontend.
- [ ] Evitar referencias a rascunhos locais nao commitados na documentacao versionada.

---

## Preferences

**Model Guidance Shown:** never

---

## Handoff

**Feature:** agente-previsao-atraso
**Phase/Task:** Phase 1 (Backend Foundation) complete — T1, T2, T3 done. Next: Phase 2, T4.
**Completed:**
- T1 `7154e85` — backend scaffold (`backend/`: app package, requirements.txt, pyproject pytest config, health smoke, README, .gitignore). Gate: `cd backend && ./.venv/bin/pytest`.
- T2 `7eb6695` — `backend/app/schemas.py`: Pydantic v2 `OrderInput`/`RiskEvidence`/`DelayPrediction`, UF + non-negative guardrails, `format_validation_error()`. 17 tests.
- T3 `4ab224a` — `backend/app/data_prep.py`: `build_order_features()`/`load_prepared_features()`, stdlib-only, delayed target, leakage excluded, aggregates. 7 tests. Real-data smoke: 96,470 delivered / 8.112% delayed (matches L-001).
**Test state:** 24 passed, 0 failed.
**Next step:** T4 — historical risk tool (`backend/app/risk_tool.py`): `estimate_delay_risk(order) -> RiskEvidence`, fallback hierarchy (design.md), risk score/level/confidence. Depends on T3 (done). Then T5, T6, T7.
**Blockers:** none active on Phase 2. B-001 (dataset license) still open for report.
**Uncommitted files:** none — tree clean.
**Branch:** main.
**Notes:** Executing on `main` (matches T1). One sub-agent worker died on a transient API error mid-T3; T3 finished inline. Verifier not yet run — fires after feature's final task (T12).
