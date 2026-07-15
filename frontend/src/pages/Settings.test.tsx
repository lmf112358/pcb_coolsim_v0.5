import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Settings from "./Settings";

vi.mock("../api/client", () => ({
  default: {
    get: vi.fn().mockImplementation((url: string) => {
      if (url.includes("/defaults")) {
        return Promise.resolve({
          data: {
            civil_load_index: 30,
            lighting_load_index: 15,
            air_density: 1.2,
            indoor_calc_temp: 26,
            indoor_calc_humidity: 55,
          },
        });
      }
      if (url.includes("/cities")) {
        return Promise.resolve({
          data: { results: [{ id: 1, city_name: "广州", province: "广东" }] },
        });
      }
      return Promise.resolve({ data: { results: [] } });
    }),
  },
}));

function renderSettings() {
  return render(
    <MemoryRouter>
      <Settings />
    </MemoryRouter>
  );
}

function findTab(text: string) {
  const tabs = document.querySelectorAll(".ant-tabs-tab");
  for (const tab of tabs) {
    if (tab.textContent?.replace(/\s/g, "").includes(text)) return tab as HTMLElement;
  }
  throw new Error(`Tab "${text}" not found`);
}

describe("Settings Page", () => {
  it("renders 4 tabs (冷冻水/默认值/国标/气象)", () => {
    renderSettings();
    expect(findTab("冷冻水配置")).toBeInTheDocument();
    expect(findTab("默认值配置")).toBeInTheDocument();
    expect(findTab("国标参数")).toBeInTheDocument();
    expect(findTab("气象数据")).toBeInTheDocument();
  });

  it("switches to 默认值配置 tab and loads defaults", async () => {
    const user = userEvent.setup();
    renderSettings();
    await user.click(findTab("默认值配置"));
    await waitFor(() => {
      expect(screen.getByText(/30/)).toBeInTheDocument();
    });
  });

  it("switches to 国标参数 tab", async () => {
    const user = userEvent.setup();
    renderSettings();
    await user.click(findTab("国标参数"));
    await waitFor(() => {
      expect(screen.getByText("广州")).toBeInTheDocument();
    });
  });

  it("renders page title", () => {
    renderSettings();
    expect(screen.getAllByText(/PCB-CoolSim|系统设置/i).length).toBeGreaterThan(0);
  });
});
