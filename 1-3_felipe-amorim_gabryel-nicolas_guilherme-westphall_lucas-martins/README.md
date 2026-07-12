# Definição do problema - Trilha 1.3

## Problema

O projeto busca identificar, com antecedência, pedidos que têm alto risco de atraso antes que o atraso se concretize. A proposta é apoiar a operação logística, a equipe de atendimento e a equipe operacional na tomada de decisão, permitindo intervenções preventivas.

## Stakeholders

- Equipe logística: precisa identificar pedidos em risco para agir antes do atraso.
- Equipe de atendimento: precisa entender por que um pedido está em risco e comunicar isso de forma clara.
- Equipe operacional: precisa ter visibilidade sobre a situação dos pedidos e agir com mais rapidez.

## Métricas de negócio

- Reduzir o número de pedidos que chegam atrasados sem aviso.
- Aumentar a proporção de pedidos com intervenção antecipada.
- Melhorar a velocidade de resposta da equipe operacional.

## Métrica técnica

- Classificar corretamente pedidos em risco de atraso, priorizando a detecção de casos críticos.

## Escopo inicial do MVP

- Classificar se um pedido provavelmente vai atrasar ou não.
- Devolver uma explicação simples dos fatores principais que levaram à classificação.
- Exibir os resultados em uma tela de operação/logística.

## Como subir com Docker Compose

Pré-requisitos:

- Docker com Docker Compose.
- Dataset Olist presente em `dataset/` (já versionado neste projeto).

Subir API e frontend:

```bash
docker compose up --build
```

Na primeira subida, o backend gera automaticamente `backend/data/prepared_orders.jsonl`
a partir dos CSVs em `dataset/`. O arquivo fica em um volume Docker e é reutilizado
nas próximas execuções.

Serviços:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- Health check da API: <http://localhost:8000/health>
- Proxy da API via frontend/Nginx: <http://localhost:5173/api/health>

Exemplo de chamada direta ao agente:

```bash
curl -X POST http://localhost:8000/predict-delay \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "demo-1",
    "customer_state": "RJ",
    "seller_state": "SP",
    "product_category_name": "moveis_decoracao",
    "freight_value": 42.9,
    "price": 180.0,
    "items_count": 1,
    "payment_type": "credit_card",
    "payment_installments": 3
  }'
```

Configuração opcional de LLM:

```bash
LLM_API_KEY=sua_chave \
LLM_MODEL=gpt-4o-mini \
docker compose up --build
```

Sem chave de LLM, o agente continua funcionando com explicação determinística e
registra o fallback `llm_unconfigured`.
