import { create } from "zustand";
import type { Session } from "../types";
import {
  fetchSessions,
  createSession as apiCreateSession,
  deleteSession as apiDeleteSession,
  fetchSessionDetail,
} from "../services/api";
import { useChatStore } from "./chatStore";
import { useChartStore } from "./chartStore";

interface SessionState {
  sessions: Session[];
  currentSessionId: string | null;
  loading: boolean;
  setSessions: (sessions: Session[]) => void;
  setCurrentSessionId: (id: string | null) => void;
  updateSessionTitle: (id: string, title: string) => void;

  loadSessions: () => Promise<void>;
  createSession: () => Promise<void>;
  deleteSession: (id: string) => Promise<void>;
  switchSession: (id: string) => Promise<void>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  loading: false,
  setSessions: (sessions) => set({ sessions }),
  setCurrentSessionId: (id) => set({ currentSessionId: id }),
  updateSessionTitle: (id, title) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, title } : s
      ),
    })),

  loadSessions: async () => {
    set({ loading: true });
    try {
      const sessions = await fetchSessions();
      set({ sessions, loading: false });
      if (sessions.length > 0 && !get().currentSessionId) {
        await get().switchSession(sessions[0].id);
      }
    } catch {
      set({ loading: false });
    }
  },

  createSession: async () => {
    try {
      const session = await apiCreateSession();
      set((state) => ({
        sessions: [session, ...state.sessions],
        currentSessionId: session.id,
      }));
      useChatStore.getState().setMessages([]);
      useChartStore.getState().clearCharts();
    } catch (err) {
      console.error("创建会话失败", err);
    }
  },

  deleteSession: async (id: string) => {
    try {
      await apiDeleteSession(id);
      set((state) => {
        const sessions = state.sessions.filter((s) => s.id !== id);
        const currentSessionId =
          state.currentSessionId === id
            ? sessions[0]?.id ?? null
            : state.currentSessionId;
        return { sessions, currentSessionId };
      });
      const newId = get().currentSessionId;
      if (newId) {
        await get().switchSession(newId);
      } else {
        useChatStore.getState().setMessages([]);
        useChartStore.getState().clearCharts();
      }
    } catch (err) {
      console.error("删除会话失败", err);
    }
  },

  switchSession: async (id: string) => {
    set({ currentSessionId: id });
    useChartStore.getState().clearCharts();
    try {
      const detail = await fetchSessionDetail(id);
      useChatStore.getState().setMessages(detail.messages);
      const chartEntries = detail.messages
        .filter((m) => m.chart_config)
        .map((m) => ({ option: m.chart_config!, sql: m.sql }));
      const chartStore = useChartStore.getState();
      chartStore.clearCharts();
      chartEntries.forEach((e) => chartStore.addChart(e.option, e.sql));
    } catch {
      useChatStore.getState().setMessages([]);
    }
  },
}));
