const orders = [
  {
    id: "BR-10294",
    route: "SP -> RJ",
    category: "moveis_decoracao",
    promisedDate: "18/07/2026",
    freight: "R$ 42,90",
    status: "Pronto",
    risk: "Pendente",
  },
  {
    id: "BR-10431",
    route: "PR -> BA",
    category: "beleza_saude",
    promisedDate: "20/07/2026",
    freight: "R$ 68,10",
    status: "Rascunho",
    risk: "Pendente",
  },
  {
    id: "BR-10802",
    route: "MG -> PE",
    category: "informatica_acessorios",
    promisedDate: "21/07/2026",
    freight: "R$ 59,80",
    status: "Pronto",
    risk: "Pendente",
  },
];

function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Trilha 1.3</p>
          <h1>Torre de controle de entregas</h1>
        </div>
        <div className="topbar-actions">
          <button className="button secondary" type="button">
            Importar JSON
          </button>
          <button className="button primary" type="button">
            Novo pedido
          </button>
        </div>
      </header>

      <section className="summary-grid" aria-label="Resumo operacional">
        <article className="metric-card">
          <span>Pedidos na fila</span>
          <strong>24</strong>
        </article>
        <article className="metric-card">
          <span>Prontos para classificar</span>
          <strong>18</strong>
        </article>
        <article className="metric-card">
          <span>Risco alto</span>
          <strong>-</strong>
        </article>
        <article className="metric-card">
          <span>Explicacoes solicitadas</span>
          <strong>0</strong>
        </article>
      </section>

      <section className="workspace">
        <aside className="entry-panel">
          <div className="section-heading">
            <p className="eyebrow">Entrada</p>
            <h2>Cadastrar pedido</h2>
          </div>

          <form className="order-form">
            <label>
              ID do pedido
              <input placeholder="BR-10921" />
            </label>
            <label>
              UF do cliente
              <select defaultValue="">
                <option value="" disabled>
                  Selecione
                </option>
                <option>SP</option>
                <option>RJ</option>
                <option>MG</option>
                <option>BA</option>
                <option>PE</option>
              </select>
            </label>
            <label>
              UF do seller
              <select defaultValue="">
                <option value="" disabled>
                  Selecione
                </option>
                <option>SP</option>
                <option>PR</option>
                <option>MG</option>
                <option>SC</option>
                <option>RS</option>
              </select>
            </label>
            <label>
              Categoria
              <input placeholder="cama_mesa_banho" />
            </label>
            <label>
              Data prometida
              <input type="date" />
            </label>
            <label>
              Valor do frete
              <input placeholder="42.90" />
            </label>
            <button className="button primary full" type="button">
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
            <button className="button secondary" type="button">
              Classificar selecionados
            </button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>
                    <input aria-label="Selecionar todos" type="checkbox" />
                  </th>
                  <th>Pedido</th>
                  <th>Rota</th>
                  <th>Categoria</th>
                  <th>Promessa</th>
                  <th>Frete</th>
                  <th>Status</th>
                  <th>Risco</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <input aria-label={`Selecionar ${order.id}`} type="checkbox" />
                    </td>
                    <td className="order-id">{order.id}</td>
                    <td>{order.route}</td>
                    <td>{order.category}</td>
                    <td>{order.promisedDate}</td>
                    <td>{order.freight}</td>
                    <td>
                      <span className="status-pill">{order.status}</span>
                    </td>
                    <td>{order.risk}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </main>
  );
}

export default App;
