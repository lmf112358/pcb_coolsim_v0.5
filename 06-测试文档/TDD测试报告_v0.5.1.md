# PCB-CoolSim v0.5.1 测试报告（TDD 完整版）

| 项目 | PCB-CoolSim（PCB 工厂冷量仿真平台） |
|------|------|
| 分支 | `feat/code-scaffold` |
| 最新提交 | `746bc2e test(tdd): 第十批 Tab1 BasicConfig` |
| 测试日期 | 2026-07-15 |
| 后端框架 | pytest 8.2 + pytest-django 4.8 + pytest-cov 5.0 |
| 前端框架 | Vitest + React Testing Library + jsdom |
| 测试环境 | Python 3.13 / Django 5.0.6 / Node 24 / SQLite(in-memory) |

---

## 一、执行结果总览

| 指标 | 后端 | 前端 | 合计 |
|------|:----:|:----:|:----:|
| **用例总数** | 143 | 25 | **168** |
| **通过** | 143 ✅ | 25 ✅ | **168 ✅** |
| **失败** | 0 | 0 | **0** |
| **通过率** | 100% | 100% | **100%** |
| **覆盖率** | 97% | — | — |
| **结论** | 🟢 | 🟢 | 🟢 **全部通过** |

---

## 二、前端测试明细（25 测试，5 文件）

| 组件 | 测试文件 | 用例 | PRD |
|------|---------|:----:|-----|
| 登录页 | Login.test.tsx | 4 | F1-001~006 |
| 工作台 6 Tab | Workbench.test.tsx | 5 | F2-001~008 |
| 地图首页 | MapHome.test.tsx | 5 | F1-007~014 |
| 系统设置 | Settings.test.tsx | 4 | F9-001~018 |
| Tab1 基础配置 | BasicConfig.test.tsx | 7 | F2-001~020 |

---

## 三、TDD 流程总结（10 批迭代）

| 批次 | 模块 | 用例 |
|------|------|:----:|
| 1-7 后端 | F1~F10 全模块 API + services + models | 143 |
| 8 | 前端 Login + Workbench | 9 |
| 9 | 前端 MapHome + Settings | 9 |
| 10 | 前端 Tab1 BasicConfig | 7 |
| **合计** | | **168** |

---

## 四、已知限制

| # | 项目 | 优先级 |
|---|------|--------|
| 1 | 工作台 Tab2~Tab6 业务组件 | P1 |
| 2 | 2D 编辑器 Canvas 组件 | P2 |
| 3 | 对话采集页三栏 Codex 布局 | P2 |
| 4 | 集成测试（PG+TimescaleDB） | P2 |
| 5 | NF-SAC-04 性能基准 | P1 |
| 6 | PRD 测试数据精度基准 | P1 |

---

**报告生成时间**：2026-07-15
**测试执行**：自动化（pytest + Vitest）
