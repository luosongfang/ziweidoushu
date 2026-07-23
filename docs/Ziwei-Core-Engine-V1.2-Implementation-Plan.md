# Ziwei Core Engine V1.2 Phase 2 — Implementation Plan

> 审计日期：2026-07-23 | 引擎版本：1.2 | Schema：2.5

## Phase 0 代码审计结论

### 已有功能（不重复开发）

| 模块 | 状态 | 位置 |
|------|------|------|
| 十四主星 | ✅ 100% | `StarPlacementEngine` / `FourteenStarsCalculator` |
| 六吉六煞 | ✅ 100% | `StarPlacementEngine` |
| 禄存 / 天马 | ✅ 100% | `StarPlacementEngine` |
| 生年四化 | ✅ 100% | `FourHuaCalculator` / `FourTransformEngine` |
| 十二宫 | ✅ 100% | `PalaceEngine` / `TwelvePalaceBuilder` |
| 大限 | ✅ 100% | `DaXianCalculator` / `FortuneEngine` |
| 三合 / 对宫 | ✅ V1.1 | `PalaceEngine` |

### 生产数据流

```
POST /api/chart/create
  → ChartBuilder.build()          # ziwei_engine/chart_builder.py
  → ChartNormalizer.normalize()   # ziwei/core/chart_normalizer.py
  → StandardChartSchema V2.5
  → persist_chart()               # schema_version 2.5
```

### Trace 系统

- `ChartBuilder.trace_steps`：calendar / palace / star_placement / auxiliary_star / four_transform / xiaoxian / daxian_transform / annual_transform
- 各新增引擎均含 `trace` 字段，来源可追溯

---

## V1.2 新增实现

### Phase 1 — 辅助星系统

- `backend/app/ziwei/rules/auxiliary_star_rules.py` — 9 颗杂曜规则
- `backend/app/ziwei/engines/auxiliary_star_engine.py` — 计算引擎
- `database/migrations/021_auxiliary_stars.sql` — `auxiliary_star_rules` 表
- Schema：`stars.auxiliary[]`，每星含 name / category / palace / source / trace

### Phase 2 — 小限系统

- `backend/app/ziwei/fortune/xiaoxian.py`
- 规则：阳男阴女顺、阴男阳女逆，命宫起 1 岁
- Schema：`xiaoxian.{enabled, current_*, yearly_cycle, ranges, trace}`

### Phase 3 — 大限四化

- `backend/app/ziwei/transformation/daxian_hua.py`
- 取当前大限宫位天干 → 十天干四化表
- Schema：`daxian_transform.{period, stem, lu/quan/ke/ji, trace}`

### Phase 4 — 流年四化

- `backend/app/ziwei/transformation/liunian_hua.py`
- Schema：`liunian.annual_transform.{year, stem, lu/quan/ke/ji, trace}`

### Phase 5 — 星曜亮度

- `database/migrations/022_star_brightness.sql` — `star_brightness_rules` 表
- `BrightnessEngine` 优先读 `star_brightness_rules`
- Schema：`stars.main[].brightness` + `brightness` 索引

### Phase 6 — Schema V2.5

- `chart_schema_v2.py` — 兼容 2.0 / 2.5
- `chart_normalizer.py` — 映射全部 V1.2 字段
- `chart_validator.py` — 十四主星 / 辅助星 / 四化 / 小限 / 亮度完整性

### Phase 7 — 标准命盘测试库

- `tests/fixtures/standard_charts/SC-01` ~ `SC-10`
- `tests/golden/SC-01` ~ `SC-10` — V2.5 回归快照

### Phase 8 — 性能优化

- `ChartBuilder` 单次调用 `StarPlacementEngine.compute()`，结果复用于主星/辅煞/四化

---

## 约束遵守

- ❌ 未修改 `backend/app/knowledge/**`
- ❌ 未修改 AI 分析逻辑
- ❌ 未修改前端 UI
- ❌ 未调用 LLM
- ✅ 十四主星 / 十二宫 / 生年四化规则不变
- ✅ 所有新增计算保留 trace
