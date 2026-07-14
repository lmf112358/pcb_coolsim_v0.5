# 变更日志

本文件记录本项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

## [未发布]

### 新增
- 项目文档体系重构
- 四层 Spec 结构（系统级、模块级、接口级、实现级）
- 完整的版本控制与协作流程
- CI/CD 配置（GitHub Actions）
- PR 和 Issue 模板
- pre-commit 配置

### 变更
- 文档结构重组为新的层次体系
- 统一文档语言为中文
- 更新 CLAUDE.md 指南

### 修复
- 清理无关文档和重复文件

## [v0.5.1] - 2026-07-10

### 新增
- 初始化 PCB-CoolSim v0.5 项目结构
- 创建 Git 仓库和 .gitignore
- 建立版本控制与协作流程
- 配置 CI/CD 流水线
- 创建 PR 和 Issue 模板
- 配置 pre-commit hooks

### 变更
- 文档体系重构为四层 Spec 结构
- 统一文档语言为中文
- 更新项目目录结构
- SDD 全量收敛：移除「冷站配置 / 水蓄冷 / P&ID 生成」描述（PRD v0.5.1 范围修正），对齐负荷分析；新增对话式采集（模块二 / Page 6）覆盖——会话表、对话 API、用户故事、测试用例同步补齐

### 修复
- 清理无关文档和重复文件
- 修复文档引用路径

## [v0.5.0] - 2026-07-01

### 新增
- 项目初始化
- 基础框架搭建
- 核心功能开发
  - 用户认证
  - 项目管理
  - 数据采集
  - 2D 可视化
  - 静态冷量计算
  - 动态仿真
  - 报告导出

### 变更
- 无

### 修复
- 无

---

## 版本说明

### 版本号规则

- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

### 变更类型

- **新增**：新功能
- **变更**：对现有功能的变更
- **废弃**：已经不建议使用，即将移除的功能
- **移除**：已移除的功能
- **修复**：Bug 修复
- **安全**：安全相关的变更

### 贡献指南

1. 每次提交都应在 CHANGELOG 中记录
2. 使用中文描述变更内容
3. 按照变更类型分类
4. 关联相关的 Issue 和 PR
5. 保持简洁清晰

---

## 链接

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [GitHub Releases](https://github.com/your-org/pcb_coolsim_v0.5/releases)
