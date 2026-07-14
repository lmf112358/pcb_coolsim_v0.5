import type { ThemeConfig } from "antd";

// PRD 3.3 UI 规范：主色调工业蓝
// 暗色 #1E88E5 / 浅色 #1565C0
export const lightTheme: ThemeConfig = {
  token: {
    colorPrimary: "#1565C0",
    borderRadius: 4,
  },
};

export const darkTheme: ThemeConfig = {
  token: {
    colorPrimary: "#1E88E5",
    borderRadius: 4,
  },
  algorithm: undefined, // 由 ConfigProvider darkAlgorithm 控制
};

// PRD 3.3 热力图色阶（蓝→红连续渐变）
export const HEATMAP_COLORS = {
  light: { low: "#1E88E5", high: "#C62828" },
  dark: { low: "#42A5F5", high: "#E53935" },
};

// PRD F3-016 工艺色编码（7 色，优先级：温控精度 > 洁净度 > 压差）
export const PROCESS_COLORS = {
  red: "#FF4D4F",    // ±1°C
  orange: "#FA8C16", // ±2°C
  yellow: "#FADB14", // ISO7
  green: "#52C41A",  // ISO8
  blue: "#1890FF",   // ISO7.5
  purple: "#722ED1", // 正压
  gray: "#BFBFBF",   // 负压/普通
} as const;

export type ThemeMode = "light" | "dark";
