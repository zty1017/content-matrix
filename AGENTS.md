# Content Matrix 协作指南

本文件给队友和 AI agent 使用，目标是让大家能从 `main` 分支直接启动后端、对接前端、同步演示资产，并避免误提交密钥或大文件。

## 当前协作基线

- 以远程 `main` 为当前 demo v0 基线。
- 后端默认是离线 mock / fixture 模式，不接真实抖音 API，不需要数据库。
- 复制的抖音链接只会在本地 `source_mappings.json` 中做 token 映射。
- 真实视频、封面、ASR、摘要等大文件不进 Git；它们放在仓库同级的 `content-matrix-asset-inbox/`。

推荐本地目录结构：

```text
douyinHackathon/
├── content-matrix/              # Git 仓库
└── content-matrix-asset-inbox/  # 网盘/压缩包同步的演示资产，不进 Git
```

## 从零开始

```bash
git clone git@github.com:zty1017/content-matrix.git
cd content-matrix/backend
uv sync --extra dev
uv run pytest
uv run uvicorn backend.app.main:app --reload
```

服务启动后：

- 健康检查：`http://localhost:8000/health`
- Swagger UI：`http://localhost:8000/docs`
- OpenAPI JSON：`http://localhost:8000/openapi.json`

如果本地还没有 `uv`，先安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 资产同步

资产目录不要提交到 Git。由负责人打包 `content-matrix-asset-inbox` 后通过网盘/飞书等方式同步。队友下载后解压到 `content-matrix` 的同级目录。

本地后端 fixture 里引用的是相对路径，例如：

```text
../content-matrix-asset-inbox/05-douyin-resolver-test-links/...
```

所以只要保持兄弟目录结构，路径就能对上。

## 后端主 demo API 流程

内容魔方主流程建议前端按这个顺序调用：

```text
POST /api/v1/source/resolve
POST /api/v1/tasks
GET  /api/v1/cube/tasks/{task_id}
GET  /api/v1/cube/tasks/{task_id}/progress
POST /api/v1/tasks/{task_id}/generate-card
GET  /api/v1/cube/tasks/{task_id}
POST /api/v1/tasks/{task_id}/save-snapshot
GET  /api/v1/snapshots
```

常用演示输入：

- 08-美食主素材 token：`w3JLRkaZ6UQ`
- 淮安旧链路 alias：`K5I9o0ITcJ8`
- 本地未预解析职场视频：`demo_unparsed_workplace_06`
- 本地未预解析财经视频：`demo_unparsed_finance_12`

内容魔方聚合端点：

```http
GET /api/v1/cube/tasks/{task_id}
```

返回固定 6 个面：

- `source`
- `primary_card`
- `related_assets`
- `inferences`
- `evidence`
- `snapshot`

进度端点：

```http
GET /api/v1/cube/tasks/{task_id}/progress
```

该进度是 fixture/runtime 状态推导的演示进度，不是真实后台异步任务。前端可以用它驱动魔方旋转、变换、进度文案。

## 文档入口

- `docs/setup.md`：环境安装、资产同步、启动、测试命令。
- `docs/api-contract.md`：全部 API 端点和请求/响应说明。
- `docs/mock-data.md`：fixture、runtime、本地视频 registry 说明。
- `docs/v0-scope-and-exclusions.md`：哪些是真实接入，哪些仍是 mock。
- `docs/architecture.md`：后端分层结构。
- `docs/domain-model.md`：Pydantic schema 和领域模型。

## 禁止事项

- 不要提交 `.env`、真实 API key、cookie、账号密码。
- 不要提交 `backend/app/data/runtime/*.json`。
- 不要把 `content-matrix-asset-inbox/`、视频、音频、封面大文件直接塞进普通 Git。
- 不要在 v0 demo 中接真实抖音 API；当前叙事是本地 fixture 映射。
- 不要修改已通过的 API 契约后不更新测试和文档。

## Git 协作建议

- 日常开发先从 `main` 拉最新代码。
- 小改动可在自己的 feature 分支完成后合并；不要 force push `main`。
- commit message 沿用现有语义化风格，例如 `feat: ...`、`fix: ...`、`docs: ...`、`test: ...`。
- 合并前至少运行：

```bash
cd backend
uv run pytest
```
