const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export type ApiError = {
  status: number;
  data: unknown;
};

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    credentials: "include",
  });

  const data = await parseJsonSafe(res);
  if (!res.ok) {
    const err: ApiError = { status: res.status, data };
    throw err;
  }

  return data as T;
}

