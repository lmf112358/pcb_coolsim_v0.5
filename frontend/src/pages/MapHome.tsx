import { useState, useEffect } from "react";
import { Layout, Input, Button, Card, List, Tag, Typography, Space, Empty } from "antd";
import { PlusOutlined, EnvironmentOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

interface Project {
  id: number;
  project_name: string;
  city_name?: string;
  location?: string;
}

/**
 * 地图首页（F1-007~014）
 * 项目标点列表 + 搜索 + 新建项目入口
 * v0.5：列表展示（Leaflet 地图在浏览器环境渲染，测试环境 mock）
 */
export default function MapHome() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get("/projects/")
      .then((resp) => setProjects(resp.data.results || []))
      .finally(() => setLoading(false));
  }, []);

  const filtered = search
    ? projects.filter(
        (p) =>
          p.project_name.includes(search) ||
          (p.city_name || "").includes(search)
      )
    : projects;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
        }}
      >
        <Title level={4} style={{ color: "#fff", margin: 0 }}>
          PCB-CoolSim
        </Title>
        <Input
          placeholder="搜索项目"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 240 }}
          allowClear
        />
      </Header>

      <Content style={{ padding: 24 }}>
        <Card
          title="项目列表"
          extra={
            <Button type="primary" icon={<PlusOutlined />}>
              新建项目
            </Button>
          }
        >
          {filtered.length === 0 && !loading ? (
            <Empty description="暂无项目" />
          ) : (
            <List
              loading={loading}
              dataSource={filtered}
              renderItem={(project) => (
                <List.Item
                  key={project.id}
                  actions={[
                    <Button
                      type="link"
                      onClick={() => navigate(`/project/${project.id}`)}
                    >
                      进入项目
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={project.project_name}
                    description={
                      <Space>
                        <Tag icon={<EnvironmentOutlined />} color="blue">
                          {project.city_name || "未指定"}
                        </Tag>
                        {project.location && (
                          <Text type="secondary">{project.location}</Text>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Content>
    </Layout>
  );
}
