# 后端架构说明

Content Matrix 后端采用分层架构，代码位于 `backend/app/` 下。每一层职责单一，测试覆盖充分，且全部基于离线 fixture 运行。

## 分层结构

```
backend/app/
├── main.py                  # FastAPI 应用工厂与启动入口
├── api/
│   ├── error_handlers.py    # 全局异常处理注册
│   └── v1/
│       ├── router.py        # v1 路由聚合
│       ├── source.py        # 来源解析端点
│       ├── assets.py        # 资产构建与检索端点
│       ├── demo_contexts.py # 演示上下文端点
│       └── tasks.py         # 任务工作流端点
├── core/
│   ├── config.py            # Pydantic Settings 配置
│   └── errors.py            # 领域异常基类与具体异常
├── schemas/
│   ├── common.py            # 公共枚举与 FlexibleSchema 基类
│   ├── assets.py            # VideoContentAsset 及相关模型
│   ├── demo_contexts.py     # DemoUserAssetContext 与 bundle
│   ├── tasks.py             # ReconstructionTask 与工作流模型
│   ├── snapshots.py         # SavedReconstructionSnapshot
│   ├── feedback.py          # LLMFeedback 与提供商枚举
│   └── errors.py            # API 错误响应 Schema
├── repositories/
│   └── json_repository.py   # JsonFixtureRepository 读写层
└── services/
    ├── source_resolver.py   # 来源解析服务
    ├── asset_builder.py     # 资产构建服务
    ├── retrieval.py         # 检索服务（demo-contexts / search）
    ├── task_state.py        # 任务创建与状态读取
    ├── reconstruction_generator.py  # 卡片生成服务
    ├── snapshot_service.py  # 快照保存服务
    └── llm_client.py        # LLM 客户端边界（仅 mock）
```

## 关键设计决策

### 1. 应用工厂模式

`main.py` 中的 `create_app(settings=None)` 是唯一的应用构造入口。它负责：

- 初始化 FastAPI 实例（带标题、版本、调试开关）
- 挂载 CORS 中间件（基于 `Settings.allowed_origins`）
- 注册领域异常处理器
- 包含 `/health` 健康检查端点
- 挂载 `/api/v1` 业务路由

模块级变量 `app = create_app()` 供 Uvicorn 直接引用，同时工厂模式支持测试中注入自定义 `Settings`。

### 2. 路由聚合

`api/v1/router.py` 使用 `APIRouter` 将各业务模块路由合并到统一的 `/api/v1` 前缀下。即使路由表为空，也会通过空 mount 保证 `/api/v1` 路径可见。

### 3. 配置管理

`core/config.py` 使用 `pydantic-settings` 的 `BaseSettings`：

- 自动读取 `.env` 文件
- 默认全部为安全 mock 值
- `allowed_origins` 支持逗号分隔字符串，通过 `mode="before"` validator 解析
- `get_settings()` 使用 `lru_cache` 避免重复构造

### 4. 错误处理

`core/errors.py` 定义了 `DomainError` 基类，包含 `code`、`status_code`、`message`、`detail` 四个属性。具体异常包括：

- `NotFoundError`（404）
- `InvalidSourceError`（400）
- `ConstrainedRequestError`（422）
- `FixtureDataError`（500）

`api/error_handlers.py` 将这些异常统一序列化为 `{code, message, detail}` JSON 响应。FastAPI 原生的参数校验 422 错误保持默认格式不变，不做覆盖。

### 5. 仓储层

`JsonFixtureRepository` 是 v0 唯一的数据访问层：

- `fixtures/` 目录：只读种子数据，随代码提交
- `runtime/` 目录：运行时写入的任务和快照数据，不提交
- 支持 fixture 与 runtime 数据的 ID 级合并（runtime 覆盖 fixture）
- 所有读取结果按 ID 排序，保证确定性

### 6. 服务层

每个服务类接收可选的 `JsonFixtureRepository` 参数，测试中可注入基于临时目录的仓库实例，实现真正的隔离。

服务之间不直接耦合，而是通过依赖注入在路由层组合。例如 `tasks.py` 使用 `Depends(get_task_state_service)` 等函数提供默认实例，测试中通过 `app.dependency_overrides` 替换。

## 数据流示例

以“创建任务 -> 生成卡片 -> 保存快照”为例：

1. 客户端 `POST /api/v1/tasks`，`TaskStateService.create_task` 校验 source_mapping，深拷贝 fixture task 并覆盖 session_context，写入 runtime JSON
2. 客户端 `POST /api/v1/tasks/{task_id}/generate-card`，`ReconstructionGenerator.generate_card` 校验任务状态（拒绝 draft 和高风险任务），更新状态为 `asset_complete`，写入 runtime JSON
3. 客户端 `POST /api/v1/tasks/{task_id}/save-snapshot`，`SnapshotService.save_snapshot` 校验 `asset_status == asset_complete`，构造 `SavedReconstructionSnapshot`，写入 runtime JSON
