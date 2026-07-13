# Estrategia de Deploy no Render

**Decisao:** Render para frontend e backend.
**Meta de custo:** manter o MVP no plano gratuito sempre que possivel.
**Registrado em:** 2026-07-12
**Status:** Configuracao local implementada; criacao e UAT dos servicos publicos pendentes.

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

## Implementacao e Evidencias Locais

O Blueprint versionado em `1-3_felipe-amorim_gabryel-nicolas_guilherme-westphall_lucas-martins/render.yaml` cria o backend Docker e o frontend Static Site. Ao criar o Blueprint no Render, esse caminho deve ser informado explicitamente. No primeiro sync, o Render solicita os valores que nao podem ser inferidos ou versionados:

- `LLM_API_KEY`: secret da API Gemini;
- `FRONTEND_ORIGIN`: URL HTTPS final do Static Site, sem barra ao final;
- `VITE_API_BASE`: URL HTTPS final do backend, sem barra ao final.

Validacao local em 2026-07-12:

- suite backend: 67 testes aprovados;
- build de producao do frontend: aprovado;
- imagem multi-stage: preparo de 96.470 pedidos concluido durante o build;
- container iniciado usando `PORT=10000` e `/health` respondeu com status `ok`;
- imagem final contem `prepared_orders.jsonl` e nao contem `/app/dataset`;
- memoria em repouso observada no smoke local: aproximadamente 97 MiB.

O valor de memoria e apenas evidencia local, nao substitui a medicao no Render. Cold start, pico durante classificacoes, URLs e smoke publico continuam pendentes.
