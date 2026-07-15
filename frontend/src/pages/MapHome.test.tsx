import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import MapHome from "./MapHome";

// mock Leaflet（jsdom 不支持地图渲染）
vi.mock("leaflet", () => ({
  map: () => ({ remove: () => {}, setView: () => {} }),
  tileLayer: () => ({ addTo: () => {} }),
  marker: () => ({ addTo: () => {}, bindPopup: () => ({ addTo: () => {} }) }),
  icon: () => ({}),
  latLng: () => ({}),
}));

vi.mock("../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        results: [
          { id: 1, project_name: "广州PCB工厂", city_name: "广州", location: "黄埔区" },
          { id: 2, project_name: "西安PCB工厂", city_name: "西安", location: "高新区" },
        ],
      },
    }),
  },
}));

function renderMapHome() {
  return render(
    <MemoryRouter>
      <MapHome />
    </MemoryRouter>
  );
}

function findByText(text: string) {
  return screen.getByText((_, node) => {
    if (!node) return false;
    return node.textContent?.replace(/\s/g, "").includes(text);
  });
}

describe("MapHome Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page title and search box", () => {
    renderMapHome();
    expect(screen.getByPlaceholderText(/搜索/i)).toBeInTheDocument();
    // PCB-CoolSim 标题（用 getAllByText 容忍多次出现）
    expect(screen.getAllByText(/PCB-CoolSim/i).length).toBeGreaterThan(0);
  });

  it("loads and displays project list", async () => {
    renderMapHome();
    await waitFor(() => {
      expect(screen.getByText("广州PCB工厂")).toBeInTheDocument();
      expect(screen.getByText("西安PCB工厂")).toBeInTheDocument();
    });
  });

  it("shows new project button", () => {
    renderMapHome();
    // AntD 按钮文本含空格
    const btn = document.querySelector('button.ant-btn-primary');
    expect(btn?.textContent?.replace(/\s/g, "")).toContain("新建项目");
  });

  it("filters projects by search keyword", async () => {
    const user = userEvent.setup();
    renderMapHome();
    await waitFor(() => expect(screen.getByText("广州PCB工厂")).toBeInTheDocument());
    await user.type(screen.getByPlaceholderText(/搜索/i), "广州");
    await waitFor(() => {
      expect(screen.getByText("广州PCB工厂")).toBeInTheDocument();
      expect(screen.queryByText("西安PCB工厂")).not.toBeInTheDocument();
    });
  });

  it("displays city name for each project", async () => {
    renderMapHome();
    await waitFor(() => {
      expect(screen.getByText("广州")).toBeInTheDocument();
      expect(screen.getByText("西安")).toBeInTheDocument();
    });
  });
});
