import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import LoadAnalysis from "./LoadAnalysis";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        by_room: [
          { room_name: "电镀区", total_load: 18.8 },
          { room_name: "曝光区", total_load: 27.3 },
        ],
        by_category: {
          civil: 5.0, lighting: 3.0, personnel: 2.0, equipment: 15.5, fresh_air: 20.6,
        },
        suggestions: [
          { room_name: "曝光区", message: "冷指标偏高(550 W/m²)，建议核查设备发热" },
        ],
      },
    }),
  },
}));

function renderLoadAnalysis() {
  return render(<LoadAnalysis projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("LoadAnalysis (Tab3)", () => {
  it("renders five analysis dimensions title", () => {
    renderLoadAnalysis();
    expect(findByText("五维度负荷分析")).toBeInTheDocument();
  });

  it("renders by-room ranking table with data", async () => {
    renderLoadAnalysis();
    await waitFor(() => {
      // Table 存在且有数据行
      const rows = document.querySelectorAll(".ant-table-row");
      expect(rows.length).toBeGreaterThan(0);
    });
  });

  it("renders load category pie chart section", () => {
    renderLoadAnalysis();
    expect(findByText("负荷构成")).toBeInTheDocument();
  });

  it("renders auto-generated suggestions section", async () => {
    renderLoadAnalysis();
    await waitFor(() => {
      // Card title 含"建议"
      const titles = document.querySelectorAll(".ant-card-head-title");
      const has = Array.from(titles).some((t) =>
        t.textContent?.replace(/\s/g, "").includes("自动分析建议")
      );
      expect(has).toBe(true);
    });
  });

  it("renders dimension switcher (功能区域/楼层/建筑)", () => {
    renderLoadAnalysis();
    expect(findByText("分析维度")).toBeInTheDocument();
  });

  it("loads suggestion from API", async () => {
    renderLoadAnalysis();
    await waitFor(() => {
      expect(screen.getByText(/冷指标偏高/)).toBeInTheDocument();
    });
  });
});
