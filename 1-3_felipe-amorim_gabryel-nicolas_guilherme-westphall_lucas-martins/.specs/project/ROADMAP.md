# Roadmap

**Current Milestone:** M4 - Refinamento final
**Status:** Executing

---

## M1 - Fundacao SDD e Baseline do Agente

**Goal:** Ter a arquitetura, tarefas e criterio de sucesso prontos para executar o MVP sem ambiguidade.
**Target:** Documentos aprovados e feature principal pronta para implementacao.

### Features

**Mapeamento do Projeto** - COMPLETE

- Documentar stack, estrutura, arquitetura atual, convencoes, testes, integracoes e riscos.
- Registrar decisoes do projeto e limites do MVP.

**Agente de Previsao de Atraso** - COMPLETE

- Preparar dataset derivado com features seguras.
- Calcular risco com estatisticas historicas e fallback por recortes progressivos.
- Responder com risco, confianca, explicacao e acao sugerida.

---

## M2 - API Deployable

**Goal:** Expor o agente como API reproduzivel.

### Features

**API REST de Classificacao** - COMPLETE

- Endpoint `POST /predict-delay`.
- Validacao de schema e guardrails.
- Respostas padronizadas para sucesso, fallback e erro de entrada.

**Observabilidade Minima** - COMPLETE

- Medir latencia por chamada.
- Registrar fallback, erros de guardrail e custo/latencia estimados da chamada LLM.
- Criar logs consultaveis para o relatorio.

---

## M3 - Produto Operacional

**Goal:** Permitir que uma pessoa use o sistema pelo navegador.

### Features

**Painel de Torre de Controle** - COMPLETE

- Cadastrar ou importar pedidos.
- Classificar selecionados via API.
- Exibir nivel de risco, explicacao, confianca e acao sugerida.
- Mostrar estados de carregamento, erro e fallback.

**Demo e Relatorio** - COMPLETE

- Documentar arquitetura, dados, metricas, guardrails, fallback, limitacoes e etica.
- Gravar demonstracao com casos reais e extremos.

---

## M4 - Modelo, Experimentos e Refinamento Final

**Goal:** Evoluir o baseline, comprovar o ganho e fechar as lacunas de produto identificadas na validacao.

### Features

**Modelo calibrado + MLflow** - COMPLETE

- Usar um classificador calibrado como fonte do risco e preservar evidencia historica/fallback.
- Comparar baseline e modelo com artefatos reproduziveis e rastreamento MLflow opcional.

**Saida LLM estruturada e observabilidade no painel** - COMPLETE

- Separar explicacao e acao, validar a intencao da acao contra a politica deterministica e degradar com seguranca.
- Mostrar latencia, fallback/guardrails e tokens agregados apenas para a sessao atual do navegador.

---

## Future Considerations

- Avaliar modelos alternativos e ajuste de limiares conforme custo operacional real.
- Adicionar historico de decisoes do operador.
- Conectar notificacao proativa de atendimento.
- Criar dashboard de performance por regiao/categoria/vendedor.
