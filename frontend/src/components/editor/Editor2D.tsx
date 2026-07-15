import { useState, useRef, useEffect } from "react";
import { Button, Space, Upload, Select, Typography, Card, Tag } from "antd";
import {
  BorderOuterOutlined, BorderOutlined, AimOutlined,
  CompassOutlined, SaveOutlined, UploadOutlined, ArrowLeftOutlined,
} from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

const TOOLS = [
  { key: "rect", label: "矩形绘制", icon: <BorderOutlined /> },
  { key: "outline", label: "外墙轮廓", icon: <BorderOuterOutlined /> },
  { key: "scale", label: "比例尺", icon: <AimOutlined /> },
  { key: "compass", label: "指北针", icon: <CompassOutlined /> },
];

/**
 * 2D 编辑器（F3-001~013）
 * Fabric.js Canvas 编辑器：底图上传/矩形绘制/外墙轮廓/比例尺/指北针/保存
 */
export default function Editor2D({ floorId }: { floorId: number }) {
  const [tool, setTool] = useState("rect");
  const [planData, setPlanData] = useState<any>({ blocks: [] });
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // 加载已有平面图数据
  useEffect(() => {
    client.get(`/floors/${floorId}/floor-plan/`).then((r) => {
      setPlanData(r.data.floor_plan_data || { blocks: [] });
    });
  }, [floorId]);

  const handleSave = async () => {
    await client.put(`/floors/${floorId}/floor-plan/`, {
      floor_plan_data: planData,
    });
  };

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    await client.post(`/floors/${floorId}/floor-plan/upload/`, formData);
    return false; // 阻止 antd 默认上传
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* 顶部工具栏 */}
      <Card size="small" style={{ borderRadius: 0 }}>
        <Space wrap>
          <Button icon={<ArrowLeftOutlined />}>返回</Button>
          <Upload beforeUpload={handleUpload} accept=".pdf" showUploadList={false}>
            <Button icon={<UploadOutlined />}>上传底图</Button>
          </Upload>
          {TOOLS.map((t) => (
            <Button
              key={t.key}
              type={tool === t.key ? "primary" : "default"}
              icon={t.icon}
              onClick={() => setTool(t.key)}
            >
              {t.label}
            </Button>
          ))}
          <Text type="secondary">当前工具：</Text>
          <Tag color="blue">{TOOLS.find((t) => t.key === tool)?.label}</Tag>
          <Select
            placeholder="关联功能区域"
            style={{ width: 150 }}
            options={[
              { label: "电镀区", value: 1 },
              { label: "曝光区", value: 2 },
            ]}
          />
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
            保存
          </Button>
        </Space>
      </Card>

      {/* 画布区域 */}
      <div style={{ flex: 1, background: "#f0f2f5", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Card size="small" style={{ width: "90%", height: "85%", display: "flex", flexDirection: "column" }}>
          <Text strong style={{ marginBottom: 8 }}>画布编辑区</Text>
          <canvas
            ref={canvasRef}
            width={800}
            height={500}
            style={{ border: "1px solid #d9d9d9", background: "#fff", flex: 1 }}
            data-testid="editor-canvas"
          />
        </Card>
      </div>
    </div>
  );
}
