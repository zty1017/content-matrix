# Mock 数据与 Fixture 机制

Content Matrix v0 完全基于本地 JSON 数据运行。数据分为两类：只读的 **Fixture（种子数据）** 和可写的 **Runtime（运行时数据）**。

## 目录结构

```
backend/app/data/
├── fixtures/          # 只读种子数据，随代码提交
│   ├── source_mappings.json
│   ├── video_content_assets.json
│   ├── reconstruction_tasks.json
│   ├── demo_user_asset_contexts.json
│   └── saved_reconstruction_snapshots.json
└── runtime/           # 运行时写入数据，不提交（仅保留 .gitkeep）
    ├── reconstruction_tasks.json
    └── saved_reconstruction_snapshots.json
```

## Fixture 数据说明

### source_mappings.json

来源映射表，连接外部来源标识与系统内部资产。每条记录必须包含：

- `mapping_id`：映射唯一标识
- `source_type`：来源类型（如 `preset_video`）
- `source_id`：外部来源标识
- `video_asset_id`：关联的视频资产 ID
- 可选：`task_id`、`demo_user_context_id`、`title`、`resolution_strategy`

v0 仅包含一条映射，用于演示低预算学生探店场景。

### video_content_assets.json

视频内容资产种子库，包含 9 条演示资产，覆盖三类用户上下文：

- **低预算学生**：`asset_huaian_low_budget_daytrip`、`asset_bus_accessible_foods`、`asset_under_100_local_experience`
- **效率优先上班族**：`asset_weekend_queue_avoidance`、`asset_short_city_route`、`asset_reservation_offpeak_tips`
- **本地特色体验**：`asset_huaian_cuisine_background`、`asset_old_brand_local_restaurants`、`asset_local_culture_route`

所有资产的 `source.type` 均为 `demo_seed`，`reconstruction_type` 为 `decision`。

### reconstruction_tasks.json

重构任务种子库。v0 包含一条完整的演示任务 `task_demo_p0a_low_budget_student`，其 `session_context` 描述了一位用户希望在周六下午用 2 小时、100 元以内预算体验本地特色餐厅的场景。

### demo_user_asset_contexts.json

演示用户资产上下文种子库，包含 3 条上下文记录，分别对应三类典型用户画像。每条上下文引用 3 条历史资产。

### saved_reconstruction_snapshots.json

快照种子库。v0 包含一条演示快照 `snap_demo_p0a_low_budget_student`。

## Runtime 数据行为

### 写入时机

以下操作会向 `backend/app/data/runtime/` 写入 JSON 文件：

| 操作 | 写入文件 | 说明 |
|------|----------|------|
| 创建任务 | `reconstruction_tasks.json` | 深拷贝 fixture task 并覆盖请求字段 |
| 生成卡片 | `reconstruction_tasks.json` | 更新任务状态为 `asset_complete` |
| 保存快照 | `saved_reconstruction_snapshots.json` | 新建快照记录 |

### 读取合并策略

`JsonFixtureRepository` 在读取 task 和 snapshot 时，采用 **fixture 为基、runtime 覆盖** 的合并策略：

1. 先加载 `fixtures/` 中的全部记录
2. 再加载 `runtime/` 中的记录
3. 以 ID 为键合并，runtime 记录覆盖同名 fixture 记录
4. 最终结果按 ID 排序

这意味着：

- 创建任务时，fixture 中的 `task_id` 被保留，但字段值被请求参数覆盖后写入 runtime
- 生成卡片时，同一个 `task_id` 的 runtime 记录再次被覆盖，状态得到更新
- 测试中若注入临时 `runtime_dir`，则实现完全隔离，不影响全局 fixture

### 搜索与检索行为

`RetrievalService` 和 `JsonFixtureRepository` 对 fixture 资产提供两种检索方式：

1. **自由文本搜索**：对 `asset_id`、`source.title`、`base_summary`、`content_domain_tags`、`key_points` 做大小写不敏感子串匹配
2. **标签过滤**：要求 asset 的 `content_domain_tags` **同时包含**所有传入的 tag

若 `query` 和 `tag` 均为空，返回空数组 `[]`。

## 数据校验

所有 fixture JSON 在加载时经过 Pydantic 模型校验：

- 结构不符：抛出 `FixtureRepositoryError`，进而转为 HTTP 500 领域错误
- 缺少必填键：如 `source_mappings.json` 缺少 `mapping_id` 等必填字段，同样抛出 `FixtureRepositoryError`

## 与真实数据的关系

v0 的 fixture 数据是**手工编排的演示数据**，不代表任何真实抖音视频或真实 LLM 生成结果。其目的是：

1. 验证 API 契约和 Schema 的正确性
2. 为前端集成提供稳定的响应示例
3. 支撑完整的任务工作流测试（创建 -> 生成 -> 快照）
