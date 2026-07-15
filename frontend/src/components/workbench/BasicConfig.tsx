import { useState, useMemo } from "react";
import { Row, Col, Card, Tree, Form, Input, InputNumber, Button, Descriptions, Statistic, Space, Divider, Typography } from "antd";
import { CalculatorOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Text } = Typography;

/**
 * Tab1 基础配置（F2-001~008 左树右详情 + 实时计算预览）
 * PRD §3.1 工作台 Tab1
 */
export default function BasicConfig({ projectId }: { projectId: number }) {
  const [form] = Form.useForm();
  const [preview, setPreview] = useState<{ terminal_load?: number; fresh_air_load?: number; total_load?: number } | null>(null);
  const [calculating, setCalculating] = useState(false);

  // 自动计算体积
  const area = Form.useWatch("area", form);
  const height = Form.useWatch("height", form);
  const volume = useMemo(() => {
    if (area && height) return (Number(area) * Number(height)).toFixed(2);
    return null;
  }, [area, height]);

  const handleCalculate = async () => {
    const values = await form.validateFields();
    setCalculating(true);
    try {
      const resp = await client.post("/calculations/preview/", values);
      setPreview(resp.data);
    } finally {
      setCalculating(false);
    }
  };

  return (
    <Row gutter={12} style={{ height: "calc(100vh - 140px)" }}>
      {/* 左侧：层级树 */}
      <Col span={8}>
        <Card title="层级结构" size="small" style={{ height: "100%", overflow: "auto" }}>
          <Tree
            treeData={[
              {
                title: `项目 #${projectId}`,
                key: "root",
                children: [
                  {
                    title: "建筑 1#厂房",
                    key: "b1",
                    children: [
                      { title: "楼层 1F", key: "f1", children: [
                        { title: "电镀区", key: "r1" },
                        { title: "曝光区", key: "r2" },
                      ]},
                    ],
                  },
                ],
              },
            ]}
            defaultExpandAll
          />
        </Card>
      </Col>

      {/* 右侧：详情表单 + 实时预览 */}
      <Col span={16}>
        <Card title="功能区域详情" size="small" style={{ height: "100%", overflow: "auto" }}>
          <Form form={form} layout="vertical" size="small">
            {/* 第一组：基本信息 */}
            <Text strong>基本信息</Text>
            <Row gutter={12}>
              <Col span={8}>
                <Form.Item name="room_name" label="功能区域名称">
                  <Input placeholder="如 电镀区" />
                </Form.Item>
              </Col>
              <Col span={5}>
                <Form.Item name="area" label="面积(m²)">
                  <InputNumber style={{ width: "100%" }} placeholder="100" />
                </Form.Item>
              </Col>
              <Col span={5}>
                <Form.Item name="height" label="吊顶高度(m)">
                  <InputNumber style={{ width: "100%" }} placeholder="3.5" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item label="体积(m³)">
                  <Input value={volume || ""} disabled placeholder="自动计算" />
                </Form.Item>
              </Col>
            </Row>

            {/* 第三组：负荷计算参数 */}
            <Divider />
            <Text strong>负荷计算参数</Text>
            <Row gutter={12}>
              <Col span={6}>
                <Form.Item name="civil_load_index" label="土建指标(W/m²)">
                  <InputNumber style={{ width: "100%" }} placeholder="30" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="lighting_load_index" label="照明指标(W/m²)">
                  <InputNumber style={{ width: "100%" }} placeholder="15" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="personnel_load_index" label="人员指标(W/人)">
                  <InputNumber style={{ width: "100%" }} placeholder="60" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="personnel_count" label="人数">
                  <InputNumber style={{ width: "100%" }} placeholder="5" />
                </Form.Item>
              </Col>
            </Row>

            {/* 设备参数 */}
            <Divider />
            <Text strong>设备参数</Text>
            <Row gutter={12}>
              <Col span={6}>
                <Form.Item name="electric_equipment_power" label="电动设备功率(kW)">
                  <InputNumber style={{ width: "100%" }} />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="electric_equipment_coefficient" label="电动设备系数">
                  <InputNumber style={{ width: "100%" }} step={0.1} min={0} max={1} />
                </Form.Item>
              </Col>
            </Row>

            <Button type="primary" icon={<CalculatorOutlined />} loading={calculating} onClick={handleCalculate}>
              计算预览
            </Button>

            {/* 实时计算预览 */}
            <Divider />
            <Card title="实时计算预览" size="small" style={{ marginTop: 12 }}>
              {preview ? (
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic title="末端负荷(kW)" value={preview.terminal_load} precision={2} />
                  </Col>
                  <Col span={8}>
                    <Statistic title="新风冷负荷(kW)" value={preview.fresh_air_load} precision={2} />
                  </Col>
                  <Col span={8}>
                    <Statistic title="总负荷(kW)" value={preview.total_load} precision={2} />
                  </Col>
                </Row>
              ) : (
                <Text type="secondary">填写参数后点击「计算预览」查看结果（响应 {"<500ms"}）</Text>
              )}
            </Card>
          </Form>
        </Card>
      </Col>
    </Row>
  );
}
