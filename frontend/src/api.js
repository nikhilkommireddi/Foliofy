// Thin API client. Requests are relative so the Vite proxy (dev) or Flask
// (prod) serves them from the same origin.

async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

const post = (url, data) =>
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  }).then(handle);

export const api = {
  health: () => fetch("/api/health").then(handle),
  preview: (data) => post("/api/preview", data),
  score: (data) => post("/api/score", data),
  generate: (data) => post("/api/generate", data),
  history: () => fetch("/api/history").then(handle),
  historyItem: (id) => fetch(`/api/history/${id}`).then(handle),
  deleteItem: (id) => fetch(`/api/history/${id}`, { method: "DELETE" }).then(handle),
  stats: () => fetch("/api/stats").then(handle),
  downloadUrl: (id) => `/api/download/${id}`,
};
