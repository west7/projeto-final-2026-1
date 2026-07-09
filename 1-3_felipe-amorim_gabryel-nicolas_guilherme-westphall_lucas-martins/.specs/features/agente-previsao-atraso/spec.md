# Agente de Previsao de Atraso Specification

## Problem Statement

Equipes de logistica e atendimento precisam identificar pedidos com risco de atraso antes que o atraso aconteca. O sistema deve usar o historico Olist como contexto, calcular risco de forma explicavel, devolver uma acao recomendada e operar como agente exposto por API e consumido por um produto.

## Goals

- [ ] Classificar pedidos em risco baixo, medio ou alto com base em historico de pedidos semelhantes.
- [ ] Explicar os principais fatores da classificacao com evidencias e tamanho de amostra.
- [ ] Sugerir uma acao operacional clara para cada nivel de risco.
- [ ] Validar entrada e saida com guardrails e responder graciosamente quando faltar dado.
- [ ] Registrar latencia, fallback, erros e custo estimado para avaliacao.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Modelo supervisionado treinado | Fora da direcao definida no HTML e consome tempo do que sera avaliado no MVP. |
| Analise de sentimento de reviews | Reviews acontecem depois da entrega e nao resolvem previsao antecipada. |
| Acionamento real de sistemas externos | MVP foca recomendacao, nao automacao operacional em producao. |
| Autenticacao | Nao e necessaria para demonstracao do fluxo agente -> API -> produto. |

---

## User Stories

### P1: Classificar risco de atraso - MVP

**User Story:** Como operador logistico, quero enviar os dados de um pedido para receber um nivel de risco de atraso, para priorizar pedidos antes que o cliente seja impactado.

**Why P1:** E o valor central do produto e a base para explicacao e acao.

**Acceptance Criteria:**

1. WHEN um pedido valido for enviado THEN system SHALL retornar `risk_level`, `risk_score`, `confidence` e `fallback_used`.
2. WHEN houver historico suficiente para recortes especificos THEN system SHALL usar o recorte mais especifico disponivel e reportar o tamanho da amostra.
3. WHEN o recorte especifico tiver poucos exemplos THEN system SHALL aplicar fallback para recortes mais amplos e marcar `fallback_used=true`.
4. WHEN a entrada nao tiver campos obrigatorios THEN system SHALL rejeitar com erro de validacao amigavel e sem stack trace.

**Independent Test:** Enviar um pedido via API ou tela e verificar risco, score, confianca e flag de fallback.

---

### P1: Explicar fatores e recomendar acao - MVP

**User Story:** Como equipe de atendimento, quero entender por que o pedido esta em risco e o que devo fazer, para comunicar o cliente ou acionar a operacao com clareza.

**Why P1:** O enunciado diferencia agente de modelo pela explicacao e proximo passo.

**Acceptance Criteria:**

1. WHEN o risco for retornado THEN system SHALL incluir uma explicacao curta baseada nos segmentos historicos consultados.
2. WHEN o risco for alto THEN system SHALL sugerir acao preventiva de prioridade logistica ou comunicacao proativa.
3. WHEN a confianca for baixa THEN system SHALL dizer que ha pouco historico comparavel e recomendar revisao humana.
4. WHEN a saida nao contiver evidencias rastreaveis THEN system SHALL acionar guardrail de saida e retornar fallback seguro.

**Independent Test:** Classificar pedidos de baixo e alto risco e verificar se a explicacao cita rota, prazo, categoria, frete ou outro fator usado.

---

### P1: Produto operacional integrado - MVP

**User Story:** Como operador, quero usar uma tela de torre de controle para cadastrar/importar pedidos e classifica-los, para nao depender de chamadas manuais de API.

**Why P1:** O trabalho exige agente integrado a produto.

**Acceptance Criteria:**

1. WHEN um pedido for adicionado na tela THEN system SHALL exibi-lo na fila.
2. WHEN o operador classificar pedidos selecionados THEN system SHALL chamar a API e atualizar risco/status na tabela.
3. WHEN a API estiver indisponivel THEN system SHALL mostrar erro amigavel e manter os dados da fila.
4. WHEN houver fallback na resposta THEN system SHALL exibir isso de forma compreensivel.

**Independent Test:** Usar a interface para classificar um pedido e ver risco e explicacao sem abrir ferramentas tecnicas.

---

### P2: Observabilidade para avaliacao

**User Story:** Como equipe do projeto, quero registrar sinais de execucao, para avaliar confiabilidade, latencia e custo no relatorio.

**Why P2:** E requisito de reliable e monitoramento, mas pode ser minimo.

**Acceptance Criteria:**

1. WHEN uma classificacao acontecer THEN system SHALL registrar latencia ponta a ponta.
2. WHEN fallback ou guardrail for acionado THEN system SHALL registrar o tipo de evento.
3. WHEN LLM for usado THEN system SHALL registrar custo estimado por interacao; se nao for usado, custo SHALL ser reportado como zero.

**Independent Test:** Realizar chamadas e inspecionar logs gerados.

---

### P2: Avaliacao tecnica com conjunto historico

**User Story:** Como avaliador tecnico, quero ver metricas do baseline no historico, para saber se a solucao funciona alem da demo.

**Why P2:** O relatorio exige avaliacao com metricas adequadas.

**Acceptance Criteria:**

1. WHEN o script de avaliacao rodar THEN system SHALL calcular matriz de confusao ou metricas por threshold/faixa de risco.
2. WHEN a avaliacao for reportada THEN system SHALL incluir recall de atrasos e taxa de fallback.
3. WHEN grupos regionais forem comparados THEN system SHALL destacar diferencas relevantes de cobertura ou erro.

**Independent Test:** Rodar avaliacao offline e obter metricas salvas ou impressas.

---

## Edge Cases

- WHEN pedido tiver categoria ausente THEN system SHALL usar fallback sem quebrar.
- WHEN CEP/estado nao existir na geolocalizacao THEN system SHALL continuar sem distancia e reduzir confianca.
- WHEN entrada tiver texto abusivo ou fora de escopo THEN system SHALL rejeitar como fora de escopo.
- WHEN pedido tiver multiplos vendedores THEN system SHALL agregar rota/frete/produtos e explicitar limitacao se necessario.
- WHEN historico comparavel tiver amostra muito pequena THEN system SHALL evitar falsa certeza e recomendar revisao humana.
- WHEN API/LLM falhar THEN system SHALL devolver resposta padrao de indisponibilidade graciosa.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| DELAY-01 | P1: Classificar risco | Design | Pending |
| DELAY-02 | P1: Fallback por recorte | Design | Pending |
| DELAY-03 | P1: Validacao amigavel | Design | Pending |
| DELAY-04 | P1: Explicar fatores | Design | Pending |
| DELAY-05 | P1: Recomendar acao | Design | Pending |
| DELAY-06 | P1: Guardrail de saida | Design | Pending |
| DELAY-07 | P1: Produto integrado | Design | Pending |
| DELAY-08 | P2: Observabilidade | Design | Pending |
| DELAY-09 | P2: Avaliacao tecnica | Design | Pending |

**Coverage:** 9 total, 9 mapped to tasks, 0 unmapped.

---

## Success Criteria

- [ ] Uma pessoa consegue subir e usar o fluxo agente -> API -> produto.
- [ ] API retorna risco, explicacao, confianca e acao para pedidos validos.
- [ ] Entradas invalidas e falhas de dependencia nao mostram erro tecnico cru.
- [ ] O relatorio inclui dados, fonte/licenca, vieses, metricas, guardrails, fallback e monitoramento.
- [ ] A demo cobre pelo menos um caso de risco baixo, um de risco alto e um fallback.
