const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");

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

export async function waitForApiReady({ attempts = 12, delayMs = 3000 } = {}) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        signal: AbortSignal.timeout(5000),
      });
      if (response.ok) {
        return true;
      }
    } catch {
      // A free Render service can refuse or time out while it wakes up.
    }

    if (attempt < attempts - 1) {
      await new Promise((resolve) => window.setTimeout(resolve, delayMs));
    }
  }

  return false;
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
