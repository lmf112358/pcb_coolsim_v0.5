import { useState, useEffect } from "react";
import { ConfigProvider, theme as antdTheme, Button, Space } from "antd";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { RouterProvider } from "react-router-dom";
import zhCN from "antd/locale/zh_CN";
import enUS from "antd/locale/en_US";
import "antd/dist/reset.css";
import "./locales";
import router from "./router";
import { lightTheme, darkTheme, type ThemeMode } from "./theme";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false, retry: 1 },
  },
});

function App() {
  const { i18n } = useTranslation();
  // PRD F9-022/F9-024：主题偏好持久化到 localStorage
  const [mode, setMode] = useState<ThemeMode>(
    () => (localStorage.getItem("theme") as ThemeMode) || "light"
  );

  useEffect(() => {
    localStorage.setItem("theme", mode);
  }, [mode]);

  const isDark = mode === "dark";
  const antdLocale = i18n.language === "en" ? enUS : zhCN;

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          ...(isDark ? darkTheme : lightTheme),
          algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        }}
        locale={antdLocale}
      >
        <Space style={{ position: "fixed", top: 12, right: 24, zIndex: 1000 }}>
          <Button
            size="small"
            onClick={() => i18n.changeLanguage(i18n.language === "zh" ? "en" : "zh")}
          >
            {i18n.language === "zh" ? "EN" : "中文"}
          </Button>
          <Button
            size="small"
            onClick={() => setMode(isDark ? "light" : "dark")}
          >
            {isDark ? "☀️" : "🌙"}
          </Button>
        </Space>
        <RouterProvider router={router} />
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
