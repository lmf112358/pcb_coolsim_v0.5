import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import View2D from "./View2D";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        rooms: [
          { id: 1, room_name: "电镀区", total_load: 18.8, area: 100 },
          { id: 2, room_name: "曝光区", total_load: 27.3, area: 120 },
        ],
      },
    }),
  },
}));

function renderView2D() {
  return render(<View2D projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("View2D (Tab5)", () => {
  it("renders color mode switcher (热力图/工艺编码)", () => {
    renderView2D();
    expect(findByText("热力图模式")).toBeInTheDocument();
  });

  it("renders legend section", () => {
    renderView2D();
    expect(findByText("图例")).toBeInTheDocument();
  });

  it("renders room detail panel placeholder", () => {
    renderView2D();
    expect(findByText("功能区域详情")).toBeInTheDocument();
  });

  it("renders canvas placeholder for 2D plan", () => {
    renderView2D();
    expect(findByText("平面图")).toBeInTheDocument();
  });

  it("loads room data from API", async () => {
    renderView2D();
    await waitFor(() => {
      expect(findByText("电镀区")).toBeInTheDocument();
    });
  });
});
