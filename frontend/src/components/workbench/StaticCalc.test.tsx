import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import StaticCalc from "./StaticCalc";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockImplementation((url: string) => {
      if (url.includes("results") || url.includes("summary")) {
        return Promise.resolve({
          data: {
            results: [
              { room_name: "电镀区", temp_type: "中温", terminal_load: 10.5, fresh_air_load: 8.3, total_load: 18.8 },
              { room_name: "曝光区", temp_type: "低温", terminal_load: 15.2, fresh_air_load: 12.1, total_load: 27.3 },
            ],
            summary: {
              low_temp_total: 27.3,
              mid_temp_total: 18.8,
              grand_total: 46.1,
            },
          },
        });
      }
      return Promise.resolve({ data: { results: [] } });
    }),
  },
}));

function renderStaticCalc() {
  return render(<StaticCalc projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("StaticCalc (Tab2)", () => {
  it("renders summary cards (低温/中温/合计)", async () => {
    renderStaticCalc();
    await waitFor(() => {
      expect(findByText("中温")).toBeInTheDocument();
    });
  });

  it("renders results table with room data", async () => {
    renderStaticCalc();
    await waitFor(() => {
      expect(screen.getByText("电镀区")).toBeInTheDocument();
      expect(screen.getByText("曝光区")).toBeInTheDocument();
    });
  });

  it("renders load composition section", () => {
    renderStaticCalc();
    expect(findByText("负荷构成")).toBeInTheDocument();
  });

  it("renders chart placeholder for bar/pie charts", () => {
    renderStaticCalc();
    expect(findByText("柱状图")).toBeInTheDocument();
  });

  it("loads summary data from API on mount", async () => {
    renderStaticCalc();
    await waitFor(() => {
      // 汇总卡片标题出现表示数据已加载
      expect(findByText("总负荷合计")).toBeInTheDocument();
    });
  });

  it("renders water temperature classification columns", () => {
    renderStaticCalc();
    expect(findByText("末端负荷")).toBeInTheDocument();
    expect(findByText("新风负荷")).toBeInTheDocument();
    expect(findByText("总负荷")).toBeInTheDocument();
  });
});
