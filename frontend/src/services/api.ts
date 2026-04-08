import axios from "axios";
import type { Session, Message, SSEEvent } from "../types";

const API_BASE = "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

/* ───────── Session APIs ───────── */

export async function fetchSessions(): Promise<Session[]> {
  const { data } = await api.get<Session[]>("/sessions");
  return data;
}

export async function createSession(title = "新对话"): Promise<Session> {
  const { data } = await api.post<Session>("/sessions", { title });
  return data;
}

export async function fetchSessionDetail(
  sessionId: string
): Promise<{ messages: Message[] } & Session> {
  const { data } = await api.get(`/sessions/${sessionId}`);
  return data;
}

export async function updateSession(
  sessionId: string,
  title: string
): Promise<Session> {
  const { data } = await api.put<Session>(`/sessions/${sessionId}`, { title });
  return data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/sessions/${sessionId}`);
}

/* ───────── Chat SSE ───────── */

export function chatSSE(
  sessionId: string,
  message: string,
  onEvent: (event: SSEEvent) => void,
  onError: (err: Error) => void
): AbortController {
  const controller = new AbortController();

  fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }
      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        let currentEvent = "";
        for (const line of lines) {
          if (line.startsWith("event:")) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            const data = line.slice(5).trim();
            if (currentEvent) {
              onEvent({
                type: currentEvent as SSEEvent["type"],
                data,
              });
              currentEvent = "";
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError(err);
      }
    });

  return controller;
}

/* ───────── Database APIs ───────── */

export interface TableInfo {
  name: string;
  columns: { name: string; type: string }[];
  row_count: number;
}

export async function fetchTables(): Promise<TableInfo[]> {
  const { data } = await api.get<TableInfo[]>("/database/tables");
  return data;
}

export async function previewTable(
  tableName: string,
  limit = 10
): Promise<{ columns: string[]; rows: unknown[][] }> {
  const { data } = await api.get(`/database/preview/${tableName}`, {
    params: { limit },
  });
  return data;
}

export default api;
