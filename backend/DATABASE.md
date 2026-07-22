# Phase 2.5 — Supabase PostgreSQL 迁移指南

## 1. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 Supabase DATABASE_URL 与 SUPABASE_KEY
```

从 Supabase Dashboard → **Project Settings → Database → Connection string (URI)** 复制连接串。

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 执行迁移

```bash
cd backend
alembic upgrade head
```

## 4. 验证连接

```bash
pytest tests/test_database.py -v
```

## 5. 启动 API

```bash
uvicorn app.main:app --reload
```

## 数据表

| 表名 | 说明 |
|------|------|
| `users` | 用户 |
| `birth_profiles` | 出生资料 |
| `ziwei_charts` | 命盘主表 |
| `chart_palaces` | 十二宫明细 |
| `star_rules` | 星曜规则 |
| `four_hua_rules` | 四化规则 |
| `ai_reports` | AI 报告 |
| `memberships` | 会员 |
| `orders` | 订单 |
