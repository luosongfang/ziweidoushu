# 部署与环境配置指南

> 版本：0.1.0

## 1. 本地开发环境

### 必备软件

| 软件 | 版本 | 下载 |
|------|------|------|
| Node.js | 20+ | https://nodejs.org |
| Python | 3.11+ | https://python.org |
| Git | 最新 | https://git-scm.com |

### 注册账号

| 服务 | 用途 | 注册地址 |
|------|------|----------|
| Supabase | 数据库 + 认证 | https://supabase.com |
| OpenAI / DeepSeek | LLM API | 对应平台 |

---

## 2. 本地启动步骤

### 步骤 1：配置环境变量

```bash
# 在项目根目录
copy .env.example .env
# 编辑 .env，填入 Supabase 和 API Key
```

### 步骤 2：启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

### 步骤 3：启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API 文档 http://localhost:8000/docs
```

### 步骤 4：初始化数据库

1. 登录 Supabase Dashboard
2. 进入 SQL Editor
3. 依次执行 `database/migrations/` 下的 001–004 文件

---

## 3. 生产部署（阶段 6）

| 组件 | 推荐平台 | 说明 |
|------|----------|------|
| 前端 | Vercel | 连接 GitHub 自动部署 |
| 后端 | Railway / Fly.io | Docker 或原生 Python |
| 数据库 | Supabase Cloud | 已托管 |
| 域名 | 阿里云 / Cloudflare | 需 ICP 备案（国内） |

### 环境变量（生产）

生产环境需在部署平台分别配置：
- Vercel：前端 `NEXT_PUBLIC_*` 变量
- Railway：后端全部 `.env` 变量

---

## 4. 健康检查

部署后验证：
- 前端：`https://your-domain.com`
- 后端：`https://api.your-domain.com/api/v1/health`
- 应返回：`{"status":"ok","service":"ziwei-ai-api"}`
