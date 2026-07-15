import { useState } from "react";
import { Layout, Tabs, Tree, Card, Typography, Space, Button } from "antd";
import { SettingOutlined } from "@ant-design/icons";
import { useNavigate, useParams } from "react-router-dom";

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

/** 工作台 6 Tab（PRD §3.1，Tab3=负荷分析） */
const TAB_ITEMS = [
  { key: "basic", label: "基础配置" },
  { key: "static", label: "静态计算" },
  { key: "analysis", label: "负荷分析" },
  { key: "dynamic", label: "动态仿真" },
  { key: "view2d", label: "2D展示" },
  { key: "forecast", label: "负荷预测" },
];

/**
 * 项目工作台（F2-001~008，左树右详情 6 Tab）
 * PRD §3.1 页面三
 */
export default function Workbench() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("basic");

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          color: "#fff",
        }}
      >
        <Space>
          <Title level={4} style={{ color: "#fff", margin: 0 }}>
            PCB-CoolSim
          </Title>
          <Text style={{ color: "rgba(255,255,255,0.7)" }}>
            项目 #{projectId}
          </Text>
        </Space>
        <Button
          type="text"
          icon={<SettingOutlined />}
          style={{ color: "#fff" }}
          onClick={() => navigate("/settings")}
        >
          系统设置
        </Button>
      </Header>

      <Layout>
        <Sider width={300} style={{ background: "#fff", padding: "12px" }}>
          <Card title="层级结构" size="small" style={{ height: "100%" }}>
            <Tree
              treeData={[
                {
                  title: "项目根节点",
                  key: "root",
                  children: [
                    {
                      title: "建筑 1#厂房",
                      key: "b1",
                      children: [
                        { title: "楼层 1F", key: "f1" },
                        { title: "楼层 2F", key: "f2" },
                      ],
                    },
                  ],
                },
              ]}
              defaultExpandAll
            />
          </Card>
        </Sider>

        <Content style={{ padding: "12px", background: "#f0f2f5" }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={TAB_ITEMS.map((tab) => ({
              key: tab.key,
              label: tab.label,
              children: (
                <Card>
                  <Text type="secondary">
                    {tab.label} — 待按 PRD 实现具体内容（功能区域参数录入/计算结果/分析图表等）
                  </Text>
                </Card>
              ),
            }))}
          />
        </Content>
      </Layout>
    </Layout>
  );
}
