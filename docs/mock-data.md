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

当前 fixture 包含多条稳定映射：

- `preset_current_techu_huaian_hotel_candidate`：旧版淮安探店 preset。
- `K5I9o0ITcJ8`：淮安探店的抖音风格链接 token alias，仍映射到旧版淮安任务；该视频尚未作为本地媒体下载接入。
- `w3JLRkaZ6UQ`：08-美食“昨晚做了个饿梦，梦到我又去雾都了”，主 demo 资产。
- `w3JLRkaZ6UQ_later_bbq`：07-旅行/重庆烤肉相关视频，用于演示“后续相关视频受已保存资产影响”。

这些映射只做本地 token 匹配，不访问抖音服务器。

### video_content_assets.json

视频内容资产种子库，包含 11 条演示资产。前 9 条是三类用户上下文的历史资产：

- **低预算学生**：`asset_huaian_low_budget_daytrip`、`asset_bus_accessible_foods`、`asset_under_100_local_experience`
- **效率优先上班族**：`asset_weekend_queue_avoidance`、`asset_short_city_route`、`asset_reservation_offpeak_tips`
- **本地特色体验**：`asset_huaian_cuisine_background`、`asset_old_brand_local_restaurants`、`asset_local_culture_route`

另外 2 条是本地素材映射资产：

- `asset_douyin_08_chongqing_food_daydream`：08-美食主素材，引用 asset inbox 中的本地视频、封面、Doubao ASR 和摘要路径。
- `asset_douyin_07_chongqing_bbq_travel`：07-旅行/重庆烤肉后续相关视频，用于展示已保存资产影响新视频重构。

历史资产的 `source.type` 为 `demo_seed`；本地素材资产的 `source.type` 为 `local_mapping`。所有当前卡片仍使用 `decision` 类型。

### reconstruction_tasks.json

重构任务种子库。当前包含：

- `task_demo_p0a_low_budget_student`：旧版淮安低预算探店任务。
- `task_demo_douyin_08_food_low_budget`：08-美食在低预算学生上下文下的决策卡。
- `task_demo_douyin_08_food_efficiency`：同一 08-美食视频在效率优先上下文下的决策卡。
- `task_demo_douyin_08_food_culture`：同一 08-美食视频在本地文化上下文下的决策卡。
- `task_demo_douyin_07_later_related_bbq`：后续刷到 07-旅行/重庆烤肉相关视频时，召回已保存 08-美食资产并影响新重构的演示任务。

### demo_user_asset_contexts.json

演示用户资产上下文种子库，包含 3 条上下文记录，分别对应三类典型用户画像。每条上下文引用 3 条历史资产。

### saved_reconstruction_snapshots.json

快照种子库。当前包含旧版淮安快照 `snap_demo_p0a_low_budget_student` 和 08-美食低预算快照 `snap_demo_douyin_08_food_low_budget`。这些快照表示本地 demo 中“已转换/已保存”的内容资产，不代表真实抖音收藏夹。

## Runtime 数据行为

### 本地视频解析演示 registry

`POST /api/v1/local-video/parse` 使用代码内 registry 管理“已下载但未进入主 fixture 链路”的演示视频，当前包括：

- `demo_unparsed_workplace_06`：06-职场短剧，视频已下载且已有 Doubao ASR 文件；端点默认返回本地硬编码兜底转写和剧情/广告/脚本钩子展示块。
- `demo_unparsed_finance_12`：12-财经长视频，视频已下载且已有 Doubao ASR 文件；端点默认返回本地硬编码兜底转写和观点/风险/待确认数据展示块。

该 registry 不是抖音 API，也不是任意文件上传；它只接受预登记 ID，便于现场演示“近实时解析入口”而不依赖网络。

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
3. 支撑完整的任务工作流测试（创建 -> 生成 -> 快照 -> 快照列表）
4. 演示本地资产库如何影响后续相关视频的内容重构
