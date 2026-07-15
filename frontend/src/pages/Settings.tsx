import { useState, useEffect } from "react";
import { Layout, Tabs, Card, Table, Descriptions, Typography, Space } from "antd";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

const { Header, Content } = Layout;
const { Title } = Typography;

/** 系统设置 4 Tab（F9-001~018） */
const TAB_KEYS = {
  waterTemp: "waterTemp",
  defaults: "defaults",
  national: "national",
  weather: "weather",
};

/**
 * 系统设置页（F9-001~018）
 * Tab1 冷冻水配置 / Tab2 默认值配置 / Tab3 国标参数查询 / Tab4 气象数据管理
 */
export default function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(TAB_KEYS.waterTemp);
  const [defaults, setDefaults] = useState<Record<string, number> | null>(null);
  const [cities, setCities] = useState<any[]>([]);

  useEffect(() => {
    if (activeTab === TAB_KEYS.defaults && !defaults) {
      client.get("/defaults/").then((r) => setDefaults(r.data));
    }
    if (activeTab === TAB_KEYS.national && cities.length === 0) {
      client.get("/cities/").then((r) => setCities(r.data.results || []));
    }
  }, [activeTab]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          padding: "0 24px",
        }}
      >
        <Title level={4} style={{ color: "#fff", margin: 0, cursor: "pointer" }} onClick={() => navigate("/map")}>
          PCB-CoolSim — 系统设置
        </Title>
      </Header>

      <Content style={{ padding: 24 }}>
        <Card>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: TAB_KEYS.waterTemp,
                label: "冷冻水配置",
                children: (
                  <Space direction="vertical">
                    <p>项目级冷冻水温度配置 CRUD（低温 7/12°C、中温 12/17°C）</p>
                    <Table
                      size="small"
                      dataSource={[
                        { key: 1, name: "低温冷冻水", supply: 7, return: 12 },
                        { key: 2, name: "中温冷冻水", supply: 12, return: 17 },
                      ]}
                      columns={[
                        { title: "配置名称", dataIndex: "name" },
                        { title: "供水(℃)", dataIndex: "supply" },
                        { title: "回水(℃)", dataIndex: "return" },
                      ]}
                    />
                  </Space>
                ),
              },
              {
                key: TAB_KEYS.defaults,
                label: "默认值配置",
                children: defaults ? (
                  <Descriptions title="系统默认值" bordered column={2}>
                    <Descriptions.Item label="土建指标(W/m²)">
                      {defaults.civil_load_index}
                    </Descriptions.Item>
                    <Descriptions.Item label="照明指标(W/m²)">
                      {defaults.lighting_load_index}
                    </Descriptions.Item>
                    <Descriptions.Item label="空气密度(kg/m³)">
                      {defaults.air_density}
                    </Descriptions.Item>
                    <Descriptions.Item label="室内温度(℃)">
                      {defaults.indoor_calc_temp}
                    </Descriptions.Item>
                    <Descriptions.Item label="室内湿度(%)">
                      {defaults.indoor_calc_humidity}
                    </Descriptions.Item>
                  </Descriptions>
                ) : (
                  <p>加载中...</p>
                ),
              },
              {
                key: TAB_KEYS.national,
                label: "国标参数",
                children: (
                  <Table
                    size="small"
                    dataSource={cities}
                    rowKey="id"
                    columns={[
                      { title: "城市", dataIndex: "city_name" },
                      { title: "省份", dataIndex: "province" },
                    ]}
                  />
                ),
              },
              {
                key: TAB_KEYS.weather,
                label: "气象数据",
                children: <p>气象数据管理（API 拉取 / CSV 上传 / 数据概览）</p>,
              },
            ]}
          />
        </Card>
      </Content>
    </Layout>
  );
}
