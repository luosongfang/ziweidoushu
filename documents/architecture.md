# 系统架构说明

> 版本：0.1.0 | 阶段：项目初始化

## 1. 系统分层

```
用户层        Next.js Web 应用
接入层        FastAPI REST API + Supabase Auth
核心业务层    命盘引擎 / AI 分析 / RAG 检索 / 用户会员
数据层        Supabase PostgreSQL + pgvector + Storage
外部服务      LLM API（OpenAI / DeepSeek / 通义等）
```

## 2. 核心模块

| 模块 | 目录位置 | 阶段 |
|------|----------|------|
| 命盘计算引擎 | `backend/app/core/chart_engine/` | 阶段 1 |
| 命盘可视化 | `frontend/src/components/chart/` | 阶段 2 |
| 用户系统 | `backend/app/api/v1/users.py` + Supabase Auth | 阶段 3 |
| AI 解读 | `backend/app/core/ai/` | 阶段 4 |
| RAG 知识库 | `knowledge/` + `database/migrations/004_*` | 阶段 4 |
| 商业化 | `frontend/src/app/pricing/` | 阶段 5 |

## 3. 数据流

1. 用户输入出生信息 → 前端表单
2. 前端调用 `POST /api/v1/charts/generate` → 后端命盘引擎
3. 引擎返回结构化 JSON → 存入 `charts` 表
4. 用户请求 AI 解读 → RAG 检索知识库 → LLM 生成 → 流式返回

## 4. 技术选型理由

- **Next.js**：SEO 友好，适合商业化落地页
- **FastAPI**：Python 生态便于实现农历/排盘算法
- **Supabase**：一站式 Auth + DB + Storage，降低运维成本
- **pgvector**：向量检索与主库一体，无需额外向量数据库

详细目录结构见项目根目录 `README.md`。
