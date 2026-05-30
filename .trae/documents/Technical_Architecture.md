# 技术架构文档 - Content Matrix 前端 Web Demo

## 1. 技术栈
- 构建工具：Vite
- 核心框架：React + TypeScript
- 样式方案：Tailwind CSS
- 图标库：lucide-react

## 2. 项目结构规划
```text
frontend/
├── src/
│   ├── api/
│   │   └── api.ts (封装后端请求)
│   ├── components/
│   │   ├── VideoCard.tsx
│   │   ├── AICollectButton.tsx
│   │   ├── ProcessingTimeline.tsx
│   │   ├── BasicAssetCard.tsx
│   │   ├── DemoUserSwitcher.tsx
│   │   ├── RelatedAssetCard.tsx
│   │   ├── InfluenceTypeBadge.tsx
│   │   ├── DecisionCard.tsx
│   │   ├── SnapshotList.tsx
│   │   └── DebugJsonPanel.tsx
│   ├── views/
│   │   ├── MainDemo.tsx
│   │   └── AssetLibrary.tsx
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
```

## 3. API 接口集成
根据演示流程，将集成以下 API：
1. `POST /api/v1/source/resolve`: 解析抖音链接。
2. `POST /api/v1/assets/build`: 构建资产。
3. `GET /api/v1/demo-contexts`: 获取三个用户上下文。
4. `GET /api/v1/tasks/{task_id}`: 读取预置任务 (例如 `task_demo_douyin_08_food_low_budget`)。
5. `POST /api/v1/tasks/{task_id}/save-snapshot`: 保存当前判断快照。
6. `GET /api/v1/snapshots`: 获取快照列表。
7. `GET /api/v1/assets/search`: 资产库搜索。

## 4. 关键实现逻辑
- **三栏布局**：桌面端采用典型的左(视频)、中(资产化与上下文)、右(决策判断)布局。
- **模拟延迟**：资产化过程不真正走异步队列，前端使用 300-600ms 的 `setTimeout` 模拟进度条和状态更新。
- **数据展示**：将 `primary_card` 结构拆分展示，明确显示决策等级、影响类型、来源引用等。
