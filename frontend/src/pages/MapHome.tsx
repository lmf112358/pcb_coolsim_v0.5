import { Card } from "antd";
import { useTranslation } from "react-i18next";

/** MapHome 页面占位（后续按 PRD 实现） */
export default function MapHome() {
  const { t } = useTranslation();
  return (
    <Card title={t("page.mapHome")} style={{ margin: 24 }}>
      <p>MapHome 页面 — 待按 PRD 实现</p>
    </Card>
  );
}
