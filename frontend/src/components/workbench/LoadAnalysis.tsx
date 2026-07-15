import { useState, useEffect } from "react";
import { Row, Col, Card, Table, Segmented, Empty, Alert, Typography, List, Tag } from "antd";
import { BulbOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

/**
 * Tab3 负荷分析（F5-001~007）
 * 五维度分析：功能区域/楼层/建筑/冷量种类/负荷构成 + 自动建议
 */
export default function LoadAnalysis({ projectId }: { projectId: number }) {
  const [dimension, setDimension] = useState("room");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(`/calc/results/${projectId}/?dimension=${dimension}`)
      .then((resp) => setData(resp.data))
      .finally(() => setLoading(false));
  }, [projectId, dimension]);

  const byRoom = data?.by_room || [];
  const byCategory = data?.by_category || {};
  const suggestions = data?.suggestions || [];

  return (
    <div style={{ padding: 12 }}>
      {/* 维度切换 */}
      <Card size="small" style={{ marginBottom: 12 }}>
        <Text strong>分析维度：</Text>
        <Segmented
          value={dimension}
          onChange={(v) => setDimension(v as string)}
          options={[
            { label: "功能区域", value: "room" },
            { label: "楼层", value: "floor" },
            { label: "建筑", value: "building" },
            { label: "冷量种类", value: "temp" },
            { label: "负荷构成", value: "category" },
          ]}
          style={{ marginLeft: 12 }}
        />
      </Card>

      <Text style={{ fontSize: 16, fontWeight: "bold" }}>五维度负荷分析</Text>

      {/* 功能区域排名表 */}
      <Card title="功能区域排名" size="small" style={{ marginTop: 8, marginBottom: 12 }}>
        <Table
          size="small"
          loading={loading}
          dataSource={byRoom}
          rowKey="room_name"
          pagination={false}
          columns={[
            { title: "功能区域", dataIndex: "room_name" },
            { title: "总负荷(kW)", dataIndex: "total_load", align: "right" as const,
              sorter: (a, b) => a.total_load - b.total_load },
          ]}
        />
      </Card>

      {/* 负荷构成 + 图表占位 */}
      <Row gutter={12}>
        <Col span={12}>
          <Card title="负荷构成" size="small">
            <Empty description="饼图（土建/照明/人员/设备/新风）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="按水温分布" size="small">
            <Empty description="堆叠柱状图（低温/中温）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>
      </Row>

      {/* 自动分析建议 */}
      <Card
        title={<span><BulbOutlined /> 自动分析建议</span>}
        size="small"
        style={{ marginTop: 12 }}
      >
        {suggestions.length > 0 ? (
          <List
            dataSource={suggestions}
            renderItem={(s: any) => (
              <List.Item>
                <Alert
                  type="warning"
                  message={<><Tag color="orange">{s.room_name}</Tag> {s.message}</>}
                />
              </List.Item>
            )}
          />
        ) : (
          <Text type="secondary">暂无建议</Text>
        )}
      </Card>
    </div>
  );
}
