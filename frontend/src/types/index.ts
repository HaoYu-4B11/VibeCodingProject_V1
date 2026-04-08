export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  sql?: string;
  chart_config?: EChartsOption | null;
  created_at: string;
}

/**
 * 后端直接返回原生 ECharts option JSON，结构示例:
 * { title: {text: "..."}, xAxis: {...}, yAxis: {...}, series: [{type: "bar", data: [...]}] }
 */
export type EChartsOption = Record<string, unknown>;

export interface SSEEvent {
  type: "text" | "sql" | "data" | "chart" | "error" | "done";
  data: string;
}

/**
 * 从 EChartsOption 中提取图表类型（用于 UI 图标映射）
 */
export function getChartType(option: EChartsOption): string {
  const series = option.series;
  if (Array.isArray(series) && series.length > 0) {
    return series[0].type || "bar";
  }
  return "bar";
}

/**
 * 从 EChartsOption 中提取图表标题
 */
export function getChartTitle(option: EChartsOption): string {
  const title = option.title;
  if (title && typeof title === "object" && "text" in title) {
    return (title as { text: string }).text;
  }
  return "图表";
}
