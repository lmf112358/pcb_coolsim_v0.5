import axios from "axios";

// API 客户端（PRD 附录 D，统一 /api/v1/ 前缀）
const client = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
});

// 请求拦截：附加 JWT（F1-001）
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截：401 时用 refresh 续期（F1-004）
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const res = await axios.post("/api/v1/auth/refresh/", {
            refresh: refreshToken,
          });
          const { access } = res.data;
          localStorage.setItem("access_token", access);
          error.config.headers.Authorization = `Bearer ${access}`;
          return client(error.config);
        } catch {
          // refresh 失败，跳转登录
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
