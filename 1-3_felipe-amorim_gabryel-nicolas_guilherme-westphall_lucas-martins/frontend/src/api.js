const API_BASE = "/api";

export async function predictDelay(order) {
  const response = await fetch(`${API_BASE}/predict-delay`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(order),
  });

  const body = await readJson(response);

  if (!response.ok) {
    const error = new Error(errorMessage(body, response.status));
    error.status = response.status;
    error.details = body?.details ?? null;
    throw error;
  }

  return body;
}

async function readJson(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function errorMessage(body, status) {
  if (body?.message) {
    return body.message;
  }

  if (body?.details?.length) {
    return body.details.map((detail) => `${detail.field}: ${detail.message}`).join("; ");
  }

  return `Nao foi possivel classificar o pedido (HTTP ${status}).`;
}
