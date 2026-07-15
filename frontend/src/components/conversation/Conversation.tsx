import { useState, useEffect, useRef } from "react";
import { Layout, Steps, Input, Button, Tree, Card, Progress, Typography, Space, Tag, Empty } from "antd";
import { SendOutlined, ExportOutlined } from "@ant-design/icons";
import client from "../../api/client";

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

const STAGES = [
  { key: "s1_project", title: "项目基本信息", desc: "展示确认" },
  { key: "s2_water_temp", title: "冷冻水温度", desc: "配置" },
  { key: "s3_building", title: "建筑结构", desc: "信息" },
  { key: "s4_room", title: "功能区域", desc: "参数" },
  { key: "s5_extra_load", title: "额外负荷", desc: "信息" },
  { key: "s6_summary", title: "汇总确认", desc: "入库" },
];

/**
 * 对话采集页（F2-046~061，三栏 Codex 布局）
 * 左：阶段导航 / 中：对话主区 / 右：结构化预览
 */
export default function Conversation({ projectId }: { projectId: number }) {
  const [currentStage] = useState(0);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<number | null>(null);
  const inputRef = useRef<any>(null);

  // 创建/恢复会话
  useEffect(() => {
    client.post(`/projects/${projectId}/conversation-sessions/`, {}).then((r) => {
      setSessionId(r.data.id);
      // 加载历史消息
      client.get(`/conversation-sessions/${r.data.id}/messages/`).then((mr) => {
        setMessages(mr.data.results || []);
      });
    });
  }, [projectId]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    const userMsg = { role: "user", content: input, stage: STAGES[currentStage].key };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    await client.post(`/conversation-sessions/${sessionId}/messages/`, userMsg);
  };

  const stageIdx = currentStage;
  const progress = ((stageIdx + 1) / STAGES.length) * 100;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* 左栏：阶段导航 */}
      <Sider width={260} style={{ background: "#fff", padding: 16, overflow: "auto" }}>
        <Title level={5}>阶段导航</Title>
        <Progress percent={Math.round(progress)} size="small" />
        <Text type="secondary">总进度</Text>
        <Steps
          direction="vertical"
          size="small"
          current={stageIdx}
          items={STAGES.map((s, i) => ({
            title: s.title,
            description: s.desc,
            status: i < stageIdx ? "finish" : i === stageIdx ? "process" : "wait",
          }))}
          style={{ marginTop: 16 }}
        />
      </Sider>

      {/* 中栏：对话主区 */}
      <Content style={{ display: "flex", flexDirection: "column", background: "#f5f5f5" }}>
        <Card size="small" style={{ borderRadius: 0 }}>
          <Space>
            <Title level={5} style={{ margin: 0 }}>对话主区</Title>
            <Tag color="blue">{STAGES[stageIdx].title}</Tag>
            <Button size="small" icon={<ExportOutlined />}>导出</Button>
          </Space>
        </Card>

        {/* 消息流 */}
        <div style={{ flex: 1, padding: 16, overflow: "auto" }}>
          {messages.length === 0 ? (
            <Empty description="系统即将开始提问..." />
          ) : (
            messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: 8,
                }}
              >
                <Card
                  size="small"
                  style={{
                    maxWidth: "70%",
                    background: msg.role === "user" ? "#1565C0" : "#fff",
                    color: msg.role === "user" ? "#fff" : "inherit",
                  }}
                >
                  <Text style={{ color: msg.role === "user" ? "#fff" : undefined }}>
                    {msg.content}
                  </Text>
                </Card>
              </div>
            ))
          )}
        </div>

        {/* 输入框 */}
        <Card size="small" style={{ borderRadius: 0 }}>
          <Space.Compact style={{ width: "100%" }}>
            <Input
              ref={inputRef}
              placeholder="输入消息..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={handleSend}
            />
            <Button type="primary" icon={<SendOutlined />} onClick={handleSend} />
          </Space.Compact>
        </Card>
      </Content>

      {/* 右栏：结构化预览 */}
      <Sider width={300} style={{ background: "#fff", padding: 16, overflow: "auto" }}>
        <Title level={5}>结构化预览</Title>
        <Card title="数据树" size="small">
          <Tree
            treeData={[
              {
                title: "项目",
                key: "project",
                children: [
                  { title: "建筑 1#厂房", key: "b1", children: [
                    { title: "1F 楼层", key: "f1" },
                  ]},
                ],
              },
            ]}
            defaultExpandAll
          />
        </Card>
        <Card title="当前区域摘要" size="small" style={{ marginTop: 8 }}>
          <Empty description="待采集" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        </Card>
        <Card title="缺失项提示" size="small" style={{ marginTop: 8 }}>
          <Tag color="orange">人员指标</Tag>
          <Tag color="orange">压差</Tag>
        </Card>
      </Sider>
    </Layout>
  );
}
