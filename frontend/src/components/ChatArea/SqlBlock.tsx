import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Typography, Button, message } from "antd";
import { CopyOutlined } from "@ant-design/icons";

const { Text } = Typography;

interface SqlBlockProps {
  sql: string;
}

export default function SqlBlock({ sql }: SqlBlockProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    message.success("SQL 已复制");
  };

  return (
    <div className="sql-block">
      <div className="sql-block__header">
        <Text type="secondary" style={{ fontSize: 12 }}>
          SQL 查询
        </Text>
        <Button
          type="text"
          size="small"
          icon={<CopyOutlined />}
          onClick={handleCopy}
        />
      </div>
      <SyntaxHighlighter
        language="sql"
        style={oneLight}
        customStyle={{
          margin: 0,
          borderRadius: "0 0 8px 8px",
          fontSize: 13,
        }}
      >
        {sql}
      </SyntaxHighlighter>
    </div>
  );
}
