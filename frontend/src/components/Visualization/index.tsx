import { Typography, Empty, Tabs, Button, message } from "antd";
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  CopyOutlined,
  CodeOutlined,
} from "@ant-design/icons";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useChartStore } from "../../store";
import type { ChartEntry } from "../../store/chartStore";
import { getChartType, getChartTitle } from "../../types";
import ChartRenderer from "./ChartRenderer";
import { buildTripleChartOptions } from "./chartUtils";
import "./style.css";

const { Title, Text } = Typography;

const CHART_HEIGHT_BAR = 340;
const CHART_HEIGHT_LINE = 340;
const CHART_HEIGHT_PIE = 380;

const chartTabIconMap: Record<string, React.ReactNode> = {
  bar: <BarChartOutlined />,
  line: <LineChartOutlined />,
  pie: <PieChartOutlined />,
};

function SqlPanel({ sql }: { sql: string }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    message.success("SQL 已复制");
  };

  return (
    <div className="viz-sql-panel">
      <div className="viz-sql-header">
        <Text type="secondary" style={{ fontSize: 12 }}>
          <CodeOutlined style={{ marginRight: 4 }} />
          SQL 查询
        </Text>
        <Button
          type="text"
          size="small"
          icon={<CopyOutlined />}
          onClick={handleCopy}
        />
      </div>
      <div className="viz-sql-code">
        <SyntaxHighlighter
          language="sql"
          style={oneLight}
          customStyle={{
            margin: 0,
            padding: "8px 12px",
            fontSize: 12,
            lineHeight: 1.5,
            background: "#fafafa",
            maxHeight: 120,
            overflow: "auto",
          }}
          wrapLongLines
        >
          {sql}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

function ChartPanel({ entry }: { entry: ChartEntry }) {
  const { bar, line, pie } = buildTripleChartOptions(entry.option);

  return (
    <div className="viz-chart-container">
      {entry.sql && <SqlPanel sql={entry.sql} />}
      <div className="viz-triple-stack">
        <section className="viz-chart-block">
          <Text strong className="viz-chart-block__label">
            <BarChartOutlined /> 柱状图
          </Text>
          <div className="viz-chart-block__canvas">
            <ChartRenderer option={bar} height={CHART_HEIGHT_BAR} />
          </div>
        </section>
        <section className="viz-chart-block">
          <Text strong className="viz-chart-block__label">
            <LineChartOutlined /> 折线图
          </Text>
          <div className="viz-chart-block__canvas">
            <ChartRenderer option={line} height={CHART_HEIGHT_LINE} />
          </div>
        </section>
        <section className="viz-chart-block">
          <Text strong className="viz-chart-block__label">
            <PieChartOutlined /> 饼图
          </Text>
          <div className="viz-chart-block__canvas">
            <ChartRenderer option={pie} height={CHART_HEIGHT_PIE} />
          </div>
        </section>
      </div>
    </div>
  );
}

export default function Visualization() {
  const { charts, activeChartIndex, setActiveChartIndex } = useChartStore();

  if (charts.length === 0) {
    return (
      <div className="visualization">
        <div className="viz-header">
          <Title level={5}>可视化图表</Title>
        </div>
        <div className="viz-empty">
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="查询数据后将在此展示图表"
          />
        </div>
      </div>
    );
  }

  const tabItems = charts.map((entry: ChartEntry, idx: number) => {
    const type = getChartType(entry.option);
    const title = getChartTitle(entry.option);
    return {
      key: String(idx),
      label: (
        <span>
          {chartTabIconMap[type] || <BarChartOutlined />}
          <span style={{ marginLeft: 4 }}>{title}</span>
        </span>
      ),
      children: <ChartPanel entry={entry} />,
    };
  });

  return (
    <div className="visualization">
      <div className="viz-header">
        <Title level={5}>可视化图表</Title>
      </div>
      <div className="viz-tabs-wrapper">
        <Tabs
          activeKey={String(activeChartIndex)}
          onChange={(key) => setActiveChartIndex(Number(key))}
          type="card"
          size="small"
          items={tabItems}
        />
      </div>
    </div>
  );
}
