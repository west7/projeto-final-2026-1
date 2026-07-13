# Estrategia de Deploy no Render

**Decisao:** Render para frontend e backend.
**Meta de custo:** manter o MVP no plano gratuito sempre que possivel.
**Registrado em:** 2026-07-12
**Status:** Aprovado para implementacao.

## Arquitetura Alvo

```text
Render Static Site (React/Vite)
              |
              | HTTPS
              v
Render Free Web Service (FastAPI/Docker)
              |
              v
          Gemini API
```

- O frontend sera um Static Site gratuito, servido pelo CDN do Render e sem spin-down.
- O backend sera um Web Service Docker Free, com `/health` como health check.
- A chave Gemini e as demais configuracoes sensiveis serao cadastradas como secrets no painel do Render, nunca enviadas em `.env`.

## Restricoes do Plano Gratuito

- O backend entra em spin-down depois de 15 minutos sem trafego e pode levar cerca de um minuto para responder novamente.
- O filesystem e efemero: arquivos escritos em runtime sao perdidos em restart, redeploy ou spin-down.
- O workspace recebe 750 horas gratuitas de instancia por mes.
- A instancia Free oferece 512 MB de RAM e 0,1 CPU e pode ser reiniciada sem aviso.
- O Render pode suspender servicos gratuitos que gerem trafego externo incomum; chamadas ao Gemini devem permanecer proporcionais ao uso real.

Fontes oficiais:

- [Render Free](https://render.com/docs/free)
- [Render Web Services](https://render.com/docs/web-services)
- [Render Pricing](https://render.com/pricing)
- [Render Acceptable Use Policy](https://render.com/acceptable-use)

## Posicao sobre UptimeRobot

UptimeRobot Free oferece monitor HTTP em intervalo de cinco minutos. Esse intervalo impediria o spin-down de 15 minutos do backend e consumiria praticamente toda a cota mensal de 750 horas.

Nao usar UptimeRobot com a finalidade de contornar o mecanismo de suspensao do Render Free. Essa pratica cria risco de esgotamento da cota e pode ser interpretada como tentativa de evitar restricoes de uso/pagamento previstas na politica do Render.

Uso aceitavel planejado:

- monitorar o frontend estatico e gerar alertas de disponibilidade;
- manter o backend sem ping artificial permanente;
- aquecer manualmente o backend acessando `/health` dois ou tres minutos antes da demonstracao.

Fonte oficial: [UptimeRobot Pricing](https://uptimerobot.com/pricing/).

## Adaptacoes Necessarias

### Backend

1. Gerar `prepared_orders.jsonl` durante o build da imagem.
2. Usar build multi-stage para que a imagem final contenha app + JSONL, sem os CSVs brutos.
3. Iniciar Uvicorn em `0.0.0.0:${PORT:-8000}`.
4. Configurar `/health` no Render.
5. Configurar CORS somente para o dominio publico do frontend.
6. Medir pico de memoria no startup e em classificacoes simultaneas para validar o limite de 512 MB.

Variaveis do backend no painel:

```dotenv
LLM_API_KEY=<secret>
LLM_MODEL=gemini-2.5-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_TIMEOUT_SECONDS=20
PREPARED_FEATURES_PATH=/app/backend/data/prepared_orders.jsonl
```

### Frontend

1. Tornar a base da API configuravel por `VITE_API_BASE`.
2. Configurar no build a URL publica do backend.
3. Exibir estado de aquecimento quando o backend estiver acordando.
4. Consultar `/health` com retry limitado antes de liberar/repetir classificacao.
5. Configurar fallback SPA para `index.html`.

Configuracao planejada:

```text
Root directory: frontend
Build command: npm ci && npm run build
Publish directory: dist
```

## Estrategia de Cold Start

1. Frontend abre normalmente pelo Static Site.
2. Frontend consulta `/health` do backend.
3. Se o servico estiver acordando, mostra `Preparando agente...` sem descartar a fila local.
4. Repete o health check com intervalo e limite total de aproximadamente 90 segundos.
5. Em sucesso, habilita a classificacao; em falha, oferece nova tentativa com mensagem amigavel.

Antes da demo, um integrante deve abrir o health check e realizar uma classificacao completa para confirmar backend, Gemini e frontend.

## Contingencia

Se cold start, memoria ou disponibilidade comprometerem a demonstracao:

1. promover temporariamente o backend para Render Starter;
2. executar novamente health, previsao normal, alto risco e fallback;
3. manter o frontend como Static Site gratuito;
4. retornar ao Free depois do periodo de avaliacao, se apropriado.

## Criterios de Aceite do Deploy

- [ ] Frontend publico abre por HTTPS.
- [ ] Backend publico responde `/health`.
- [ ] Cold start apresenta estado compreensivel e se recupera.
- [ ] Classificacao via frontend retorna risco, explicacao e acao.
- [ ] Gemini funciona sem expor secrets.
- [ ] Fallback deterministico funciona quando a LLM falha.
- [ ] Imagem final nao depende de filesystem persistente.
- [ ] Uso de memoria fica abaixo do limite da instancia.
- [ ] URLs finais e procedimento de demo sao registrados no README.
- [ ] Licenca do dataset e publicacao do derivado sao confirmadas antes do deploy publico.
