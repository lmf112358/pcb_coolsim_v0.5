import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Editor2D from "./Editor2D";

// mock fabric.js（jsdom 不支持 Canvas）
vi.mock("fabric", () => ({
  Canvas: vi.fn().mockImplementation(() => ({
    add: vi.fn(), remove: vi.fn(), clear: vi.fn(),
    toJSON: vi.fn().mockReturnValue({ objects: [] }),
    loadFromJSON: vi.fn().mockResolvedValue({}),
    dispose: vi.fn(),
    on: vi.fn(),
  })),
}));

vi.mock("../../api/client", () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { detail: "保存成功" } }),
    put: vi.fn().mockResolvedValue({ data: { detail: "保存成功" } }),
    get: vi.fn().mockResolvedValue({ data: { floor_plan_data: {} } }),
  },
}));

function renderEditor2D() {
  return render(<Editor2D floorId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

function findButton(text: string) {
  const btns = screen.getAllByRole("button");
  const b = btns.find((b) => b.textContent?.replace(/\s/g, "").includes(text.replace(/\s/g, "")));
  if (!b) throw new Error(`Button "${text}" not found`);
  return b;
}

describe("Editor2D (F3-001~013)", () => {
  it("renders toolbar with drawing tools", () => {
    renderEditor2D();
    expect(findByText("矩形绘制")).toBeInTheDocument();
    expect(findByText("外墙轮廓")).toBeInTheDocument();
    expect(findByText("比例尺")).toBeInTheDocument();
    expect(findByText("指北针")).toBeInTheDocument();
  });

  it("renders upload PDF button", () => {
    renderEditor2D();
    expect(findByText("上传底图")).toBeInTheDocument();
  });

  it("renders save button", () => {
    renderEditor2D();
    expect(findByText("保存")).toBeInTheDocument();
  });

  it("renders canvas area", () => {
    renderEditor2D();
    expect(findByText("画布编辑区")).toBeInTheDocument();
  });

  it("saves plan data on save button click", async () => {
    const user = userEvent.setup();
    const client = (await import("../../api/client")).default;
    renderEditor2D();
    await user.click(findButton("保存"));
    await waitFor(() => {
      expect(client.put).toHaveBeenCalled();
    });
  });

  it("renders tool mode indicator", () => {
    renderEditor2D();
    expect(findByText("当前工具")).toBeInTheDocument();
  });

  it("renders room association dropdown label", () => {
    renderEditor2D();
    expect(findByText("关联功能区域")).toBeInTheDocument();
  });
});
