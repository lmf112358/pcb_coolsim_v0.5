# PCB-CoolSim v0.5.1 测试报告（TDD 完整版）

| 项目 | PCB-CoolSim（PCB 工厂冷量仿真平台） |
|------|------|
| 分支 | `feat/code-scaffold` |
| 最新提交 | `c38e6b3 test(tdd): 第十二批 Tab4+5+6` |
| 测试日期 | 2026-07-15 |
| 后端 | pytest 8.2 + pytest-django 4.8 + pytest-cov 5.0 |
| 前端 | Vitest + React Testing Library + jsdom |
| 环境 | Python 3.13 / Django 5.0.6 / Node 24 / SQLite(in-memory) |

---

## 一、执行结果总览

| 指标 | 后端 | 前端 | 合计 |
|------|:----:|:----:|:----:|
| **用例总数** | 143 | 53 | **196** |
| **通过** | 143 ✅ | 53 ✅ | **196 ✅** |
| **失败** | 0 | 0 | **0** |
| **通过率** | 100% | 100% | **100%** |
| **覆盖率** | 97% | — | — |

---

## 二、前端测试明细（53 测试，10 文件）

| 组件 | 用例 | PRD |
|------|:----:|-----|
| Login | 4 | F1-001~006 |
| Workbench 6 Tab | 5 | F2-001~008 |
| MapHome | 5 | F1-007~014 |
| Settings 4 Tab | 4 | F9-001~018 |
| Tab1 BasicConfig | 7 | F2-001~020 |
| Tab2 StaticCalc | 6 | F4-001~033 |
| Tab3 LoadAnalysis | 6 | F5-001~007 |
| Tab4 DynamicSim | 5 | F6-001~023 |
| Tab5 View2D | 5 | F7-017~024 |
| Tab6 Forecast | 6 | F10-001~021 |

---

## 三、TDD 流程总结（12 批迭代）

| 批次 | 模块 | 用例 |
|------|------|:----:|
| 1-7 后端 | F1~F10 全模块 | 143 |
| 8-12 前端 | 4 页面 + 6 Tab 业务组件 | 53 |
| **合计** | | **196** |

---

## 四、已知限制

| # | 项目 | 优先级 |
|---|------|--------|
| 1 | 2D 编辑器 Canvas 组件（Fabric.js） | P2 |
| 2 | 对话采集页三栏 Codex 布局 | P2 |
| 3 | 集成测试（PG+TimescaleDB） | P2 |
| 4 | NF-SAC-04 性能基准 | P1 |
| 5 | PRD 测试数据精度基准 | P1 |
| 6 | ECharts 图表深度集成 | P2 |

---

**报告生成时间**：2026-07-15
**测试执行**：自动化（pytest + Vitest）
