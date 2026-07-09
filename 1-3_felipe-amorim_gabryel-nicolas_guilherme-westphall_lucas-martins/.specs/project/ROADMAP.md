# Roadmap

**Current Milestone:** M1 - Baseline planejado
**Status:** Planning

---

## M1 - Fundacao SDD e Baseline do Agente

**Goal:** Ter a arquitetura, tarefas e criterio de sucesso prontos para executar o MVP sem ambiguidade.
**Target:** Documentos aprovados e feature principal pronta para implementacao.

### Features

**Mapeamento do Projeto** - COMPLETE

- Documentar stack, estrutura, arquitetura atual, convencoes, testes, integracoes e riscos.
- Registrar decisoes do projeto e limites do MVP.

**Agente de Previsao de Atraso** - PLANNED

- Preparar dataset derivado com features seguras.
- Calcular risco com estatisticas historicas e fallback por recortes progressivos.
- Responder com risco, confianca, explicacao e acao sugerida.

---

## M2 - API Deployable

**Goal:** Expor o agente como API reproduzivel.

### Features

**API REST de Classificacao** - PLANNED

- Endpoint `POST /predict-delay`.
- Validacao de schema e guardrails.
- Respostas padronizadas para sucesso, fallback e erro de entrada.

**Observabilidade Minima** - PLANNED

- Medir latencia por chamada.
- Registrar fallback, erros de guardrail e custo estimado de LLM se usado.
- Criar logs consultaveis para o relatorio.

---

## M3 - Produto Operacional

**Goal:** Permitir que uma pessoa use o sistema pelo navegador.

### Features

**Painel de Torre de Controle** - PLANNED

- Cadastrar ou importar pedidos.
- Classificar selecionados via API.
- Exibir nivel de risco, explicacao, confianca e acao sugerida.
- Mostrar estados de carregamento, erro e fallback.

**Demo e Relatorio** - PLANNED

- Documentar arquitetura, dados, metricas, guardrails, fallback, limitacoes e etica.
- Gravar demonstracao com casos reais e extremos.

---

## Future Considerations

- Treinar modelo supervisionado como comparativo de proximo passo.
- Adicionar historico de decisoes do operador.
- Conectar notificacao proativa de atendimento.
- Criar dashboard de performance por regiao/categoria/vendedor.
