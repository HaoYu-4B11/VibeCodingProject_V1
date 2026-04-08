import type { CSSProperties } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "../../types";

interface ChartRendererProps {
  option: EChartsOption;
  /** 固定图表高度（px），用于纵向多图布局 */
  height?: number;
}

function enhanceOption(raw: EChartsOption): EChartsOption {
  const option = JSON.parse(JSON.stringify(raw)) as EChartsOption;
  const series = option.series as Record<string, unknown>[] | undefined;
  const chartType =
    Array.isArray(series) && series.length > 0
      ? (series[0].type as string) || "bar"
      : "bar";

  if (!option.tooltip) {
    option.tooltip =
      chartType === "pie"
        ? { trigger: "item", formatter: "{b}: {c} ({d}%)" }
        : {
            trigger: "axis",
            textStyle: { fontSize: 12 },
            confine: true,
          };
  }

  if (chartType === "pie") {
    const firstSeries = (series || [])[0];
    const dataLen = Array.isArray(firstSeries?.data)
      ? (firstSeries.data as unknown[]).length
      : 0;
    const showPieLabels = dataLen > 0 && dataLen <= 8;

    option.series = (series || []).map((s) => ({
      ...s,
      radius: s.radius || ["40%", "68%"],
      center: s.center || ["50%", "46%"],
      avoidLabelOverlap: true,
      minShowLabelAngle: 8,
      label: showPieLabels
        ? {
            show: true,
            formatter: "{b}\n{d}%",
            fontSize: 10,
            overflow: "truncate",
            width: 52,
            lineHeight: 14,
            ...(typeof s.label === "object" && s.label ? s.label : {}),
          }
        : { show: false },
      labelLine: showPieLabels
        ? {
            length: 6,
            length2: 8,
            maxSurfaceAngle: 80,
            ...(typeof s.labelLine === "object" && s.labelLine
              ? s.labelLine
              : {}),
          }
        : { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 8,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.2)",
        },
        ...(typeof s.emphasis === "object" && s.emphasis ? s.emphasis : {}),
      },
    }));
    if (!option.legend) {
      option.legend = {
        orient: "horizontal",
        bottom: 6,
        type: "scroll",
        textStyle: { fontSize: 11 },
        itemWidth: 12,
        itemHeight: 8,
        pageIconSize: 10,
      };
    }
  } else {
    option.grid = {
      left: 14,
      right: 18,
      top: 48,
      bottom: 28,
      containLabel: true,
      ...(typeof option.grid === "object" && option.grid ? option.grid : {}),
    };

    if (option.xAxis && typeof option.xAxis === "object") {
      const xAxis = option.xAxis as Record<string, unknown>;
      const dataArr = xAxis.data as unknown[] | undefined;
      const needRotate = Array.isArray(dataArr) && dataArr.length > 4;
      xAxis.axisLabel = {
        fontSize: 11,
        rotate: needRotate ? 22 : 0,
        margin: 10,
        overflow: "truncate",
        width: 72,
        hideOverlap: true,
        ...(typeof xAxis.axisLabel === "object" && xAxis.axisLabel
          ? xAxis.axisLabel
          : {}),
      };
      xAxis.axisTick = { alignWithLabel: true };
    }

    if (option.yAxis && typeof option.yAxis === "object") {
      const yAxis = option.yAxis as Record<string, unknown>;
      yAxis.axisLabel = {
        fontSize: 11,
        hideOverlap: true,
        margin: 8,
        ...(typeof yAxis.axisLabel === "object" && yAxis.axisLabel
          ? yAxis.axisLabel
          : {}),
      };
      yAxis.splitLine = {
        lineStyle: { type: "dashed", color: "#e8e8e8" },
        ...(typeof yAxis.splitLine === "object" && yAxis.splitLine
          ? yAxis.splitLine
          : {}),
      };
    }

    option.series = (series || []).map((s) => ({
      ...s,
      label: { show: false },
      barMaxWidth: chartType === "bar" ? 48 : undefined,
      ...(chartType === "line"
        ? { smooth: true, symbol: "circle", symbolSize: 6 }
        : {}),
    }));
  }

  const titleObj = option.title as Record<string, unknown> | undefined;
  if (titleObj && typeof titleObj === "object") {
    titleObj.textStyle = {
      fontSize: 14,
      fontWeight: 600,
      ...(typeof titleObj.textStyle === "object" && titleObj.textStyle
        ? titleObj.textStyle
        : {}),
    };
    titleObj.left = titleObj.left || "center";
    titleObj.top = titleObj.top ?? 8;
  }

  option.animationDuration = 500;
  option.animationEasing = "cubicOut";

  return option;
}

export default function ChartRenderer({ option, height }: ChartRendererProps) {
  const enhanced = enhanceOption(option);
  const h = height ?? undefined;
  const style: CSSProperties = {
    width: "100%",
    height: h ? `${h}px` : "100%",
    minHeight: h ? `${h}px` : 280,
  };

  return (
    <div className="chart-renderer" style={h ? { height: h, minHeight: h } : undefined}>
      <ReactECharts
        option={enhanced}
        style={style}
        opts={{ renderer: "canvas" }}
        notMerge
      />
    </div>
  );
}
