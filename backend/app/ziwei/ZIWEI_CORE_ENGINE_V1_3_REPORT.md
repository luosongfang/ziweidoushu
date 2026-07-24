# Ziwei Core Engine V1.3 Report

> Professional Chart Completion  
> 日期：2026-07-24  
> 原则：不改 Knowledge Core / AI 分析 / 会员；禁止虚假排盘数据

## 1. 新增文件

| 路径 | 说明 |
|------|------|
| `app/ziwei/core/professional_chart_schema.py` | ProfessionalChartSchema V3 |
| `app/ziwei/core/professional_normalizer.py` | Builder → V3 |
| `app/ziwei/core/chart_quality_validator.py` | 质量门禁 |
| `app/ziwei/STAR_COMPLETENESS_REPORT.md` | Phase 1 审计 |
| `app/ziwei/engines/minor_star_placement_engine.py` | 杂曜统一安置 |
| `app/ziwei/transformation/four_transform_engine_v2.py` | 生年/大限/流年/自化 |
| `tests/fixtures/professional_charts/cases.py` | 20 标准出生案例 |
| `tests/test_professional_chart_v13.py` | V1.3 回归 |

### 主要修改

| 路径 | 变更 |
|------|------|
| `rules/auxiliary_star_rules.py` | +咸池/天官/天福/天寿/天才/天月 |
| `engines/auxiliary_star_engine.py` | stem_lookup / ming_to_year / 天寿 |
| `engines/combination_engine.py` | +flank_ji；新格局规则 |
| `rules/seed_generator.py` | 府相朝垣/昌曲夹命/左右夹命/羊陀夹忌 |
| `ziwei_engine/chart_builder.py` | V1.3 编排 |
| `api/chart_api.py` | 默认返回 V3；`schema_version=2.5` 兼容 |
| `schemas/chart_schema.py` | `schema_version` 字段 |
| `ziwei_data/stars/star_strength.py` | 十四主星完整亮度倒排 |
| `core/chart_schema_v2.py` | AUXILIARY 扩展至 15 |

## 2. 算法完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 十四主星 | 100% | |
| 六吉六煞 | 100% | |
| 禄存天马 | 100% | |
| 杂曜（含桃花孤寡） | 15/15 | Phase2 补齐 6 颗 |
| 生年四化 | 100% | |
| 大限四化 | 100% | |
| 流年四化 | 100% | |
| 宫干自化/飞化 | 100% | `self_transform` |
| 小限 | 100% | |
| 大限/流年落宫 | 100% | |
| 流月/流日/流时 | 0% | `enabled=false`，无假数据 |
| 格局组合 | ~24 规则 | 已接入 Builder→V3 |
| 主星亮度 | 100% | |
| 辅煞亮度 | 骨架 | 不伪造数值 |

## 3. 字段覆盖率（V3）

| 区块 | 覆盖 |
|------|------|
| birth / bazi / meta | ✓ |
| 十二宫（主吉煞杂+亮度+四化+运限引用） | ✓ |
| stars 索引（main/six_lucky/six_sha/others） | ✓ |
| four_transform（birth/daxian/liunian/self） | ✓ |
| fortune（daxian/liuxian/xiaoxian；其余 disabled） | ✓ |
| star_combination / sanhe / feixing / quality / trace | ✓ |
| legacy_v2 | 可选嵌入 |

## 4. 测试结果

运行：

```bash
cd backend
python -m pytest tests/test_professional_chart_v13.py tests/test_star_placement.py -q --tb=line
```

预期：

- 20 个 PC 案例全部通过质量门禁（十四主星、十二宫、四化、杂曜齐全）
- 杂曜 15 颗均有 `rule_source` + `trace`
- 流月/流日/流时保持 `enabled=false`

## 5. 剩余不足

1. **流月/流日/流时**尚未实现经典安星（仅占位）
2. **辅煞亮度表**未完整录入
3. **飞星派**未启用（仅宫干飞化/自化）
4. **双入口**：ChartGenerator(v1) 仍存在；生产以 ChartBuilder→V3 为准
5. **V2.5 golden（SC-01…）**可能因辅助星数量从 9→15 产生新 warnings，需择机刷新 golden
6. **真太阳时**仍依赖地点经度；无地点则不修正

## 6. API 用法

```http
POST /api/chart/create
{
  "name": "测试",
  "gender": "male",
  "solar_date": "1982-02-22",
  "time": "14:00",
  "schema_version": "3.0",
  "persist": false
}
```

兼容旧前端：`"schema_version": "2.5"`。
