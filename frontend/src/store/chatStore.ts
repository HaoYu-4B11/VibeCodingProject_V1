import { create } from "zustand";
import type { Message, EChartsOption } from "../types";

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  appendToLastAssistant: (text: string) => void;
  setLastAssistantSql: (sql: string) => void;
  setLastAssistantChart: (chart: EChartsOption) => void;
  setIsStreaming: (streaming: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  appendToLastAssistant: (text) =>
    set((state) => {
      const messages = [...state.messages];
      const lastIdx = messages.findLastIndex((m) => m.role === "assistant");
      if (lastIdx !== -1) {
        messages[lastIdx] = {
          ...messages[lastIdx],
          content: messages[lastIdx].content + text,
        };
      }
      return { messages };
    }),
  setLastAssistantSql: (sql) =>
    set((state) => {
      const messages = [...state.messages];
      const lastIdx = messages.findLastIndex((m) => m.role === "assistant");
      if (lastIdx !== -1) {
        messages[lastIdx] = { ...messages[lastIdx], sql };
      }
      return { messages };
    }),
  setLastAssistantChart: (chart) =>
    set((state) => {
      const messages = [...state.messages];
      const lastIdx = messages.findLastIndex((m) => m.role === "assistant");
      if (lastIdx !== -1) {
        messages[lastIdx] = { ...messages[lastIdx], chart_config: chart };
      }
      return { messages };
    }),
  setIsStreaming: (streaming) => set({ isStreaming: streaming }),
  clearMessages: () => set({ messages: [] }),
}));
