# PCB-CoolSim — PCB 工厂冷量仿真平台

基于 Web 的 PCB 制造工厂冷量计算与仿真平台，用自动化、可视化、可协作的工具替代传统手工 Excel 计算。

> 当前阶段：SSD 规范文档已完成（00~10 目录），进入代码开发。本仓库已搭建前后端骨架。

## 技术栈

- **前端**：React 18 + TypeScript + Vite + Ant Design 5 + React Query 5 + React Router
- **后端**：Django 5 + DRF + Celery 5 + SimpleJWT
- **数据库**：PostgreSQL 16 + TimescaleDB（逐时数据超表）
- **缓存/队列**：Redis 7
- **对象存储**：MinIO（底图 PDF / 导出文件）
- **计算库**：NumPy / Pandas / psychrolib（焓值，PRD §15）

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 24+
- Docker（可选，用于 PostgreSQL/Redis/MinIO）

### 2. 启动基础设施

```bash
# 复制环境变量
cp .env.example .env

# 启动 PostgreSQL+TimescaleDB / Redis / MinIO
docker-compose up -d
```

### 3. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements-dev.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver      # http://localhost:8000
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173（代理 /api 到 8000）
```

## 目录结构

```
pcb_coolsim_v0.5/
├── 00-PRD/                     # 产品需求文档（事实源）
├── 01-系统级-Spec/             # 系统级规范
├── 02-模块级-Spec/             # 模块级规范（10 个模块）
├── 03-接口级-Spec/             # 接口级规范（18 份接口文档）
├── 04-实现级-Spec/             # 实现级规范（算法/服务层/模板）
├── 05-UI-UX-设计/              # UI/UX 设计
├── 06-测试文档/ 07-质量保障/ 08-运维文档/ 09-参考文档/ 10-管理文档/
├── backend/                    # Django 后端
│   ├── config/                 # 项目配置（settings 分层 + celery）
│   ├── apps/                   # 业务应用（8 个，按 PRD 模块组织）
│   │   ├── accounts/           # 模块一：账户与权限
│   │   ├── projects/           # 模块二：项目/建筑/楼层/功能区域
│   │   ├── calculation/        # 模块四：静态冷量计算（核心）
│   │   ├── simulation/         # 模块六/七：动态仿真
│   │   ├── forecast/           # 模块十：负荷预测
│   │   ├── conversation/       # 模块二：对话式采集
│   │   ├── exports/            # 模块八：报告导出
│   │   └── common/             # 公共配置
│   └── manage.py
├── frontend/                   # React 前端
│   └── src/
│       ├── pages/              # 6 个页面
│       ├── router/             # 路由
│       ├── theme/              # 主题（工业蓝 + 工艺色）
│       ├── locales/            # i18n 中英文
│       └── api/                # API 客户端
└── docker-compose.yml          # 基础设施
```

## 开发指引

- 文档规范、命名基线、计算逻辑基线见 `CLAUDE.md`
- 各模块需求条目见 `02-模块级-Spec/`
- API 端点契约见 `03-接口级-Spec/`
- 核心计算算法见 `04-实现级-Spec/算法伪代码.md` 与 `backend/apps/calculation/services.py`

## 许可证

私有项目
