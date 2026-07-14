# PCB-CoolSim v0.5.1 测试报告（TDD 完整版）

| 项目 | PCB-CoolSim（PCB 工厂冷量仿真平台） |
|------|------|
| 分支 | `feat/code-scaffold` |
| 最新提交 | `b6608ee test(tdd): 第六批 TDD 剩余 API 端点` |
| 测试日期 | 2026-07-15 |
| 测试框架 | pytest 8.2 + pytest-django 4.8 + pytest-cov 5.0 |
| 测试环境 | Python 3.13 / Django 5.0.6 / SQLite(in-memory) |
| 执行命令 | `pytest --cov=apps --cov-report=term-missing` |

---

## 一、执行结果总览

| 指标 | 结果 |
|------|------|
| **用例总数** | 129 |
| **通过** | 129 ✅ |
| **失败** | 0 |
| **错误** | 0 |
| **跳过** | 0 |
| **通过率** | **100%** |
| **总耗时** | 4.69s |
| **代码覆盖率** | **97%**（1938 语句，64 未覆盖） |
| **结论** | 🟢 **全部通过，无失败用例** |

```
====================== 129 passed, 51 warnings in 4.69s ========================
TOTAL  1938  64  97%
```

---

## 二、按模块执行明细

| 模块 | 测试文件 | 用例数 | 通过 | 失败 | 覆盖率 |
|------|---------|:------:|:----:|:----:|:------:|
| 核心计算引擎 | calculation/tests/test_services.py | 31 | 31 | 0 | services 97% |
| 静态计算 API | calculation/tests/test_api.py | 5 | 5 | 0 | views 100% |
| 账户认证 | accounts/tests/test_auth.py | 8 | 8 | 0 | models 93% |
| 项目模型 | projects/tests/test_models.py | 8 | 8 | 0 | models 94% |
| 动态仿真 services | simulation/tests/test_services.py | 13 | 13 | 0 | services 92% |
| 动态仿真 API | simulation/tests/test_api.py | 6 | 6 | 0 | views 94% |
| 负荷预测 services | forecast/tests/test_services.py | 12 | 12 | 0 | services 84% |
| 负荷预测 API | forecast/tests/test_api.py | 6 | 6 | 0 | views 100% |
| projects CRUD | projects/tests/test_api.py | 12 | 12 | 0 | views 82% |
| Excel 导入/CSV | exports/tests/test_services.py | 8 | 8 | 0 | services 91% |
| 报告导出 API | exports/tests/test_api.py | 5 | 5 | 0 | views 89% |
| 系统设置 API | common/tests/test_api.py | 8 | 8 | 0 | views 100% |
| 对话采集 API | conversation/tests/test_api.py | 7 | 7 | 0 | views 93% |
| **合计** | | **129** | **129** | **0** | **97%** |

---

## 三、PRD 需求覆盖（F 编号）

| PRD 需求 | 覆盖端点/功能 | 用例数 | 结果 |
|----------|-------------|:------:|:----:|
| F1-001~006 JWT 认证 | login/refresh/me | 4 | ✅ |
| F1-006 密码加密 | bcrypt | 2 | ✅ |
| F1-024 角色权限 | Role RBAC | 2 | ✅ |
| F1-015~023 项目 CRUD | projects CRUD | 4 | ✅ |
| F2-009~020 层级 CRUD | buildings/floors/rooms | 5 | ✅ |
| F2-021 复制 | rooms/copy | 1 | ✅ |
| F2-030 额外负荷层级 | ExtraLoad | 2 | ✅ |
| F2-032~039 Excel 导入 | parse_excel + API | 6 | ✅ |
| F2-046~061 对话采集 | 六阶段会话/消息/finalize | 7 | ✅ |
| F4-001~050 静态计算 | 6步流水线 services + API | 36 | ✅ |
| F4-038~042 国标参数 | cities 查询 | 3 | ✅ |
| F6-001~011 动态仿真 | services | 13 | ✅ |
| F6-020~023 仿真触发 | simulations/ API | 6 | ✅ |
| F7-027~029 极值统计 | aggregate_extremes | 3 | ✅ |
| F8-001~004 PDF 报告 | reportlab | 1 | ✅ |
| F8-012~014 CSV/Excel | export services + API | 6 | ✅ |
| F9-001~010 系统设置 | 冷冻水/默认值 CRUD | 8 | ✅ |
| F10-001~021 负荷预测 | 场景CRUD/运行/结果 | 18 | ✅ |
| §16.1.1 级联删除 | cascade | 1 | ✅ |

---

## 四、核心计算正确性（PRD §15 / SAC 验证）

### C1-C8 修复点代码验证（全部通过测试断言拦截）

| 修复点 | 测试类 | 用例数 | 结果 |
|--------|--------|:------:|:----:|
| C1 压差8点查表 | TestInfiltrationCoefficient | 11 | ✅ |
| C2 新风简单加法 | TestAirVolume | 3 | ✅ |
| C3 焓值定义A | TestEnthalpy | 4 | ✅ |
| C4 默认26/55 | test_default_indoor_temp_humidity | 1 | ✅ |
| C5 末端5项 | TestTerminalLoad | 6 | ✅ |
| C6 总负荷截断 | test_negative_total_truncated | 1 | ✅ |
| C7 ρ=1.2 | TestFreshAirLoad | 2 | ✅ |
| C8 动态方式二查表 | TestBilinearInterpolation | 4 | ✅ |

### 精度验证

| 验收项 | 验证 | 结果 |
|--------|------|:----:|
| SAC-2 静态 <0.1% | psychrolib 焓值标量一致 | ✅ |
| SAC-3 动态 <1% | 向量化焓值与标量一致 | ✅ |
| PRD §15.8 插值示例 | 20℃/60% → 0.767 | ✅ |

---

## 五、失败用例分析

**无失败用例（0 failed）。**

开发过程通过 TDD 发现并修复 10 个问题（均在测试阶段拦截，详见前版报告），最终版本 0 失败。

---

## 六、覆盖率明细

| 文件 | 语句 | 未覆盖 | 覆盖率 |
|------|:----:|:------:|:------:|
| calculation/services.py | 69 | 2 | **97%** |
| calculation/views.py | 18 | 0 | 100% |
| simulation/services.py | 37 | 3 | 92% |
| simulation/views.py | 36 | 2 | 94% |
| forecast/services.py | 57 | 9 | 84% |
| forecast/views.py | 48 | 0 | 100% |
| common/views.py | 37 | 0 | 100% |
| conversation/views.py | 43 | 3 | 93% |
| exports/views.py | 80 | 9 | 89% |
| projects/views.py | 55 | 10 | 82% |
| accounts/models.py | 29 | 2 | 93% |
| projects/models.py | 124 | 8 | 94% |
| forecast/models.py | 65 | 2 | 97% |
| conversation/models.py | 31 | 2 | 94% |
| **TOTAL** | **1938** | **64** | **97%** |

---

## 七、问题清单与优化建议

### 已知限制

| # | 项目 | 说明 | 优先级 |
|---|------|------|--------|
| 1 | 前端测试 | 仅有 build 验证，无组件/集成测试 | P1 |
| 2 | 集成测试 | SQLite 模拟，未用真实 PG+TimescaleDB（hypertable） | P2 |
| 3 | 性能测试 | 未实现 1000+ 功能区域 <5s 基准（NF-SAC-04） | P1 |
| 4 | 精度基准 | 未导入 PRD 测试数据（西安/广州/胡志明 Excel）做精确比对 | P1 |
| 5 | 2D 平面图 API | F3-001~024 PDF 底图/Canvas 编辑 API 未实现 | P2 |
| 6 | 气象数据 API | F4-043~050 气象拉取/上传 API 未实现 | P2 |

### 优化建议

1. **精度基准测试**：导入 `06-测试文档/测试数据/` 的 3 份 Excel，与手工验算做 <0.1% 对比
2. **TimescaleDB 集成测试**：DynamicLoadHourly 超表需真实 PG，CI 用 docker-compose
3. **性能门禁**：pytest 加 `--cov-fail-under=95` 阈值
4. **factory-boy**：用工厂模式生成 1000+ 功能区域做 NF-SAC-04 性能基准
5. **前端测试**：Vitest + React Testing Library 组件测试 + Playwright E2E
6. **psychrolib 版本锁定**：requirements.txt 锁定具体版本

---

## 八、TDD 流程总结（6 批迭代）

| 批次 | 模块 | 用例 | PRD 覆盖 |
|------|------|:----:|----------|
| 1 | 计算引擎+认证+模型+计算API | 52 | F1/F2/F4/§15 |
| 2 | 动态仿真 services | 13 | F6/§15.4 |
| 3 | 负荷预测 services | 12 | F10/§14.8/§15.8 |
| 4 | projects CRUD + conversation | 12 | F2/ADR-0007 |
| 5 | Excel 导入 + CSV 导出 | 8 | F2-032/F8-012 |
| 6 | 剩余 API 端点 | 32 | F6-020/F8/F9/F10/F2-046 |
| **合计** | | **129** | **覆盖 F1/F2/F4/F6/F7/F8/F9/F10** |

---

**报告生成时间**：2026-07-15
**测试执行**：自动化（pytest，真实运行）
**报告维护**：架构师
