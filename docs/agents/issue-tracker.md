# 问题追踪器：本地 Markdown

本仓库的 issue 与 PRD 以 Markdown 文件存放在仓库内的 `.scratch/` 目录。无需 GitHub 鉴权，工程技能（triage / qa / to-issues / wayfinder）直接读写本地文件。

## 约定

- 每个特性一个目录：`.scratch/<feature-slug>/`
- 该特性的 PRD：`.scratch/<feature-slug>/PRD.md`
- 实现类 issue：`.scratch/<feature-slug>/issues/<NN>-<slug>.md`，编号从 `01` 起
- 分诊状态记录在 issue 文件顶部附近的 `Status:` 行（角色字符串见 `triage-labels.md`）
- 评论与对话历史追加到文件底部的 `## Comments` 标题下

## 当技能说「发布到问题追踪器」

在 `.scratch/<feature-slug>/` 下新建文件（如目录不存在则创建）。

## 当技能说「获取相关工单」

读取对应路径的文件。用户通常会直接给出路径或 issue 编号。

## Wayfinding 操作（供 /wayfinder 使用）

- **地图**：`.scratch/<effort>/map.md` —— Notes / Decisions-so-far / Fog 主体。
- **子工单**：`.scratch/<effort>/issues/NN-<slug>.md`，编号从 `01`，正文为问题。`Type:` 行记录工单类型（`research`/`prototype`/`grilling`/`task`）；`Status:` 行记录 `claimed`/`resolved`。
- **阻塞**：顶部 `Blocked by: NN, NN` 行。当其列出的文件全部 `resolved` 时解除阻塞。
- **前沿**：扫描 `.scratch/<effort>/issues/` 中开放、未阻塞、未认领的工单，按编号优先。
- **认领**：先设 `Status: claimed` 并保存，再做任何工作。
- **解决**：在 `## Answer` 标题下追加答案，设 `Status: resolved`，再向 `map.md` 的 Decisions-so-far 追加上下文指针（要点 + 链接）。
