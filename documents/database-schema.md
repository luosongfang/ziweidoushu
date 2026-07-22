# 数据库 Schema 说明

> 数据库：Supabase PostgreSQL | 迁移文件：`database/migrations/`

## 表一览

| 表名 | 用途 | 迁移文件 |
|------|------|----------|
| `auth.users` | 用户账号（Supabase 内置） | — |
| `profiles` | 用户扩展信息、会员等级 | 001 |
| `charts` | 命盘数据 | 002 |
| `analyses` | AI 解读记录 | 003 |
| `knowledge_chunks` | RAG 向量知识库 | 004 |

---

## profiles

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 关联 auth.users.id |
| display_name | TEXT | 显示名称 |
| avatar_url | TEXT | 头像 URL |
| membership | TEXT | 会员等级：free / basic / premium |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

---

## charts

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 所属用户 |
| name | TEXT | 命盘名称 |
| birth_datetime | TIMESTAMPTZ | 出生日期时间 |
| gender | TEXT | male / female |
| calendar_type | TEXT | solar（公历）/ lunar（农历） |
| timezone | TEXT | 时区 |
| chart_data | JSONB | 完整命盘结构（见下方） |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

### chart_data JSON 结构（草案）

```json
{
  "ming_gong": "子",
  "shen_gong": "午",
  "palaces": [
    {
      "index": 0,
      "name": "命宫",
      "branch": "子",
      "stars": [
        { "name": "紫微", "brightness": "庙", "sihua": null }
      ]
    }
  ],
  "daxian": [
    { "start_age": 4, "end_age": 13, "palace": "命宫", "branch": "子" }
  ],
  "liunian": { "year": 2026, "palace": "财帛", "branch": "辰" }
}
```

---

## analyses

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 所属用户 |
| chart_id | UUID | 关联命盘 |
| analysis_type | TEXT | overall / palace / daxian / liunian |
| prompt_version | TEXT | Prompt 版本号 |
| input_context | JSONB | 传入 LLM 的上下文摘要 |
| result_text | TEXT | AI 解读全文 |
| tokens_used | INTEGER | 消耗 Token 数 |
| created_at | TIMESTAMPTZ | 创建时间 |

---

## knowledge_chunks

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| source | TEXT | 来源古籍 |
| category | TEXT | 分类（主星/四化/宫位等） |
| title | TEXT | 片段标题 |
| content | TEXT | 文本内容 |
| metadata | JSONB | 扩展元数据 |
| embedding | vector(1536) | 向量 embedding |
| created_at | TIMESTAMPTZ | 创建时间 |

---

## 安全策略（RLS）

所有业务表均启用 Row Level Security：
- 用户只能读写自己的 `profiles`、`charts`、`analyses`
- `knowledge_chunks` 对所有认证用户只读
