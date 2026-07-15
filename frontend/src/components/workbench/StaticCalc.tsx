import { useState, useEffect } from "react";
import { Row, Col, Card, Table, Statistic, Typography, Empty, Divider } from "antd";
import { FireOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

interface RoomResult {
  room_name: string;
  temp_type: string;
  terminal_load: number;
  fresh_air_load: number;
  total_load: number;
}

/**
 * Tab2 静态计算（F4-001~033）
 * 汇总卡片 + 结果表 + 负荷构成 + 图表占位
 */
export default function StaticCalc({ projectId }: { projectId: number }) {
  const [results, setResults] = useState<RoomResult[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(`/calc/results/${projectId}/`)
      .then((resp) => {
        setResults(resp.data.results || []);
        setSummary(resp.data.summary || null);
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  return (
    <div style={{ padding: 12 }}>
      {/* 汇总卡片 */}
      <Row gutter={12} style={{ marginBottom: 12 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="低温冷冻水合计 (kW)"
              value={summary?.low_temp_total || 0}
              prefix={<FireOutlined style={{ color: "#C62828" }} />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="中温冷冻水合计 (kW)"
              value={summary?.mid_temp_total || 0}
              prefix={<FireOutlined style={{ color: "#1565C0" }} />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="总负荷合计 (kW)"
              value={summary?.grand_total || 0}
              prefix={<FireOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      {/* 结果明细表 */}
      <Card title="静态计算结果明细" size="small" style={{ marginBottom: 12 }}>
        <Table
          size="small"
          loading={loading}
          dataSource={results}
          rowKey="room_name"
          pagination={false}
          columns={[
            { title: "功能区域", dataIndex: "room_name", width: 120 },
            { title: "水温分类", dataIndex: "temp_type", width: 100 },
            { title: "末端负荷(kW)", dataIndex: "terminal_load", align: "right" as const },
            { title: "新风负荷(kW)", dataIndex: "fresh_air_load", align: "right" as const },
            { title: "总负荷(kW)", dataIndex: "total_load", align: "right" as const },
          ]}
        />
      </Card>

      {/* 图表区域 */}
      <Row gutter={12}>
        <Col span={12}>
          <Card title="柱状图 — 按功能区域" size="small">
            <Empty description="ECharts 柱状图（按功能区域排名）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="负荷构成 — 饼图" size="small">
            <Empty description="ECharts 饼图（土建/照明/人员/设备/新风占比）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
