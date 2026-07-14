import { Card } from "antd";
import { useTranslation } from "react-i18next";

/** Login 页面占位（后续按 PRD 实现） */
export default function Login() {
  const { t } = useTranslation();
  return (
    <Card title={t("page.login")} style={{ margin: 24 }}>
      <p>Login 页面 — 待按 PRD 实现</p>
    </Card>
  );
}
