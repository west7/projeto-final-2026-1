# Agente de Previsao de Atraso Olist

**Vision:** Construir um agente de IA que estime o risco de atraso de um pedido, explique os fatores principais e recomende uma acao operacional antes que o atraso aconteca.
**For:** Equipes de logistica, atendimento e operacao de e-commerce.
**Solves:** Atrasos hoje sao percebidos tarde demais; o sistema antecipa risco para permitir priorizacao, comunicacao proativa e intervencao operacional.

## Goals

- Entregar um MVP deployable ate 13/07/2026 com ciclo completo agente -> API -> produto.
- Classificar pedidos em faixas de risco com explicacao rastreavel baseada no historico Olist.
- Expor uma API com validacao de entrada, fallback e resposta sem erro tecnico cru.
- Disponibilizar uma interface operacional que permita cadastrar/importar pedidos, classificar risco e ver explicacoes.
- Registrar latencia, custo estimado, fallback e erros de guardrail para suportar a avaliacao do sistema.

## Tech Stack

**Core:**

- Frontend: React 19 + Vite 6, ja presente em `frontend`.
- Backend/API: Python a definir durante implementacao, recomendado FastAPI pelo encaixe com API REST e validacao de schema.
- Agent layer: agente deterministico com ferramenta de consulta estatistica ao dataset; LLM opcional para redacao controlada da explicacao.
- Data: CSVs do Olist em `dataset`.

**Key dependencies planned:**

- Python stdlib para baseline de leitura/agregacao se o tempo for curto.
- FastAPI e Pydantic para API e validacao, se dependencias puderem ser adicionadas.
- React/Vite para produto.
- Docker/Docker Compose para reproducibilidade.

## Scope

**v1 includes:**

- Preparacao offline de uma base derivada com features seguras para previsao antes da entrega.
- Ferramenta de consulta que calcula risco por similaridade historica e fallback por recortes mais amplos.
- Agente que chama a ferramenta, classifica risco, explica fatores e sugere acao.
- API REST para classificar um pedido e retornar explicacao, nivel de confianca e metadados.
- Painel logistico que envia pedidos para a API e exibe risco, explicacao e acao sugerida.
- Guardrails de entrada, guardrails de saida, fallback e logging minimo.
- Relatorio/documentacao de dados, metricas, limitacoes, vieses e arquitetura.

**Explicitly out of scope:**

- Treinar um modelo de ML separado no MVP, como LightGBM ou rede neural.
- Usar reviews para prever risco, pois reviews acontecem depois da experiencia do pedido.
- Otimizacao operacional automatica real, como disparar mensagens ou alterar rota em sistemas externos.
- Autenticacao multiusuario.
- Banco de dados transacional completo.

## Constraints

- Timeline: entrega em 13/07/2026.
- Technical: dataset local em CSV; sem backend implementado ainda.
- Evaluation: trabalho precisa demonstrar agente, API, produto, guardrails, fallback, latencia/custo e monitoramento.
- Data/license: dataset Olist deve ter origem e licenca declaradas no relatorio; a licenca deve ser confirmada na pagina oficial do Kaggle antes da entrega.
