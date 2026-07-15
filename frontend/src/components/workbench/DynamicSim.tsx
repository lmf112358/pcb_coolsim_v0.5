import { useState, useEffect } from "react";
import { Row, Col, Card, Button, Statistic, Segmented, Empty, Typography } from "antd";
import { PlayCircleOutlined, ThunderboltOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

/**
 * Tab4 动态仿真（F6-001~023）
 * 逐时曲线 + 极值统计 + 时间筛选
 */
export default function DynamicSim({ projectId }: { projectId: number }) {
  const [timeView, setTimeView] = useState("year");
  const [extremes, setExtremes] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadExtremes = () => {
    setLoading(true);
    client
      .get(`/calc/dynamic/${projectId}/summary/`)
      .then((r) => setExtremes(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadExtremes();
  }, [projectId]);

  const handleSimulate = async () => {
    await client.post(`/calc/dynamic/${projectId}/`);
    loadExtremes();
  };

  return (
    <div style={{ padding: 12 }}>
      {/* 触发仿真 + 时间筛选 */}
      <Card size="small" style={{ marginBottom: 12 }}>
        <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleSimulate}>
          运行动态仿真
        </Button>
        <span style={{ marginLeft: 24 }}>
          <Text strong>时间筛选：</Text>
          <Segmented
            value={timeView}
            onChange={(v) => setTimeView(v as string)}
            options={[
              { label: "年视图", value: "year" },
              { label: "月视图", value: "month" },
              { label: "日视图", value: "day" },
            ]}
            style={{ marginLeft: 8 }}
          />
        </span>
      </Card>

      {/* 极值统计 */}
      <Card title="极值统计" size="small" style={{ marginBottom: 12 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="峰值负荷(kW)" value={extremes?.extremes?.max_load || 0}
              prefix={<ThunderboltOutlined style={{ color: "#E53935" }} />} loading={loading} />
          </Col>
          <Col span={6}>
            <Statistic title="最小负荷(kW)" value={extremes?.extremes?.min_load || 0} loading={loading} />
          </Col>
          <Col span={6}>
            <Statistic title="平均负荷(kW)" value={extremes?.extremes?.avg_load || 0} loading={loading} />
          </Col>
          <Col span={6}>
            <Statistic title="数据点数" value={extremes?.point_count || 0} loading={loading} />
          </Col>
        </Row>
      </Card>

      {/* 逐时曲线 */}
      <Card title="逐时负荷曲线（约26280点）" size="small">
        <Empty description="ECharts LTTB 降采样折线图（X轴时间，Y轴kW）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </Card>
    </div>
  );
}
