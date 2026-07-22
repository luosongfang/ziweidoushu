# 规则种子数据目录

Sprint 1 完整规则系统，与 `backend/app/ziwei/rules/seed_generator.py` 数据一致。

## 文件说明

| 文件 | 表 | 记录数 |
|------|-----|--------|
| `nayin_rules.sql` | nayin_rules | 60 |
| `ziwei_position_rules.sql` | ziwei_position_rules | 180 (6局×30日) |
| `star_placement_rules.sql` | star_placement_rules | 28 |
| `four_transform_rules.sql` | four_transform_rules | 10 |
| `brightness_rules.sql` | brightness_rules | 168 (14星×12宫) |
| `daxian_rules.sql` | daxian_rules | 4 |
| `star_combination_rules.sql` | star_combination_rules | 20 |
| `palace_meaning_rules.sql` | palace_meaning_rules | 12 |
| `stars.sql` | stars | 28（运行 Python 导出脚本生成） |

## Supabase 初始化步骤

1. 执行 `database/migrations/005_rules_tables.sql`
2. 按顺序执行本目录下 `*.sql` 种子文件
3. 或一键执行：

```sql
-- 在 Supabase SQL Editor 中依次 Run 各文件
```

## 重新生成种子（开发用）

```bash
# 方式 1：Node（推荐，无需 Python）
node database/rules/export_seeds.mjs

# 方式 2：Python（完整含 stars 表）
cd backend && python scripts/export_rules_sql.py
```

## 运行时加载

`RulesLoader` 从 `seed_generator.build_all_rules()` 内存缓存读取，与 DB seeds **数据一致**。

Sprint 2+ 将优先查 Supabase，缓存失效时回退内存。
