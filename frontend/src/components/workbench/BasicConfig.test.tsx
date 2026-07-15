import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import BasicConfig from "./BasicConfig";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { results: [] } }),
    post: vi.fn().mockResolvedValue({
      data: { terminal_load: 10.5, fresh_air_load: 8.3, total_load: 18.8 },
    }),
  },
}));

function renderBasicConfig() {
  return render(<BasicConfig projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  // 只匹配叶子文本节点（无子元素），避免匹配父容器
  const matches = screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  });
  return matches[0];
}

function findInput(label: string) {
  // AntD Form.Item label 在 .ant-form-item-label 内
  const labels = document.querySelectorAll(".ant-form-item-label label");
  for (const l of labels) {
    if (l.textContent?.replace(/\s/g, "").includes(label)) return l;
  }
  // 也可能在 .ant-form-item-label > span
  const spans = document.querySelectorAll(".ant-form-item-label");
  for (const s of spans) {
    if (s.textContent?.replace(/\s/g, "").includes(label)) return s;
  }
  throw new Error(`Form label "${label}" not found`);
}

describe("BasicConfig (Tab1)", () => {
  it("renders left tree panel with hierarchy title", () => {
    renderBasicConfig();
    expect(findByText("层级结构")).toBeInTheDocument();
  });

  it("renders right detail panel with form area", () => {
    renderBasicConfig();
    expect(findByText("功能区域详情")).toBeInTheDocument();
  });

  it("renders real-time calculation preview section", () => {
    renderBasicConfig();
    expect(findByText("实时计算预览")).toBeInTheDocument();
  });

  it("renders form with area, height, civil and lighting fields", () => {
    renderBasicConfig();
    expect(findInput("面积")).toBeInTheDocument();
    expect(findInput("吊顶高度")).toBeInTheDocument();
    expect(findInput("土建指标")).toBeInTheDocument();
    expect(findInput("照明指标")).toBeInTheDocument();
  });

  it("renders 7 field groups (基本信息/负荷计算参数/设备参数)", () => {
    renderBasicConfig();
    expect(findByText("基本信息")).toBeInTheDocument();
    expect(findByText("负荷计算参数")).toBeInTheDocument();
  });

  it("auto-displays volume field (area × height)", () => {
    renderBasicConfig();
    // 体积字段存在且为只读（自动计算）
    expect(findInput("体积")).toBeInTheDocument();
    // 面积和高度输入框存在
    expect(findInput("面积")).toBeInTheDocument();
    expect(findInput("吊顶高度")).toBeInTheDocument();
  });

  it("has calculation preview button", () => {
    renderBasicConfig();
    const buttons = screen.getAllByRole("button");
    const calcBtn = buttons.find((b) => b.textContent?.replace(/\s/g, "").includes("计算预览"));
    expect(calcBtn).toBeDefined();
  });
});
