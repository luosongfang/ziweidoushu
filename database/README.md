# 数据库目录

## 目录说明

| 路径 | 作用 |
|------|------|
| **`schema.sql`** | 完整 Schema（业务表） |
| **`migrations/`** | 分步迁移（含 `005_rules_tables.sql`） |
| **`rules/`** | ★ 规则种子数据（Sprint 1） |
| `seeds/` | 测试种子数据 |

## 规则表（Sprint 1）

见 `database/rules/README.md` 及 Final Architecture 文档。

## 快速初始化

1. Supabase SQL Editor 执行 `schema.sql`
2. Sprint 1 后执行 `migrations/005_rules_tables.sql` + `rules/*.sql`
