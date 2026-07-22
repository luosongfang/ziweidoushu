# Phase 2.5 — Supabase PostgreSQL 迁移指南

## 1. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，**必须替换** `[YOUR-PASSWORD]` 为 Supabase 真实数据库密码：

```env
DATABASE_URL=postgresql://postgres.soiqjyoublmkufrhboay:你的真实密码@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require
SUPABASE_URL=https://soiqjyoublmkufrhboay.supabase.co
SUPABASE_KEY=你的publishable_key
```

密码位置：Supabase Dashboard → **Project Settings → Database → Database password**

连接串位置：**Connect → ORMs → SQLAlchemy**（复制 URI 最准确）

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 执行迁移（推荐）

```bash
cd backend
alembic upgrade head
```

> 若未执行迁移，后端启动时会**自动建表**作为兜底，但正式环境仍建议用 Alembic。

## 4. 验证连接

```bash
pytest tests/test_database.py -v
# 或
curl http://localhost:8000/api/v1/health
```

`database.ready` 应为 `true`。

## 5. 启动 API

```bash
cd backend
uvicorn app.main:app --reload
```

## 6. 测试写入

```bash
curl -X POST http://localhost:8000/api/chart/create \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"测试\",\"gender\":\"male\",\"solar_date\":\"1990-05-20\",\"time\":\"14:30\",\"location\":\"北京\",\"persist\":true}"
```

成功响应应包含：

```json
{
  "persisted": true,
  "chart_id": "...",
  "birth_profile_id": "..."
}
```

然后在 Supabase **Table Editor** 查看 `birth_profiles`、`ziwei_charts`、`chart_palaces`。

---

## 故障排查：Supabase 没有数据

| 现象 | 原因 | 处理 |
|------|------|------|
| 前端提示「DATABASE_URL 未配置」 | `.env` 仍是 `[YOUR-PASSWORD]` | 填入真实密码并**重启后端** |
| 前端提示「数据库保存失败」 | 密码错误 / 区域不对 / 未开 SSL | 从 Dashboard 重新复制连接串 |
| 排盘成功但 `persisted: false` | 请求带了 `persist: false` | 前端已默认 `persist: true` |
| `/api/v1/health` 显示 `ready: false` | 后端未读到 `.env` | 必须在 `backend/` 目录启动 uvicorn |
| 表不存在 | 未迁移 | `alembic upgrade head` 或重启后端触发自动建表 |

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
