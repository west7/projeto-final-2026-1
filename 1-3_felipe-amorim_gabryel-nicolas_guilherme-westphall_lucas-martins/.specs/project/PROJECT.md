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
- Backend/API: Python 3.12, FastAPI, Pydantic e Uvicorn.
- Agent layer: Gemini 2.5 Flash para linguagem, modelo calibrado para o risco e ferramenta historica para evidencias/fallback.
- Data: CSVs do Olist em `dataset`.

**Key dependencies:**

- scikit-learn/joblib para treino e serving do classificador calibrado.
- MLflow opcional para rastreamento de experimentos e registro do modelo.
- FastAPI e Pydantic para API e validacao.
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

- Treino online, AutoML, deep learning e busca extensa de hiperparametros.
- Usar reviews para prever risco, pois reviews acontecem depois da experiencia do pedido.
- Otimizacao operacional automatica real, como disparar mensagens ou alterar rota em sistemas externos.
- Autenticacao multiusuario.
- Banco de dados transacional completo.

## Constraints

- Timeline: entrega em 13/07/2026.
- Technical: dataset local em CSV; deploy gratuito limitado a 512 MB e sujeito a cold start.
- Evaluation: trabalho precisa demonstrar agente, API, produto, guardrails, fallback, latencia/custo e monitoramento.
- Data/license: dataset Olist Brazilian E-Commerce (Kaggle), licenciado CC BY-NC-SA 4.0. Uso academico/nao-comercial e compativel; origem e licenca devem ser declaradas no relatorio.
