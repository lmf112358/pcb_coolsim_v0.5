# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 项目文档体系重构
- 四层 Spec 结构（系统级、模块级、接口级、实现级）
- 完整的版本控制与协作流程
- CI/CD 配置（GitHub Actions）
- PR 和 Issue 模板
- pre-commit 配置

### Changed
- 文档结构重组为新的层次体系
- 统一文档语言为中文
- 更新 CLAUDE.md 指南

### Fixed
- 清理无关文档和重复文件

## [v0.5.1] - 2026-07-10

### Added
- 初始化 PCB-CoolSim v0.5 项目结构
- 创建 Git 仓库和 .gitignore
- 建立版本控制与协作流程
- 配置 CI/CD 流水线
- 创建 PR 和 Issue 模板
- 配置 pre-commit hooks

### Changed
- 文档体系重构为四层 Spec 结构
- 统一文档语言为中文
- 更新项目目录结构

### Fixed
- 清理无关文档和重复文件
- 修复文档引用路径

## [v0.5.0] - 2026-07-01

### Added
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

### Changed
- 无

### Fixed
- 无

---

## 版本说明

### 版本号规则

- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

### 变更类型

- **Added**：新功能
- **Changed**：对现有功能的变更
- **Deprecated**：已经不建议使用，即将移除的功能
- **Removed**：已移除的功能
- **Fixed**：Bug 修复
- **Security**：安全相关的变更

### 贡献指南

1. 每次提交都应在 CHANGELOG 中记录
2. 使用英文描述变更内容
3. 按照变更类型分类
4. 关联相关的 Issue 和 PR
5. 保持简洁清晰

---

## 链接

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [GitHub Releases](https://github.com/your-org/pcb_coolsim_v0.5/releases)
