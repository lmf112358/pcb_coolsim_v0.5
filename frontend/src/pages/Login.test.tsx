import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Login from "./Login";

vi.mock("../api/client", () => ({
  default: { post: vi.fn() },
}));

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );
}

/** 查找提交按钮（通过 type=submit 精确匹配） */
function findSubmitButton() {
  const btn = document.querySelector('button[type="submit"]');
  if (!btn) throw new Error("submit button not found");
  return btn;
}

describe("Login Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("renders login form with username and password inputs", () => {
    renderLogin();
    expect(screen.getByPlaceholderText("用户名")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("密码")).toBeInTheDocument();
    expect(findSubmitButton()).toBeInTheDocument();
  });

  it("shows validation error for empty submission", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.click(findSubmitButton());
    expect(await screen.findByText("请输入用户名")).toBeInTheDocument();
  });

  it("submits login and stores token on success", async () => {
    const user = userEvent.setup();
    const client = (await import("../api/client")).default;
    (client.post as any).mockResolvedValueOnce({
      data: { access: "token-123", refresh: "refresh-456" },
    });
    renderLogin();
    await user.type(screen.getByPlaceholderText("用户名"), "engineer");
    await user.type(screen.getByPlaceholderText("密码"), "Test@12345");
    await user.click(findSubmitButton());
    await waitFor(() => {
      expect(localStorage.getItem("access_token")).toBe("token-123");
      expect(localStorage.getItem("refresh_token")).toBe("refresh-456");
    });
  });

  it("shows error message on login failure", async () => {
    const user = userEvent.setup();
    const client = (await import("../api/client")).default;
    (client.post as any).mockRejectedValueOnce({
      response: { status: 401, data: { detail: "账号或密码错误" } },
    });
    renderLogin();
    await user.type(screen.getByPlaceholderText("用户名"), "wrong");
    await user.type(screen.getByPlaceholderText("密码"), "wrong");
    await user.click(findSubmitButton());
    expect(await screen.findByText("账号或密码错误")).toBeInTheDocument();
  });
});
