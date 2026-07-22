# API 接口规范

> 版本：0.1.0 | 基础 URL：`http://localhost:8000/api/v1`

## 通用约定

- 请求格式：`application/json`
- 响应格式：`application/json`
- 认证方式：`Authorization: Bearer <supabase_jwt>`（阶段 3 启用）
- 错误响应：`{ "detail": "错误信息" }`

---

## 已实现

### GET /health

健康检查。

**响应示例：**
```json
{ "status": "ok", "service": "ziwei-ai-api" }
```

---

## 待实现（阶段 1–4）

### POST /charts/generate

生成命盘（无需登录，阶段 1）。

**请求体：**
```json
{
  "birth_datetime": "1990-05-15T14:30:00",
  "gender": "male",
  "calendar_type": "solar",
  "timezone": "Asia/Shanghai"
}
```

**响应：** 完整命盘 JSON（见 `database-schema.md` 中 `chart_data` 结构）

---

### GET /charts

获取当前用户的命盘列表（需登录，阶段 3）。

### GET /charts/{id}

获取单个命盘详情。

### DELETE /charts/{id}

删除命盘。

---

### POST /analysis/interpret

AI 解读（需登录，阶段 4）。

**请求体：**
```json
{
  "chart_id": "uuid",
  "analysis_type": "overall",
  "palace_index": null
}
```

**响应：** SSE 流式文本

---

### GET /analysis/history

获取解读历史记录。

---

## 在线文档

后端启动后访问：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc
