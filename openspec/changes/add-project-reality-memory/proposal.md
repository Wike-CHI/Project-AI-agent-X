# Change: 项目实际记录与记忆系统

## Why

当前系统缺乏对AI实际行为、用户交互和项目状态的系统性记录能力。用户无法：
- 追溯AI的决策过程和执行结果
- 跨会话保持上下文和偏好记忆
- 跟踪项目整体状态和变化趋势

需要构建一个统一的记录与记忆系统，支持短期/长期记忆、行为追踪和状态监控。

## What Changes

- 新建 `RealityRecorder` 服务：记录AI行为、决策和执行结果
- 新建 `ProjectMemory` 服务：统一管理短期/长期记忆
- 新增 API 端点（遵循现有 router 模式）：
  - `POST /record/behavior` - 记录AI行为
  - `POST /record/state` - 记录项目状态
  - `GET /memory/short` - 获取短期记忆
  - `GET /memory/long` - 获取长期记忆
- 新增数据库模型（使用 `SQLModel`）
- 支持记忆自动总结和过期清理
- 复用现有 `QdrantStore` 进行语义搜索

## Impact

- Affected specs: 新建 `project-reality` 和 `memory` 两个 capability
- Affected code:
  - `backend/app/record/` - 新建记录服务模块
  - `backend/app/api/record.py` - 新建记录API路由
  - `backend/app/models/record_models.py` - 新增数据表模型
  - `backend/app/memory/` - 扩展现有memory模块（复用 `VectorStore`）
