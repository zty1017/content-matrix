# v0 范围与明确排除项

本文档说明 Content Matrix v0 **已经实现**和**明确未实现**的内容，避免前后端集成时产生错误假设。

## v0 已实现的能力

1. **后端骨架**：FastAPI 应用工厂、CORS、OpenAPI 文档、健康检查 `/health`
2. **业务 API**：`/api/v1` 下的 10 个业务端点（来源解析、资产构建/获取/搜索、演示上下文、任务创建/状态/卡片生成/快照保存）
3. **领域模型**：完整的 Pydantic Schema 层（资产、证据、事实、任务、卡片、快照、上下文、LLM 反馈）
4. **错误契约**：统一的 `{code, message, detail}` 领域错误信封，保留 FastAPI 默认 422 格式
5. **Mock 数据层**：JSON fixture 仓库 + runtime 写入机制，覆盖任务和快照生命周期
6. **离线 LLM 边界**：`LLMClient` 仅支持 `mock` 提供商，其他提供商返回明确的 503 错误
7. **配置管理**：基于 `pydantic-settings` 的环境变量与 `.env` 支持
8. **测试套件**：覆盖 API、Schema、错误契约、仓储层、LLM 边界、前端占位符的完整 pytest 用例
9. **前端占位**：`frontend/README.md` 说明 CORS  origin 和集成入口点，无实际框架代码

## 明确未实现的能力

以下功能在 v0 **不存在**，文档和代码中均不应声称已支持：

### 1. 真实抖音解析

- **不存在**：访问抖音服务器、解析真实视频链接、下载视频元数据或封面
- **实际情况**：`source/resolve` 仅对 `douyin_url` 做形状校验（域名必须包含 `douyin.com`），然后在本地 fixture 的 `source_mappings.json` 中查找匹配的 token
- **影响**：任何不在 fixture 中的真实抖音链接都会返回 `invalid_source` 错误

### 2. 真实 LLM 生成

- **不存在**：调用 OpenAI、豆包、DeepSeek、通义千问或其他任何真实 LLM API
- **实际情况**：`LLMClient.generate_feedback()` 仅在 `llm_provider == mock` 时返回固定格式的 mock 内容；配置为其他提供商会直接抛出 `llm_provider_unavailable` 错误
- **影响**：卡片生成（`/tasks/{task_id}/generate-card`）是同步的状态转换，不涉及真实模型推理

### 3. 数据库持久化

- **不存在**：PostgreSQL、MySQL、SQLite、Redis、MongoDB 或任何数据库
- **实际情况**：所有数据存储在本地 JSON 文件中。fixture 数据在 `backend/app/data/fixtures/`，运行时数据在 `backend/app/data/runtime/`
- **影响**：服务重启后 runtime 数据仍然保留（因为写入磁盘），但不具备数据库的事务、并发控制或备份能力

### 4. 部署与运维

- **不存在**：Dockerfile、docker-compose、CI/CD 流水线、K8s 配置、日志聚合、监控告警
- **实际情况**：仅支持本地 `uv run uvicorn` 启动
- **影响**：v0 不是可部署的生产服务

### 5. 前端 UI

- **不存在**：React、Vue、Angular、Svelte 或任何前端框架代码
- **实际情况**：`frontend/` 目录仅包含 `README.md`，说明后端 API 地址和 CORS 配置
- **影响**：v0 没有可交互的用户界面，所有测试均通过 HTTP 客户端或 TestClient 完成

### 6. 异步任务队列

- **不存在**：Celery、RQ、APScheduler、消息队列或后台工作进程
- **实际情况**：任务状态转换（创建 -> 生成卡片 -> 保存快照）全部是同步 HTTP 调用
- **影响**：不存在轮询、回调或 WebSocket 推送机制

### 7. 真实用户认证

- **不存在**：JWT、OAuth、Session、Cookie、API Key 认证
- **实际情况**：所有端点均为公开访问，v0 不区分用户身份
- **影响**：`demo_user_context_id` 是演示数据的分组标识，不是登录用户 ID

### 8. 嵌入与语义检索

- **不存在**：向量数据库、文本嵌入、语义相似度计算、机器学习排序
- **实际情况**：资产搜索是简单的子串匹配和标签交集过滤
- **影响**：搜索结果的相关性由 fixture 数据的人工标签决定，而非模型计算

## 升级提示

从 v0 向后续版本演进时，以下模块需要替换或增强：

| 模块 | v0 实现 | 未来方向 |
|------|---------|----------|
| 来源解析 | 本地 fixture token 匹配 | 真实抖音 API / 爬虫解析 |
| 资产构建 | fixture 深拷贝 | ASR / OCR / 关键帧提取 + LLM 结构化 |
| 卡片生成 | 同步状态转换 | 真实 LLM 调用 + 异步任务队列 |
| 数据存储 | JSON 文件 | 关系型数据库 + 缓存层 |
| 搜索检索 | 子串 + 标签 | 向量语义搜索 + 混合排序 |
| 前端 | README 占位 | React / Vue 等框架实现 |
| 部署 | 本地启动 | 容器化 + 云部署 |
