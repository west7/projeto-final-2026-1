# State

**Last Updated:** 2026-07-13
**Current Work:** agente-previsao-atraso - executing (T14 deployed; remaining public UAT next)

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

### AD-005: LLM como camada agentica primaria (2026-07-09)

**Decision:** O MVP usa LLM como camada primaria para redigir a resposta/acao do agente a partir das evidencias; a explicacao deterministica fica como fallback.
**Reason:** O enunciado pede um agente de IA, escolha de LLM, prompts, fallback e custo/latencia de LLM; um fluxo puramente deterministico ficaria fora do foco.
**Trade-off:** A demo passa a depender de credenciais/configuracao de LLM para o caminho ideal, mas segue funcionando com degradacao graciosa.
**Impact:** `backend/app/agent.py` aceita `llm_client`, registra `llm_unconfigured`/`llm_fallback` e `backend/app/llm.py` fornece cliente OpenAI-compatible configuravel por ambiente.

### AD-006: Saida hibrida e estruturada para explicacao e acao (2026-07-12)

**Decision:** A LLM deve produzir `explanation` e `recommended_action` como campos estruturados. A politica deterministica define a acao segura de referencia, valida a compatibilidade da acao gerada com risco/confianca e assume ambos os campos quando a LLM falhar ou violar guardrails.
**Reason:** O comportamento atual pede que a LLM recomende uma acao dentro da explicacao, mas a API exibe separadamente a acao deterministica, causando repeticao e deixando a acao efetivamente fora do caminho primario da LLM.
**Trade-off:** A saida estruturada e o guardrail semantico adicionam validacao e testes ao cliente LLM, mas preservam clareza, seguranca e alinhamento com AD-005.
**Impact:** `backend/app/llm.py` devera retornar explicacao e acao separadas; `backend/app/agent.py` devera usar a saida validada da LLM e manter `explain_risk()` como fallback seguro. Implementacao ainda pendente.

### AD-007: Frontend e backend no Render com custo zero como alvo (2026-07-12)

**Decision:** Hospedar o frontend como Render Static Site e o backend como Render Free Web Service Docker. Aceitar o cold start do plano gratuito, incorporar o dataset preparado na imagem e manter Render Starter como contingencia para a demo.
**Reason:** Um unico provedor reduz configuracao e risco operacional; o Render suporta site estatico, FastAPI/Docker, secrets, health check e URLs HTTPS.
**Trade-off:** O backend gratuito dorme apos inatividade, tem filesystem efemero, 512 MB/0,1 CPU e pode demorar cerca de um minuto para acordar.
**Impact:** Implementar `VITE_API_BASE`, CORS restrito, build-time data prep, uso de `$PORT`, estado de aquecimento/retry e `render.yaml`. Nao usar UptimeRobot para impedir permanentemente o spin-down; detalhes em `DEPLOYMENT.md`.

---

## Active Blockers

_None active._

## Resolved Blockers

### B-001: Licenca oficial do dataset confirmada

**Discovered:** 2026-07-09
**Resolved:** 2026-07-12
**Impact:** O relatorio exige origem e licenca claras.
**Resolution:** Dataset Olist Brazilian E-Commerce (Kaggle) licenciado sob CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International). Uso academico/nao-comercial deste projeto e compativel; o relatorio (T12) deve creditar a fonte e declarar a licenca.

### B-002: Backend fundacional inexistente

**Discovered:** 2026-07-09
**Resolved:** 2026-07-09
**Impact:** Backend fundacional criado em `backend/`, com schemas, preparo de dados e ferramenta de risco historico.
**Resolution:** T1-T4 implementadas e validadas; continuam pendentes explicacao/acao, agente, API, produto, deploy e relatorio.

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
| 001 | Validar preparo historico e fluxo local completo com Gemini 2.5 Flash | 2026-07-12 | this commit | Done |
| 002 | Dockerizar backend/frontend e validar `docker compose up --build` com health checks | 2026-07-12 | `1c97fce` | Done |
| 003 | Integrar dashboard React ao agente via `/api/predict-delay` | 2026-07-12 | `c633766` | Done |
| 004 | Carregar ambiente Gemini no Compose e publicar dados preparados atomicamente | 2026-07-12 | `1b06215` | Done |
| 005 | Exibir respostas da LLM e fallbacks em linguagem amigavel | 2026-07-12 | `c062748` | Done |
| 006 | Validar dashboard mobile em 320 px, paisagem, loading, erro e rolagem da tabela | 2026-07-12 | this commit | Done |
| 007 | Manter o Blueprint do Render dentro da pasta de entrega do grupo | 2026-07-13 | this commit | Done |

---

## Deferred Ideas

- [ ] Treinar um modelo supervisionado para comparar com o agente - Captured during: planejamento.
- [ ] Usar reviews para analise pos-entrega e insights de satisfacao - Captured during: planejamento.
- [ ] Adicionar autenticacao e perfis de operador - Captured during: planejamento.
- [ ] Reavaliar MLflow, LangChain/LangGraph e observabilidade apos T7-T12 - Criterios em `TOOLING_REVIEW.md`; captured during: integracao da API.

---

## Todos

- [ ] Confirmar licenca oficial do dataset na fonte.
- [x] Definir onde hospedar API e frontend: Render; ver `DEPLOYMENT.md`.
- [ ] Evitar referencias a rascunhos locais nao commitados na documentacao versionada.
- [ ] Implementar AD-006: resposta estruturada da LLM, guardrail da acao e fallback deterministico.
- [ ] Implementar AD-007 e validar os criterios de aceite em `DEPLOYMENT.md`.

---

## Preferences

**Model Guidance Shown:** never

---

## Handoff

**Feature:** agente-previsao-atraso
**Phase/Task:** Phase 4 in progress — T1-T11, T7, T13 done; T14 deployed, automated public smoke and dashboard classification passed. Remaining: cold-start, fallback and Render memory UAT; then AD-006 and T12.
**Completed:**
- T1 `7154e85` — backend scaffold (`backend/`: app package, requirements.txt, pyproject pytest config, health smoke, README, .gitignore). Gate: `cd backend && ./.venv/bin/pytest`.
- T2 `7eb6695` — `backend/app/schemas.py`: Pydantic v2 `OrderInput`/`RiskEvidence`/`DelayPrediction`, UF + non-negative guardrails, `format_validation_error()`. 17 tests.
- T3 `4ab224a` — `backend/app/data_prep.py`: `build_order_features()`/`load_prepared_features()`, stdlib-only, delayed target, leakage excluded, aggregates. 7 tests. Real-data smoke: 96,470 delivered / 8.112% delayed (matches L-001).
- T4 current branch — `backend/app/risk_tool.py`: `HistoricalRiskTool`/`estimate_delay_risk()`, fallback hierarchy, risk score/level/confidence and factors. 5 tests.
- T5 current branch — `backend/app/explanation.py`: deterministic explanation/action policy, low-confidence human review and output guardrail for missing evidence. 10 tests.
- T6 current branch — `backend/app/agent.py`: `DelayAgent`/`classify_order()`, latency telemetry, fallback/guardrail events and LLM-first explanation flow. 6 tests.
- Alignment current branch — `backend/app/llm.py`: OpenAI-compatible LLM client with environment configuration and fallback-safe errors. 3 tests.
- T8 current branch — `backend/app/api.py`: health/prediction endpoints, friendly validation and service errors, event/latency logging, prepared-data and LLM environment wiring. 5 tests.
- T9/T10 current branch — `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/styles.css`, `frontend/vite.config.js`: dashboard queue state, add-order form, selected-order classification through `/api/predict-delay`, risk badges, details panel, fallback/error states and Vite dev proxy.
- T11 current branch — Docker packaging: backend image prepares `prepared_orders.jsonl` from versioned CSVs, frontend image serves Vite build with Nginx and proxies `/api/*`, compose starts both services with health checks.
- T7 `b1b721a` — `backend/app/evaluate.py`: offline leave-one-out evaluation reusing the risk tool's hierarchy/thresholds via a precomputed O(n) segment index. Reports calibration/confusion by risk band, recall/precision for high and medium+high alarms, fallback rate and per-state breakdown. 5 tests. Real-data run (96,470 orders): high band 20.3% observed vs 8.1% base; high-alarm recall 5.5%, medium+high recall 44.9%; fallback rate 21.4%.
- T13 current branch — LLM token telemetry: `llm.py` parses `usage` into prompt/completion/total tokens (no server-side cost — reasoning models bill total > prompt+completion, so cost is derived offline in the report); `schemas.py` adds `LLMUsage` and `DelayPrediction.llm_usage`; `agent.py` threads usage through (null on deterministic/fallback paths); `api.py` logs `llm_model` + token counts. Live-verified against gemini-2.5-flash (226/99/1026 tokens). Closes DELAY-08 (report derives cost). 4 tests.
- Reliability fixes `1b06215`/`c062748` — Compose loads `backend/.env`, prepared data is published atomically, Gemini returns plain text and the UI accumulates friendly fallback messages.
- T10 mobile UAT — passed at 320 px and landscape for table scrolling, form flow, loading/success, API error recovery and result readability. Physical-device numeric keyboard behavior was not tested; inputs use numeric `inputMode` hints.
**Test state:** 67 passed, 0 failed (`cd backend && ./.venv/bin/pytest`); frontend production build passes with `VITE_API_BASE`; Render-target Docker image builds and starts on `PORT=10000`, health passes, raw CSVs are absent from runtime and idle memory was ~97 MiB locally.
**Next step:** Finish T14 public UAT for controlled cold start, deterministic fallback and memory from the Render dashboard. Then implement AD-006 and finish T12 with the deployed URLs and measured evidence.
**Blockers:** none active for T12. B-001 (dataset license) still open for report.
**Uncommitted files:** none expected after the reliability documentation commit.
**Branch:** main.
**Notes:** Executing on `main` (matches T1). One sub-agent worker died on a transient API error mid-T3; T3 finished inline. Verifier not yet run — fires after feature's final task (T12).
