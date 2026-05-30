# 环境安装与运行指南

本文档说明如何在本地使用 `uv` 安装依赖、运行服务并执行测试。

## 前置条件

- Python 3.12 或更高版本
- `uv` 已安装（若未安装，可通过官方脚本获取：`curl -LsSf https://astral.sh/uv/install.sh | sh`）

## 安装依赖

进入项目根目录并安装可编辑包（含开发依赖）：

```bash
cd /home/ubuntu/projects/douyinHackathon/content-matrix
uv pip install -e "backend[dev]"
```

这会安装 `fastapi[standard]`、`pydantic-settings`、`python-dotenv`、`uvicorn`，以及测试所需的 `httpx`、`pytest` 和 `pytest-asyncio`。

## 启动服务

### 开发模式（热重载）

```bash
uv run uvicorn backend.app.main:app --reload
```

### 生产模式（单次运行）

```bash
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

服务启动后，默认端点为 `http://localhost:8000`。

## 环境变量

项目支持通过 `.env` 文件或环境变量覆盖默认配置。根目录已提供 `.env.example` 作为参考。关键配置项包括：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | Content Matrix | 应用名称 |
| `APP_VERSION` | 0.0.1 | 版本号 |
| `DEBUG` | False | 调试模式 |
| `API_V1_PREFIX` | /api/v1 | API 前缀 |
| `ALLOWED_ORIGINS` | 见下方 | CORS 允许的源 |
| `LLM_PROVIDER` | mock | LLM 提供商 |
| `LLM_MOCK_MODE` | True | 是否使用 Mock LLM |
| `LLM_MODEL` | mock-content-matrix-v0 | LLM 模型名；美团 LongCat 本地测试可设为 `LongCat-2.0-Preview` |
| `MEITUAN_API_KEY` | 空 | 美团 LongCat API Key，仅保存在本地 `.env`，不要提交 |
| `MEITUAN_BASE_URL` | https://api.longcat.chat/openai | OpenAI-compatible LongCat base URL |
| `LLM_REQUEST_TIMEOUT_SECONDS` | 30 | 真实 provider 请求超时秒数 |
| `LLM_MAX_TOKENS` | 1024 | 真实 provider 单次最大输出 token 数 |
| `LLM_TEMPERATURE` | 0.7 | 真实 provider 采样温度 |

如需本地试用美团 LongCat，请在本地 `.env` 中设置：

```bash
LLM_PROVIDER=meituan
LLM_MODEL=LongCat-2.0-Preview
LLM_MOCK_MODE=false
MEITUAN_API_KEY=你的本地开发密钥
```

`.env` 不应提交到 Git；默认 `LLM_MOCK_MODE=true` 仍会走离线 mock。

默认 `ALLOWED_ORIGINS` 包含三个本地前端地址：

- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5173`

如需在 `.env` 中自定义，使用逗号分隔：

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 运行测试

### 运行全部测试

```bash
uv run pytest backend/tests/
```

### 运行单个测试文件

```bash
uv run pytest backend/tests/test_app_baseline.py
uv run pytest backend/tests/test_docs_contract.py
```

### 常用 pytest 选项

```bash
# 显示详细输出
uv run pytest -v backend/tests/

# 仅运行上次失败的用例
uv run pytest --lf backend/tests/

# 生成覆盖率报告（需额外安装 pytest-cov）
uv run pytest --cov=backend.app backend/tests/
```

## 验证服务健康状态

服务启动后，可通过以下命令快速检查：

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{
  "status": "ok",
  "app": "content-matrix",
  "version": "0.0.1",
  "mode": "mock"
}
```

## 目录结构说明

```
content-matrix/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 业务路由
│   │   ├── core/            # 配置与错误定义
│   │   ├── data/
│   │   │   ├── fixtures/    # 只读种子数据（JSON）
│   │   │   └── runtime/     # 运行时写入数据（JSON）
│   │   ├── repositories/    # JSON 仓储层
│   │   ├── schemas/         # Pydantic 领域模型
│   │   └── services/        # 业务服务层
│   ├── tests/               # 测试套件
│   └── pyproject.toml       # 后端依赖与包配置
├── docs/                    # 本文档目录
├── frontend/                # v0 仅含占位 README
└── .env.example             # 环境变量示例
```
