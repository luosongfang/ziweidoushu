# 紫微AI (Ziwei AI)

基于紫微斗数十二宫命盘，结合 AI 大语言模型的人生分析平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js + React + TypeScript + Tailwind CSS |
| 后端 | Python FastAPI |
| 数据库 | Supabase PostgreSQL |
| AI | LLM API + RAG 知识库 |

## 目录结构

```
Ziwei-AI/
├── frontend/      # Next.js 前端应用
├── backend/       # FastAPI 后端服务
├── database/      # 数据库迁移与 Schema
├── knowledge/     # RAG 知识库源文件
└── documents/     # 项目设计文档
```

## 快速开始

> 环境要求：Node.js 20+、Python 3.11+、Git

### 1. 环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 Supabase 和 LLM API 密钥
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 开发阶段

1. **阶段 0** — 项目初始化（当前）
2. **阶段 1** — 命盘计算引擎
3. **阶段 2** — 前端命盘可视化
4. **阶段 3** — 用户系统与数据持久化
5. **阶段 4** — AI 解读与 RAG
6. **阶段 5** — 商业化与支付
7. **阶段 6** — 测试与上线

详细说明见 `documents/` 目录。
