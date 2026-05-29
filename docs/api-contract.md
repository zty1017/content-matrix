# API 契约说明

本文档列出 v0 已实现的全部端点，包括请求/响应概要和错误信封格式。所有业务端点均以 `/api/v1` 为前缀。

## 端点清单

### 1. 健康检查

```
GET /health
```

响应示例：

```json
{
  "status": "ok",
  "app": "content-matrix",
  "version": "0.0.1",
  "mode": "mock"
}
```

### 2. 来源解析

```
POST /api/v1/source/resolve
```

将用户输入的来源标识解析为系统内部资产映射。支持三种 `source_type`：

- `preset`：通过 `source_id` 直接匹配 fixture 中的 source_mapping
- `douyin_url`：验证 URL 形状（必须包含 `douyin.com`），并在 fixture 的 mapping 中查找匹配的 token
- `upload_reference`：通过 `upload_reference_id` 匹配 mapping

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source_type | string | 是 | 枚举：`preset`、`douyin_url`、`upload_reference` |
| source_id | string | 条件 | `source_type=preset` 时必填 |
| source_url | string | 条件 | `source_type=douyin_url` 时必填 |
| upload_reference_id | string | 条件 | `source_type=upload_reference` 时必填 |

响应示例：

```json
{
  "resolved_source_id": "preset_current_techu_huaian_hotel_candidate",
  "source_type": "preset",
  "mapping_id": "mapping_demo_current_techu_huaian_hotel_candidate",
  "video_asset_id": "asset_current_techu_huaian_hotel_candidate",
  "task_id": "task_demo_p0a_low_budget_student",
  "demo_user_context_id": "ctx_low_budget_student",
  "title": "这条探店视频适合我周六下午去吗？",
  "resolution_strategy": "cache_matched"
}
```

### 3. 资产构建

```
POST /api/v1/assets/build
```

根据已解析的 `resolved_source_id` 构建完整的 `VideoContentAsset`。

请求体：

```json
{
  "resolved_source_id": "preset_current_techu_huaian_hotel_candidate"
}
```

响应包含 `asset_id`、`status`、`source_resolution` 和完整的 `asset` 对象。

### 4. 获取单个资产

```
GET /api/v1/assets/{asset_id}
```

返回指定 `asset_id` 的 `VideoContentAsset` 详情。若 asset 不存在，返回 404 领域错误。

### 5. 资产搜索

```
GET /api/v1/assets/search
```

查询参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 自由文本，对 asset 的多个字段做大小写不敏感子串匹配 |
| tag | string[] | 可多次传入，要求 asset 的 `content_domain_tags` 同时包含所有指定 tag |

当 `query` 和 `tag` 均为空时，返回空数组 `[]`（HTTP 200）。

### 6. 列出演示上下文

```
GET /api/v1/demo-contexts
```

返回全部 `DemoUserAssetContext` 列表，按 `demo_user_context_id` 排序。

### 7. 获取单个演示上下文

```
GET /api/v1/demo-contexts/{context_id}
```

返回指定上下文的详情，不存在时返回 404 领域错误。

### 8. 创建重构任务

```
POST /api/v1/tasks
```

根据 `source_id` 创建一条运行时 `ReconstructionTask`。系统会查找 fixture 中的 source_mapping，深拷贝关联的 fixture task，并用请求中的 `session_context`、`asset_kind` 等字段覆盖；新任务会生成 `task_runtime_*` ID，避免覆盖 fixture task 或同一来源的历史运行时任务。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source_id | string | 是 | 映射到 source_mapping 的 source_id |
| source_type | string | 否 | 使用 `/source/resolve` 返回的公开来源类型（如 `preset`）；后端会兼容 fixture 内部的 `preset_video` 映射名 |
| session_context | object | 否 | 用户会话上下文 |
| demo_user_context_id | string | 否 | 演示上下文 ID |
| asset_kind | string | 否 | 枚举：`formal`、`draft` |

创建成功后，task 被写入 `backend/app/data/runtime/reconstruction_tasks.json`，例如 `task_runtime_preset_current_techu_huaian_hotel_candidate`。

### 9. 获取任务详情

```
GET /api/v1/tasks/{task_id}
```

返回指定任务的当前状态。支持读取 fixture 和 runtime 合并后的数据。

### 10. 生成卡片

```
POST /api/v1/tasks/{task_id}/generate-card
```

触发任务卡片生成。v0 实现为同步状态转换：

- 若 `asset_kind == draft`，返回 422 约束错误（必须先补齐事实）
- 若任务标记为 `high_risk_domain`，返回 422 约束错误（需用户确认）
- 否则将 `asset_status` 更新为 `asset_complete`，并写入 `generated_outputs`

### 11. 保存快照

```
POST /api/v1/tasks/{task_id}/save-snapshot
```

将已生成卡片的任务保存为快照。要求 `asset_status == asset_complete`，否则返回 422 约束错误。

请求体字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 快照标题，默认取卡片标题 |
| user_note | string | 用户备注 |

快照写入 `backend/app/data/runtime/saved_reconstruction_snapshots.json`。

## 错误信封

### 领域错误格式

所有由后端主动抛出的领域错误，统一返回以下 JSON 结构：

```json
{
  "code": "not_found",
  "message": "Reconstruction task was not found.",
  "detail": {
    "resource": "reconstruction_task",
    "identifier": "task_missing"
  }
}
```

字段说明：

- `code`：机器可读的错误码字符串
- `message`：人类可读的错误描述
- `detail`：可选的对象，携带与具体错误相关的上下文（如字段名、资源类型、ID 等）

### 已定义的错误码与状态码

| 错误类 | code | HTTP 状态码 | 典型场景 |
|--------|------|-------------|----------|
| NotFoundError | `not_found` | 404 | 资源不存在 |
| InvalidSourceError | `invalid_source` | 400 | 来源类型或标识无法解析 |
| ConstrainedRequestError | `constrained_request` | 422 | 业务约束未满足（如 draft 任务、高风险任务） |
| FixtureDataError | `fixture_data_failure` | 500 | fixture 数据加载或校验失败 |
| LLMProviderUnavailableError | `llm_provider_unavailable` | 503 | 配置了非 mock 的 LLM 提供商（v0 仅支持 mock） |
| LLMProviderUnsupportedError | `llm_provider_unsupported` | 400 | 配置了未知的 LLM 提供商名称 |

### FastAPI 参数校验错误

当请求体或路径参数未通过 Pydantic/FastAPI 校验时，返回 **默认的 FastAPI 422 格式**，不做覆盖：

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "item_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "not-an-int"
    }
  ]
}
```

注意：此时响应 **不包含** `code` 和 `message` 顶层字段，仅包含默认的 `detail` 数组。

## OpenAPI 与文档

服务启动后，可通过以下地址访问自动生成的 API 文档：

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- OpenAPI JSON：`http://localhost:8000/openapi.json`

主要 `/api/v1` 端点在 OpenAPI 中附带请求或响应示例，包括 `POST /source/resolve`、`POST /assets/build`、`GET /assets/search`、`GET /demo-contexts`、`POST /tasks`、`POST /tasks/{task_id}/generate-card` 和 `POST /tasks/{task_id}/save-snapshot`，方便前端和 QA 直接复制使用。
