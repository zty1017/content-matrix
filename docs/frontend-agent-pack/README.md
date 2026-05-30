# Content Matrix 前端 UI/UX Agent 交付包

本包面向本地 AI 编码 agent，用于实现 `content-matrix` 前端 MVP。

## 核心结论

- 前端 MVP 优先桌面大屏，不以移动端为核心。
- 技术栈建议：React + TypeScript + React Three Fiber + Drei + Framer Motion + Zustand + Tailwind CSS。
- 主视觉是标准三阶魔方：3×3×3，用户可整体拖拽旋转，但不能手动拧层。
- 系统动画必须真实可见地表现魔方层旋转、打乱、还原。
- 后端 API 要接入，但首版必须有 typed demo fallback，保证演示稳定。
- 演示不要求现场真实解析抖音链接；优先使用本地 fixture / fallback 结果完成稳定展示。
- 资产库采用左侧可收起的上下分层玻璃陈列柜。
- 魔方工坊首版做可演示的轻量版本，后续增强项保留在 Roadmap。

## 文件说明

| 文件 | 用途 |
|---|---|
| `01-product-uiux-spec.md` | 产品定位、页面模式、核心交互、信息架构 |
| `02-implementation-plan.md` | 前端实现计划、组件拆分、开发顺序 |
| `03-types-and-api-mapping.md` | TypeScript 类型建议、后端 API 映射、fallback 策略 |
| `04-animation-spec.md` | 魔方、陈列柜、工坊、保存入柜等动效规范 |
| `05-workshop-and-cabinet-spec.md` | 资产陈列柜与魔方工坊详细设计 |
| `06-mvp-scope-and-roadmap.md` | MVP 范围、暂缓项、后续增强 |
| `07-agent-checklist.md` | 给本地 agent 的执行检查清单 |
| `demo-data-shape.json` | 本地 typed fallback 数据结构示例 |
