import { Card } from "antd";
import { useTranslation } from "react-i18next";

/** Settings 页面占位（后续按 PRD 实现） */
export default function Settings() {
  const { t } = useTranslation();
  return (
    <Card title={t("page.settings")} style={{ margin: 24 }}>
      <p>Settings 页面 — 待按 PRD 实现</p>
    </Card>
  );
}
