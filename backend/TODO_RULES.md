# TODO_RULES.md — 规则与算法待完善项

> Engine V1.0 Phase 2 · 更新日期：2026-07-23

## 已接入（DB / RulesLoader 驱动）

- [x] 公历 → 农历（lunar_python，含立春/节气月界）
- [x] 四柱干支（年/月/日/时）
- [x] 命宫 / 身宫 / 十二宫
- [x] 五行局（纳音规则表）
- [x] 紫微定位（ziwei_position_rules）
- [x] 十四主星 + 辅星 + 煞星（star_placement_rules）
- [x] 生年四化（four_hua_rules / four_transform_rules）
- [x] 大限顺逆 + 流年

## 待扩展（不影响 V1.0 核心排盘）

| 项目 | 说明 | 优先级 |
|------|------|--------|
| 农历输入排盘 | 当前 API 仅 solar_date；需扩展 calendar_type=lunar | P1 |
| 飞星派四化 | V1.0 仅三合 sanhe；feixing 策略模式预留 | P2 |
| 闰月精确展示 | 闰月排盘边界用例需扩充标准盘 | P1 |
| 真太阳时城市库 | 目前仅内置主要城市经度；可接 GeoIP | P2 |
| 星曜亮度 UI 字段 | brightness 已在 Sprint 5 引擎；Phase 2 JSON 可扩展 | P2 |
| 格局组合 | CombinationEngine 已存在；可并入 Phase 2 响应 | P2 |
| PostgreSQL 生产迁移 | 当前默认 SQLite；生产切换 DATABASE_URL | P1 |
| Supabase Auth 与 ORM User 对齐 | users 表与 auth.users 映射 | P1 |
| 晚子时跨日 | 已依赖 lunar_python；需增加 REF 标准盘 | P1 |

## 标准盘缺口

目标 ≥12 组 reference_charts.json，当前 6 组。建议补充：

- 1990-05-20 14:30 男 北京（Phase 2 测试案例）
- 闰月案例
- 立春前后案例
- 子时边界案例

## 参考

- 算法文档：`backend/app/ziwei/ALGORITHM.md`
- 规则 seeds：`backend/app/ziwei/rules/seed_generator.py`
- SQL 规则：`database/rules/`
