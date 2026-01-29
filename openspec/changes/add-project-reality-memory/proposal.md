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
- 新增 API 端点：
  - `POST /api/v1/record/behavior` - 记录AI行为
  - `POST /api/v1/record/state` - 记录项目状态
  - `GET /api/v1/memory/short` - 获取短期记忆
  - `GET /api/v1/memory/long` - 获取长期记忆
- 新增数据库表存储记录和记忆数据
- 支持记忆自动总结和过期清理

## Impact

- Affected specs: 新建 `project-reality` 和 `memory` 两个 capability
- Affected code:
  - `backend/app/record/` - 新建记录服务模块
  - `backend/app/api/record.py` - 新建记录API路由
  - `backend/app/models/database.py` - 新增数据表
  - `backend/app/memory/` - 扩展现有memory模块
