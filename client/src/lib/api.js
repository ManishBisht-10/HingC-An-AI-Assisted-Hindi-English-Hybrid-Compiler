function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl;
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname, port } = window.location;

    if (port === "5173" || port === "3000") {
      return `${protocol}//${hostname}:8000`;
    }

    return window.location.origin;
  }

  return "http://localhost:8000";
}

const API_URL = getApiBaseUrl();

export async function fetchExamples() {
  const res = await fetch(`${API_URL}/api/examples`);
  if (!res.ok) {
    throw new Error("Failed to load examples");
  }
  return res.json();
}

export async function compileSource(payload) {
  const res = await fetch(`${API_URL}/api/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Compile request failed: ${body}`);
  }

  return res.json();
}

export async function saveSnippet(payload) {
  const res = await fetch(`${API_URL}/api/snippets/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Snippet save failed: ${body}`);
  }

  return res.json();
}

export function getWsUrl() {
  const url = new URL(API_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws/compile";
  return url.toString();
}
