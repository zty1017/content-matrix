# Content Matrix 中文文档

Content Matrix 是一个面向本地生活视频内容的知识重构系统。v0 版本已完成后端骨架、Mock API、领域模型和基础测试套件，主链路默认基于离线数据运行，不依赖真实抖音解析、真实 LLM 调用或数据库存储；本地开发可显式开启美团 LongCat provider 测试 LLM 边界。

## 文档导航

| 文档 | 内容 |
|------|------|
| [setup.md](./setup.md) | 环境安装、启动、测试命令 |
| [architecture.md](./architecture.md) | 后端分层结构与技术选型 |
| [api-contract.md](./api-contract.md) | 已实现的全部端点与错误契约 |
| [domain-model.md](./domain-model.md) | 领域模型与 Pydantic Schema |
| [mock-data.md](./mock-data.md) | Fixture 与运行时 JSON 数据机制 |
| [v0-scope-and-exclusions.md](./v0-scope-and-exclusions.md) | v0 明确不包含的能力 |

## 快速启动

```bash
cd /home/ubuntu/projects/douyinHackathon/content-matrix
uv run uvicorn backend.app.main:app --reload
```

服务默认运行在 `http://localhost:8000`，可通过以下地址查看交互式文档：

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 核心设计原则

1. **离线优先**：主链路数据和逻辑都在本地 JSON fixture 中完成，默认不访问外部网络。
2. **Mock 驱动**：抖音解析、数据库持久化均使用 Mock 或占位实现；LLM 默认使用 Mock，可在本地 `.env` 中显式开启美团 LongCat provider。
3. **Schema 严格**：Pydantic v2 负责请求/响应校验和序列化，错误信封统一为 `{code, message, detail}`。
4. **前端就绪**：CORS 默认放行 `localhost:3000`、`localhost:5173` 和 `127.0.0.1:5173`。

## 技术栈

- Python 3.12+
- FastAPI + Uvicorn
- Pydantic v2 + pydantic-settings
- uv（环境管理与依赖安装）
- pytest（测试框架）

## 版本信息

当前后端版本：`0.0.1`
运行模式：`mock`
