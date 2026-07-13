# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PCB-CoolSim is a web-based platform for calculating and simulating cooling loads in PCB manufacturing factories. It replaces manual Excel-based calculations with an automated, visual, collaborative tool.

**Core Goals:**
- Static Load Calculation: Design-day cooling load with < 0.1% deviation
- Dynamic Simulation: 8760-hour annual simulation with weather data, < 1% deviation
- 2D Visualization: Heatmap visualization of load distribution
- Report Generation: PDF, Excel, CSV exports

**Target Users:** HVAC Engineers, Project Managers, System Administrators

---

## 文档语言规范

**重要：所有文档必须使用中文撰写**

- 代码注释使用中文
- README、PRD、设计文档等所有文档使用中文
- API 文档和说明使用中文
- 测试文档和用户故事使用中文
- Git 提交信息和 PR 描述使用中文
- 错误信息和日志使用中文（面向用户的内容）
- 变量名、函数名、类名使用英文（代码规范要求）
- 技术术语可使用英文（如 React, Django, PostgreSQL 等）

**原则：** 这是一个面向中国用户的项目，所有文档和界面文字都应该使用中文，以确保团队成员和用户能够顺畅地理解项目。

---

## Tech Stack

### Frontend
- **React 18** + TypeScript + Vite 5
- **Ant Design 5** for UI components
- **React Query 5** for server state management
- **React Context** for UI state
- **Leaflet** for geographic maps
- **Fabric.js** for 2D canvas editor
- **ECharts** for charts and visualizations

### Backend
- **Django 5** + Django REST Framework (DRF)
- **Celery 5** for async task processing
- **PostgreSQL 16** with TimescaleDB extension
- **Redis 7** for caching and Celery broker
- **MinIO/S3** for file storage
- **Nginx** for reverse proxy and load balancing

---

## Essential Commands

### Backend Development

```bash
# Navigate to backend
cd backend

# Activate virtual environment (Windows)
venv\Scripts\activate
# (Linux/Mac): source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (port 8000)
python manage.py runserver

# Run Django migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Check migration status
python manage.py showmigrations

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Open database shell
python manage.py dbshell
```

### Backend Code Quality & Testing

```bash
# Format code (Black formatter)
black .

# Sort imports
isort .

# Lint (Flake8)
flake8

# Type checking (MyPy)
mypy .

# Run all unit tests
pytest

# Run specific test file
pytest tests/test_calculations.py

# Run specific test
pytest tests/test_calculations.py::test_enthalpy

# Run with coverage
pytest --cov=apps --cov-report=html

# Run integration tests
pytest tests/integration/
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server (port 3000)
npm run dev

# TypeScript type checking
npm run type-check

# Lint (ESLint)
npm run lint

# Format (Prettier)
npm run format

# Build for production
npm run build

# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

### Background Services

```bash
# Start Redis
redis-server

# Verify Redis is running
redis-cli ping  # Should return: PONG

# Start Celery worker (in backend/)
celery -A config worker -l info

# Start Celery beat for scheduled tasks (optional)
celery -A config beat -l info
```

### Docker

```bash
# Start all services in development mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f <service>
```

---

## Architecture Overview

### System Layers

```
Browser (React SPA)
        ↓ HTTPS
Nginx (Reverse Proxy + SSL + Static Files)
        ↓
Django API Server + Celery Workers
        ↓
PostgreSQL + Redis + MinIO
```

### Backend Django Apps

- **accounts/**: User authentication (JWT), role-based access control
- **projects/**: Core business entities (Project → Building → Floor → Room hierarchy)
- **calculations/**: Calculation engine (static load, dynamic simulation, preview)
- **weather/**: Weather data fetching and storage (8760-hour data)
- **exports/**: PDF, Excel, CSV report generation
- **settings/**: System configuration and templates

### Frontend Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # 5 main pages (Login, Map, Workbench, 2D Editor, Settings)
│   ├── hooks/           # Custom React hooks (data fetching, auth, state)
│   ├── services/        # API client services
│   ├── stores/          # State management (React Query + Context)
│   ├── types/           # TypeScript interfaces and types
│   └── utils/           # Utility functions
```

### Key Backend Files

| File | Purpose |
|------|---------|
| `backend/config/settings.py` | Django configuration |
| `backend/config/urls.py` | URL routing and endpoint registration |
| `backend/apps/*/models.py` | Database models (Project, Building, Floor, Room) |
| `backend/apps/*/views.py` | API endpoints and request handling |
| `backend/apps/*/serializers.py` | Data validation and transformation |
| `backend/apps/calculations/engine.py` | Core calculation logic |

### Key Frontend Files

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Main app component and routing |
| `frontend/src/pages/` | Page components (5 pages) |
| `frontend/src/services/api.ts` | API client and endpoint definitions |
| `frontend/src/types/` | TypeScript interfaces |
| `frontend/src/hooks/` | Custom hooks for data fetching |

---

## API Endpoints

**Base URL:** `/api/v1/`

### Authentication
- `POST /auth/login/` - Login and get JWT tokens
- `POST /auth/refresh/` - Refresh access token
- `POST /auth/logout/` - Invalidate tokens

### Projects & Hierarchy
- `GET /projects/` - List projects
- `POST /projects/` - Create project
- `GET /projects/{id}/` - Get project details
- `GET /buildings/` - List buildings
- `GET /floors/` - List floors
- `GET /rooms/` - List rooms

### Calculations
- `POST /rooms/{id}/calculate-static/` - Calculate static load for a room
- `POST /calculations/preview/` - Real-time calculation preview
- `POST /calculations/batch/` - Batch calculation for multiple rooms
- `POST /projects/{id}/simulate/` - Run dynamic simulation
- `GET /calculations/{id}/results/` - Get calculation results

---

## Code Style

### Python (Backend)

- **PEP 8** compliance
- **100 characters** max line length
- **4 spaces** indentation (no tabs)
- **Double quotes** for docstrings, **single quotes** for strings
- **Type hints** required for all public functions
- **Docstrings** with Args, Returns, Raises, and Example sections
- **Import order**: stdlib → third-party → local

```python
def calculate_enthalpy(
    temp: float,
    humidity: float,
    pressure: float
) -> float:
    """
    Calculate moist air enthalpy.

    Args:
        temp: Dry bulb temperature in °C
        humidity: Relative humidity in %
        pressure: Atmospheric pressure in Pa

    Returns:
        Enthalpy in kJ/kg

    Raises:
        ValueError: If inputs are out of physical range

    Reference:
        Calculation Specification Section 2.1
    """
    pass
```

### TypeScript (Frontend)

- **ESLint** + **Prettier** enforced
- **Type safety** required (strict TypeScript)
- **Functional components** with hooks
- **React Query** for data fetching and caching
- **Ant Design** components as primary UI library

### Django Models

- **Field ordering**: Primary Key → Foreign Keys → Regular Fields → Timestamps
- **Meta class**: `db_table`, `ordering`, `verbose_name`
- **`__str__` method** required
- **Properties** for computed values
- **Help text** on all fields

```python
class Room(models.Model):
    """
    Room model - the smallest calculation unit.

    Related: PRD F2-001, DB Design Section 4.4
    """

    id = models.BigAutoField(primary_key=True)
    floor = models.ForeignKey(
        'Floor',
        on_delete=models.CASCADE,
        related_name='rooms',
        help_text="Parent floor"
    )
    room_name = models.CharField(max_length=100, help_text="Room name")
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Area in m²"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'room'
        ordering = ['floor', 'room_name']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return self.room_name
```

---

## Calculation Engine

### Static Load Calculation (6-Step Pipeline)

1. **Internal Heat Sources**: Equipment, lighting, personnel
2. **Building Envelope**: Solar radiation, conduction, infiltration
3. **Ventilation Loads**: Fresh air sensible and latent
4. **Process Loads**: Production equipment and exhaust
5. **Safety Factor**: Confidence and adjustment factors
6. **Aggregation**: Zone → Room → Floor → Building

**Accuracy Target:** < 0.1% deviation from Excel reference

### Dynamic Simulation (Weather-Driven)

- Uses 8760-hour TMY (Typical Meteorological Year) weather data
- Coefficient method for load profiles
- Accounts for thermal mass and thermal lag
- Generates load duration curves

**Accuracy Target:** < 1% deviation from reference script

### Real-time Preview

- Lightweight calculation for instant feedback
- Simplified formulas (no full 8760h simulation)
- Uses current weather conditions
- Response time: < 500ms

---

## Testing Philosophy

### Test Coverage Targets

| Test Type | Coverage Target |
|-----------|-----------------|
| Unit Tests | 80% |
| Integration Tests | 70% |
| E2E Tests | 60% |

### Calculation Validation

- **Static load**: Compare with Excel reference (< 0.1% deviation)
- **Dynamic simulation**: Compare with reference script (< 1% deviation)
- **Performance**: Real-time preview < 500ms

**Reference Data:** PCB工厂测试数据_西北_西安.xlsx

### Test Structure

- `tests/unit/` - Individual function and class tests
- `tests/integration/` - API endpoint and database tests
- `tests/e2e/` - Full workflow tests (browser automation)
- `tests/performance/` - Load and performance tests

---

## SSD 文档工程：从 PRD 到代码的规范路径

### 核心理念

**SSD（Software Specification Document）方法论** 是连接产品需求与代码实现的桥梁。核心原则：

- **PRD 是唯一需求源**：所有功能必须追溯到 PRD 中的需求条目（F1-001, F2-001, 等）
- **Spec 是开发契约**：开发人员只能按照 Spec 编写代码，不能"发挥"
- **四层 Spec 结构**：系统级 → 模块级 → 接口级 → 实现级
- **双向可追溯**：PRD → Spec → Code → Test，任何变更必须全链路同步

### Spec 层次结构

```
PRD（产品需求文档）── 唯一需求源
  ↓ 需求条目映射
00-PRD/
  ├── README.md（PRD 索引）
  └── PRD_v0.5.1.md（产品需求文档）
  ↓ 系统分解
01-系统级-Spec/（System Specification）
  ├── 系统架构设计.md
  ├── 数据库设计.md
  └── API 总览.md
  ↓ 模块分解
02-模块级-Spec/（Module Specification）
  ├── 模块-01-账户与项目管理.md
  ├── 模块-02-用户数据采集.md
  ├── 模块-03-2D可视化标注.md
  ├── 模块-04-静态冷量计算.md
  ├── 模块-05-负荷分析与冷站配置.md
  ├── 模块-06-动态仿真负荷计算.md
  ├── 模块-07-8760可视化与基础验证.md
  ├── 模块-08-报告与数据导出.md
  ├── 模块-09-系统设置与全局交互.md
  └── 模块-10-负荷预测.md
  ↓ 接口细化
03-接口级-Spec/（Interface Specification）
  ├── API/（API 详细设计）
  ├── 数据库/（数据库详细设计）
  └── 前端组件/（前端组件规范）
  ↓ 实现指导
04-实现级-Spec/（Implementation Specification）
  ├── 计算逻辑/（计算算法实现）
  ├── 前端实现/（前端实现规范）
  ├── 后端实现/（后端实现规范）
  └── 代码模板/（代码模板）
```

### 文档体系结构

```
pcb_coolsim_v0.5_fuben/
├── 00-PRD/（L0：需求层）
├── 01-系统级-Spec/（L1：架构层）
├── 02-模块级-Spec/（L2：模块层）
├── 03-接口级-Spec/（L3：接口层）
├── 04-实现级-Spec/（L4：实现层）
├── 05-UI-UX-设计/（设计层）
├── 06-测试文档/（测试层）
├── 07-质量保障/（质量层）
├── 08-运维文档/（运维层）
├── 09-参考文档/（参考层）
├── 10-管理文档/（管理层）
└── config/（配置层）
```

### 可追溯性矩阵

每个需求条目必须建立完整的追溯链：

| PRD 需求 | Spec 文档 | 测试用例 | 状态 |
|----------|----------|----------|------|
| F2-001 | module-01-account.md Section 2 | TC-AUTH-001 | ✅ |
| F2-002 | module-02-data-collection.md Section 3 | TC-DATA-001 | ✅ |
| F4-001 | module-04-static-calculation.md Section 4 | TC-CALC-001 | ✅ |

**追溯规则：**
- 每个 PRD 需求必须有对应的 Spec 文档
- 每个 Spec 必须有对应的测试用例
- 任何变更必须更新整个追溯链
- 缺失追溯的需求不能进入开发

### Spec 编写规范

#### 1. 系统级 Spec 模板

```markdown
# 系统架构设计

> PRD 引用：F1-001, F1-002, F2-001
> 版本：1.0
> 状态：Baseline

## 1. 需求概述
[对应 PRD 中的需求描述]

## 2. 架构设计
[系统架构图、技术选型、设计原则]

## 3. 数据流设计
[数据流向、存储方案、缓存策略]

## 4. 安全设计
[认证授权、数据加密、安全防护]

## 5. 部署架构
[部署方案、环境要求、扩展策略]
```

#### 2. 模块级 Spec 模板

```markdown
# 模块 04：静态冷量计算

> PRD 引用：F4-001, F4-002, F4-003
> 版本：1.0
> 状态：Baseline

## 1. 需求概述
### 1.1 PRD 需求条目
| PRD ID | 需求描述 | 优先级 |
|--------|----------|--------|
| F4-001 | [需求描述] | P0 |
| F4-002 | [需求描述] | P1 |

## 2. 模块设计
### 2.1 功能职责
[模块的核心功能和边界]

### 2.2 数据模型
[模块涉及的数据库表、字段、关系]

### 2.3 计算逻辑
[详细的计算公式、步骤、算法]

## 3. API 设计
### 3.1 接口列表
| 方法 | 路径 | 功能 | PRD 引用 |
|------|------|------|----------|
| POST | /rooms/{id}/calculate-static/ | 静态冷量计算 | F4-001 |

### 3.2 请求/响应格式
[详细的 JSON 格式、字段说明、校验规则]

## 4. 测试用例
### 4.1 单元测试
| 测试 ID | 测试场景 | 预期结果 | PRD 引用 |
|---------|----------|----------|----------|
| TC-CALC-001 | [测试场景] | [预期结果] | F4-001 |

### 4.2 集成测试
[集成测试场景和预期结果]

## 5. 验收标准
[可量化的验收标准，对应 PRD 目标 G2]
```

#### 3. 接口级 Spec 模板

```markdown
# API：静态冷量计算

> PRD 引用：F4-001
> 模块引用：module-04-static-calculation.md
> 版本：1.0

## 1. 接口概述
- **路径**: `POST /api/v1/rooms/{room_id}/calculate-static/`
- **功能**: 计算指定功能区域的静态冷负荷
- **认证**: 需要 JWT Token

## 2. 请求规范
### 2.1 路径参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| room_id | int | 是 | 功能区域 ID |

### 2.2 请求体
```json
{
  "temperature_setpoint": 26.0,
  "humidity_setpoint": 55.0,
  "equipment_load": 100.0,
  "lighting_load": 50.0,
  "occupancy_load": 20.0
}
```

### 2.3 字段说明
| 字段 | 类型 | 必填 | 说明 | 校验规则 |
|------|------|------|------|----------|
| temperature_setpoint | float | 是 | 设定温度（℃） | 范围：18.0-30.0 |
| humidity_setpoint | float | 是 | 设定湿度（%） | 范围：40-70 |
| equipment_load | float | 是 | 设备冷量（W/m²） | ≥ 0 |

## 3. 响应规范
### 3.1 成功响应（200 OK）
```json
{
  "code": 200,
  "message": "计算成功",
  "data": {
    "room_id": 1,
    "static_load": 15000.5,
    "load_components": {
      "equipment": 8000.0,
      "lighting": 3000.0,
      "occupancy": 2000.0,
      "envelope": 1500.5,
      "ventilation": 500.0
    },
    "calculated_at": "2026-07-10T10:30:00Z"
  }
}
```

### 3.2 错误响应（400 Bad Request）
```json
{
  "code": 400,
  "message": "参数校验失败",
  "errors": {
    "temperature_setpoint": ["温度设定值超出有效范围（18.0-30.0）"]
  }
}
```

## 4. 计算逻辑
[对应的计算公式、精度要求、参考规范]

## 5. 测试用例
| 测试 ID | 请求数据 | 预期结果 | PRD 引用 |
|---------|----------|----------|----------|
| TC-API-CALC-001 | [请求数据] | [预期响应] | F4-001 |
```

### 文档工程最佳实践

#### 1. 文档分层原则

| 层次 | 文档类型 | 职责 | 维护者 |
|------|----------|------|--------|
| L0 | PRD | 需求定义 | 产品经理 |
| L1 | 系统级 Spec | 架构设计 | 架构师 |
| L2 | 模块级 Spec | 模块设计 | 开发负责人 |
| L3 | 接口级 Spec | 接口定义 | 开发人员 |
| L4 | 实现级 Spec | 实现细节 | 开发人员 |

#### 2. 文档关联原则

- **单向依赖**：下层文档必须引用上层文档
- **版本同步**：文档版本号与 PRD 版本号对应
- **变更追踪**：任何变更必须记录在变更日志中
- **交叉引用**：使用 `> PRD 引用：F2-001` 格式建立链接

#### 3. 文档质量检查清单

- [ ] 每个需求条目都有对应的 Spec
- [ ] 每个 Spec 都有对应的测试用例
- [ ] API 设计覆盖所有 PRD 功能
- [ ] 数据库设计匹配 PRD 数据需求
- [ ] 计算逻辑符合计算规范
- [ ] 验收标准可量化、可测试
- [ ] 无歧义、无矛盾、无遗漏

### 确保代码不跑偏的机制

#### 1. Spec 优先原则

```bash
# 代码开发流程
1. 阅读 PRD 相关需求条目
2. 查阅对应的 Spec 文档
3. 按照 Spec 编写代码
4. 运行 Spec 中定义的测试用例
5. 更新测试覆盖矩阵
```

#### 2. 代码追溯机制

在代码中添加追溯注释：

```python
def calculate_static_load(room_id: int) -> dict:
    """
    计算静态冷负荷

    PRD 引用：F4-001
    Spec 引用：module-04-static-calculation.md Section 3
    计算规范：冷量仿真核心计算规范.md Section 2.1
    """
    pass
```

#### 3. 测试覆盖检查

```bash
# 检查测试覆盖
pytest --cov=apps --cov-report=html

# 生成测试覆盖矩阵
python scripts/generate_coverage_matrix.py
```

#### 4. 代码审查检查点

- [ ] 代码是否符合 Spec 设计
- [ ] 是否有遗漏的需求
- [ ] 计算逻辑是否与规范一致
- [ ] 错误处理是否完善
- [ ] 性能是否达标

### 文档工程重构检查清单

#### 第一阶段：文档完整性（已完成 ✅）

- [x] PRD 文档基线化
- [x] 系统架构设计完成
- [x] 数据库设计完成
- [x] API 设计完成
- [x] 模块设计完成（10 个模块）

#### 第二阶段：Spec 完善性（当前阶段 🔄）

- [ ] 补充接口级 Spec（API 详细设计）
- [ ] 补充实现级 Spec（算法实现细节）
- [ ] 建立追溯性矩阵（PRD → Spec → Test）
- [ ] 编写测试用例（基于 Spec）
- [ ] 代码模板和示例

#### 第三阶段：质量验证（下一阶段 ⏳）

- [ ] Spec 审查（无歧义、无矛盾、无遗漏）
- [ ] 代码实现对照 Spec 检查
- [ ] 测试覆盖矩阵验证
- [ ] 验收标准量化检查

---

## Development Workflow

### Quality Gates (5 Phases)

1. **Requirements Gate**: PRD complete, reviewed, approved
2. **Design Gate**: Architecture, API, UI design complete, no contradictions
3. **Implementation Gate**: Code complete, tests passing
4. **Testing Gate**: All tests passed, defects resolved
5. **Release Gate**: All gates passed, documentation complete

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-feature

# Work and commit
git commit -m "feat(scope): description"

# Create PR to main
# After review and approval, merge
```

---

## Key Documentation

### 核心文档（L0-L1）

| Document | Location | When to Reference |
|----------|----------|-------------------|
| PRD v0.5.1 | `00-PRD/PRD_v0.5.1.md` | Understanding feature requirements |
| 系统架构设计 | `01-系统级-Spec/系统架构设计.md` | Understanding 4-layer architecture |
| 数据库设计 | `01-系统级-Spec/数据库设计.md` | Database schema and relationships |
| API 总览 | `01-系统级-Spec/API总览.md` | API endpoint details (60+ endpoints) |

### 模块级 Spec（L2）

| Document | Location | When to Reference |
|----------|----------|-------------------|
| 模块 01：账户与项目管理 | `02-模块级-Spec/模块-01-账户与项目管理.md` | Auth and RBAC implementation |
| 模块 04：静态冷量计算 | `02-模块级-Spec/模块-04-静态冷量计算.md` | 6-step calculation pipeline |
| 模块 06：动态仿真负荷计算 | `02-模块级-Spec/模块-06-动态仿真负荷计算.md` | Weather-driven simulation |

### 接口级 Spec（L3）

| Document | Location | When to Reference |
|----------|----------|-------------------|
| API 接口详细设计 | `03-接口级-Spec/API/` | API endpoint implementation |
| 数据库详细设计 | `03-接口级-Spec/数据库/` | Database implementation |
| 前端组件规范 | `03-接口级-Spec/前端组件/` | Frontend component implementation |

### 实现级 Spec（L4）

| Document | Location | When to Reference |
|----------|----------|-------------------|
| 静态冷量计算实现 | `04-实现级-Spec/计算逻辑/静态冷量计算实现.md` | Calculation formulas |
| 计算逻辑实现 | `04-实现级-Spec/计算逻辑/` | Algorithm implementation |
| 代码模板 | `04-实现级-Spec/代码模板/` | Code templates |

### 支持文档

| Document | Location | When to Reference |
|----------|----------|-------------------|
| 设计系统 | `05-UI-UX-设计/设计系统.md` | UI components and design tokens |
| 页面设计 | `05-UI-UX-设计/页面设计/页面设计总览.md` | Page layouts and interactions |
| 测试策略 | `06-测试文档/测试策略.md` | Testing approach and targets |
| 测试计划 | `06-测试文档/测试计划.md` | Test cases (100+ cases) |
| 质量门禁 | `07-质量保障/质量门禁.md` | Gate checklists and criteria |
| 追溯性矩阵 | `07-质量保障/追溯性矩阵.md` | PRD → Spec → Test mapping |
| 部署指南 | `08-运维文档/部署指南.md` | Deployment procedures |
| 监控指南 | `08-运维文档/监控指南.md` | Monitoring and alerting |
| 术语表 | `09-参考文档/术语表.md` | Terminology and context |
| ADR | `09-参考文档/架构决策记录/` | Architecture decisions |
| CLAUDE.md | `CLAUDE.md` | Claude Code guidance |

### 快速导航

| Role | Start With | Then Reference |
|------|------------|----------------|
| 产品经理 | `00-PRD/README.md` | PRD, User Stories |
| 架构师 | `01-系统级-Spec/README.md` | System Architecture, ADR |
| 后端开发 | `02-模块级-Spec/README.md` | Module Spec, API, Calculation Logic |
| 前端开发 | `05-UI-UX-设计/README.md` | Design System, Page Designs, Components |
| 测试人员 | `06-测试文档/README.md` | Test Strategy, Test Plan, Traceability Matrix |
| 运维工程师 | `08-运维文档/README.md` | Deployment, Monitoring, Troubleshooting |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 500ms |
| Error Rate | < 0.1% |
| Availability | 99.9% |
| Calculation Time (100 rooms) | < 5s |
| Calculation Time (1000 rooms) | < 30s |
| Real-time Preview | < 500ms |

---

## Common Issues & Debugging

### Database Connection

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Redis Connection

```bash
# Test Redis connection
redis-cli ping

# Restart Redis
redis-server
```

### Port Conflicts

```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### CORS Errors

Check `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
]
```

### Migration Issues

```bash
# View migration status
python manage.py showmigrations

# Fake migration (use carefully)
python manage.py migrate app_name 0002 --fake
```

---

## Quick Navigation

- **Start here:** `README.md` for project overview
- **Setup:** `docs/glossary/DEVELOPER_QUICKSTART.md` for 30-minute guide
- **Architecture:** `design/architecture/system-architecture.md` for 4-layer design
- **API:** `design/architecture/api-design.md` for endpoint details
- **Calculations:** `design/modules/module-04-static-calculation.md` for formulas
- **Code Style:** `docs/glossary/CODE_STYLE_GUIDE.md` for conventions
- **Testing:** `tests/test-strategy.md` for testing approach

---

## Important Notes

1. **Calculation accuracy is critical** - All calculations must match reference data within tolerance
2. **Python 3.11+ required** - Use latest features and type hints
3. **Node.js 18+ required** - For frontend build tools
4. **PostgreSQL 16+ required** - For TimescaleDB support
5. **Redis 7+ required** - For Celery broker and caching
6. **Follow quality gates** - All 5 phases must pass before release
7. **Traceability matters** - Link code to PRD requirement IDs (PRD: F2-001, etc.)

---

## Spec 构建路线图

### 当前状态

```
阶段 1：PRD 基线化 ✅
  ├── PRD v0.5.1 已完成
  ├── 所有需求条目已定义（F1-001 ~ F10-XXX）
  └── 验收标准已明确（G1 ~ G12）

阶段 2：Spec 文档工程 🔄（当前）
  ├── 系统级 Spec ✅
  │   ├── 系统架构设计 ✅
  │   ├── 数据库设计 ✅
  │   └── API 总览 ✅
  ├── 模块级 Spec ✅
  │   ├── 模块 01-10 设计文档 ✅
  │   └── 模块间接口定义 ⏳
  ├── 接口级 Spec ⏳
  │   ├── API 详细设计 ⏳
  │   ├── 前端组件规范 ⏳
  │   └── 数据库表结构细化 ⏳
  └── 实现级 Spec ⏳
      ├── 计算逻辑实现细节 ⏳
      ├── 算法伪代码 ⏳
      └── 代码模板 ⏳

阶段 3：代码开发（下一步）
  ├── 基于 Spec 编写代码
  ├── 测试驱动开发
  └── 代码审查
```

### Spec 文档构建优先级

#### 第一优先级（核心 Spec）

1. **接口级 API 设计**（api/*.md）
   - 所有 API 端点详细规范
   - 请求/响应格式定义
   - 错误码和异常处理
   - PRD 引用：F2-001 ~ F10-XXX

2. **前端组件规范**（ui/components/*.md）
   - 核心组件接口定义
   - 状态管理规范
   - 数据流设计
   - PRD 引用：F3-001, F7-001

3. **数据库表结构细化**（数据库设计文档.md Section 4+）
   - 表结构详细定义
   - 索引设计
   - 分区策略
   - PRD 引用：F1-001, F2-001

#### 第二优先级（实现细节）

4. **计算逻辑实现细节**
   - 静态冷量计算算法
   - 动态仿真算法
   - 8760h 数据处理
   - PRD 引用：F4-001, F6-001, F7-001

5. **前端页面实现规范**
   - 页面组件结构
   - 状态管理流程
   - API 调用时机
   - PRD 引用：F3-001 ~ F9-001

6. **后端实现规范**
   - 服务层设计
   - 数据访问层设计
   - 异步任务设计
   - PRD 引用：F2-001 ~ F10-XXX

#### 第三优先级（质量保障）

7. **测试用例设计**
   - 单元测试用例
   - 集成测试用例
   - E2E 测试用例
   - 性能测试用例

8. **追溯性矩阵**
   - PRD → Spec 映射
   - Spec → Test 映射
   - Test → Code 映射

9. **代码模板和示例**
   - 模型层代码模板
   - 服务层代码模板
   - 控制器层代码模板
   - 前端组件模板

### Spec 构建标准

#### 完整性检查清单

```markdown
## 系统级 Spec ✅
- [x] 系统架构设计（system-architecture.md）
- [x] 数据库设计（数据库设计文档.md）
- [x] API 总览（api-design.md）

## 模块级 Spec ✅
- [x] 模块 01：账户与项目管理（module-01-account.md）
- [x] 模块 02：用户数据采集（module-02-data-collection.md）
- [x] 模块 03：2D 可视化标注（module-03-2d-visualization.md）
- [x] 模块 04：静态冷量计算（module-04-static-calculation.md）
- [x] 模块 05：负荷分析与冷站配置（module-05-load-analysis.md）
- [x] 模块 06：动态仿真负荷计算（module-06-dynamic-simulation.md）
- [x] 模块 07：8760 可视化与基础验证（module-07-8760-visualization.md）
- [x] 模块 08：报告与数据导出（module-08-report-export.md）
- [x] 模块 09：系统设置与全局交互（module-09-system-settings.md）
- [x] 模块 10：负荷预测（module-10-load-forecast.md）

## 接口级 Spec ⏳
- [ ] API 详细设计（api/auth-api.md）
- [ ] API 详细设计（api/project-api.md）
- [ ] API 详细设计（api/room-api.md）
- [ ] API 详细设计（api/calculation-api.md）
- [ ] API 详细设计（api/export-api.md）
- [ ] 前端组件规范（ui/components/*.md）
- [ ] 数据库表结构细化

## 实现级 Spec ⏳
- [ ] 计算逻辑实现细节
- [ ] 算法伪代码
- [ ] 代码模板
- [ ] 测试用例设计
- [ ] 追溯性矩阵
```

#### 质量检查清单

```markdown
## PRD 覆盖性检查
- [ ] 所有 PRD 需求条目都有对应的 Spec
- [ ] 所有 PRD 验收标准都在 Spec 中有定义
- [ ] 无遗漏的需求

## Spec 质量检查
- [ ] 无歧义（每个术语都有明确的定义）
- [ ] 无矛盾（不同 Spec 之间一致）
- [ ] 完整性（覆盖所有场景和异常）
- [ ] 可测试性（验收标准可量化）
- [ ] 可追溯性（每个需求都能追溯到 PRD）

## 技术可行性检查
- [ ] 架构设计可行
- [ ] 数据库设计合理
- [ ] API 设计符合 RESTful 规范
- [ ] 计算逻辑精度达标
- [ ] 性能目标可实现
```

### 开发阶段 Spec 使用流程

#### 1. 开发前准备

```bash
# 1. 阅读 PRD 相关需求
grep "F4-001" PCB工厂冷源仿真平台_PRD_v0.5.1_修订版.md

# 2. 查阅模块级 Spec
cat design/modules/module-04-static-calculation.md

# 3. 查阅接口级 Spec
cat docs/api/calculation-api.md

# 4. 查阅实现级 Spec
cat 冷量仿真核心计算规范.md

# 5. 确认测试用例
grep "TC-CALC-001" tests/test-plan.md
```

#### 2. 开发中检查

```python
# 代码追溯注释
def calculate_static_load(room_id: int) -> dict:
    """
    计算静态冷负荷

    PRD 引用：F4-001
    Spec 引用：module-04-static-calculation.md Section 3
    接口引用：calculation-api.md Section 2
    计算规范：冷量仿真核心计算规范.md Section 2.1
    测试用例：TC-CALC-001, TC-CALC-002
    """
    pass
```

#### 3. 开发后验证

```bash
# 1. 运行单元测试
pytest tests/unit/test_calculations.py -v

# 2. 运行集成测试
pytest tests/integration/test_calculation_api.py -v

# 3. 检查测试覆盖
pytest --cov=apps --cov-report=html

# 4. 更新追溯性矩阵
python scripts/update_traceability_matrix.py
```

### Spec 工程关键原则

1. **PRD 是圣经**：所有需求必须追溯到 PRD，不能自行添加需求
2. **Spec 是契约**：开发必须按照 Spec 编写代码，不能偏离
3. **测试是验证**：测试必须基于 Spec 设计，不能遗漏场景
4. **文档是资产**：任何变更必须更新整个追溯链，不能文档不同步
5. **质量是底线**：所有 Spec 必须通过质量检查，不能上线不完整的功能

### 下一步行动项

#### 立即行动（本周）

1. **补充接口级 Spec**
   - 为每个模块编写详细的 API 设计文档
   - 包括请求/响应格式、错误处理、性能要求

2. **建立追溯性矩阵**
   - 创建 PRD → Spec → Test 映射表
   - 确保每个需求条目都有对应的 Spec 和 Test

3. **编写测试用例**
   - 基于 Spec 设计单元测试
   - 基于 API 设计集成测试

#### 短期行动（下周）

4. **补充实现级 Spec**
   - 计算逻辑的详细算法说明
   - 算法伪代码
   - 代码模板和示例

5. **质量检查**
   - Spec 完整性检查
   - PRD 覆盖性检查
   - 无歧义、无矛盾、无遗漏检查

#### 中期行动（两周内）

6. **代码开发准备**
   - 代码模板准备
   - 测试框架搭建
   - CI/CD 配置

7. **团队培训**
   - SSD 方法论培训
   - Spec 使用流程培训
   - 代码追溯性培训

---

## 总结

**SSD 文档工程的核心目标**：

✅ **确保代码不跑偏** - 严格遵循 Spec 编写代码
✅ **保证需求不遗漏** - 建立完整的追溯性矩阵
✅ **质量可量化** - 定义明确的验收标准和测试用例
✅ **团队协作一致** - 统一的文档规范和开发流程

**当前状态**：PRD 已基线化，系统级和模块级 Spec 已完成，下一步是补充接口级和实现级 Spec，然后进入代码开发阶段。

**关键原则**：PRD 是唯一需求源，Spec 是开发契约，测试是验证手段，文档是团队资产。

---

## Agent skills

### Issue tracker

本仓库使用本地 Markdown 问题追踪器：issue 以文件形式存放在仓库内 `.scratch/<feature>/` 目录。工程技能（triage / qa / to-issues / wayfinder 等）读写本地文件，无需 GitHub 鉴权。详见 `docs/agents/issue-tracker.md`。

### Triage labels

采用五个默认分诊角色标签：`needs-triage` / `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`。详见 `docs/agents/triage-labels.md`。

### Domain docs

单上下文布局：根目录 `CONTEXT.md` 为领域词汇/上下文入口；架构决策记录（ADR）沿用现有 `09-参考文档/架构决策记录/` 目录（不另起 `docs/adr/`）。技能探索代码前先读 `CONTEXT.md` 与相关 ADR。详见 `docs/agents/domain.md`。

---

## 文档一致性规则（PRD 为唯一事实源）

> 本规则用于指导全量文档的维护与重构，遵循**奥卡姆剃刀原则**：不引入不必要的实体/表/章节；移除冗余；复用既有结构；PRD 变更后依赖文档必须同步。

### 1. 事实源与依赖方向
- **PRD（`00-PRD/PRD_v0.5.1.md`）是唯一需求与数据模型事实源**。
- 依赖链：PRD → 01-系统级-Spec → 02-模块级-Spec → 03-接口级-Spec → 04-实现级-Spec → 05-UI-UX-设计 → 06-测试文档 → 07-质量保障 → 08-运维文档 → 09-参考文档（术语表/ADR/用户故事） → 10-管理文档。
- PRD 变更时，**下游所有文档必须同步**，不允许遗留断裂的交叉引用（章节号、表名、`SAC-xx`、附录 H）。

### 2. 当前必须向下游传播的事实增量（docs/prd-revision 分支，4 个提交）
- **模块五「冷站配置」已移除**（仅保留负荷分析）：所有 冷站配置 / 水蓄冷 / PID 相关描述须移除或收敛；`CLAUDE.md` Core Goals 中的 `Cooling Station Configuration` 须删除；相关 ADR（`09-参考文档/架构决策记录/ADR-0005-PID与水蓄冷范围.md`）须复核范围。
- **模块二新增「对话式采集」（§6.10）**：须在 API 总览、数据库设计、系统架构设计、相关模块 Spec、页面设计总览、测试策略/计划、用户故事、完成报告等处同步新增。
- **SOP 对齐既有数据字段**：对话采集六阶段（①项目基本信息[展示确认] ②冷冻水温度配置 ③建筑结构信息 ④功能区域参数 ⑤额外负荷信息 ⑥汇总预览与确认）与 `Project`/`WaterTempConfig`/`Building`/`Floor`/`Room`/`ExtraLoad`/`RoomCalcResult`/`LoadSummary` 严格对应；① 仅展示确认（项目创建时已在地图页关联气象）。
- **附录 H / SAC**：新增需求 ID 与数量须自洽（附录 H 合计 53 / P0:46, P1:6, P2:1）。

### 3. 奥卡姆剃刀约束
- 不新增未在 PRD 出现的实体/表/章节；确需补充时先在 `09-参考文档/架构决策记录/` 落 ADR。
- ADR 复用 `09-参考文档/架构决策记录/`，不另建 `docs/adr/`。
- 删除内容时同步清理所有引用，不留死链。
- 文档语言规范（见上文「文档语言规范」）：全部中文；代码标识符英文。

### 4. 一致性校验清单（每次文档改动后自检）
- [ ] 章节号、表名、`SAC-xx`、附录 H 引用自洽
- [ ] 数据模型表名与附录 E 一致
- [ ] 无与 PRD 矛盾的 stale 描述（如已移除的冷站配置）
- [ ] 新增功能在依赖链各层均有落点
