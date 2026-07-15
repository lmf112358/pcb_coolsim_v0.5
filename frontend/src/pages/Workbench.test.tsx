import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Workbench from "./Workbench";

vi.mock("../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { results: [] } }),
    post: vi.fn(),
  },
}));

function renderWorkbench() {
  return render(
    <MemoryRouter initialEntries={["/project/1"]}>
      <Workbench />
    </MemoryRouter>
  );
}

/** 查找 Tab 标签（限定在 .ant-tabs-tab 内，避免匹配内容区文本） */
function findTab(text: string) {
  const tabs = document.querySelectorAll(".ant-tabs-tab");
  for (const tab of tabs) {
    if (tab.textContent?.replace(/\s/g, "").includes(text)) {
      return tab as HTMLElement;
    }
  }
  throw new Error(`Tab "${text}" not found`);
}

describe("Workbench Page", () => {
  it("renders 6 tabs with correct labels", () => {
    renderWorkbench();
    expect(findTab("基础配置")).toBeInTheDocument();
    expect(findTab("静态计算")).toBeInTheDocument();
    expect(findTab("负荷分析")).toBeInTheDocument();
    expect(findTab("动态仿真")).toBeInTheDocument();
    expect(findTab("2D展示")).toBeInTheDocument();
    expect(findTab("负荷预测")).toBeInTheDocument();
  });

  it("shows tree panel on Tab1 (基础配置)", async () => {
    renderWorkbench();
    // 左侧树形导航标题（Workbench 顶层 Sider 与 BasicConfig 内部均含此标题）
    expect(screen.getAllByText(/层级结构/i).length).toBeGreaterThan(0);
  });

  it("switches to Tab2 (静态计算) on click", async () => {
    const user = userEvent.setup();
    renderWorkbench();
    await user.click(findTab("静态计算"));
    // AntD 选中 Tab 的父容器含 ant-tabs-tab-active class
    const tab = findTab("静态计算");
    const tabBtn = tab.closest(".ant-tabs-tab");
    expect(tabBtn?.className).toContain("active");
  });

  it("switches to Tab3 (负荷分析) on click", async () => {
    const user = userEvent.setup();
    renderWorkbench();
    await user.click(findTab("负荷分析"));
    const tab = findTab("负荷分析");
    const tabBtn = tab.closest(".ant-tabs-tab");
    expect(tabBtn?.className).toContain("active");
  });

  it("renders top navigation with project name", () => {
    renderWorkbench();
    // 顶部导航含 PCB-CoolSim 或项目名
    expect(screen.getByText(/PCB-CoolSim/i)).toBeInTheDocument();
  });
});
