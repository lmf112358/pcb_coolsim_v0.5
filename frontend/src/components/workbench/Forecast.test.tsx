import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Forecast from "./Forecast";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        results: [
          { id: 1, name: "7月预测", status: "active", start_date: "2024-07-01" },
          { id: 2, name: "8月预测", status: "paused", start_date: "2024-08-01" },
        ],
      },
    }),
    post: vi.fn(),
  },
}));

function renderForecast() {
  return render(<Forecast projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("Forecast (Tab6)", () => {
  it("renders scenario management section", () => {
    renderForecast();
    expect(findByText("预测场景管理")).toBeInTheDocument();
  });

  it("renders create scenario button", () => {
    renderForecast();
    const buttons = screen.getAllByRole("button");
    const createBtn = buttons.find((b) => b.textContent?.replace(/\s/g, "").includes("创建场景"));
    expect(createBtn).toBeDefined();
  });

  it("renders weather source configuration section", () => {
    renderForecast();
    expect(findByText("天气配置")).toBeInTheDocument();
  });

  it("renders production rate configuration section", () => {
    renderForecast();
    expect(findByText("生产负荷率")).toBeInTheDocument();
  });

  it("renders forecast results curve placeholder", () => {
    renderForecast();
    expect(findByText("预测结果")).toBeInTheDocument();
  });

  it("loads scenarios from API", async () => {
    renderForecast();
    await waitFor(() => {
      expect(screen.getByText("7月预测")).toBeInTheDocument();
    });
  });
});
