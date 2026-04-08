import type { EChartsOption } from "../../types";
import { getChartType } from "../../types";

export function convertChartType(
  originalOption: EChartsOption,
  targetType: string
): EChartsOption {
  const option = JSON.parse(JSON.stringify(originalOption)) as EChartsOption;
  const series = option.series as Record<string, unknown>[] | undefined;
  if (!Array.isArray(series) || series.length === 0) return option;

  const currentType = (series[0].type as string) || "bar";
  if (currentType === targetType) return option;

  if (targetType === "pie") {
    const xAxis = option.xAxis as Record<string, unknown> | undefined;
    const categories = (xAxis?.data as string[]) || [];
    const firstSeries = series[0];
    const values = (firstSeries.data as unknown[]) || [];

    const pieData = categories.map((name: string, i: number) => ({
      name,
      value: values[i],
    }));

    return {
      title: option.title,
      tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
      legend: { orient: "horizontal", bottom: 4, type: "scroll" },
      series: [
        {
          type: "pie",
          radius: ["38%", "62%"],
          data: pieData,
          avoidLabelOverlap: true,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0,0,0,0.25)",
            },
          },
        },
      ],
    };
  }

  if (currentType === "pie") {
    const firstSeries = series[0];
    const pieData =
      (firstSeries.data as { name: string; value: unknown }[]) || [];
    const categories = pieData.map((d) => d.name);
    const values = pieData.map((d) => d.value);

    return {
      title: option.title,
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: categories },
      yAxis: { type: "value" },
      series: [{ type: targetType, data: values }],
    };
  }

  option.series = series.map((s) => {
    const { label: _label, ...rest } = s;
    return { ...rest, type: targetType };
  });
  return option;
}

export function withTitleSuffix(
  option: EChartsOption,
  suffix: string
): EChartsOption {
  const o = JSON.parse(JSON.stringify(option)) as EChartsOption;
  const t = o.title as { text?: string; [k: string]: unknown } | undefined;
  if (t && typeof t === "object" && t.text) {
    t.text = `${t.text}（${suffix}）`;
  } else {
    o.title = { text: suffix, left: "center", top: 8 };
  }
  return o;
}

export function buildTripleChartOptions(
  baseOption: EChartsOption
): { bar: EChartsOption; line: EChartsOption; pie: EChartsOption } {
  const rootType = getChartType(baseOption);
  let normalized = JSON.parse(
    JSON.stringify(baseOption)
  ) as EChartsOption;
  if (rootType === "pie") {
    normalized = convertChartType(normalized, "bar");
  }

  const barOpt = withTitleSuffix(convertChartType(normalized, "bar"), "柱状图");
  const lineOpt = withTitleSuffix(
    convertChartType(normalized, "line"),
    "折线图"
  );
  const pieOpt = withTitleSuffix(convertChartType(normalized, "pie"), "饼图");

  return { bar: barOpt, line: lineOpt, pie: pieOpt };
}
