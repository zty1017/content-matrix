# 02. 前端实现计划

## 1. 技术栈

推荐：

```text
Vite + React + TypeScript
React Three Fiber + Drei
Framer Motion
Zustand
Tailwind CSS
```

使用 TypeScript 是明确建议。该项目前端存在大量状态、数据结构、动画阶段、后端契约和 fallback 数据，TS 能降低本地 AI agent 写错字段、状态串用和 API 映射错误的概率。

## 2. 桌面端优先

MVP 只优先桌面大屏：

```text
最佳展示：1920×1080
主开发基准：1440×900
最低可用：1366×768
```

平板尽量可浏览，手机提示使用桌面端或只做极简预览。

## 3. 推荐目录结构

```text
frontend/
├── src/
│   ├── types/
│   │   ├── api.ts
│   │   ├── cube.ts
│   │   ├── assets.ts
│   │   ├── workshop.ts
│   │   └── demo.ts
│   ├── data/
│   │   ├── demoScenarios.ts
│   │   └── fallbackCabinetAssets.ts
│   ├── lib/
│   │   ├── apiClient.ts
│   │   ├── demoFallback.ts
│   │   ├── cubeAdapter.ts
│   │   ├── localStorage.ts
│   │   └── animationSequences.ts
│   ├── store/
│   │   ├── useAppStore.ts
│   │   ├── useCubeStore.ts
│   │   ├── useCabinetStore.ts
│   │   └── useWorkshopStore.ts
│   ├── components/
│   │   ├── layout/
│   │   ├── cube/
│   │   ├── cabinet/
│   │   ├── panels/
│   │   ├── workshop/
│   │   └── common/
│   └── App.tsx
```

## 4. 开发顺序

1. 定义 TypeScript 类型和本地 demo 数据。
2. UI 骨架：TopNav、中央魔方占位、左侧陈列柜、右侧面板、底部输入条、阶段状态栏。
3. 主魔方 3D：标准 3×3×3 外观、整体拖拽、面点击。
4. 系统层旋转动画：打乱、还原、停止在 3/4 视角。
5. 一键体验流程：三示例切换、历史资产注入、结果态。
6. 资产陈列柜：收起 / 半展开 / 全展开，搜索、筛选、预览、多选。
7. 右侧六面详情。
8. 保存入柜。
9. 魔方工坊轻量版。
10. 后端 API 接入与 fallback。

## 5. 状态管理建议

Zustand store：

```text
useAppStore:
- currentMode: current | cabinet | workshop
- demoMode: prefer_backend | force_fallback
- animationSpeed
- currentDemoContext
- apiBaseUrl

useCubeStore:
- currentCubeView
- selectedFaceId
- cubeInteractionState
- isAnimating
- narrativeStage
- processEvents

useCabinetStore:
- cabinetState: collapsed | half | expanded
- assets
- shelves
- selectedAssetIds
- previewAssetId
- searchQuery
- filterMode
- relationPreviewState

useWorkshopStore:
- selectedAssets
- semanticBlocks
- selectedBlockIds
- recombinationTarget
- outputStyle
- workshopStage
- resultCube
```

## 6. Demo 控制面板

首版不做完整设置页，但要做右上角 Demo 控制面板：

```text
后端 API 地址
数据模式：[优先后端] [强制 fallback]
动画速度：[正常] [快速] [跳过]
当前演示上下文
示例场景
操作：[测试后端连接] [重置本地演示数据]
```

## 7. localStorage

需要轻量持久化：

```text
fallback 模式下保存入柜的资产魔方
Demo 控制面板配置
当前演示上下文
是否强制 fallback
动画速度
最近选择的示例场景
```

不持久化：大型视频、完整日志、复杂工坊草稿、API key、cookie、token、敏感信息。

## 8. 工程约束

- 所有复杂状态必须用 enum / union type。
- 不允许散落字符串状态。
- API 响应必须通过 adapter 转为 UI 类型。
- fallback 数据必须与 UI 类型一致。
- 3D 魔方逻辑和业务面板逻辑分离。
- 动画 sequence 独立管理，不要散落在组件里。
- 陈列柜不能实现成普通列表。
- 首页不能实现成普通上传页。
