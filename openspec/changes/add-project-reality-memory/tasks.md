## 1. 数据库设计
- [ ] 1.1 设计并创建 `reality_records` 表（行为记录）
- [ ] 1.2 设计并创建 `project_states` 表（项目状态）
- [ ] 1.3 扩展现有 `memories` 表支持短期/长期记忆
- [ ] 1.4 编写数据库迁移脚本

## 2. 核心服务实现
- [ ] 2.1 实现 `RealityRecorder` 服务类
- [ ] 2.2 实现 `ProjectMemory` 服务类（短期记忆）
- [ ] 2.3 实现 `LongTermMemory` 服务类（长期记忆）
- [ ] 2.4 实现记忆自动总结机制
- [ ] 2.5 实现记忆过期清理任务

## 3. API 端点实现
- [ ] 3.1 创建 `POST /api/v1/record/behavior` - 记录AI行为
- [ ] 3.2 创建 `POST /api/v1/record/state` - 记录项目状态
- [ ] 3.3 创建 `GET /api/v1/record/states` - 获取项目状态历史
- [ ] 3.4 创建 `GET /api/v1/memory/short` - 获取短期记忆
- [ ] 3.5 创建 `GET /api/v1/memory/long` - 获取长期记忆
- [ ] 3.6 创建 `DELETE /api/v1/memory/{id}` - 删除记忆

## 4. 与现有系统集成
- [ ] 4.1 在 `ChatService` 中集成行为记录
- [ ] 4.2 在 `Agent` 执行时自动记录决策
- [ ] 4.3 集成现有 `GraphMemory` 服务
- [ ] 4.4 集成现有向量存储（Qdrant）

## 5. 测试
- [ ] 5.1 编写服务单元测试
- [ ] 5.2 编写 API 集成测试
- [ ] 5.3 编写记忆检索测试
- [ ] 5.4 测试记忆过期清理功能

## 6. 文档
- [ ] 6.1 更新 API 文档
- [ ] 6.2 编写使用指南
