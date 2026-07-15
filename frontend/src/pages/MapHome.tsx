import { useState, useEffect, useRef } from "react";
import { Layout, Input, Button, Card, List, Tag, Typography, Space, Empty, Modal, Form, Select, message } from "antd";
import { PlusOutlined, EnvironmentOutlined, LogoutOutlined, SettingOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import client from "../api/client";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

// 修复 Leaflet 默认图标路径（安全 try-catch，测试环境 mock 时跳过）
try {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
} catch {
  // 测试环境（leaflet mocked）忽略
}

// 项目状态颜色映射
const STATUS_COLORS: Record<string, string> = {
  completed: "#52C41A", // 绿色
  designing: "#1890FF", // 蓝色
};

interface Project {
  id: number;
  project_name: string;
  city_name?: string;
  city?: number;
  location?: string;
  status?: string;
  latitude?: string;
  longitude?: string;
}

/**
 * 地图首页（F1-007~014）
 * Leaflet 地图 + 项目标点 + 摘要卡片 + 新建项目
 */
export default function MapHome() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [cities, setCities] = useState<any[]>([]);
  const [form] = Form.useForm();
  const mapRef = useRef<L.Map | null>(null);
  const mapDivRef = useRef<HTMLDivElement>(null);

  const loadProjects = () => {
    setLoading(true);
    client
      .get("/projects/")
      .then((resp) => setProjects(resp.data.results || []))
      .catch(() => {
        // Token 可能过期，跳转登录
        if (!localStorage.getItem("access_token")) navigate("/login");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProjects();
    // 加载城市列表（新建项目用）
    client.get("/cities/?page_size=9999").then((r) => setCities(r.data.results || []));
  }, []);

  // 初始化 Leaflet 地图
  useEffect(() => {
    if (mapDivRef.current && !mapRef.current) {
      mapRef.current = L.map(mapDivRef.current).setView([35.86, 104.19], 4); // 中国中心
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap",
      }).addTo(mapRef.current);
    }
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // 添加项目标点到地图
  useEffect(() => {
    if (!mapRef.current) return;
    // 清除旧标点
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) mapRef.current!.removeLayer(layer);
    });
    // 添加新标点（使用城市经纬度，暂时用随机偏移）
    projects.forEach((p) => {
      // 后续从 city 获取实际经纬度；v0.5 使用中国范围内的偏移
      const lat = 30 + (p.id % 10) * 2;
      const lng = 110 + (p.id % 8) * 2;
      const color = STATUS_COLORS[p.status || "designing"];
      const marker = L.marker([lat, lng]).addTo(mapRef.current!);
      marker.bindPopup(
        `<b>${p.project_name}</b><br/>${p.city_name || ""}<br/><a href="#/project/${p.id}">进入项目</a>`
      );
    });
  }, [projects]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  const handleCreateProject = async () => {
    const values = await form.validateFields();
    try {
      const resp = await client.post("/projects/", {
        project_name: values.project_name,
        city: values.city,
        location: values.location || "",
      });
      message.success("项目创建成功");
      setModalOpen(false);
      form.resetFields();
      loadProjects();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "创建失败");
    }
  };

  const filtered = search
    ? projects.filter(
        (p) => p.project_name.includes(search) || (p.city_name || "").includes(search)
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
        <Space>
          <Title level={4} style={{ color: "#fff", margin: 0 }}>
            PCB-CoolSim
          </Title>
        </Space>
        <Space>
          <Input
            placeholder="搜索项目"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            新建项目
          </Button>
          <Button type="text" icon={<SettingOutlined />} style={{ color: "#fff" }} onClick={() => navigate("/settings")} />
          <Button type="text" icon={<LogoutOutlined />} style={{ color: "#fff" }} onClick={handleLogout} />
        </Space>
      </Header>

      <Content style={{ display: "flex", gap: 0 }}>
        {/* 左侧：地图 */}
        <div style={{ flex: 1, position: "relative" }}>
          <div
            ref={mapDivRef}
            style={{ width: "100%", height: "calc(100vh - 64px)" }}
          />
        </div>

        {/* 右侧：项目列表 */}
        <Card
          title={`项目列表（${filtered.length}）`}
          style={{ width: 360, overflow: "auto", maxHeight: "calc(100vh - 64px)" }}
          size="small"
        >
          {filtered.length === 0 && !loading ? (
            <Empty description="暂无项目，点击「新建项目」创建" />
          ) : (
            <List
              loading={loading}
              dataSource={filtered}
              renderItem={(project) => (
                <List.Item
                  key={project.id}
                  style={{ cursor: "pointer", padding: "8px 4px" }}
                  onClick={() => navigate(`/project/${project.id}`)}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>{project.project_name}</span>
                      </Space>
                    }
                    description={
                      <Space size="small">
                        <Tag icon={<EnvironmentOutlined />} color="blue">
                          {project.city_name || "未指定城市"}
                        </Tag>
                        {project.location && <Text type="secondary">{project.location}</Text>}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Content>

      {/* 新建项目 Modal */}
      <Modal
        title="新建项目"
        open={modalOpen}
        onOk={handleCreateProject}
        onCancel={() => setModalOpen(false)}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="project_name" label="项目名称" rules={[{ required: true, message: "请输入项目名称" }]}>
            <Input placeholder="如：上海松江 PCB 工厂" />
          </Form.Item>
          <Form.Item name="city" label="所属城市" rules={[{ required: true, message: "请选择城市" }]}>
            <Select
              showSearch
              placeholder="选择城市"
              filterOption={(input, option) =>
                (option?.label || "").toLowerCase().includes(input.toLowerCase())
              }
              options={cities.map((c) => ({
                label: `${c.province} ${c.city_name}`,
                value: c.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="location" label="详细地址">
            <Input placeholder="如：黄埔区XX路XX号" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}
