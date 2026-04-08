import type { Session, Message, EChartsOption } from "../types";

export const mockSessions: Session[] = [
  {
    id: "s1",
    title: "销售数据分析",
    created_at: "2026-04-07T10:00:00Z",
    updated_at: "2026-04-07T10:30:00Z",
  },
  {
    id: "s2",
    title: "用户增长趋势",
    created_at: "2026-04-06T14:00:00Z",
    updated_at: "2026-04-06T15:00:00Z",
  },
  {
    id: "s3",
    title: "库存预警查询",
    created_at: "2026-04-05T09:00:00Z",
    updated_at: "2026-04-05T09:20:00Z",
  },
];

export const mockMessages: Record<string, Message[]> = {
  s1: [
    {
      id: "m1",
      session_id: "s1",
      role: "user",
      content: "查询每个月的销售总额",
      created_at: "2026-04-07T10:00:00Z",
    },
    {
      id: "m2",
      session_id: "s1",
      role: "assistant",
      content:
        "根据查询结果，以下是各月销售总额的分析：\n\n| 月份 | 销售总额 |\n|------|----------|\n| 1月 | ¥128,500 |\n| 2月 | ¥95,200 |\n| 3月 | ¥156,800 |\n\n从数据来看，**3月份的销售额最高**，达到了 ¥156,800，而2月份由于春节假期影响，销售额相对较低。",
      sql: "SELECT strftime('%m', order_date) AS month,\n       SUM(amount) AS total_sales\nFROM orders\nGROUP BY month\nORDER BY month;",
      chart_config: {
        title: { text: "月度销售总额" },
        xAxis: {
          type: "category",
          data: ["1月", "2月", "3月", "4月", "5月", "6月"],
        },
        yAxis: { type: "value", name: "销售额 (¥)" },
        series: [
          {
            data: [128500, 95200, 156800, 142300, 168900, 185600],
            type: "bar",
            itemStyle: { color: "#1677ff" },
          },
        ],
        tooltip: { trigger: "axis" },
      },
      created_at: "2026-04-07T10:00:05Z",
    },
    {
      id: "m3",
      session_id: "s1",
      role: "user",
      content: "各产品类别的销售占比是多少？",
      created_at: "2026-04-07T10:05:00Z",
    },
    {
      id: "m4",
      session_id: "s1",
      role: "assistant",
      content:
        "各产品类别的销售占比如下：\n\n- **电子产品**: 35.2%\n- **服装**: 28.1%\n- **食品**: 20.5%\n- **家居**: 16.2%\n\n电子产品类别贡献了最大的销售份额。",
      sql: "SELECT category,\n       ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM orders), 1) AS percentage\nFROM orders\nJOIN products ON orders.product_id = products.id\nGROUP BY category\nORDER BY percentage DESC;",
      chart_config: {
        title: { text: "产品类别销售占比" },
        series: [
          {
            type: "pie",
            radius: ["40%", "70%"],
            data: [
              { value: 35.2, name: "电子产品" },
              { value: 28.1, name: "服装" },
              { value: 20.5, name: "食品" },
              { value: 16.2, name: "家居" },
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
          },
        ],
        tooltip: { trigger: "item" },
        legend: { orient: "vertical", left: "left" },
      },
      created_at: "2026-04-07T10:05:08Z",
    },
  ],
  s2: [
    {
      id: "m5",
      session_id: "s2",
      role: "user",
      content: "展示最近6个月的用户增长趋势",
      created_at: "2026-04-06T14:00:00Z",
    },
    {
      id: "m6",
      session_id: "s2",
      role: "assistant",
      content:
        "最近6个月的用户注册数据如下：\n\n整体呈现**稳定增长**趋势，其中5月和6月增长最为明显，可能与营销活动有关。",
      sql: "SELECT strftime('%Y-%m', created_at) AS month,\n       COUNT(*) AS new_users\nFROM users\nWHERE created_at >= date('now', '-6 months')\nGROUP BY month\nORDER BY month;",
      chart_config: {
        title: { text: "用户增长趋势" },
        xAxis: {
          type: "category",
          data: ["1月", "2月", "3月", "4月", "5月", "6月"],
        },
        yAxis: { type: "value", name: "新增用户数" },
        series: [
          {
            data: [820, 932, 901, 1234, 1890, 2150],
            type: "line",
            smooth: true,
            areaStyle: { opacity: 0.15 },
            itemStyle: { color: "#52c41a" },
          },
        ],
        tooltip: { trigger: "axis" },
      },
      created_at: "2026-04-06T14:00:06Z",
    },
  ],
  s3: [],
};

export const mockChartConfigs: EChartsOption[] = [
  mockMessages.s1[1].chart_config!,
  mockMessages.s1[3].chart_config!,
];

let _delay = 300;

export function simulateStreamResponse(
  text: string,
  onChunk: (chunk: string) => void,
  onDone: () => void
) {
  let i = 0;
  const chars = text.split("");
  const timer = setInterval(() => {
    if (i < chars.length) {
      const chunkSize = Math.floor(Math.random() * 3) + 1;
      onChunk(chars.slice(i, i + chunkSize).join(""));
      i += chunkSize;
    } else {
      clearInterval(timer);
      onDone();
    }
  }, _delay / 10);
  return () => clearInterval(timer);
}
