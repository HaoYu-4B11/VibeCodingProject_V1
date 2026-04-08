import { Avatar } from "antd";
import { UserOutlined, RobotOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../../types";

interface MessageItemProps {
  message: Message;
}

export default function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-item ${isUser ? "message-item--user" : "message-item--assistant"}`}>
      <Avatar
        className="message-item__avatar"
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{
          backgroundColor: isUser ? "#1677ff" : "#52c41a",
          flexShrink: 0,
        }}
      />
      <div className="message-item__body">
        <div className="message-item__bubble">
          {isUser ? (
            <p className="message-item__text">{message.content}</p>
          ) : (
            <div className="message-item__markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
