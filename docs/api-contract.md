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

### 12. 列出已保存快照

```
GET /api/v1/snapshots
```

返回 fixture 与 runtime 合并后的 `SavedReconstructionSnapshot[]`，用于前端展示“已转换/已保存资产库”。该列表只表示用户在本地 demo 中保存过的重构结果，不代表真实抖音收藏夹，也不会读取任何真实平台账号数据。

响应示例：

```json
[
  {
    "snapshot_id": "snap_demo_p0a_low_budget_student",
    "source_asset_id": "asset_current_techu_huaian_hotel_candidate",
    "source_task_id": "task_demo_p0a_low_budget_student",
    "card_type": "decision",
    "title": "周末探店备选",
    "saved_summary": "价格和排队情况待确认后再决定。",
    "key_decision_or_action": "确认人均与排队情况",
    "evidence_refs": ["asset_huaian_low_budget_daytrip_ev1"],
    "related_asset_refs": ["asset_huaian_low_budget_daytrip"],
    "saved_at": "2026-05-30T00:00:00Z",
    "user_note": "适合预算内备选",
    "high_risk_domain": false,
    "risk_domain_tags": []
  }
]
```

### 13. 本地视频解析演示

```
POST /api/v1/local-video/parse
```

用于演示“视频已下载，但尚未进入后端主 fixture 链路”的近实时解析入口。该端点只接受后端 registry 中登记过的 `local_reference_id`，不会接收任意文件路径，也不会访问抖音服务器。当前支持：

- `demo_unparsed_workplace_06`：06-职场短剧，适合展示剧情结构、广告植入点和可复用脚本钩子。
- `demo_unparsed_finance_12`：12-财经长视频，适合展示观点摘要、风险提示和待确认数据。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| local_reference_id | string | 是 | 后端登记过的本地视频引用 ID |
| parse_mode | string | 否 | `fallback` 或 `doubao_if_configured`，默认 `fallback` |
| demo_user_context_id | string | 否 | 用于前端标记当前演示用户模板 |

响应会返回 `LocalVideoParseResult`，包含：

- `asset`：即时构造出的 `VideoContentAsset`
- `asr`：ASR 来源、是否 fallback、转写文本和本地转写路径
- `display_blocks`：按内容类型设计的前端展示块
- `warnings`：默认不联网、使用本地兜底等说明

注意：`parse_mode=doubao_if_configured` 只表示后端边界已靠近 Doubao BigASR Flash。当前 demo 仍会返回确定性的本地 fallback 结果，避免现场网络不稳定；未来可在该边界替换为真实 `volc.bigasr.auc_turbo` 调用。

### 14. 内容魔方视图聚合

```
GET /api/v1/cube/tasks/{task_id}
```

将现有 `ReconstructionTask` 投影成前端更容易消费的 6 个魔方面。该端点不创建新状态、不调用模型、不访问外部服务，只读取 fixture/runtime 合并后的任务数据，并返回：

- `cube_state`：整体魔方状态，枚举包括 `input_ready`、`transforming`、`ready`、`blocked`、`failed`
- `animation_phase`：建议动画阶段，枚举包括 `source_resolution`、`content_reconstruction`、`matrix_linking`、`final_form`、`needs_confirmation`、`error`
- `source_status` / `asset_status` / `retrieval_status`：原始任务状态，前端可用于更细粒度动效
- `progress`：由 fixture/runtime 任务状态推导的演示进度，包含 `percent`、`message` 和 4 个固定步骤；它不代表真实后台异步任务
- `faces`：稳定的 6 个面，顺序为 `source`、`primary_card`、`related_assets`、`inferences`、`evidence`、`snapshot`

响应示例：

```json
{
  "task_id": "task_demo_douyin_08_food_low_budget",
  "video_asset_id": "asset_douyin_08_chongqing_food_daydream",
  "cube_state": "ready",
  "animation_phase": "final_form",
  "source_status": "source_ready",
  "asset_status": "asset_complete",
  "retrieval_status": "retrieval_applied",
  "progress": {
    "task_id": "task_demo_douyin_08_food_low_budget",
    "cube_state": "ready",
    "animation_phase": "final_form",
    "percent": 100.0,
    "message": "内容魔方已完成，可以点击各面查看重构结果。",
    "steps": [
      {"step_id": "source_resolution", "title": "链接映射", "phase": "source_resolution", "percent": 20.0, "status": "ready"},
      {"step_id": "content_reconstruction", "title": "内容重构", "phase": "content_reconstruction", "percent": 45.0, "status": "ready"},
      {"step_id": "matrix_linking", "title": "资产关联", "phase": "matrix_linking", "percent": 70.0, "status": "ready"},
      {"step_id": "final_form", "title": "魔方成型", "phase": "final_form", "percent": 100.0, "status": "ready"}
    ]
  },
  "faces": [
    {
      "face_id": "source",
      "face_type": "source_asset",
      "title": "原始视频与来源",
      "status": "ready",
      "target_ref": {"type": "asset", "id": "asset_douyin_08_chongqing_food_daydream"},
      "display_blocks": []
    },
    {
      "face_id": "snapshot",
      "face_type": "save_snapshot",
      "title": "保存到内容魔方",
      "status": "ready",
      "target_ref": {"type": "task", "id": "task_demo_douyin_08_food_low_budget"},
      "display_blocks": [],
      "action": {"method": "POST", "href": "/api/v1/tasks/task_demo_douyin_08_food_low_budget/save-snapshot"}
    }
  ],
  "warnings": []
}
```

推荐前端使用方式：

1. 首屏魔方面输入仍调用 `/source/resolve`、`/tasks` 或 `/local-video/parse`。
2. 创建 task 后调用 `/cube/tasks/{task_id}` 获取统一 6 面结构。
3. 若 `cube_state=transforming`，可根据 `progress.percent`、`progress.message` 和 `animation_phase` 播放魔方旋转/展开动效；v0 后端为同步 fixture 状态跳转，进度值是演示用推导值，前端仍可插值动画时间。
4. 最终点击各面时根据 `target_ref` 和 `action` 跳转或执行保存。

### 15. 内容魔方进度视图

```
GET /api/v1/cube/tasks/{task_id}/progress
```

返回与 `CubeView.progress` 相同的轻量进度对象，适合前端在魔方变换期间单独轮询。该端点只根据当前 `ReconstructionTask` 的 `source_status`、`asset_status`、`retrieval_status` 推导演示进度，不创建任务、不推进状态、不调用真实抖音或真实解析。

响应示例：

```json
{
  "task_id": "task_runtime_preset_current_techu_huaian_hotel_candidate",
  "cube_state": "transforming",
  "animation_phase": "matrix_linking",
  "percent": 70.0,
  "message": "正在关联历史资产与证据链，组装魔方面。",
  "steps": [
    {"step_id": "source_resolution", "title": "链接映射", "phase": "source_resolution", "percent": 20.0, "status": "ready"},
    {"step_id": "content_reconstruction", "title": "内容重构", "phase": "content_reconstruction", "percent": 45.0, "status": "ready"},
    {"step_id": "matrix_linking", "title": "资产关联", "phase": "matrix_linking", "percent": 70.0, "status": "ready"},
    {"step_id": "final_form", "title": "魔方成型", "phase": "final_form", "percent": 100.0, "status": "pending"}
  ]
}
```

推荐前端策略：创建 task 后立即显示 0→70 的本地插值动画，同时轮询该端点；调用 `/tasks/{task_id}/generate-card` 后再次读取进度，看到 `percent=100.0` 时切换到最终 6 面可点击状态。

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
| LLMProviderUnavailableError | `llm_provider_unavailable` | 503 | 配置的真实 LLM 提供商不可用、未实现或缺少本地密钥 |
| LLMProviderResponseError | `llm_provider_response_error` | 502 | 真实 LLM 提供商返回无法解析或不符合预期的响应 |
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

主要 `/api/v1` 端点在 OpenAPI 中附带请求或响应示例，包括 `POST /source/resolve`、`POST /assets/build`、`GET /assets/search`、`GET /demo-contexts`、`POST /tasks`、`POST /tasks/{task_id}/generate-card`、`POST /tasks/{task_id}/save-snapshot`、`GET /snapshots`、`POST /local-video/parse`、`GET /cube/tasks/{task_id}` 和 `GET /cube/tasks/{task_id}/progress`，方便前端和 QA 直接复制使用。
