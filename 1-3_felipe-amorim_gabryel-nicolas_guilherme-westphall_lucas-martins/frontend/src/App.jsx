import { useEffect, useMemo, useState } from "react";

import { predictDelay, waitForApiReady } from "./api";

const initialOrders = [
  {
    id: "BR-AL-001",
    customer_state: "AL",
    seller_state: "SP",
    product_category_name: "beleza_saude",
    order_purchase_timestamp: "2026-07-11",
    order_estimated_delivery_date: "2026-07-16",
    freight_value: 42.9,
    price: 180,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 1,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-MA-002",
    customer_state: "MA",
    seller_state: "SP",
    product_category_name: "beleza_saude",
    order_purchase_timestamp: "2026-07-12",
    order_estimated_delivery_date: "2026-07-17",
    freight_value: 120,
    price: 120,
    items_count: 3,
    payment_type: "credit_card",
    payment_installments: 8,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-SP-003",
    customer_state: "SP",
    seller_state: "PR",
    product_category_name: "cama_mesa_banho",
    order_purchase_timestamp: "2026-07-13",
    order_estimated_delivery_date: "2026-07-18",
    freight_value: 80,
    price: 60,
    items_count: 2,
    payment_type: "boleto",
    payment_installments: 1,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-RJ-004",
    customer_state: "RJ",
    seller_state: "SP",
    product_category_name: "eletronicos",
    order_purchase_timestamp: "2026-07-14",
    order_estimated_delivery_date: "2026-07-19",
    freight_value: 39.9,
    price: 310,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 6,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-BA-005",
    customer_state: "BA",
    seller_state: "SP",
    product_category_name: "telefonia",
    order_purchase_timestamp: "2026-07-05",
    order_estimated_delivery_date: "2026-07-20",
    freight_value: 40,
    price: 180,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 3,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-RJ-006",
    customer_state: "RJ",
    seller_state: "SP",
    product_category_name: "bebes",
    order_purchase_timestamp: "2026-07-11",
    order_estimated_delivery_date: "2026-07-21",
    freight_value: 80,
    price: 60,
    items_count: 2,
    payment_type: "boleto",
    payment_installments: 1,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-ES-007",
    customer_state: "ES",
    seller_state: "SP",
    product_category_name: "cama_mesa_banho",
    order_purchase_timestamp: "2026-07-07",
    order_estimated_delivery_date: "2026-07-22",
    freight_value: 40,
    price: 180,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 5,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-RJ-008",
    customer_state: "RJ",
    seller_state: "MG",
    product_category_name: "utilidades_domesticas",
    order_purchase_timestamp: "2026-07-01",
    order_estimated_delivery_date: "2026-08-10",
    freight_value: 120,
    price: 120,
    items_count: 3,
    payment_type: "credit_card",
    payment_installments: 8,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-MG-009",
    customer_state: "MG",
    seller_state: "SP",
    product_category_name: "bebes",
    order_purchase_timestamp: "2026-07-01",
    order_estimated_delivery_date: "2026-08-10",
    freight_value: 120,
    price: 120,
    items_count: 3,
    payment_type: "credit_card",
    payment_installments: 8,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-PR-010",
    customer_state: "PR",
    seller_state: "SP",
    product_category_name: "moveis_decoracao",
    order_purchase_timestamp: "2026-07-01",
    order_estimated_delivery_date: "2026-08-10",
    freight_value: 120,
    price: 120,
    items_count: 3,
    payment_type: "credit_card",
    payment_installments: 8,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-AL-011",
    customer_state: "AL",
    seller_state: "PR",
    product_category_name: "agro_industria_e_comercio",
    order_purchase_timestamp: "2026-07-16",
    order_estimated_delivery_date: "2026-07-26",
    freight_value: 40,
    price: 180,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 1,
    status: "Pronto",
    prediction: null,
    error: null,
  },
  {
    id: "BR-AC-012",
    customer_state: "AC",
    seller_state: "MA",
    product_category_name: "beleza_saude",
    order_purchase_timestamp: "2026-07-22",
    order_estimated_delivery_date: "2026-07-27",
    freight_value: 40,
    price: 180,
    items_count: 1,
    payment_type: "credit_card",
    payment_installments: 1,
    status: "Pronto",
    prediction: null,
    error: null,
  },
];

const initialForm = {
  id: "",
  customer_state: "",
  seller_state: "",
  product_category_name: "",
  order_estimated_delivery_date: "",
  freight_value: "",
  price: "",
  items_count: "1",
  payment_type: "credit_card",
  payment_installments: "1",
};

const ufs = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
  "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
  "SP", "SE", "TO",
];

const riskLabels = {
  low: "Baixo",
  medium: "Medio",
  high: "Alto",
};

function App() {
  const [orders, setOrders] = useState(initialOrders);
  const [selectedOrderIds, setSelectedOrderIds] = useState(new Set(initialOrders.map((order) => order.id)));
  const [activeOrderId, setActiveOrderId] = useState(initialOrders[0].id);
  const [form, setForm] = useState(initialForm);
  const [formError, setFormError] = useState("");
  const [isClassifying, setIsClassifying] = useState(false);
  const [serviceStatus, setServiceStatus] = useState("warming");

  useEffect(() => {
    let active = true;

    async function warmUpBackend() {
      const ready = await waitForApiReady();
      if (active) {
        setServiceStatus(ready ? "ready" : "unavailable");
      }
    }

    warmUpBackend();
    return () => {
      active = false;
    };
  }, []);

  const activeOrder = orders.find((order) => order.id === activeOrderId) ?? orders[0] ?? null;
  const selectedCount = selectedOrderIds.size;

  const metrics = useMemo(() => {
    const classified = orders.filter((order) => order.prediction);
    const totalLatency = classified.reduce((sum, order) => sum + order.prediction.latency_ms, 0);
    return {
      total: orders.length,
      ready: orders.filter((order) => order.status === "Pronto").length,
      classified: classified.length,
      highRisk: classified.filter((order) => order.prediction.risk_level === "high").length,
      averageLatency: classified.length ? `${Math.round(totalLatency / classified.length)} ms` : "-",
      fallbackEvents: classified.filter(
        (order) => order.prediction.fallback_used || order.prediction.guardrails.length > 0,
      ).length,
      totalTokens: classified.reduce(
        (sum, order) => sum + (order.prediction.llm_usage?.total_tokens ?? 0),
        0,
      ),
    };
  }, [orders]);

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function addOrder(event) {
    event.preventDefault();
    setFormError("");

    if (!form.id.trim() || !form.customer_state || !form.seller_state) {
      setFormError("Informe ID do pedido, UF do cliente e UF do seller.");
      return;
    }

    if (orders.some((order) => order.id === form.id.trim())) {
      setFormError("Ja existe um pedido com esse ID na fila.");
      return;
    }

    const order = normalizeFormOrder(form);
    setOrders((current) => [order, ...current]);
    setSelectedOrderIds(new Set([order.id]));
    setActiveOrderId(order.id);
    setForm(initialForm);
  }

  function toggleSelected(orderId) {
    setSelectedOrderIds((current) => {
      const next = new Set(current);
      if (next.has(orderId)) {
        next.delete(orderId);
      } else {
        next.add(orderId);
      }
      return next;
    });
    setActiveOrderId(orderId);
  }

  function toggleAllSelected(checked) {
    setSelectedOrderIds(checked ? new Set(orders.map((order) => order.id)) : new Set());
  }

  async function classifySelected() {
    if (selectedOrderIds.size === 0 || isClassifying || serviceStatus !== "ready") {
      return;
    }

    const ids = new Set(selectedOrderIds);
    setIsClassifying(true);
    setOrders((current) =>
      current.map((order) =>
        ids.has(order.id)
          ? { ...order, status: "Classificando", error: null }
          : order,
      ),
    );

    const selectedOrders = orders.filter((order) => ids.has(order.id));
    for (const order of selectedOrders) {
      await classifyOrder(order);
    }
    setIsClassifying(false);
  }

  async function retryBackend() {
    setServiceStatus("warming");
    const ready = await waitForApiReady();
    setServiceStatus(ready ? "ready" : "unavailable");
  }

  async function classifyOrder(order) {
    try {
      const prediction = await predictDelay(toApiPayload(order));
      setOrders((current) =>
        current.map((item) =>
          item.id === order.id
            ? { ...item, status: "Classificado", prediction, error: null }
            : item,
        ),
      );
    } catch (error) {
      setOrders((current) =>
        current.map((item) =>
          item.id === order.id
            ? {
                ...item,
                status: "Erro",
                error: error.message || "Nao foi possivel classificar o pedido.",
              }
            : item,
        ),
      );
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Trilha 1.3</p>
          <h1>Torre de controle de entregas</h1>
        </div>
        <div className="topbar-actions">
          <div className={`service-chip ${serviceStatus}`} aria-live="polite">
            {serviceStatusText(serviceStatus)}
          </div>
          {serviceStatus === "unavailable" ? (
            <button className="button secondary" type="button" onClick={retryBackend}>
              Tentar novamente
            </button>
          ) : null}
        </div>
      </header>

      <section className="summary-grid" aria-label="Resumo operacional">
        <Metric label="Pedidos na fila" value={metrics.total} />
        <Metric label="Prontos para classificar" value={metrics.ready} />
        <Metric label="Classificados" value={metrics.classified} />
        <Metric label="Risco alto" value={metrics.highRisk} />
        <Metric label="Latencia media" value={metrics.averageLatency} />
        <Metric label="Fallbacks / guardrails" value={metrics.fallbackEvents} />
        <Metric label="Tokens LLM" value={formatInteger(metrics.totalTokens)} />
      </section>

      <section className="workspace">
        <aside className="entry-panel">
          <div className="section-heading">
            <p className="eyebrow">Entrada</p>
            <h2>Cadastrar pedido</h2>
          </div>

          <form className="order-form" onSubmit={addOrder}>
            <label>
              ID do pedido
              <input
                placeholder="BR-10921"
                value={form.id}
                onChange={(event) => updateForm("id", event.target.value)}
              />
            </label>
            <label>
              UF do cliente
              <UfSelect
                value={form.customer_state}
                onChange={(value) => updateForm("customer_state", value)}
              />
            </label>
            <label>
              UF do seller
              <UfSelect
                value={form.seller_state}
                onChange={(value) => updateForm("seller_state", value)}
              />
            </label>
            <label>
              Categoria
              <input
                placeholder="cama_mesa_banho"
                value={form.product_category_name}
                onChange={(event) => updateForm("product_category_name", event.target.value)}
              />
            </label>
            <label>
              Data prometida
              <input
                type="date"
                value={form.order_estimated_delivery_date}
                onChange={(event) => updateForm("order_estimated_delivery_date", event.target.value)}
              />
            </label>
            <div className="form-grid">
              <label>
                Frete
                <input
                  inputMode="decimal"
                  placeholder="42.90"
                  value={form.freight_value}
                  onChange={(event) => updateForm("freight_value", event.target.value)}
                />
              </label>
              <label>
                Preco
                <input
                  inputMode="decimal"
                  placeholder="180.00"
                  value={form.price}
                  onChange={(event) => updateForm("price", event.target.value)}
                />
              </label>
            </div>
            <div className="form-grid">
              <label>
                Itens
                <input
                  inputMode="numeric"
                  value={form.items_count}
                  onChange={(event) => updateForm("items_count", event.target.value)}
                />
              </label>
              <label>
                Parcelas
                <input
                  inputMode="numeric"
                  value={form.payment_installments}
                  onChange={(event) => updateForm("payment_installments", event.target.value)}
                />
              </label>
            </div>
            <label>
              Pagamento
              <select
                value={form.payment_type}
                onChange={(event) => updateForm("payment_type", event.target.value)}
              >
                <option value="credit_card">Cartao</option>
                <option value="boleto">Boleto</option>
                <option value="voucher">Voucher</option>
                <option value="debit_card">Debito</option>
              </select>
            </label>
            {formError ? <p className="inline-error">{formError}</p> : null}
            <button className="button primary full" type="submit">
              Adicionar a fila
            </button>
          </form>
        </aside>

        <section className="orders-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Fila</p>
              <h2>Pedidos para analise</h2>
            </div>
            <button
              className="button secondary"
              type="button"
              disabled={selectedCount === 0 || isClassifying || serviceStatus !== "ready"}
              onClick={classifySelected}
            >
              {isClassifying ? "Classificando..." : `Classificar selecionados (${selectedCount})`}
            </button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>
                    <input
                      aria-label="Selecionar todos"
                      checked={orders.length > 0 && selectedOrderIds.size === orders.length}
                      type="checkbox"
                      onChange={(event) => toggleAllSelected(event.target.checked)}
                    />
                  </th>
                  <th>Pedido</th>
                  <th>Rota</th>
                  <th>Categoria</th>
                  <th>Promessa</th>
                  <th>Frete</th>
                  <th>Status</th>
                  <th>Risco</th>
                  <th>Confianca</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr
                    className={order.id === activeOrder?.id ? "active-row" : ""}
                    key={order.id}
                    onClick={() => setActiveOrderId(order.id)}
                  >
                    <td>
                      <input
                        aria-label={`Selecionar ${order.id}`}
                        checked={selectedOrderIds.has(order.id)}
                        type="checkbox"
                        onChange={() => toggleSelected(order.id)}
                        onClick={(event) => event.stopPropagation()}
                      />
                    </td>
                    <td className="order-id">{order.id}</td>
                    <td>{`${order.seller_state} -> ${order.customer_state}`}</td>
                    <td>{order.product_category_name || "-"}</td>
                    <td>{formatDate(order.order_estimated_delivery_date)}</td>
                    <td>{formatCurrency(order.freight_value)}</td>
                    <td>
                      <span className={`status-pill ${statusClass(order.status)}`}>
                        {order.status}
                      </span>
                    </td>
                    <td><RiskBadge prediction={order.prediction} /></td>
                    <td>{order.prediction?.confidence ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <PredictionDetail order={activeOrder} />
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function serviceStatusText(status) {
  if (status === "ready") {
    return "Agente pronto";
  }
  if (status === "unavailable") {
    return "Agente indisponivel";
  }
  return "Preparando agente...";
}

function UfSelect({ value, onChange }) {
  return (
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      <option value="" disabled>
        Selecione
      </option>
      {ufs.map((uf) => (
        <option key={uf} value={uf}>
          {uf}
        </option>
      ))}
    </select>
  );
}

function RiskBadge({ prediction }) {
  if (!prediction) {
    return <span className="risk-badge pending">Pendente</span>;
  }

  const level = prediction.risk_level;
  return (
    <span className={`risk-badge ${level}`}>
      {riskLabels[level] ?? level} {formatPercent(prediction.risk_score)}
    </span>
  );
}

function PredictionDetail({ order }) {
  if (!order) {
    return null;
  }

  const prediction = order.prediction;

  return (
    <section className="prediction-detail" aria-label="Detalhe da classificacao">
      <div className="detail-header">
        <div>
          <p className="eyebrow">Resultado</p>
          <h3>{order.id}</h3>
        </div>
        <RiskBadge prediction={prediction} />
      </div>

      {order.error ? (
        <p className="alert error">{order.error}</p>
      ) : null}

      {!prediction && !order.error ? (
        <p className="empty-state">Selecione e classifique o pedido para ver explicacao, acao e evidencias.</p>
      ) : null}

      {prediction ? (
        <>
          <div className="detail-grid">
            <DetailItem label="Confianca" value={prediction.confidence} />
            <DetailItem label="Amostra" value={`${prediction.evidence.sample_size} pedidos`} />
            <DetailItem label="Recorte" value={prediction.evidence.segment_used} />
            <DetailItem label="Latencia" value={`${prediction.latency_ms} ms`} />
            <DetailItem label="Modelo LLM" value={prediction.llm_usage?.model ?? "Fallback deterministico"} />
            <DetailItem
              label="Tokens LLM"
              value={prediction.llm_usage?.total_tokens == null ? "-" : formatInteger(prediction.llm_usage.total_tokens)}
            />
          </div>

          <div className="detail-copy">
            <h4>Explicacao</h4>
            <p>{prediction.explanation}</p>
          </div>

          <div className="detail-copy">
            <h4>Acao recomendada</h4>
            <p>{prediction.recommended_action}</p>
          </div>

          {prediction.guardrails.length > 0 || prediction.fallback_used ? (
            <p className="alert warning">
              {fallbackText(prediction)}
            </p>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function normalizeFormOrder(formValue) {
  return {
    id: formValue.id.trim(),
    customer_state: formValue.customer_state,
    seller_state: formValue.seller_state,
    product_category_name: optionalString(formValue.product_category_name),
    order_estimated_delivery_date: optionalString(formValue.order_estimated_delivery_date),
    freight_value: optionalNumber(formValue.freight_value),
    price: optionalNumber(formValue.price),
    items_count: optionalInteger(formValue.items_count),
    payment_type: optionalString(formValue.payment_type),
    payment_installments: optionalInteger(formValue.payment_installments),
    status: "Pronto",
    prediction: null,
    error: null,
  };
}

function toApiPayload(order) {
  return {
    order_id: order.id,
    customer_state: order.customer_state,
    seller_state: order.seller_state,
    product_category_name: order.product_category_name,
    order_purchase_timestamp: toBackendTimestamp(order.order_purchase_timestamp ?? todayIso(), "10:00:00"),
    order_estimated_delivery_date: toBackendTimestamp(order.order_estimated_delivery_date, "10:00:00"),
    freight_value: order.freight_value,
    price: order.price,
    items_count: order.items_count,
    payment_type: order.payment_type,
    payment_installments: order.payment_installments,
  };
}

function todayIso() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function toBackendTimestamp(value, time) {
  if (!value) {
    return null;
  }
  if (String(value).includes(":")) {
    return value;
  }
  return `${value} ${time}`;
}

function optionalString(value) {
  const trimmed = String(value ?? "").trim();
  return trimmed ? trimmed : null;
}

function optionalNumber(value) {
  const normalized = String(value ?? "").replace(",", ".").trim();
  if (!normalized) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function optionalInteger(value) {
  const parsed = optionalNumber(value);
  return parsed === null ? null : Math.max(0, Math.trunc(parsed));
}

function formatCurrency(value) {
  if (value === null || value === undefined) {
    return "-";
  }
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

function formatPercent(value) {
  return new Intl.NumberFormat("pt-BR", { style: "percent", maximumFractionDigits: 1 }).format(value);
}

function formatInteger(value) {
  return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(value);
}

function formatDate(value) {
  if (!value) {
    return "-";
  }
  const [year, month, day] = value.split("-");
  if (!year || !month || !day) {
    return value;
  }
  return `${day}/${month}/${year}`;
}

function statusClass(status) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

function fallbackText(prediction) {
  const messages = [];

  if (prediction.fallback_used) {
    messages.push("O agente usou um recorte historico mais amplo por falta de amostra especifica.");
  }

  if (prediction.guardrails.includes("low_confidence")) {
    messages.push("A confianca e baixa; recomenda-se revisao humana.");
  }

  if (prediction.guardrails.includes("llm_unconfigured")) {
    messages.push("A explicacao foi produzida pelo fallback deterministico porque a LLM nao esta configurada.");
  }

  if (prediction.guardrails.includes("llm_fallback:rate_limited")) {
    messages.push("A cota da LLM foi atingida; a resposta segura foi utilizada.");
  } else if (prediction.guardrails.includes("llm_fallback:action_mismatch")) {
    messages.push("A acao sugerida pela LLM nao era compativel com a politica segura e foi substituida.");
  } else if (prediction.guardrails.some((event) => event.startsWith("llm_fallback"))) {
    messages.push("A LLM estava indisponivel e a explicacao segura foi usada.");
  }

  if (prediction.guardrails.some((event) => event.startsWith("output_guardrail"))) {
    messages.push("A saida original nao passou pela validacao e foi substituida por uma resposta segura.");
  }

  return messages.join(" ");
}

export default App;
