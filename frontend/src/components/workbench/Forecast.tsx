import { useState, useEffect } from "react";
import { Row, Col, Card, Button, Table, Tag, Segmented, Empty, Typography, Space, Statistic } from "antd";
import { PlusOutlined, CloudUploadOutlined, ReloadOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

/**
 * Tab6 负荷预测（F10-001~021）
 * 场景管理 + 天气配置 + 生产负荷率 + 预测结果
 */
export default function Forecast({ projectId }: { projectId: number }) {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(`/projects/${projectId}/forecast-scenarios/`)
      .then((r) => setScenarios(r.data.results || []))
      .finally(() => setLoading(false));
  }, [projectId]);

  return (
    <div style={{ padding: 12 }}>
      <Row gutter={12}>
        {/* 左：场景管理 */}
        <Col span={10}>
          <Card
            title="预测场景管理"
            size="small"
            extra={
              <Button size="small" type="primary" icon={<PlusOutlined />}>
                创建场景
              </Button>
            }
          >
            <Table
              size="small"
              loading={loading}
              dataSource={scenarios}
              rowKey="id"
              pagination={false}
              columns={[
                { title: "场景名称", dataIndex: "name" },
                {
                  title: "状态",
                  dataIndex: "status",
                  render: (s: string) => {
                    const color = s === "active" ? "green" : s === "paused" ? "orange" : "default";
                    return <Tag color={color}>{s === "active" ? "活跃" : s === "paused" ? "暂停" : "归档"}</Tag>;
                  },
                },
                { title: "开始日期", dataIndex: "start_date", width: 100 },
              ]}
            />
          </Card>
        </Col>

        {/* 右：配置 + 结果 */}
        <Col span={14}>
          {/* 天气配置 */}
          <Card title="天气配置" size="small" style={{ marginBottom: 12 }}>
            <Space>
              <Segmented
                options={[
                  { label: "API 自动", value: "api" },
                  { label: "手动上传", value: "manual" },
                ]}
              />
              <Button size="small" icon={<ReloadOutlined />}>刷新天气</Button>
              <Button size="small" icon={<CloudUploadOutlined />}>上传 CSV</Button>
            </Space>
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">最后更新：— | 状态：待运行 | 记录数：168/168</Text>
            </div>
          </Card>

          {/* 生产负荷率 */}
          <Card title="生产负荷率（多段配置）" size="small" style={{ marginBottom: 12 }}>
            <Row gutter={12}>
              <Col span={8}><Statistic title="段1" value="100%" suffix="× 168h" /></Col>
              <Col span={8}><Statistic title="段2" value="--" suffix="（可选）" /></Col>
              <Col span={8}><Statistic title="总时长" value={168} suffix="小时" /></Col>
            </Row>
          </Card>

          {/* 预测结果 */}
          <Card title="预测结果（7×24=168点）" size="small">
            <Empty description="ECharts 逐时负荷曲线（预测 vs 历史对比）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
