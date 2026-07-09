# State

**Last Updated:** 2026-07-09
**Current Work:** agente-previsao-atraso - planning

---

## Recent Decisions

### AD-001: MVP sem modelo supervisionado (2026-07-09)

**Decision:** O MVP usara um agente com ferramenta de consulta estatistica ao historico Olist, sem treinar um modelo de ML separado.
**Reason:** O enunciado valoriza agente, API, produto, guardrails, fallback, monitoramento e deploy; o HTML de visao geral ja aponta essa direcao.
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
**Impact:** API, agente, guardrails e monitoramento ainda precisam ser implementados.
**Workaround:** Planejar backend em modulo isolado dentro desta pasta de entrega.
**Resolution:** Executar feature `agente-previsao-atraso` e depois API/produto.

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
- [ ] Decidir se `projeto_agente_atraso_visao_geral.html` sera removido ou mantido como material historico fora do MVP.

---

## Preferences

**Model Guidance Shown:** never
