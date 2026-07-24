# Classical Rule Coverage

> Ziwei Classical Rule Engine V1.6 — 16册规则覆盖  
> 原则：经典理论 > 软件实现 > 单一案例

## 模块完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 历法 | 80% | CAL_LUNAR_001 已编目；实现复用 CalendarEngine |
| 命身宫 | 95% | PALACE_MING/SHEN_001 + 可执行 rule 模块；措辞冲突已文档化 |
| 五行局 | 95% | five_element_table.json（60甲子纳音） |
| 紫微定位 | 100% | ziwei_position_table.json **150** 条查表 |
| 天府 | 90% | 多规则配置；**冲突不自动选择** |
| 十四主星 | 95% | fourteen_star_rule.json 起点/顺逆/来源齐全 |
| 四化 | 70% | 生年已编目；大限/流年/自化待深化 |
| 辅星（六吉） | 85% | traditional_aux 目录 + 运行时安置 |
| 杂曜 | 75% | 刑姚鸾喜孤寡华盖哭虚等 |
| 十二长生 | 60% | 框架 + rule_source/formula/trace |
| 博士十二神 | 60% | 框架 |
| 岁前十二神 | 60% | 框架 |
| 将前十二神 | 60% | 框架 |
| 大限 | 30% | 骨架 |
| 小限 | 20% | 骨架 |
| 流年 | 20% | 骨架 |
| 格局 | 10% | stub |

## 16册编目

`rules/sources/book_001.json` … `book_016.json`（目录级引用，全文数字化=false）

## 生产门禁

- `production_requires_source=true`
- 无 `source` 的规则 → `PermissionError`，禁止进入生产
