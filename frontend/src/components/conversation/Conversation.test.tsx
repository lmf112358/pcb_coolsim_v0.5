import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Conversation from "./Conversation";

vi.mock("../../api/client", () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { id: 1, current_stage: "s1_project" } }),
    get: vi.fn().mockResolvedValue({
      data: {
        results: [
          { role: "system", content: "请确认项目信息", stage: "s1_project" },
        ],
      },
    }),
    patch: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

function renderConversation() {
  return render(<Conversation projectId={1} />);
}

function findByText(text: string) {
  const normalized = text.replace(/\s/g, "");
  return screen.getAllByText((_, node) => {
    if (!node || node.children.length > 0) return false;
    return (node.textContent || "").replace(/\s/g, "").includes(normalized);
  })[0];
}

describe("Conversation (F2-046~061 三栏 Codex 布局)", () => {
  it("renders left panel with six-stage navigation", () => {
    renderConversation();
    expect(findByText("阶段导航")).toBeInTheDocument();
    expect(findByText("项目基本信息")).toBeInTheDocument();
    expect(findByText("冷冻水温度")).toBeInTheDocument();
    expect(findByText("建筑结构")).toBeInTheDocument();
    expect(findByText("功能区域")).toBeInTheDocument();
    expect(findByText("额外负荷")).toBeInTheDocument();
    expect(findByText("汇总确认")).toBeInTheDocument();
  });

  it("renders center panel with conversation area", () => {
    renderConversation();
    expect(findByText("对话主区")).toBeInTheDocument();
  });

  it("renders message input box", () => {
    renderConversation();
    expect(screen.getByPlaceholderText("输入消息...")).toBeInTheDocument();
  });

  it("renders right panel with structured preview", () => {
    renderConversation();
    expect(findByText("结构化预览")).toBeInTheDocument();
  });

  it("renders data tree in right panel", () => {
    renderConversation();
    expect(findByText("数据树")).toBeInTheDocument();
  });

  it("renders progress indicator", () => {
    renderConversation();
    expect(findByText("总进度")).toBeInTheDocument();
  });

  it("loads message history from API", async () => {
    renderConversation();
    await waitFor(() => {
      expect(findByText("请确认项目信息")).toBeInTheDocument();
    });
  });
});
