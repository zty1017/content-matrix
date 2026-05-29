# 前端目录占位说明

> 前端实现已在 v0 阶段被**有意延后**。当前目录仅保留集成边界与后端契约指引，方便后续前端开发者快速接入。

## 后端服务地址

- 默认本地地址：`http://localhost:8000`
- 健康检查端点：`GET /health`
- OpenAPI 机器契约：`GET /openapi.json`

## 允许的本地前端开发来源

后端 CORS 默认放行以下本地来源（可在 `.env` 中通过 `ALLOWED_ORIGINS` 调整）：

- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5173`

## 接入必读文档

1. `docs/setup.md` — 环境安装、依赖管理与启动命令
2. `docs/api-contract.md` — `/api/v1` 全部端点语义、请求/响应示例与错误包络说明
3. `docs/` — 完整中文文档目录，包含架构、领域模型、Mock 数据与 v0 范围说明
4. `/openapi.json` — 运行时自动生成的 OpenAPI Schema，可作为前端类型生成与接口联调的直接依据

## v0 范围提示

- 本阶段不创建任何前端框架代码（React/Vue/Next/Vite 等）、构建配置、UI 页面或静态资源。
- 所有业务接口均为基于 JSON Fixture 的确定性 Mock，不依赖真实抖音解析、真实 LLM 调用或数据库。
- 如需查看后端领域模型与数据结构定义，请参考 `backend/app/schemas/` 中的 Pydantic 模型。
