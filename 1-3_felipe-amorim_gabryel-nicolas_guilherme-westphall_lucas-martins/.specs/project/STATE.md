# State

**Last Updated:** 2026-07-13
**Current Work:** agente-previsao-atraso - final refinements (T15-T18)

---

## Recent Decisions

### AD-001: MVP sem modelo supervisionado (2026-07-09)

**Status:** superseded by AD-008 (2026-07-13) — valido apenas para o MVP.
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
**Impact:** Implementado em T16/T17: `backend/app/llm.py` retorna os campos separados sob JSON Schema; `backend/app/agent.py` valida `action_intent` e mantém `explain_risk()` como fallback seguro para ambos os textos.

### AD-007: Frontend e backend no Render com custo zero como alvo (2026-07-12)

**Decision:** Hospedar o frontend como Render Static Site e o backend como Render Free Web Service Docker. Aceitar o cold start do plano gratuito, incorporar o dataset preparado na imagem e manter Render Starter como contingencia para a demo.
**Reason:** Um unico provedor reduz configuracao e risco operacional; o Render suporta site estatico, FastAPI/Docker, secrets, health check e URLs HTTPS.
**Trade-off:** O backend gratuito dorme apos inatividade, tem filesystem efemero, 512 MB/0,1 CPU e pode demorar cerca de um minuto para acordar.
**Impact:** Implementar `VITE_API_BASE`, CORS restrito, build-time data prep, uso de `$PORT`, estado de aquecimento/retry e `render.yaml`. Nao usar UptimeRobot para impedir permanentemente o spin-down; detalhes em `DEPLOYMENT.md`.

### AD-008: Modelo supervisionado calibrado como evolucao pos-MVP (2026-07-13)

**Status:** active — supersedes AD-001.
**Decision:** Apos o MVP entregue, adicionar um classificador calibrado (sklearn `HistGradientBoostingClassifier` + `CalibratedClassifierCV`) como fonte do numero de risco, treinado apenas com features reconstrutiveis do `OrderInput` (exclui `sellers_count`). O `HistoricalRiskTool` permanece como fallback e como fonte das evidencias/fatores; a camada LLM (AD-005/AD-006) nao muda. Rastreamento de experimentos e registro do modelo via MLflow, estritamente opcional. Trabalho na branch `feat/modelo-ml-mlflow`.
**Reason:** MVP ja entregue; a rubrica premia a iteracao baseline→modelo, exploracao de modelos e proximos passos. A discriminacao fraca do baseline (recall de alarme alto 5.5%) e a fraqueza honesta que o modelo enderaca. MLflow realiza a competencia de rastreamento de experimentos da disciplina.
**Trade-off:** Adiciona dependencias (`scikit-learn`, `mlflow`) isoladas em `requirements-ml.txt` e um servico opcional; risco de perder calibracao/interpretabilidade — mitigado por calibracao isotonica, reuso dos limiares existentes e degradacao graciosa.
**Impact:** Nova feature `.specs/features/modelo-ml-mlflow/`; `ModelRiskTool` atras do mesmo seam `estimate_delay_risk`; `evaluate.py --scorer model`; artefato JSON de comparacao baseline-vs-modelo + quebra por estado para a secao de etica.

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

- [ ] Usar reviews para analise pos-entrega e insights de satisfacao - Captured during: planejamento.
- [ ] Adicionar autenticacao e perfis de operador - Captured during: planejamento.
- [ ] Reavaliar LangChain/LangGraph somente se o fluxo ganhar multiplas ferramentas/etapas; criterios em `TOOLING_REVIEW.md`.

---

## Todos

- [x] Confirmar licenca oficial do dataset na fonte.
- [x] Definir onde hospedar API e frontend: Render; ver `DEPLOYMENT.md`.
- [x] Evitar referencias a rascunhos locais nao commitados na documentacao versionada.
- [x] Implementar AD-006: resposta estruturada da LLM, guardrail da acao e fallback deterministico.
- [ ] Concluir UAT restante de AD-007: cold start controlado, fallback publico e memoria no Render.

---

## Preferences

**Model Guidance Shown:** never

---

## Handoff

**Feature:** agente-previsao-atraso — final refinements on `main`.
**Current task:** T18, observabilidade da sessao no dashboard. T15-T17 concluidas.
**Implemented baseline:** public Render frontend/API, calibrated model behind `ModelRiskTool`, historical evidence/fallback, optional MLflow, report and demo video.
**Evaluation evidence:** 96,470 orders; high-alarm recall 5.5% -> 37.6%, precision 20.3% -> 32.2%, fallback 21.4% -> 0%; committed in `backend/data/eval_{historical,model}.json`.
**Public URLs:** `https://olist-delay-dashboard.onrender.com/` and `https://olist-delay-agent-api.onrender.com/`.
**Test state:** 98 backend tests aprovados apos AD-006; o ambiente local instala ambos os arquivos de requisitos.
**Remaining deploy UAT:** controlled cold start, public deterministic fallback and Render memory observation. These do not block T15-T18.
**Blockers:** none.
