# PCB-CoolSim v0.5.1 测试报告（TDD 完整版）

| 项目 | PCB-CoolSim（PCB 工厂冷量仿真平台） |
|------|------|
| 分支 | `feat/code-scaffold` |
| 最新提交 | `0f1dba7 test(tdd): 第五批 TDD Excel 导入 + CSV 导出` |
| 测试日期 | 2026-07-14 |
| 测试框架 | pytest 8.2 + pytest-django 4.8 + pytest-cov 5.0 |
| 测试环境 | Python 3.13 / Django 5.0.6 / SQLite(in-memory) |
| 执行命令 | `pytest --cov=apps --cov-report=term-missing` |

---

## 一、执行结果总览

| 指标 | 结果 |
|------|------|
| **用例总数** | 97 |
| **通过** | 97 ✅ |
| **失败** | 0 |
| **错误** | 0 |
| **跳过** | 0 |
| **通过率** | **100%** |
| **总耗时** | 3.71s |
| **代码覆盖率** | **96%**（1353 语句，49 未覆盖） |
| **结论** | 🟢 **全部通过，无失败用例** |

```
======================= 97 passed, 18 warnings in 3.71s ========================
TOTAL  1353  49  96%
```

---

## 二、按模块执行明细

| 模块 | 测试文件 | 用例数 | 通过 | 失败 | 覆盖率（核心文件） |
|------|---------|:------:|:----:|:----:|:------:|
| 核心计算引擎 | `calculation/tests/test_services.py` | 31 | 31 | 0 | services 97% |
| 静态计算 API | `calculation/tests/test_api.py` | 5 | 5 | 0 | views 100% |
| 账户认证 | `accounts/tests/test_auth.py` | 8 | 8 | 0 | models 93% |
| 项目模型 | `projects/tests/test_models.py` | 8 | 8 | 0 | models 94% |
| 动态仿真 | `simulation/tests/test_services.py` | 13 | 13 | 0 | services 92% |
| 负荷预测 | `forecast/tests/test_services.py` | 12 | 12 | 0 | services 84% |
| projects CRUD API + conversation | `projects/tests/test_api.py` | 12 | 12 | 0 | views 82% |
| Excel 导入 + CSV 导出 | `exports/tests/test_services.py` | 8 | 8 | 0 | services 91% |
| **合计** | | **97** | **97** | **0** | **96%** |

---

## 三、PRD 需求覆盖（F 编号）

| PRD 需求 | 测试类 | 用例数 | 结果 |
|----------|--------|:------:|:----:|
| F1-001~006 JWT 认证 | TestJWTAuth | 4 | ✅ |
| F1-006 密码加密 | TestPasswordSecurity | 2 | ✅ |
| F1-024 角色权限 | TestRoleModel | 2 | ✅ |
| F1-015~023 项目 CRUD | TestProjectAPI | 4 | ✅ |
| F2-009~013 层级 CRUD | TestBuildingAPI/TestFloorAPI | 2 | ✅ |
| F2-014~020 功能区域 CRUD | TestRoomAPI | 3 | ✅ |
| F2-021 复制功能区域 | TestRoomAPI.test_copy_room | 1 | ✅ |
| F2-030 额外负荷层级 | TestExtraLoadLevel | 2 | ✅ |
| F2-032~039 Excel 导入 | TestExcelImport | 5 | ✅ |
| F2-057 断点续采 | TestConversationModel | 3 | ✅ |
| F4-001~050 静态计算 | TestCalcStaticIntegration + services | 31+5 | ✅ |
| F6-001~011 动态仿真 | TestSimulateWeatherDriven | 13 | ✅ |
| F7-027~028 极值统计 | TestExtremes | 3 | ✅ |
| F8-012~014 CSV 导出 | TestCsvExport | 3 | ✅ |
| F10-014~018 负荷预测 | TestForecastRoom | 12 | ✅ |
| §16.1.1 级联删除 | TestProjectCascade | 1 | ✅ |

---

## 四、核心计算正确性（PRD §15 / SAC 验证）

### C1-C8 修复点代码验证

| 修复点 | 测试 | 验证结果 |
|--------|------|:--------:|
| C1 压差8点查表 | TestInfiltrationCoefficient（11 用例） | ✅ |
| C2 新风简单加法 | TestAirVolume（3 用例） | ✅ |
| C3 焓值定义A | TestEnthalpy（4 用例） | ✅ |
| C4 默认26/55 | test_default_indoor_temp_humidity | ✅ |
| C5 末端5项 | TestTerminalLoad（6 用例） | ✅ |
| C6 总负荷截断 | test_negative_total_truncated | ✅ |
| C7 ρ=1.2 | TestFreshAirLoad（2 用例） | ✅ |
| C8 动态方式二查表 | TestBilinearInterpolation（4 用例） | ✅ |

### 精度验证（SAC-2/SAC-3）

| 验收项 | 验证方法 | 结果 |
|--------|---------|:----:|
| SAC-2 静态 <0.1% | psychrolib 焓值与标量一致（test_consistent_with_scalar） | ✅ |
| SAC-3 动态 <1% | 向量化焓值与标量一致（test_consistent_with_scalar） | ✅ |
| PRD §15.8 插值示例 | 20℃/60% → 0.767（test_prd_example_20c_60pct） | ✅ |

---

## 五、失败用例分析

**无失败用例（0 failed）。**

开发过程中通过 TDD 红→绿循环发现并修复了以下问题（均在测试阶段暴露，未流入生产）：

| # | 阶段 | 问题 | 根因 | 修复 |
|---|------|------|------|------|
| 1 | 第一批 | conftest 引用不存在的字段 | CityConfig 无 temp_dry_vent_summer | 移除字段 |
| 2 | 第一批 | psychrolib 参数过多 | 该版本 API 只接受 (TDryBulb, HumRatio) | 删除 pressure 参数 |
| 3 | 第一批 | 焓值 55646 异常 | SI 单位 J/kg 未 /1000 | 增加 /1000 |
| 4 | 第一批 | RH 55% 报错 | psychrolib 要求 0~1 小数 | 自动转换 |
| 5 | 第一批 | DRF force_login 失败 | JWT 不走 session | force_authenticate + SessionAuth |
| 6 | 第二批 | datetime64 arange 错误 | 需 start/stop | 改用 timedelta64 构造 |
| 7 | 第二批 | 湿球 > 干球报错 | psychrolib 约束 | 测试数据保证湿球<干球 |
| 8 | 第三批 | ForecastScenario 缺 start_date | NOT NULL 约束 | 测试补字段 |
| 9 | 第四批 | create_room 400 | serializer floor 必填 | floor 改 read_only |
| 10 | 第五批 | 错误字段名断言 | 测试写英文实际中文 | 断言改中文列名 |

---

## 六、覆盖率明细

| 文件 | 语句 | 未覆盖 | 覆盖率 |
|------|:----:|:------:|:------:|
| calculation/services.py | 69 | 2 | **97%** |
| calculation/views.py | 18 | 0 | 100% |
| calculation/models.py | 58 | 3 | 95% |
| accounts/models.py | 29 | 2 | 93% |
| projects/models.py | 124 | 8 | 94% |
| projects/serializers.py | 26 | 0 | 100% |
| projects/views.py | 55 | 10 | 82% |
| simulation/services.py | 37 | 3 | 92% |
| forecast/models.py | 65 | 2 | 97% |
| forecast/services.py | 57 | 9 | 84% |
| conversation/models.py | 31 | 2 | 94% |
| common/models.py | 42 | 2 | 95% |
| exports/services.py | 69 | 6 | 91% |
| **TOTAL** | **1353** | **49** | **96%** |

未覆盖的 49 行主要是模型的 `__str__` 方法、部分边界分支、DRF viewset 的 list/retrieve 等。

---

## 七、问题清单与优化建议

### 已知限制

| # | 项目 | 说明 | 优先级 |
|---|------|------|--------|
| 1 | 前端测试 | 仅有 build 验证，无组件/集成测试 | P1 |
| 2 | 集成测试 | SQLite 模拟，未用真实 PG+TimescaleDB（hypertable） | P2 |
| 3 | 性能测试 | 未实现 1000+ 功能区域 <5s 基准（NF-SAC-04） | P1 |
| 4 | 精度基准 | 未导入 PRD 测试数据（西安/广州/胡志明 Excel）做精确比对 | P1 |
| 5 | API 端点 | 对话采集/气象/平面图/数据管理 API 端点未实现 | P2 |

### 优化建议

1. **精度基准测试**：导入 `06-测试文档/测试数据/` 的 3 份 Excel，与手工验算做 <0.1% 对比
2. **TimescaleDB 集成测试**：DynamicLoadHourly 超表需真实 PG，建议 CI 用 docker-compose
3. **性能门禁**：pytest 加 `--cov-fail-under=95` 阈值，CI 自动拦截覆盖率下降
4. **factory-boy**：用工厂模式生成 1000+ 功能区域做 NF-SAC-04 性能基准
5. **前端测试**：Vitest + React Testing Library 组件测试 + Playwright E2E
6. **psychrolib 版本锁定**：不同版本 API 签名不同，requirements.txt 应锁版本

---

## 八、TDD 流程总结

本批严格遵循 **Red→Green→Refactor** 循环，5 批迭代：

| 批次 | 模块 | 用例 | PRD 覆盖 | 提交 |
|------|------|:----:|----------|------|
| 1 | 计算引擎+认证+模型+计算API | 52 | F1/F2/F4/§15 | `180f971` |
| 2 | 动态仿真 services | 13 | F6/§15.4 | `4ece0df` |
| 3 | 负荷预测 services | 12 | F10/§14.8/§15.8 | `b743296` |
| 4 | projects CRUD + conversation | 12 | F2/ADR-0007 | `dd7f80b` |
| 5 | Excel 导入 + CSV 导出 | 8 | F2-032/F8-012 | `0f1dba7` |
| **合计** | | **97** | | |

每个修复点（C1-C8）都通过测试直接断言拦截，验证了 TDD 对 PRD §15 计算正确性的保障。

---

**报告生成时间**：2026-07-14
**测试执行**：自动化（pytest，真实运行）
**报告维护**：架构师
