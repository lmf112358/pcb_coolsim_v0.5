# Architecture Decision Records (ADR) Index

> Version: 1.1
> Date: 2026-07-14
> Status: Baselined
> Reference: PRD v0.5.1 Section 4.4

---

## Overview

Architecture Decision Records document significant architectural decisions made during the project. Each ADR is immutable once accepted - new decisions require new ADRs.

---

## ADR Index

| ADR | Title | Status | Date | Decision Makers |
|-----|-------|--------|------|-----------------|
| [ADR-0001](ADR-0001-末端负荷分配.md) | 末端负荷按房间级冷冻水档分配 (End-load allocation by room water temperature tier) | Accepted | 2026-07-09 | Architect, Domain Expert |
| [ADR-0002](ADR-0002-异步任务Celery+Redis.md) | 异步任务使用 Celery + Redis (Async tasks with Celery + Redis) | Accepted | 2026-07-09 | Tech Lead, Backend Lead |
| [ADR-0003](ADR-0003-比例系数表统一.md) | 两套比例系数表合并为单一权威表 `RatioCoefficient` | Accepted（系数待校准） | 2026-07-09 | Domain Expert, Architect |
| [ADR-0004](ADR-0004-校验V3运行容量.md) | 校验 V3：冷站冷机运行容量校验 | Superseded (v0.5.1) | 2026-07-09 | Domain Expert, QA Lead |
| [ADR-0005](ADR-0005-PID与水蓄冷范围.md) | P&ID 生成与水蓄冷范围 (P&ID generation and water storage scope) | Superseded (v0.5.1) | 2026-07-09 | Architect, PM |
| [ADR-0006](ADR-0006-缺失实体补齐.md) | 数据库设计缺失实体补齐 (Missing entity backfill) | Accepted | 2026-07-13 | Architect |
| [ADR-0007](ADR-0007-对话采集会话表.md) | 对话式采集会话与消息表 (Conversational collection session & message tables) | Accepted | 2026-07-14 | Architect, Product, Backend Lead |

### Status 说明

- **Accepted**：已采纳，作为权威决策。
- **Superseded (v0.5.1)**：随 v0.5.1 范围调整（模块五「冷站配置」移除）被取代，正文保留作为历史记录，请勿据此实现已移除特性。
  - ADR-0004：冷站冷机容量校验作废；负荷分析装机容量校核（PRD F7-022~024）沿用「运行容量」原则。
  - ADR-0005：P&ID 生成与水蓄冷容量配置两项特性均不在 v0.5 范围。

---

## ADR Template

Use this template for new ADRs:

```markdown
# ADR-{XXXX}: {Title}

**Status:** {Proposed | Accepted | Deprecated | Superseded}
**Date:** {YYYY-MM-DD}
**Decision Makers:** {List of people involved}

---

## Context

{Describe the problem or decision that needs to be made. What are the forces at play?}

## Decision

{State the decision that was made clearly and concisely.}

## Rationale

{Explain why this decision was made. What are the benefits?}

## Consequences

### Positive
- {List positive outcomes}

### Negative
- {List negative outcomes or trade-offs}

### Risks
- {List potential risks}

## Alternatives Considered

### Alternative 1: {Name}
{Description and why it was rejected}

### Alternative 2: {Name}
{Description and why it was rejected}

## Related

- PRD: {Section reference}
- Related ADRs: {List}
```

---

## Notes

- ADRs are immutable once accepted
- If a decision is reversed, create a new ADR that supersedes the old one
- ADRs should be concise but provide enough context for future understanding
- Link ADRs to relevant PRD sections and implementation details
