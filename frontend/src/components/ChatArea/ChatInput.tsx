import { useState, type KeyboardEvent } from "react";
import { Input, Button } from "antd";
import { SendOutlined, LoadingOutlined } from "@ant-design/icons";

const { TextArea } = Input;

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <TextArea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入你的问题，如：查询销售额最高的前10个产品..."
        autoSize={{ minRows: 1, maxRows: 4 }}
        disabled={disabled}
      />
      <Button
        type="primary"
        icon={disabled ? <LoadingOutlined /> : <SendOutlined />}
        onClick={handleSend}
        disabled={disabled || !value.trim()}
      />
    </div>
  );
}
