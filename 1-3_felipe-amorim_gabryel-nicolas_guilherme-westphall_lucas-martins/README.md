# Agente de Previsão de Atraso - Olist

> **Aplicação:** https://olist-delay-dashboard.onrender.com/  
> **API:** https://olist-delay-agent-api.onrender.com/  
> **Repositório:** https://github.com/west7/projeto-final-2026-1   
> **Equipe:** Felipe Amorim, Gabryel Nicolas, Guilherme Westphall, Lucas Martins  
> **Trilha:** 1.3 - Previsão de atraso de entrega

---

## 1. Definição do problema

**Dor:** hoje o atraso de um pedido só é percebido depois que ele já aconteceu - quando o cliente já está insatisfeito e a operação já perdeu a janela de agir. O projeto propõe antecipar esse risco logo após a compra/aprovação do pedido, para que logística, atendimento e operação possam intervir antes do problema se concretizar.

**Stakeholders:**
- **Equipe logística** - precisa identificar pedidos em risco para priorizar e agir antes do atraso.
- **Equipe de atendimento** - precisa entender *por que* um pedido está em risco, para comunicar o cliente com clareza.
- **Equipe operacional** - precisa de visibilidade agregada da situação dos pedidos para reagir com rapidez.

**Métricas de negócio:** reduzir o número de pedidos que chegam atrasados sem aviso prévio; aumentar a proporção de pedidos com intervenção antecipada; melhorar a velocidade de resposta da operação.

**Métrica técnica:** priorizar **recall** na detecção de casos críticos de atraso (não apenas acurácia), já que o alvo é fortemente desbalanceado.

**Escopo do MVP:** classificar se um pedido tem risco baixo/médio/alto de atraso, devolver uma explicação rastreável dos fatores e exibir tudo em um painel operacional.

---

## 2. Como o sistema é montado

### Arquitetura

![Fluxo da requisição: Cliente → FastAPI /predict-delay → DelayAgent → ModelRiskTool ou HistoricalRiskTool → guardrail explain_risk → LLM (explicação PT-BR) → DelayPrediction](assets/architecture.png)

O fluxo de uma predição: o operador envia/seleciona um pedido no painel → o frontend chama `POST /api/predict-delay` → a entrada passa por guardrails de validação (Pydantic) → o `DelayAgent` consulta a ferramenta de risco → o resultado passa por guardrails de saída → a LLM (ou o fallback determinístico) escreve a explicação e a ação recomendada → a resposta volta para o painel, junto com telemetria de latência, fallback e uso de tokens.

**Exploração de abordagens (agent/model exploration):** a decisão inicial (AD-001) foi não treinar nenhum modelo supervisionado no MVP, e usar só uma ferramenta determinística de consulta a segmentos históricos - isso mantinha o foco do trabalho no ciclo agente → API → produto, guardrails e confiabilidade, em vez de otimização de modelo. Depois do MVP entregue, a equipe evoluiu essa decisão (AD-008): um classificador `HistGradientBoostingClassifier` calibrado (`CalibratedClassifierCV`, calibração isotônica) foi adicionado como fonte do número de risco, atrás do mesmo contrato `estimate_delay_risk`, com rastreamento opcional via MLflow. A ferramenta histórica continua ativa como fallback e como fonte dos fatores explicativos.

**Deployment:** backend (FastAPI + Docker) e frontend (React/Vite, servido por Nginx) publicados no Render - o frontend como Static Site (sem spin-down) e o backend como Web Service Docker do plano gratuito. O dataset preparado (`prepared_orders.jsonl`) é gerado durante o build multi-stage da imagem, então a imagem final não carrega os CSVs brutos nem depende de disco persistente em runtime. Validação pública registrada em 13/07/2026: frontend HTTP 200 em 0,25s; `/health` em 4,96s; `POST /predict-delay` em 7,23s (latência interna de 6.880ms, a maior parte gasta na chamada ao Gemini; essa medição é anterior à otimização de latência descrita na seção 4, que reduziu a latência interna para ~1,1s); CORS restrito ao domínio do frontend.

**Restrição conhecida do plano gratuito do Render:** o backend "dorme" após 15 minutos de inatividade e pode levar cerca de um minuto para acordar. O frontend mostra um estado de "preparando agente" e reconsulta `/health` por até ~90 segundos antes de liberar a classificação, em vez de travar silenciosamente.

**CI/CD:** não há pipeline de CI configurado; os gates de qualidade (suíte pytest do backend e `npm run build` do frontend) são executados localmente antes de cada entrega, e o deploy no Render é feito via Blueprint (`render.yaml`) versionado no repositório.

### Como rodar o projeto

**Pré-requisitos:**
- Docker com Docker Compose.
- Dataset Olist presente em `dataset/` (já versionado no repositório).
- `backend/.env` criado a partir de `backend/.env.example`.

**Subir API e frontend:**

```bash
docker compose up --build
```

Na primeira subida, o backend gera automaticamente `backend/data/prepared_orders.jsonl` a partir dos CSVs em `dataset/`. O arquivo fica em um volume Docker e é reutilizado nas próximas execuções - não precisa reprocessar o dataset a cada `up`.

**Serviços disponíveis localmente:**

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| Health check da API | http://localhost:8000/health |
| Proxy da API via frontend/Nginx | http://localhost:5173/api/health |

**Exemplo de chamada direta ao agente:**

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

**Configuração da LLM** (`backend/.env`):

```dotenv
LLM_API_KEY=sua_chave
LLM_MODEL=gemini-2.5-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_TIMEOUT_SECONDS=20
```

Sem chave de LLM configurada, o agente continua funcionando normalmente com a explicação determinística e registra o guardrail `llm_unconfigured` - nenhuma requisição quebra por falta de credencial.

**Rodar os testes e o build (gates de qualidade):**

```bash
# backend: 92 testes automatizados (pytest)
cd backend && ./.venv/bin/python -m pytest -q

# frontend: build de produção
cd frontend && npm run build
```

**Rodar com MLflow (opcional, só para o rastreamento do modelo calibrado):**

```bash
docker compose --profile mlflow up --build
# painel do MLflow em http://localhost:5000
```

**Usando a versão em produção (sem instalar nada):** basta abrir o frontend em https://olist-delay-dashboard.onrender.com/ - não é necessário rodar nada localmente para avaliar o sistema. Só é preciso lembrar que o backend gratuito do Render pode levar cerca de um minuto para "acordar" na primeira requisição depois de um período ocioso (cold start).

---

## 3. Descrição do agente

**Modelo base:** Gemini 2.5 Flash, consumido via um cliente compatível com a API da OpenAI (`backend/app/llm.py`), configurável por variáveis de ambiente (`LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`). A escolha prioriza custo e latência baixos para uma tarefa de reescrita de texto curto, não geração aberta longa.

**Ferramentas do agente:**
- `HistoricalRiskTool` - calcula risco por similaridade a segmentos históricos do Olist, com uma hierarquia de 7 fallbacks (do recorte mais específico - vendedor + cliente + categoria - até a base global), cada um com um tamanho mínimo de amostra exigido.
- `ModelRiskTool` (evolução pós-MVP) - usa o classificador calibrado como fonte do score, mantendo a mesma interface e os mesmos fatores explicativos da ferramenta histórica.
- Cliente LLM - não decide o risco; só transforma as evidências numéricas (score, confiança, amostra, recorte, fatores) em uma explicação curta e uma ação recomendada, em português, sem Markdown e sem inventar dados (restrição explícita no prompt de sistema).

**Dados e contexto:** o dataset Olist Brazilian E-Commerce (Kaggle, licença **CC BY-NC-SA 4.0** - uso não comercial, compatível com este trabalho acadêmico) é processado offline para gerar features por pedido sem vazamento temporal: apenas pedidos entregues recebem rótulo, `order_delivered_customer_date` só é usado para construir o alvo (nunca como entrada), e campos posteriores à entrega - reviews e status final - são excluídos das features. O resultado é `prepared_orders.jsonl`, com 96.470 pedidos entregues.

**Guardrails:**
- **Entrada** (Pydantic): estado do cliente e do vendedor precisam ser UFs brasileiras válidas; valores monetários e contagens não podem ser negativos; campos obrigatórios ausentes retornam erro de validação amigável, sem stack trace.
- **Saída:** a explicação só é gerada se a evidência tiver fatores, um recorte (`segment_used`) e uma amostra maior que zero; se qualquer um faltar, o guardrail bloqueia o caminho normal e devolve uma resposta segura ("revisão humana", risco baixo, confiança baixa).
- Quando a LLM não está configurada, falha, expira ou devolve texto vazio, o agente registra o evento (`llm_unconfigured` / `llm_fallback` / `llm_fallback:empty_response`) e usa a explicação determinística como resposta - o usuário nunca vê um erro técnico cru.

**Iterações de design (o que não funcionou / mudou):**
- A ação recomendada pela LLM e a ação da política determinística ficavam duplicadas na interface porque a LLM era instruída a sugerir a ação *dentro* da explicação; a equipe registrou essa limitação (AD-006) e planejou separar `explanation` e `recommended_action` como campos estruturados da LLM, com um guardrail semântico comparando a ação da LLM com a política de referência - implementação ainda pendente no momento desta entrega.
- O baseline puramente histórico tinha discriminação fraca em alarmes de alto risco (recall de 5,5%), o que motivou a evolução pós-MVP para o modelo calibrado (ver seção de avaliação).

---

## 4. Avaliação do sistema

### Performance (avaliação offline sobre os 96.470 pedidos entregues)

| Métrica | Baseline histórico | Modelo calibrado |
|---|---|---|
| Recall (alarme alto risco) | 5,5% | **37,6%** |
| Precisão (alarme alto risco) | 20,3% | 32,2% |
| Recall (alarme médio+alto) | 44,9% | 64,1% |
| Taxa de fallback | 21,4% | **0%** |
| Taxa base de atraso | 8,1% | 8,1% |

O modelo calibrado (`HistGradientBoostingClassifier` + `CalibratedClassifierCV`) eleva bastante o recall de casos críticos e elimina o fallback por amostra insuficiente, porque não depende de segmentos com poucos exemplos. As faixas de risco permanecem monotônicas em ambas as abordagens (risco "alto" observado > "médio" > "baixo"), o que indica calibração coerente.

**Por estado (baseline → modelo), recall de detecção de atraso:** SP 1,7% → 19,4%; RJ 9,5% → 63,9%; MG 0% → 26,2%; DF 0% → 26,5%; SC 0% → 35,8%; BA 0% → 51,6%. O baseline histórico praticamente não detectava atraso em vários estados (recall 0%) por falta de amostra suficiente nesses recortes; o modelo calibrado reduz essa disparidade de forma relevante, embora ainda existam diferenças entre estados.

### Latência e custo por chamada (antes → depois)

Quase toda a latência de uma predição está na chamada à LLM, não no núcleo determinístico: o cálculo de risco (modelo + consulta histórica + guardrails) leva **~175ms**. O Gemini 2.5 Flash vinha com o modo de raciocínio ("thinking") ligado por padrão, gastando ~870 tokens de raciocínio ocultos por chamada antes de escrever uma explicação curta. Desativar o raciocínio (`reasoning_effort=none`, configurável por `LLM_REASONING_EFFORT`) reduziu drasticamente a latência **sem alterar a resposta**:

| | Chamada à LLM | Latência interna (ponta a ponta) | Tokens por chamada |
|---|---|---|---|
| Antes (raciocínio ligado) | ~4,7s | ~6,9s | 1.178 |
| Depois (`reasoning_effort=none`) | ~0,9s | **~1,1s** | 307 |

Os tokens de conclusão (a resposta em si) não mudaram (82 tokens); apenas os ~870 tokens de raciocínio oculto foram eliminados: para uma tarefa de reescrita das evidências, zero raciocínio é adequado. A redução de ~5x na latência e de ~74% nos tokens também simplifica o custo: com o raciocínio desligado, `total ≈ prompt + conclusão`, então a estimativa de custo por chamada deixa de ser inflada por tokens de raciocínio. A latência interna (`latency_ms`) e a contagem de tokens são registradas na telemetria de cada requisição, o que permite acompanhar esses números em produção.

**UX:** o painel exibe o nível de risco como badge, a explicação e a ação recomendada lado a lado, e trata de forma visível os estados de fallback (LLM indisponível), erro de API e carregamento - inclusive o estado de "aquecendo" durante o cold start do plano gratuito do Render. Validação manual em mobile (320px, paisagem) cobriu rolagem de tabela, formulário, loading e recuperação de erro; o comportamento do teclado numérico em dispositivo físico não foi testado (os campos usam apenas a dica `inputMode="numeric"`).

**Testes automatizados:** 92 testes de backend (`pytest`), 0 falhas, cobrindo schemas/guardrails de entrada, ferramenta de risco, explicação/fallback, agente, API, cliente LLM, preparo de dados, encoding de features, treino, avaliação e MLflow. O frontend tem gate de build (`npm run build`), sem testes automatizados de componente.

---

## 5. Demonstração

- Link do vídeo de demonstração: [Vídeo de demonstração de funcionamento](https://youtu.be/47ArI0O_ljg)

---

## 6. Reflexão sobre o que aprendemos

**O que funcionou bem:** separar a ferramenta de risco (determinística, auditável) da camada de linguagem (LLM, responsável só por redigir) deu previsibilidade ao sistema mesmo quando a LLM falha - o fallback gracioso funcionou como planejado nos testes. A avaliação offline com dados reais (96.470 pedidos) expôs cedo a fraqueza do baseline histórico em alarmes de alto risco, o que justificou a evolução para o modelo calibrado dentro do prazo.

**O que não funcionou como planejado:** a separação entre explicação e ação recomendada da LLM ficou pendente (AD-006) - hoje a ação sempre vem da política determinística, e o prompt da LLM ainda menciona um próximo passo dentro do texto, gerando alguma redundância na interface. O teste do teclado numérico em dispositivo físico e a validação completa de cold start/memória em produção também ficaram como itens em aberto no momento desta entrega.

**Próximos passos (com mais tempo):** implementar o contrato estruturado LLM (explicação + ação separadas, com guardrail semântico de compatibilidade); medir o pico de memória do backend no Render sob classificações simultâneas; investigar mais a fundo a disparidade regional de recall que persiste mesmo com o modelo calibrado.

---

## 7. Impactos e ética

**Quem pode ser prejudicado por um erro do sistema:** um falso negativo (pedido marcado como baixo risco que atrasa) deixa a operação sem tempo de reagir e o cliente sem aviso - o dano recai sobre o cliente final. Um falso positivo pode gerar comunicação preventiva desnecessária ou uso de recursos logísticos em um pedido que chegaria no prazo.

**Viés entre grupos (regional):** a avaliação por estado mostra que o baseline histórico tinha recall 0% de detecção de atraso em vários estados (MG, RS, DF, SC, entre outros) simplesmente por falta de amostra suficiente nesses recortes - um viés estrutural contra regiões menos representadas no histórico, coerente com o risco de sub-representação de Norte/Nordeste identificado na análise de dados do projeto. O modelo calibrado reduz essa disparidade (por exemplo, DF sai de 0% para 26,5% de recall, BA de 0% para 51,6%), mas os estados continuam com desempenho desigual entre si, então uma recomendação operacional automática ainda deveria ser tratada com mais cautela em regiões historicamente sub-representadas.

**Privacidade e segurança:** os identificadores do Olist são pseudônimos; o sistema não expõe dados pessoais adicionais do cliente além do que já está nos CSVs públicos. A entrada é restrita a campos estruturados do pedido (não texto livre), o que reduz a superfície de abuso/prompt injection sobre a LLM.

**Mitigações adotadas ou recomendadas:** priorizar recall em vez de acurácia para não mascarar o desempenho fraco em atrasos (dado o desbalanceamento de 8,1%); reportar amostra e confiança junto com o risco, para que baixa confiança vire sinal de revisão humana em vez de decisão automática; manter a quebra de métricas por estado visível no processo de avaliação, para acompanhar disparidades regionais ao longo do tempo.

---

## 8. Referências

- Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle), licença **CC BY-NC-SA 4.0**.
- Modelo de linguagem: Gemini 2.5 Flash, via API compatível com OpenAI.
- Bibliotecas principais: FastAPI, Pydantic v2, scikit-learn (`HistGradientBoostingClassifier`, `CalibratedClassifierCV`), MLflow (rastreamento opcional), React 19, Vite 6.
- Infraestrutura: Docker / Docker Compose, Render (Static Site + Web Service Docker), Nginx.
- Documentação do enunciado do projeto: `readme.md` e `trilhas.md` do repositório da disciplina.

---