# API 接口设计文档

## 1. 概述

基于 FastAPI 构建 RESTful API，为前端和外部服务提供接口。

## 2. 接口列表

### 2.1 基础信息

| 方法 | 路径 | 描述 |
|-----|------|-----|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/version | 版本信息 |

### 2.2 智能体接口

| 方法 | 路径 | 描述 |
|-----|------|-----|
| POST | /api/v1/agents/chat | 发送消息 |
| POST | /api/v1/agents/stream | 流式对话 |
| GET | /api/v1/agents/{agent_id} | 获取智能体信息 |
| PUT | /api/v1/agents/{agent_id}/config | 更新配置 |

### 2.3 记忆接口

| 方法 | 路径 | 描述 |
|-----|------|-----|
| GET | /api/v1/memories | 搜索记忆 |
| POST | /api/v1/memories | 创建记忆 |
| GET | /api/v1/memories/{memory_id} | 获取记忆详情 |
| DELETE | /api/v1/memories/{memory_id} | 删除记忆 |

### 2.4 用户接口

| 方法 | 路径 | 描述 |
|-----|------|-----|
| POST | /api/v1/users | 创建用户 |
| GET | /api/v1/users/{user_id} | 获取用户信息 |
| PUT | /api/v1/users/{user_id}/preferences | 更新偏好 |

## 3. 请求/响应示例

### 3.1 发送消息

```json
// POST /api/v1/agents/chat
{
    "message": "今天过得怎么样？",
    "user_id": "user_123",
    "agent_type": "emotion_companion",
    "context": {
        "include_memory": true,
        "memory_limit": 5
    }
}
```

### 3.2 响应

```json
{
    "response": "今天我过得挺好的，谢谢你的关心！",
    "emotion_detected": "neutral",
    "memories_used": 3,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 4. 文件结构

```
backend/src/pdns/api/
├── __init__.py
├── main.py               # FastAPI 应用
├── routes/
│   ├── __init__.py
│   ├── health.py         # 健康检查
│   ├── agents.py         # 智能体接口
│   ├── memories.py       # 记忆接口
│   └── users.py          # 用户接口
├── models/
│   ├── __init__.py
│   ├── request.py        # 请求模型
│   └── response.py       # 响应模型
└── middleware/
    ├── __init__.py
    ├── auth.py           # 认证
    └── logging.py        # 日志
```
