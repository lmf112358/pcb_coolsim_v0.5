# Architecture Decision Records (ADR) Index

> Version: 1.0
> Date: 2026-07-09
> Status: Baselined
> Reference: PRD v0.5.1 Section 4.4

---

## Overview

Architecture Decision Records document significant architectural decisions made during the project. Each ADR is immutable once accepted - new decisions require new ADRs.

---

## ADR Index

| ADR | Title | Status | Date | Decision Makers |
|-----|-------|--------|------|-----------------|
| [ADR-0001](0001-end-load-allocation.md) | End-load allocation by room water temperature tier | Accepted | 2026-07-09 | Architect, Domain Expert |
| [ADR-0002](0002-async-celery-redis.md) | Async tasks with Celery + Redis | Accepted | 2026-07-09 | Tech Lead, Backend Lead |
| [ADR-0003](0003-coefficient-table.md) | Consolidate coefficient tables into single matrix | Accepted | 2026-07-09 | Domain Expert, Architect |
| [ADR-0004](0004-validation-v3.md) | Validation V3: Operating capacity validation | Accepted | 2026-07-09 | Domain Expert, QA Lead |
| [ADR-0005](0005-pid-water-storage.md) | P&ID generation and water storage scope | Superseded (v0.5.1) | 2026-07-09 | Architect, PM |
| [ADR-0006](0006-missing-entities.md) | 缺失实体补齐 (Missing entity backfill) | Accepted | 2026-07-13 | Architect |

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
