import { useState, useEffect } from "react";
import { Row, Col, Card, Segmented, Typography, Empty, Tag, Space, Table, Statistic } from "antd";
import client from "../../api/client";

const { Text } = Typography;

const PROCESS_LEGEND = [
  { color: "#FF4D4F", label: "±1°C 红色" },
  { color: "#FA8C16", label: "±2°C 橙色" },
  { color: "#FADB14", label: "ISO7 黄色" },
  { color: "#52C41A", label: "ISO8 绿色" },
  { color: "#1890FF", label: "ISO7.5 蓝色" },
  { color: "#722ED1", label: "正压 紫色" },
  { color: "#BFBFBF", label: "负压/普通 灰色" },
];

/**
 * Tab5 2D展示（F7-017~024）
 * 热力图/工艺编码双模式 + 功能区域详情
 */
export default function View2D({ projectId }: { projectId: number }) {
  const [mode, setMode] = useState("heatmap");
  const [rooms, setRooms] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    client.get(`/calc/results/${projectId}/?dimension=room`).then((r) => {
      setRooms(r.data.results || r.data.rooms || []);
    });
  }, [projectId]);

  return (
    <div style={{ padding: 12 }}>
      {/* 模式切换 */}
      <Card size="small" style={{ marginBottom: 12 }}>
        <Segmented
          value={mode}
          onChange={(v) => setMode(v as string)}
          options={[
            { label: "热力图模式", value: "heatmap" },
            { label: "工艺编码模式", value: "process" },
          ]}
        />
        {/* 图例 */}
        <Space wrap style={{ marginLeft: 24 }}>
          <Text strong>图例：</Text>
          {mode === "heatmap" ? (
            <>
              <Tag color="blue">低负荷</Tag>
              <span style={{ background: "linear-gradient(90deg,#1E88E5,#C62828)", width: 80, height: 12, display: "inline-block", borderRadius: 2 }} />
              <Tag color="red">高负荷</Tag>
            </>
          ) : (
            PROCESS_LEGEND.map((l) => (
              <Tag key={l.label} color={l.color}>{l.label}</Tag>
            ))
          )}
        </Space>
      </Card>

      <Row gutter={12}>
        {/* 左：平面图 Canvas */}
        <Col span={16}>
          <Card title="平面图" size="small" style={{ height: 500 }}>
            <Empty description="2D 热力图渲染区（Fabric.js Canvas + 色块 + 比例尺 + 指北针）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          </Card>
        </Col>

        {/* 右：功能区域详情 */}
        <Col span={8}>
          <Card title="功能区域详情" size="small">
            {selected ? (
              <Space direction="vertical" style={{ width: "100%" }}>
                <Statistic title="总负荷(kW)" value={selected.total_load} />
                <Statistic title="冷指标(W/m²)" value={selected.cold_index} />
              </Space>
            ) : (
              <Table
                size="small"
                dataSource={rooms}
                rowKey="id"
                pagination={false}
                onRow={(r) => ({ onClick: () => setSelected(r) })}
                columns={[
                  { title: "功能区域", dataIndex: "room_name" },
                  { title: "总负荷", dataIndex: "total_load", align: "right" as const },
                ]}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
