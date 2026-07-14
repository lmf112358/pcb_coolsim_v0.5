import { createBrowserRouter, Navigate } from "react-router-dom";
import Login from "../pages/Login";
import MapHome from "../pages/MapHome";
import Workbench from "../pages/Workbench";
import Settings from "../pages/Settings";

// PRD §3.1：6 个页面（①登录 ②地图首页 ③工作台6Tab ④2D编辑 ⑤设置 ⑥对话采集）
// 对话采集页由工作台 Tab1 入口进入，独立全屏
const router = createBrowserRouter([
  { path: "/", element: <Navigate to="/login" replace /> },
  { path: "/login", element: <Login /> },
  { path: "/map", element: <MapHome /> },
  { path: "/project/:projectId", element: <Workbench /> },
  { path: "/project/:projectId/conversation", element: <Workbench /> }, // 对话采集（占位，后续独立页）
  { path: "/settings", element: <Settings /> },
]);

export default router;
