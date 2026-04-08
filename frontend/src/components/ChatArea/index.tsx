import { useRef } from "react";
import { Typography, message as antMessage } from "antd";
import { DatabaseOutlined } from "@ant-design/icons";
import { useChatStore, useSessionStore, useChartStore } from "../../store";
import { chatSSE } from "../../services/api";
import { useAutoScroll } from "../../hooks/useAutoScroll";
import type { SSEEvent, EChartsOption } from "../../types";
import MessageItem from "./MessageItem";
import ChatInput from "./ChatInput";
import "./style.css";

const { Title, Paragraph } = Typography;

export default function ChatArea() {
  const {
    messages,
    addMessage,
    appendToLastAssistant,
    setLastAssistantSql,
    setLastAssistantChart,
    isStreaming,
    setIsStreaming,
  } = useChatStore();
  const { currentSessionId } = useSessionStore();
  const updateSessionTitle = useSessionStore((s) => s.updateSessionTitle);
  const addChart = useChartStore((s) => s.addChart);
  const scrollRef = useAutoScroll([messages]);
  const abortRef = useRef<AbortController | null>(null);

  const handleSend = (content: string) => {
    if (!currentSessionId || isStreaming) return;

    const userMsg = {
      id: `m${Date.now()}`,
      session_id: currentSessionId,
      role: "user" as const,
      content,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    const assistantMsg = {
      id: `m${Date.now() + 1}`,
      session_id: currentSessionId,
      role: "assistant" as const,
      content: "",
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMsg);
    setIsStreaming(true);

    let collectedSql = "";

    const controller = chatSSE(
      currentSessionId,
      content,
      (event: SSEEvent) => {
        switch (event.type) {
          case "text":
            appendToLastAssistant(event.data);
            break;
          case "sql":
            collectedSql = event.data;
            setLastAssistantSql(event.data);
            break;
          case "data":
            break;
          case "chart":
            try {
              const chartOption: EChartsOption = JSON.parse(event.data);
              setLastAssistantChart(chartOption);
              addChart(chartOption, collectedSql);
            } catch {
              console.error("Failed to parse chart config:", event.data);
            }
            break;
          case "error":
            appendToLastAssistant(`\n\n**错误**: ${event.data}`);
            antMessage.error(`请求出错: ${event.data}`);
            setIsStreaming(false);
            break;
          case "done": {
            setIsStreaming(false);
            const sessions = useSessionStore.getState().sessions;
            const session = sessions.find((s) => s.id === currentSessionId);
            if (session?.title === "新对话") {
              const newTitle =
                content.slice(0, 20) + (content.length > 20 ? "..." : "");
              updateSessionTitle(currentSessionId, newTitle);
            }
            break;
          }
        }
      },
      (err: Error) => {
        appendToLastAssistant(`\n\n**连接错误**: ${err.message}`);
        antMessage.error("连接后端失败，请检查服务是否启动");
        setIsStreaming(false);
      }
    );
    abortRef.current = controller;
  };

  return (
    <div className="chat-area">
      <div className="message-list" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <DatabaseOutlined style={{ fontSize: 48, color: "#bfbfbf" }} />
            <Title level={4} style={{ marginTop: 16 }}>
              智能数据分析系统
            </Title>
            <Paragraph type="secondary">
              {currentSessionId
                ? "输入自然语言查询，我会帮你分析数据库并生成可视化图表"
                : "请先在左侧新建一个对话"}
            </Paragraph>
          </div>
        ) : (
          messages.map((msg) => <MessageItem key={msg.id} message={msg} />)
        )}
        {isStreaming && (
          <div className="streaming-indicator">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} disabled={isStreaming || !currentSessionId} />
    </div>
  );
}
