import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import MapHome from "./MapHome";

// mock Leaflet（jsdom 不支持地图）
vi.mock("leaflet", () => ({
  default: {
    map: () => ({ remove: () => {}, setView: () => {}, eachLayer: () => {}, addLayer: () => {}, removeLayer: () => {} }),
    tileLayer: () => ({ addTo: () => {} }),
    marker: () => ({ addTo: () => {}, bindPopup: () => ({ addTo: () => {} }) }),
    icon: () => ({}),
    Icon: { Default: { prototype: { mergeOptions: () => {} } } },
  },
}));
vi.mock("leaflet/dist/leaflet.css", () => ({}));

vi.mock("../api/client", () => ({
  default: {
    get: vi.fn().mockImplementation((url: string) => {
      if (url.includes("/cities")) {
        return Promise.resolve({ data: { results: [{ id: 1, city_name: "广州", province: "广东" }] } });
      }
      return Promise.resolve({
        data: { results: [
          { id: 1, project_name: "广州PCB工厂", city_name: "广州" },
          { id: 2, project_name: "西安PCB工厂", city_name: "西安" },
        ]},
      });
    }),
    post: vi.fn().mockResolvedValue({ data: { id: 3, project_name: "新工厂" } }),
  },
}));

function renderMapHome() {
  return render(
    <MemoryRouter>
      <MapHome />
    </MemoryRouter>
  );
}

describe("MapHome Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.setItem("access_token", "test-token");
  });

  it("renders page title and search box", () => {
    renderMapHome();
    expect(screen.getByPlaceholderText("搜索项目")).toBeInTheDocument();
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
    const btn = document.querySelector("button.ant-btn-primary");
    expect(btn?.textContent?.replace(/\s/g, "")).toContain("新建项目");
  });

  it("opens create project modal on button click", async () => {
    const user = userEvent.setup();
    renderMapHome();
    const btn = document.querySelector("button.ant-btn-primary");
    if (btn) await user.click(btn);
    await waitFor(() => {
      // Modal 弹出后会出现「项目名称」label
      expect(screen.getByText("项目名称")).toBeInTheDocument();
    });
  });

  it("filters projects by search keyword", async () => {
    const user = userEvent.setup();
    renderMapHome();
    await waitFor(() => expect(screen.getByText("广州PCB工厂")).toBeInTheDocument());
    await user.type(screen.getByPlaceholderText("搜索项目"), "广州");
    await waitFor(() => {
      expect(screen.getByText("广州PCB工厂")).toBeInTheDocument();
      expect(screen.queryByText("西安PCB工厂")).not.toBeInTheDocument();
    });
  });
});
