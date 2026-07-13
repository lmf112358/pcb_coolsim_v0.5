# 本地问题追踪器目录

本目录用于存放本地 Markdown 形式的 issue / PRD / wayfinder 地图（约定见 `docs/agents/issue-tracker.md`）。

- 每个特性一个子目录：`.scratch/<feature-slug>/`
- 工程技能（triage / qa / to-issues / wayfinder）会在此读写文件
- 无需 GitHub 鉴权；与远程仓库解耦
- 默认分诊标签见 `docs/agents/triage-labels.md`
