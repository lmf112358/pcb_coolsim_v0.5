import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DynamicSim from "./DynamicSim";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        extremes: { max_load: 28.5, min_load: 15.2, avg_load: 21.8, max_time: "2024-07-15T14:00" },
        point_count: 8760,
      },
    }),
    post: vi.fn().mockResolvedValue({ data: { batch_id: "test-batch", status: "SUCCESS" } }),
  },
}));

function renderDynamicSim() {
  return render(<DynamicSim projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("DynamicSim (Tab4)", () => {
  it("renders trigger simulation button", () => {
    renderDynamicSim();
    const btn = document.querySelector("button.ant-btn-primary");
    expect(btn?.textContent?.replace(/\s/g, "")).toContain("运行");
  });

  it("renders extremes statistics section", () => {
    renderDynamicSim();
    expect(findByText("极值统计")).toBeInTheDocument();
  });

  it("renders hourly curve chart placeholder", () => {
    renderDynamicSim();
    expect(findByText("逐时负荷曲线")).toBeInTheDocument();
  });

  it("renders time filter controls (年/月/日)", () => {
    renderDynamicSim();
    expect(findByText("时间筛选")).toBeInTheDocument();
  });

  it("loads extremes data from API", async () => {
    renderDynamicSim();
    await waitFor(() => {
      // 极值统计卡片标题出现表示数据已加载
      const stats = document.querySelectorAll(".ant-statistic-title");
      const has = Array.from(stats).some((s) => s.textContent?.includes("峰值"));
      expect(has).toBe(true);
    });
  });
});
