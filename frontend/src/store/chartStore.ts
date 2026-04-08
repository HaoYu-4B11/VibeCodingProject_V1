import { create } from "zustand";
import type { EChartsOption } from "../types";

export interface ChartEntry {
  option: EChartsOption;
  sql?: string;
}

interface ChartState {
  charts: ChartEntry[];
  activeChartIndex: number;
  addChart: (option: EChartsOption, sql?: string) => void;
  setActiveChartIndex: (index: number) => void;
  clearCharts: () => void;
}

export const useChartStore = create<ChartState>((set) => ({
  charts: [],
  activeChartIndex: 0,
  addChart: (option, sql) =>
    set((state) => ({
      charts: [...state.charts, { option, sql }],
      activeChartIndex: state.charts.length,
    })),
  setActiveChartIndex: (index) => set({ activeChartIndex: index }),
  clearCharts: () => set({ charts: [], activeChartIndex: 0 }),
}));
