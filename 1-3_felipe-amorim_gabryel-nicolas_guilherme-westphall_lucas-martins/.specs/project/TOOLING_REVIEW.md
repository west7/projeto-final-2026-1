# Revisao de Ferramentas Pos-MVP

**Registrado em:** 2026-07-12
**Reavaliar quando:** T7-T12 estiverem concluidas e o fluxo agente -> API -> produto estiver validado.
**Status:** Adiado; nenhuma dependencia deve ser adicionada antes da reavaliacao.

## Contexto

Foram consideradas ferramentas vistas durante a disciplina para reforcar a natureza agentica, a avaliacao e a observabilidade do projeto. A decisao atual prioriza concluir o MVP com a arquitetura simples ja implementada e revisitar as opcoes abaixo somente depois dos gates finais.

O `codenavi`, mencionado durante a navegacao do repositorio, e uma skill opcional do ambiente Codex para explorar codigo, encontrar padroes e rastrear dependencias. Ele nao e uma dependencia de runtime nem uma tecnologia a ser entregue com o projeto.

## Recomendacao Atual

### MLflow: candidato recomendado

MLflow tem aderencia direta aos requisitos de avaliacao e monitoramento. A integracao mais util seria na T7 e na instrumentacao do agente para registrar:

- recall e precision de atrasos;
- matriz de confusao e resultados por faixa de risco;
- taxa e profundidade de fallback;
- metricas por estado ou regiao;
- latencia, modelo e uso de tokens da LLM;
- artefatos CSV/JSON e comparacao entre execucoes.

A integracao deve ser opcional: o script de avaliacao e a API precisam continuar funcionando sem um servidor MLflow. Se adotado, MLflow deve entrar depois do MVP basico, preferencialmente em Docker Compose, sem se tornar requisito para o endpoint subir.

### LangChain: nao recomendado no fluxo atual

O fluxo atual e curto e controlado:

```text
entrada -> consulta historica -> evidencia -> explicacao LLM -> guardrail -> resposta
```

LangChain passa a fazer sentido quando o modelo precisa escolher entre varias ferramentas, executar um loop de raciocinio/acao, manter memoria ou coordenar passos dinamicos. O projeto possui uma ferramenta historica e uma sequencia previamente definida; trocar o cliente atual pelo framework aumentaria dependencias e superficie de falha sem resolver uma necessidade presente.

Uma possivel excecao e uma exigencia academica explicita de tool calling decidido pela LLM. Nesse caso, avaliar primeiro tool calling estruturado diretamente no cliente OpenAI-compatible. Adotar LangChain apenas se surgirem varias ferramentas ou um loop agentico real.

### LangGraph: nao recomendado no MVP

Persistencia de estado, retomada de execucao, streaming, memoria conversacional e human-in-the-loop nao fazem parte do fluxo atual. Esses requisitos justificariam LangGraph em uma evolucao futura, nao nesta entrega.

## Outras Ferramentas

| Ferramenta | Decisao atual | Motivo |
| --- | --- | --- |
| Docker Compose | Prioridade alta em T11 | Torna frontend, backend e servicos opcionais reproduziveis para avaliacao. |
| Logging JSON estruturado | Prioridade alta | Atende observabilidade minima com baixa complexidade. |
| OpenTelemetry | Adiar | Adequado para traces e metricas, mas sobrepoe parte do valor do MLflow neste MVP. |
| LangSmith | Alternativa, nao complemento | Considerar no lugar do MLflow se o projeto migrar para o ecossistema LangChain. |

## Criterios para Reavaliacao

Ao finalizar o projeto, responder:

1. O trabalho ja demonstra metricas e comparacao de experimentos de forma convincente?
2. A apresentacao ganharia valor concreto com a interface e os artifacts do MLflow?
3. Ha tempo para adicionar e testar um servico sem comprometer deploy e demo?
4. A LLM precisa realmente decidir quais ferramentas chamar?
5. Existem duas ou mais ferramentas, iteracao, memoria ou estado persistente?
6. A rubrica exige um framework agentico especifico ou apenas comportamento de agente?

**Regra de decisao:** adotar MLflow se melhorar claramente a evidencia de avaliacao sem bloquear o MVP. Adotar LangChain/LangGraph somente se os requisitos agenticos tiverem evoluido alem do fluxo deterministico atual.

## Fontes Oficiais para a Proxima Revisao

- [MLflow for GenAI](https://www.mlflow.org/docs/latest/genai/getting-started)
- [MLflow Tracing](https://www.mlflow.org/docs/latest/genai/getting-started/tracing)
- [MLflow evaluation of traces](https://www.mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [LangSmith evaluation](https://docs.langchain.com/langsmith/evaluation)
