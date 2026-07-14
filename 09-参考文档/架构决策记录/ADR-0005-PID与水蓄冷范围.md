# ADR-0005: P&ID Generation and Water Storage Scope

**Status:** Superseded (v0.5.1)
**Date:** 2026-07-09
**Decision Makers:** Architect, PM, Domain Expert

---

---

## Status Update (v0.5.1)

> **本 ADR 已被 v0.5.1 范围修正取代。** 模块五「冷站配置」（含 P&ID 生成与水蓄冷配置）已在 v0.5.1 移除，仅保留「负荷分析」。因此本 ADR 决议的两项特性（P&ID 生成、水蓄冷容量配置）均不再属于 v0.5 范围。若后续重启相关特性，应新建 ADR 重新评估。

## Context

The cooling station configuration module originally scoped two features for v0.5:
1. **P&ID System Diagram Generation:** Automatically generate piping and instrumentation diagrams
2. **Water Storage (水蓄冷):** Configure and validate water storage tanks for peak shaving

Both features are valuable but have different complexity levels.

## Decision

**For v0.5:**

### P&ID Generation
- **Include in v0.5:** Generate basic P&ID SVG diagrams
- **Scope:** Static SVG generation showing major components (chillers, pumps, tanks, pipes)
- **Not in v0.5:** Interactive P&ID editing, detailed instrumentation symbols

### Water Storage (水蓄冷)
- **Include in v0.5:** Capacity configuration and basic capacity validation
- **Not in v0.5:** Economic ROI analysis, charge/discharge simulation, optimization

**Validation Rules for Water Storage:**
```
Storage Capacity >= (Peak Load - Base Load) × Storage Hours × Safety Factor
```

## Rationale

### P&ID
- **Value:** High visual value for stakeholders
- **Complexity:** Moderate (SVG generation is well-understood)
- **Decision:** Include basic version

### Water Storage
- **Value:** Capacity config is essential; ROI is nice-to-have
- **Complexity:** ROI analysis requires electricity rate data, optimization algorithms
- **Decision:** Include capacity only, defer ROI to v0.6

## Consequences

### Positive
- P&ID provides immediate visual value
- Water storage capacity validation prevents oversights
- Clear scope boundaries for v0.5

### Negative
- Water storage users can't see ROI in v0.5
- P&ID is basic, not production-quality

### Risks
- Users expect full P&ID → Mitigated by clear documentation
- Users expect ROI analysis → Mitigated by roadmap communication

## Alternatives Considered

### Alternative 1: Full P&ID + Full Water Storage
**Rejected:** Too much scope for v0.5, delays release

### Alternative 2: Defer Both to v0.6
**Rejected:** Loses too much value for v0.5

### Alternative 3: Full P&ID + Capacity Only Water Storage
**Accepted:** Best balance of value and complexity

## Related

- PRD: 模块五「冷站配置」已在 v0.5.1 移除（详见 PRD 修订说明 / 分支 docs/prd-revision）
- Database: `cooling_station_config`, `water_storage_config` 表在 v0.5.1 已不再使用
- UI: Tab 3 P&ID viewer、水蓄冷配置表单已移除
- Roadmap: 相关特性推迟至重新评估（如重启须新建 ADR）
