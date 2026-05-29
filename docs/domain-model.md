# 领域模型说明

Content Matrix 的领域模型使用 Pydantic v2 定义，位于 `backend/app/schemas/` 目录。所有业务 Schema 均继承自 `FlexibleSchema`（`extra="allow"`），在保持必填字段严格校验的同时，允许向后兼容的扩展字段。

## 核心枚举

定义在 `backend/app/schemas/common.py` 中：

| 枚举 | 值 | 用途 |
|------|-----|------|
| `ConfidenceLevel` | `high`、`medium`、`low` | 证据、事实、推断的可信度 |
| `ReconstructionType` | `knowledge`、`procedure`、`decision`、`experience` | 内容重构类型 |
| `CardType` | `knowledge`、`procedure`、`decision` | 主卡片类型 |
| `SourceStatus` | `received` 等 8 项 | 来源处理生命周期 |
| `AssetStatus` | `asset_pending` 等 8 项 | 资产生成生命周期 |
| `RetrievalStatus` | `retrieval_pending` 等 7 项 | 检索应用生命周期 |

## 主要模型

### VideoContentAsset（视频内容资产）

位于 `schemas/assets.py`，是系统的核心数据单元，代表从视频中提取并重构后的结构化内容。

关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| asset_id | string | 全局唯一资产标识 |
| source | AssetSource | 来源信息（类型、标题、URL、本地路径等） |
| reconstruction_type | ReconstructionType | 重构类型 |
| content_domain_tags | string[] | 内容领域标签（如“淮安”、“低预算”） |
| base_summary | string | 基础摘要 |
| key_points | string[] | 关键要点 |
| evidence | EvidenceItem[] | 证据列表 |
| facts | FactItem[] | 事实列表 |
| confidence_level | ConfidenceLevel | 整体可信度 |
| is_draft | boolean | 是否为草稿 |
| needs_confirmation | boolean | 是否需要用户确认 |
| strategy_metadata | object | 策略元数据 |
| demo_metadata | object | 演示元数据 |

### EvidenceItem（证据项）

| 字段 | 类型 | 说明 |
|------|------|------|
| evidence_id | string | 证据标识 |
| source_type | EvidenceSourceType | 证据来源类型 |
| content | string | 证据内容 |
| origin | EvidenceOrigin | 内容起源（标题、ASR、OCR 等） |
| confidence | ConfidenceLevel | 可信度 |
| needs_confirmation | boolean | 是否需要确认 |
| timestamp_range | TimestampRange | 可选的时间戳范围 |
| high_risk_domain | boolean | 是否涉及高风险领域 |
| risk_domain_tags | string[] | 风险标签 |

### FactItem（事实项）

| 字段 | 类型 | 说明 |
|------|------|------|
| fact_id | string | 事实标识 |
| type | string | 事实类型 |
| content | string | 事实内容 |
| evidence_refs | string[] | 关联证据 ID 列表 |
| entities | string[] | 提及的实体 |
| confidence | ConfidenceLevel | 可信度 |

### DraftVideoContentAsset（草稿资产）

继承自 `VideoContentAsset`，强制约束：

- `is_draft = true`
- `needs_confirmation = true`
- `confidence_level` 不能为 `high`

用于表示事实尚未补齐、需要用户确认的临时资产。

## 工作流模型

### ReconstructionTask（重构任务）

位于 `schemas/tasks.py`，代表一次完整的内容重构会话。

关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务标识 |
| video_asset_id | string | 关联的视频资产 ID |
| session_context | SessionContext | 用户会话上下文（目标、约束、偏好、场景） |
| source_status | SourceStatus | 来源状态 |
| asset_status | AssetStatus | 资产状态 |
| retrieval_status | RetrievalStatus | 检索状态 |
| primary_card | PrimaryCard | 主卡片内容 |
| asset_kind | AssetKind | `formal` 或 `draft` |
| demo_user_context_id | string | 关联的演示上下文 ID |
| related_assets | RelatedAsset[] | 关联资产列表 |
| inferences | InferenceItem[] | 系统推断列表 |
| generated_outputs | object[] | 已生成输出 |
| evidence | EvidenceItem[] | 任务级证据 |

### SessionContext（会话上下文）

| 字段 | 类型 | 说明 |
|------|------|------|
| raw_text | string | 用户原始输入文本 |
| goals | string[] | 本次目标 |
| constraints | string[] | 约束条件 |
| preferences | string[] | 用户偏好 |
| scenario | string | 场景描述 |
| high_risk_domain | boolean | 是否高风险 |
| risk_domain_tags | string[] | 风险标签 |

### PrimaryCard（主卡片）

| 字段 | 类型 | 说明 |
|------|------|------|
| card_type | CardType | 卡片类型 |
| common | object | 通用字段（如 title、summary） |
| specific | object | 类型专属字段（如 decision_level、key_factors） |
| evidence_refs | string[] | 关联证据 |
| action_entries | object[] | 行动入口 |
| display_name | string | 显示名称 |

### SavedReconstructionSnapshot（保存的快照）

位于 `schemas/snapshots.py`，代表用户保存的某一时刻的任务卡片快照。

| 字段 | 类型 | 说明 |
|------|------|------|
| snapshot_id | string | 快照标识 |
| source_asset_id | string | 来源资产 ID |
| source_task_id | string | 来源任务 ID |
| card_type | CardType | 卡片类型 |
| title | string | 快照标题 |
| saved_summary | string | 保存时的摘要 |
| key_decision_or_action | string | 关键决策或行动 |
| evidence_refs | string[] | 证据引用 |
| related_asset_refs | string[] | 关联资产引用 |
| saved_at | string | 保存时间（ISO 8601） |
| user_note | string | 用户备注 |

## 演示上下文模型

### DemoUserAssetContext（演示用户资产上下文）

位于 `schemas/demo_contexts.py`，用于在演示场景中聚合历史资产。

| 字段 | 类型 | 说明 |
|------|------|------|
| demo_user_context_id | string | 上下文标识 |
| display_name | string | 展示名称 |
| asset_ids | string[] | 包含的资产 ID 列表 |
| context_summary | string | 上下文摘要 |
| high_risk_domain | boolean | 是否高风险 |
| risk_domain_tags | string[] | 风险标签 |

## 反馈与 LLM 模型

### LLMFeedback（LLM 反馈）

位于 `schemas/feedback.py`，用于描述 LLM 调用结果。v0 仅 `mock` 提供商实际返回内容。

| 字段 | 类型 | 说明 |
|------|------|------|
| provider | LLMProvider | `mock`、`openai`、`doubao`、`deepseek`、`qwen` |
| mode | FeedbackMode | 反馈模式 |
| latency_ms | int | 延迟毫秒 |
| is_mock | boolean | 是否为 mock |
| model | string | 模型名称 |
| message_metadata | FeedbackMessageMetadata | 消息统计 |
| content | string | 反馈内容 |

## 错误响应 Schema

### ApiErrorResponse（API 错误响应）

位于 `schemas/errors.py`，用于描述非领域错误（如网关层包装）时的结构。实际领域错误直接由 `DomainError.to_payload()` 序列化，不经过此模型。

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "field": "...",
    "metadata": {}
  },
  "request_id": "..."
}
```
