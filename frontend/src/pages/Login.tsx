import { useState } from "react";
import { Card, Form, Input, Button, Alert, Typography, Space } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

const { Title, Text } = Typography;

/**
 * 登录页（F1-001~006）
 * - JWT Access + Refresh Token
 * - 账号密码登录
 * - 登录成功跳转地图首页
 */
export default function Login() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await client.post("/auth/login/", values);
      localStorage.setItem("access_token", resp.data.access);
      localStorage.setItem("refresh_token", resp.data.refresh);
      navigate("/map");
    } catch (err: any) {
      const msg = err.response?.data?.detail || "登录失败，请重试";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)",
      }}
    >
      <Card style={{ width: 420, padding: "24px 32px" }} variant="borderless">
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div style={{ textAlign: "center" }}>
            <Title level={2} style={{ margin: 0, color: "#1565C0" }}>
              PCB-CoolSim
            </Title>
            <Text type="secondary">PCB 工厂冷量仿真平台</Text>
          </div>

          {error && <Alert type="error" message={error} showIcon closable />}

          <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
            validateTrigger={["onSubmit"]}
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: "请输入用户名" }]}
            >
              <Input prefix={<UserOutlined />} placeholder="用户名" aria-label="用户名" />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: "请输入密码" }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
                aria-label="密码"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button type="primary" htmlType="submit" loading={loading} block>
                登录
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>
    </div>
  );
}
