# PCB-CoolSim v0.5.1 测试报告（TDD 阶段一）

| 项目 | PCB-CoolSim（PCB 工厂冷量仿真平台） |
|------|------|
| 分支 | `feat/code-scaffold` |
| 提交 | `180f971 test(tdd): TDD 开发核心模块，52 测试全过覆盖率 98%` |
| 测试日期 | 2026-07-14 |
| 测试框架 | pytest 8.2 + pytest-django 4.8 + pytest-cov 5.0 |
| 测试环境 | Python 3.13 / Django 5.0.6 / SQLite(in-memory) |
| 执行命令 | `pytest --cov=apps --cov-report=term-missing` |

---

## 一、执行结果总览

| 指标 | 结果 |
|------|------|
| **用例总数** | 52 |
| **通过** | 52 ✅ |
| **失败** | 0 |
| **错误** | 0 |
| **跳过** | 0 |
| **通过率** | **100%** |
| **总耗时** | 2.19s |
| **代码覆盖率** | **98%**（697 语句，17 未覆盖） |
| **结论** | 🟢 **全部通过，无失败用例** |

```
======================= 52 passed, 9 warnings in 2.19s ========================
TOTAL  697  17  98%
```

---

## 二、按模块执行明细

| 模块 | 测试文件 | 用例数 | 通过 | 失败 | 覆盖率 |
|------|---------|:------:|:----:|:----:|:------:|
| 核心计算引擎 | `apps/calculation/tests/test_services.py` | 31 | 31 | 0 | services 97% |
| 静态计算 API | `apps/calculation/tests/test_api.py` | 5 | 5 | 0 | views 100% |
| 账户认证 | `apps/accounts/tests/test_auth.py` | 8 | 8 | 0 | models 93% |
| 项目模型 | `apps/projects/tests/test_models.py` | 8 | 8 | 0 | models 94% |
| **合计** | | **52** | **52** | **0** | **98%** |

---

## 三、核心计算引擎覆盖（PRD §15 / SAC-2 基线）

本批测试严格覆盖了文档审核阶段的 C1-C8 全部修复点（文档与代码一致性验证）：

| 修复点 | 测试类 | 验证内容 | 结果 |
|--------|--------|---------|:----:|
| **C1 压差8点查表** | TestInfiltrationCoefficient | 表内7点精确匹配 + 封顶 + 负压对称 + 线性插值 + 禁用 √ΔP 公式 | ✅ 11 passed |
| **C2 新风简单加法** | TestAirVolume | 总排风求和 + 压差渗透 + 无 MAX/卫生/净化 | ✅ 3 passed |
| **C3 焓值定义A** | TestEnthalpy | psychrolib + kJ/kg 单位 + RH%→小数转换 | ✅ 4 passed |
| **C4 默认26/55** | TestCalcStaticIntegration | 空值取默认温湿度 | ✅ 1 passed |
| **C5 末端5项** | TestTerminalLoad | 土建/照明/人员/电动/电热 + kW不乘1000 | ✅ 6 passed |
| **C6 总负荷截断** | TestCalcStaticIntegration | 总负荷<0 截断为0 | ✅ 1 passed |
| **C7 ρ=1.2** | TestFreshAirLoad | 定义A公式 + 可为负 | ✅ 2 passed |
| **C8 计算全流程** | TestCalcStaticIntegration | 6步流水线完整 + 冷指标 | ✅ 2 passed |

### 关键断言示例（C1 压差查表）

```python
# 绝不能用 k=ΔP/5 或 √(ΔP) 公式（v1.x 错误实现）
# 10Pa：错误公式给 k=2，正确应为 3.5
assert lookup_infiltration_coeff(Decimal("10")) == Decimal("3.5")
# 5Pa：错误公式给 k=1，正确应为 3.0
assert lookup_infiltration_coeff(Decimal("5")) == Decimal("3.0")
```

---

## 四、失败用例分析

**无失败用例。**

开发过程中共遇到并修复了以下问题（TDD 红→绿循环）：

| # | 问题 | 根因 | 修复 |
|---|------|------|------|
| 1 | conftest 引用 `temp_dry_vent_summer` 字段不存在 | CityConfig 模型未定义该字段（v0.5 仅用夏季空调参数） | conftest 移除该字段 |
| 2 | psychrolib `GetMoistAirEnthalpy` 报参数过多 | 该版本 API 只接受 (TDryBulb, HumRatio)，无 pressure | services.py 删除第3参数 |
| 3 | 焓值量级 55646 异常 | SI 单位制下返回 J/kg，需 /1000 转 kJ/kg | services.py 增加 /1000 |
| 4 | RH 55% 报 "outside range [0,1]" | psychrolib 要求 0~1 小数 | services.py 自动转换 >1 视为百分比 |
| 5 | DRF force_login 认证失败返回 401 | JWTAuthentication 不走 session | 测试改用 APIClient.force_authenticate + 启用 SessionAuthentication |
| 6 | `engineer_role` fixture 未在 test_api 找到 | fixture 定义在 test_auth.py 内部 | 提升到 conftest.py 全局共享 |

---

## 五、覆盖率明细

| 文件 | 语句 | 未覆盖 | 覆盖率 | 未覆盖行说明 |
|------|:----:|:------:|:------:|------------|
| calculation/services.py | 69 | 2 | 97% | 边界分支 |
| calculation/models.py | 58 | 3 | 95% | `__str__` 方法 |
| calculation/views.py | 18 | 0 | 100% | — |
| accounts/models.py | 29 | 2 | 93% | `__str__` 方法 |
| projects/models.py | 124 | 8 | 94% | 部分校验/`__str__` |
| common/models.py | 42 | 2 | 95% | `__str__` 方法 |
| **TOTAL** | **697** | **17** | **98%** | |

未覆盖的 17 行主要是模型的 `__str__` 方法和少量边界分支，不影响核心逻辑。

---

## 六、警告清单（9 个，非阻断）

```
UserWarning: No directory at: backend/staticfiles/
```

**原因**：WhiteNoise 中间件查找 staticfiles 目录，测试环境未创建。
**影响**：无（仅警告，不影响测试结果）。
**建议**：CI 中增加 `mkdir -p staticfiles` 或 settings 中条件加载 WhiteNoise。

---

## 七、问题清单与优化建议

### 已知限制（本批未覆盖）

| # | 项目 | 说明 | 优先级 |
|---|------|------|--------|
| 1 | 动态仿真（模块六/七） | 未实现 F6/F7 端点，services 仅有静态计算 | P0（下一批） |
| 2 | 负荷预测（模块十） | 未实现 F10 端点与 RatioCoefficient 查表 | P0（下一批） |
| 3 | 对话式采集（模块二§6.10） | 未实现 ConversationSession API | P1 |
| 4 | Excel 导入（F2-032） | 未实现 openpyxl 解析 | P1 |
| 5 | 前端测试 | 仅有 build 验证，无组件/集成测试 | P1 |
| 6 | 集成测试 | 未用真实 PG+TimescaleDB（SQLite 模拟） | P2 |

### 优化建议

1. **精度验证测试**：当前用数值范围断言（50<h<62），后续应导入 PRD 测试数据（西安/广州/胡志明 Excel）做精确比对（SAC-2 < 0.1%）
2. **CI 集成**：`backend/requirements.txt` 现已存在，CI 的 `backend-test` job 会自动启用，建议补充 `pytest --cov` 阈值门禁
3. **TimescaleDB 测试**：DynamicLoadHourly 超表测试需真实 PG+TimescaleDB（SQLite 不支持 hypertable），建议 docker-compose 集成测试
4. **fixture 工厂化**：当前 conftest 手写 fixture，后续用 factory-boy 生成批量数据（1000+ 功能区域性能测试 NF-SAC-04）
5. **psychrolib 版本锁定**：不同版本 API 签名不同（本次遇到参数差异），requirements.txt 应锁定具体版本

### TDD 流程复盘

本批严格遵循 **Red→Green→Refactor**：
- 先写测试（含 C1-C8 全部断言）→ 部分失败（Red）
- 实现/修正 services.py → 测试通过（Green）
- 提取 conftest 共享 fixture → 重构（Refactor）

6 个过程中发现的问题（见第四节）均通过测试驱动暴露并修复，验证了 TDD 对 PRD §15 计算正确性的保障作用。

---

## 八、下一批 TDD 计划

| 批次 | 模块 | 预估用例 | SAC 对应 |
|------|------|:--------:|----------|
| 第二批 | 动态仿真 services（方式一气象驱动） | ~15 | SAC-3 (<1%) |
| 第三批 | 负荷预测 services（比例系数法 K(T,R)） | ~12 | SAC-26 |
| 第四批 | projects CRUD API + 对话采集 API | ~20 | SAC-1/SAC-28 |
| 第五批 | Excel 导入 + 报告导出 | ~10 | SAC-5/SAC-17~20 |

---

**报告生成时间**：2026-07-14
**测试执行人**：自动化（pytest）
**报告维护**：架构师
