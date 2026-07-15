# PCB-CoolSim — PCB 工厂冷量仿真平台

基于 Web 的 PCB 制造工厂冷量计算与仿真平台，用自动化、可视化、可协作的工具替代传统手工 Excel 计算。

> 当前阶段：项目骨架已搭建完成，进入功能开发阶段

## 📋 目录
- [技术栈](#技术栈)
- [快速开始（开发环境）](#快速开始开发环境)
- [项目结构](#项目结构)
- [开发指引](#开发指引)
- [常见问题](#常见问题)

## 🛠️ 技术栈

| 层级 | 技术选型 |
|------|---------|
| **前端** | React 19 + TypeScript + Vite + Ant Design 5 + React Query 5 + React Router |
| **后端** | Django 5 + DRF + Celery 5 + SimpleJWT |
| **数据库** | PostgreSQL 16 + TimescaleDB（生产环境）/ SQLite（开发环境） |
| **缓存/队列** | Redis 7 |
| **对象存储** | MinIO |
| **计算库** | NumPy / Pandas / psychrolib |

## 🚀 快速开始（开发环境）

### 1. 环境要求
- **Python 3.11+**
- **Node.js 24+**
- **npm** 或 **yarn**

### 2. 一键启动（最简单方式）

```bash
# 克隆项目
git clone <repo-url>
cd pcb_coolsim_v0.5

# 1. 配置环境变量
cp .env.example .env

# 2. 安装前端依赖
cd frontend
npm install

# 3. 安装后端依赖
cd ../backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements-dev.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 创建超级用户（可选）
python manage.py createsuperuser

# 6. 启动后端（新终端）
cd backend
.venv\Scripts\activate
python manage.py runserver      # http://localhost:8000

# 7. 启动前端（新终端）
cd frontend
npm run dev                     # http://localhost:5173
```

### 3. 使用 Docker 启动完整基础设施（可选）

如果需要使用 PostgreSQL、Redis、MinIO 的完整环境：

```bash
# 启动基础设施
docker-compose up -d

# 然后按照上面的步骤启动后端和前端
```

## 📁 项目结构

```
pcb_coolsim_v0.5/
├── 00-PRD/                     # 产品需求文档
├── 01-系统级-Spec/             # 系统架构设计
├── 02-模块级-Spec/             # 10个功能模块规范
├── 03-接口级-Spec/             # API 接口文档
├── 04-实现级-Spec/             # 算法与实现细节
├── 05-UI-UX-设计/              # UI 设计文档
├── 06-测试文档/                # 测试用例
├── backend/                    # Django 后端
│   ├── apps/
│   │   ├── accounts/           # 账户与权限管理
│   │   ├── projects/           # 项目、建筑、楼层管理
│   │   ├── calculation/        # 静态冷量计算（核心）
│   │   ├── simulation/         # 动态仿真
│   │   ├── forecast/           # 负荷预测
│   │   ├── conversation/       # 对话式数据采集
│   │   ├── exports/            # 报告导出
│   │   └── common/             # 公共模块
│   ├── config/                 # Django 配置
│   └── manage.py
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── pages/              # 页面组件
│   │   ├── components/         # 业务组件
│   │   ├── api/                # API 客户端
│   │   ├── router/             # 路由配置
│   │   └── theme/              # 主题配置
│   └── package.json
└── docker-compose.yml          # 基础设施配置
```

## 💻 开发指引

### 前端开发

```bash
cd frontend

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test

# 代码检查
npm run lint
```

### 后端开发

```bash
cd backend
.venv\Scripts\activate          # 激活虚拟环境

# 运行开发服务器
python manage.py runserver

# 创建数据库迁移
python manage.py makemigrations

# 应用数据库迁移
python manage.py migrate

# 运行测试
pytest

# 代码格式化
black .
isort .
```

### 常用开发命令速查

| 操作 | 前端 | 后端 |
|------|------|------|
| 启动开发服务器 | `npm run dev` | `python manage.py runserver` |
| 安装依赖 | `npm install` | `pip install -r requirements-dev.txt` |
| 运行测试 | `npm run test` | `pytest` |
| 代码检查 | `npm run lint` | `flake8` |

## ❓ 常见问题

### Q: Docker 拉取镜像超时怎么办？
A: 可以使用国内镜像源，或者直接使用开发环境配置的 SQLite 数据库，不需要 Docker 基础设施。

### Q: 前端无法访问后端 API？
A: 检查：
1. 后端是否在 `http://localhost:8000` 运行
2. 前端 Vite 代理配置是否正确
3. 浏览器控制台是否有 CORS 错误

### Q: 数据库迁移失败？
A:
1. 确保已激活虚拟环境
2. 删除 `db.sqlite3` 文件重新初始化
3. 运行 `python manage.py migrate`

### Q: 在哪里查看 API 文档？
A: 
- 后端启动后访问 `http://localhost:8000/api/` 可以看到 DRF 的可浏览 API
- 详细的接口契约在 `03-接口级-Spec/` 目录

## 📚 更多文档

- 详细需求：`00-PRD/`
- 系统设计：`01-系统级-Spec/`
- 模块规范：`02-模块级-Spec/`
- 接口文档：`03-接口级-Spec/`
- 开发规范：`CLAUDE.md`

## 📄 许可证

私有项目
