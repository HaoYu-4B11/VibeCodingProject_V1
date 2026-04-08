import { useEffect } from "react";
import { Button, Typography, Popconfirm, Spin } from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import { useSessionStore } from "../../store";
import "./style.css";

const { Text } = Typography;

function Logo() {
  return (
    <div className="sidebar-logo">
      <div className="sidebar-logo__icon">
        <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="10" fill="url(#logo-grad)" />
          <path
            d="M12 28V18L16 14V28M18 28V20L22 16V28M24 28V16L28 12V28"
            stroke="#fff"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="28" cy="12" r="2" fill="#fff" />
          <defs>
            <linearGradient id="logo-grad" x1="0" y1="0" x2="40" y2="40">
              <stop stopColor="#1677ff" />
              <stop offset="1" stopColor="#6C5CE7" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <div className="sidebar-logo__text">
        <span className="sidebar-logo__title">智能数据分析</span>
        <span className="sidebar-logo__subtitle">NL2SQL & Visualization</span>
      </div>
    </div>
  );
}

export default function ChatSidebar() {
  const {
    sessions,
    currentSessionId,
    loading,
    loadSessions,
    createSession,
    deleteSession,
    switchSession,
  } = useSessionStore();

  useEffect(() => {
    loadSessions();
  }, []);

  return (
    <div className="chat-sidebar">
      <Logo />
      <div className="sidebar-header">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          size="large"
          onClick={createSession}
        >
          新建对话
        </Button>
      </div>
      <div className="session-list">
        {loading && sessions.length === 0 ? (
          <div style={{ textAlign: "center", padding: 24 }}>
            <Spin />
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${
                session.id === currentSessionId ? "session-item--active" : ""
              }`}
              onClick={() => switchSession(session.id)}
            >
              <div className="session-item__content">
                <MessageOutlined className="session-item__icon" />
                <div className="session-item__info">
                  <Text
                    className="session-item__title"
                    ellipsis={{ tooltip: session.title }}
                  >
                    {session.title}
                  </Text>
                  <Text type="secondary" className="session-item__time">
                    {dayjs(session.updated_at).format("MM/DD HH:mm")}
                  </Text>
                </div>
              </div>
              <Popconfirm
                title="确定删除此对话？"
                onConfirm={(e) => {
                  e?.stopPropagation();
                  deleteSession(session.id);
                }}
                onCancel={(e) => e?.stopPropagation()}
                okText="删除"
                cancelText="取消"
              >
                <DeleteOutlined
                  className="session-item__delete"
                  onClick={(e) => e.stopPropagation()}
                />
              </Popconfirm>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
