# 03. TypeScript 类型与 API 映射

## 1. 类型原则

建立三层：

```text
后端 API 类型 → adapter → 前端 UI 类型
fallback demo 类型 → adapter → 前端 UI 类型
```

不要在组件中直接猜后端字段。

## 2. 核心 API 类型

```ts
export type CubeState = "input_ready" | "transforming" | "ready" | "blocked" | "failed";

export type CubeAnimationPhase =
  | "source_resolution"
  | "content_reconstruction"
  | "matrix_linking"
  | "final_form"
  | "needs_confirmation"
  | "error";

export type CubeFaceId =
  | "source"
  | "primary_card"
  | "related_assets"
  | "inferences"
  | "evidence"
  | "snapshot";

export interface CubeFace {
  face_id: CubeFaceId;
  face_type: string;
  title: string;
  status: string;
  target_ref?: { type: string; id: string } | null;
  display_blocks: Array<Record<string, unknown>>;
  action?: Record<string, unknown> | null;
}

export interface CubeProgressStep {
  step_id: string;
  title: string;
  phase: CubeAnimationPhase;
  percent: number;
  status: string;
}

export interface CubeProgress {
  task_id: string;
  cube_state: CubeState;
  animation_phase: CubeAnimationPhase;
  percent: number;
  message: string;
  steps: CubeProgressStep[];
}

export interface CubeView {
  task_id: string;
  video_asset_id: string;
  cube_state: CubeState;
  animation_phase: CubeAnimationPhase;
  source_status: string;
  asset_status: string;
  retrieval_status: string;
  progress: CubeProgress;
  faces: CubeFace[];
  warnings: string[];
}
```

## 3. UI 类型建议

```ts
export interface UiCubeFace {
  id: CubeFaceId;
  label: string;
  subtitle?: string;
  status: "empty" | "loading" | "ready" | "needs_confirmation" | "blocked" | "failed" | "disabled";
  icon: string;
  accent: "cyan" | "blue" | "violet" | "amber" | "red" | "neutral";
  summaryItems: string[];
  detailBlocks: UiDetailBlock[];
  isAiExtracted?: boolean;
  isManuallyEnhanced?: boolean;
  isConfirmed?: boolean;
  needsConfirmation?: boolean;
  highRisk?: boolean;
}

export interface UiDetailBlock {
  type:
    | "summary"
    | "key_points"
    | "actions"
    | "evidence"
    | "related_assets"
    | "inferences"
    | "source_preview"
    | "snapshot_form"
    | "custom";
  title: string;
  items?: string[];
  data?: unknown;
}

export interface UiCubeModel {
  taskId: string;
  assetId: string;
  title: string;
  state: CubeState;
  phase: CubeAnimationPhase;
  faces: Record<CubeFaceId, UiCubeFace>;
  progress: CubeProgress;
  referencedAssetIds: string[];
  warnings: string[];
}
```

## 4. 资产陈列柜类型

```ts
export type AssetStatus = "formal" | "draft" | "needs_confirmation";
export type AssetType = "knowledge" | "decision" | "experience" | "procedure" | "script";

export interface AssetCube {
  id: string;
  title: string;
  shortSummary: string;
  type: AssetType;
  status: AssetStatus;
  scenarioTags: string[];
  sourceType: "douyin" | "local_video" | "manual" | "demo_seed" | "fallback";
  cover?: string;
  cubeView?: UiCubeModel;
  usedCount?: number;
  lastUsedFor?: string;
  currentTaskReferenced?: boolean;
  manuallyConfirmed?: boolean;
  highRisk?: boolean;
  needsConfirmation?: boolean;
  createdAt?: string;
}

export interface CabinetShelf {
  id: string;
  title: string;
  description?: string;
  assetIds: string[];
  kind: "current_related" | "recent" | "frequent" | "draft" | "type" | "scenario" | "search";
}
```

## 5. 工坊类型

```ts
export type WorkshopBlockType =
  | "summary"
  | "evidence"
  | "preference"
  | "constraint"
  | "tag"
  | "inference"
  | "source"
  | "script_hook";

export interface WorkshopBlock {
  id: string;
  type: WorkshopBlockType;
  title: string;
  content: string;
  sourceAssetId: string;
  selected: boolean;
  weight?: number;
  confidence?: "high" | "medium" | "low";
  needsConfirmation?: boolean;
}

export type OutputStyle =
  | "compact_card"
  | "decision_advice"
  | "knowledge_explanation"
  | "script_reuse"
  | "evidence_strict";
```

## 6. 后端端点映射

主链路：

```text
GET  /health
POST /api/v1/source/resolve
POST /api/v1/tasks
GET  /api/v1/cube/tasks/{task_id}
GET  /api/v1/cube/tasks/{task_id}/progress
POST /api/v1/tasks/{task_id}/generate-card
GET  /api/v1/cube/tasks/{task_id}
POST /api/v1/tasks/{task_id}/save-snapshot
GET  /api/v1/snapshots
```

本地视频演示：

```text
POST /api/v1/local-video/parse
```

## 7. Fallback 策略

默认：优先后端。  
后端失败：自动 fallback。  
Demo 控制：可强制 fallback。

触发 fallback：

- `/health` 不通；
- API 超时；
- API 返回非预期结构；
- 强制 fallback；
- 示例魔方后端无对应数据。

UI 轻量标记 `Demo fallback`，不要大面积警告。
