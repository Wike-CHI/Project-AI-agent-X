## 1. 数据库模型设计
- [ ] 1.1 使用 `SQLModel` 定义 `RealityRecord` 模型（行为记录）
- [ ] 1.2 使用 `SQLModel` 定义 `ProjectState` 模型（项目状态）
- [ ] 1.3 使用 `SQLModel` 定义 `ShortTermMemory` 模型（短期记忆）
- [ ] 1.4 使用 `SQLModel` 定义 `LongTermMemory` 模型（长期记忆）

## 2. 核心服务实现
- [ ] 2.1 实现 `RealityRecorder` 服务类（使用 `AsyncSession`）
- [ ] 2.2 实现 `ProjectMemory` 服务类（短期记忆）
- [ ] 2.3 实现 `LongTermMemory` 服务类（复用 `QdrantStore`）
- [ ] 2.4 实现记忆自动总结机制（使用 LLM）
- [ ] 2.5 实现记忆过期清理任务（后台任务）

## 3. API 端点实现（遵循现有 router 模式）
- [ ] 3.1 创建 `POST /record/behavior` - 记录AI行为
- [ ] 3.2 创建 `POST /record/state` - 记录项目状态
- [ ] 3.3 创建 `GET /record/states` - 获取项目状态历史
- [ ] 3.4 创建 `GET /memory/short` - 获取短期记忆
- [ ] 3.5 创建 `GET /memory/long` - 获取长期记忆
- [ ] 3.6 创建 `DELETE /memory/{id}` - 删除记忆
- [ ] 3.7 在 `routes.py` 中注册新路由

## 4. 与现有系统集成
- [ ] 4.1 在 `ChatService` 中集成行为记录
- [ ] 4.2 在 `Agent` 执行时自动记录决策
- [ ] 4.3 复用现有 `GraphMemory` 服务的关系追踪
- [ ] 4.4 复用现有 `QdrantStore` 进行长期记忆语义搜索
- [ ] 4.5 复用现有 `get_db()` 依赖注入获取 `AsyncSession`

## 5. 测试
- [ ] 5.1 编写服务单元测试
- [ ] 5.2 编写 API 集成测试
- [ ] 5.3 编写记忆检索测试
- [ ] 5.4 测试记忆过期清理功能

## 6. 文档
- [ ] 6.1 更新 API 文档
- [ ] 6.2 编写使用指南
