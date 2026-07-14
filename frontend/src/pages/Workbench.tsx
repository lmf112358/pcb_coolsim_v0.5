import { Card } from "antd";
import { useTranslation } from "react-i18next";

/** Workbench 页面占位（后续按 PRD 实现） */
export default function Workbench() {
  const { t } = useTranslation();
  return (
    <Card title={t("page.workbench")} style={{ margin: 24 }}>
      <p>Workbench 页面 — 待按 PRD 实现</p>
    </Card>
  );
}
