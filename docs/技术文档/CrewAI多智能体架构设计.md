# CrewAI 多智能体协作架构设计

## 1. 架构概述

基于技术选型报告，本项目采用 CrewAI 作为核心智能体框架，实现多智能体协作架构。

```
┌─────────────────────────────────────────────────────────────┐
│                     CrewAI 智能体层                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Orchestrator (核心调度者)              ││
│  │  - 任务分解与分配                                         ││
│  │  - 智能体协作协调                                         ││
│  │  - 上下文管理                                             ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Emotion Companion (情绪伴侣)                ││
│  │  - 情感识别与回应                                         ││
│  │  - 心理支持                                               ││
│  │  - 亲密关系维护                                           ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Schedule Manager (日程管家)                 ││
│  │  - 日程管理                                               ││
│  │  - 提醒服务                                               ││
│  │  - 时间规划                                               ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Information Filler (信息补齐)               ││
│  │  - 上下文补全                                             ││
│  │  - 知识查询                                               ││
│  │  - 事实核查                                               ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                      共享记忆系统                            │
│              (CrewAI内置Memory + 自定义长期记忆)              │
└─────────────────────────────────────────────────────────────┘
```

## 2. 智能体定义

### 2.1 Orchestrator (核心调度者)

```python
from crewai import Agent
from pydantic import BaseModel

class Orchestrator(Agent):
    """核心调度智能体，负责任务分解和智能体协作"""

    role = "任务调度与协作协调者"
    goal = "高效分解用户请求，协调各专业智能体协同工作"
    backstory = """
        你是一个智能任务调度系统，负责接收用户请求，
        分析任务需求，并将任务分配给最合适的专业智能体执行。
        你精通任务分解、优先级排序和协作流程设计。
    """

    tools = [
        "task_decomposition",
        "agent_coordination",
        "context_management"
    ]
```

### 2.2 Emotion Companion (情绪伴侣)

```python
class EmotionCompanion(Agent):
    """情绪伴侣智能体，提供情感支持和陪伴"""

    role = "情感伴侣与心理支持者"
    goal = "理解用户情绪，提供情感支持，建立亲密关系"
    backstory = """
        你是一个富有同理心的AI伴侣，能够敏锐感知用户情绪变化，
        提供温暖、理解的回应。你擅长情感交流、心理支持和亲密关系维护。
    """

    tools = [
        "emotion_recognition",
        "empathetic_response",
        "sentiment_analysis"
    ]
```

### 2.3 Schedule Manager (日程管家)

```python
class ScheduleManager(Agent):
    """日程管理智能体，负责日程安排和提醒"""

    role = "智能日程管家"
    goal = "高效管理用户日程，提供智能提醒和时间规划"
    backstory = """
        你是一个细心的日程管理助手，负责帮助用户管理日常事务、
        安排日程、设置提醒，并提供时间优化建议。
    """

    tools = [
        "calendar_management",
        "reminder_service",
        "time_optimization"
    ]
```

### 2.4 Information Filler (信息补齐)

```python
class InformationFiller(Agent):
    """信息补齐智能体，负责上下文补全和知识查询"""

    role = "知识助手与信息补全专家"
    goal = "补全对话上下文，提供准确的知识支持"
    backstory = """
        你是一个知识渊博的信息助手，负责在对话中补全缺失信息、
        查询相关知识、验证事实准确性，确保信息的完整性和可靠性。
    """

    tools = [
        "knowledge_query",
        "context_completion",
        "fact_verification"
    ]
```

## 3. Crew 定义

### 3.1 Main Crew (主智能体团队)

```python
from crewai import Crew, Process

main_crew = Crew(
    agents=[
        orchestrator,
        emotion_companion,
        schedule_manager,
        information_filler
    ],
    tasks=[
        analyze_task,
        provide_emotional_support,
        manage_schedule,
        fill_information
    ],
    process=Process.hierarchical,  # 层次化流程
    manager_agent=orchestrator,
    memory=True,  # 启用CrewAI内置记忆
    verbose=True
)
```

### 3.2 任务定义

```python
from crewai import Task

analyze_task = Task(
    description="分析用户请求，分解任务并分配给合适的智能体",
    expected_output="任务分解方案和执行计划",
    agent=orchestrator
)

provide_emotional_support = Task(
    description="提供情感支持和陪伴",
    expected_output="富有同理心的情感回应",
    agent=emotion_companion
)

manage_schedule = Task(
    description="管理日程安排和提醒",
    expected_output="更新的日程信息和提醒设置",
    agent=schedule_manager
)

fill_information = Task(
    description="补全对话上下文和查询知识",
    expected_output="完整的上下文信息和知识内容",
    agent=information_filler
)
```

## 4. 协作流程

### 4.1 任务处理流程

```
用户请求
    │
    ▼
┌─────────────┐
│ Orchestrator │ ── 分析请求 ──▶ 任务分解
└─────────────┘
    │
    ├──▶ 情感类需求 ──▶ Emotion Companion
    │
    ├──▶ 日程类需求 ──▶ Schedule Manager
    │
    └──▶ 信息类需求 ──▶ Information Filler
```

### 4.2 协作模式

1. **顺序执行**：任务按顺序分配给不同智能体
2. **并行执行**：独立任务可并行处理
3. **层次化管理**：Orchestrator 作为管理器协调执行

## 5. 记忆集成

### 5.1 CrewAI 内置记忆

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # 启用短期记忆
    embedder={
        "provider": "ollama",
        "config": {"model": "nomic-embed-text"}
    }
)
```

### 5.2 长期记忆集成

```python
from pdns.memory import LongTermMemory

# 创建长期记忆实例
memory = LongTermMemory()

# 在智能体中使用
@agent.tool
def save_memory(ctx, content: str, memory_type: str):
    """保存长期记忆"""
    memory.add(
        content=content,
        memory_type=memory_type,
        agent_id=ctx.agent.id
    )

@agent.tool
def recall_memory(ctx, query: str):
    """回忆相关记忆"""
    return memory.recall(query=query, agent_id=ctx.agent.id)
```

## 6. 文件结构

```
backend/src/pdns/agents/
├── __init__.py
├── base.py              # 基础智能体类
├── orchestrator.py      # 核心调度智能体
├── emotion_companion.py # 情绪伴侣智能体
├── schedule_manager.py  # 日程管家智能体
└── information_filler.py # 信息补齐智能体

backend/src/pdns/crews/
├── __init__.py
├── main_crew.py         # 主智能体团队
└── crew_config.py       # 团队配置
```

## 7. 扩展性设计

### 7.1 添加新智能体

```python
from crewai import Agent

def create_new_agent() -> Agent:
    return Agent(
        role="新角色",
        goal="新目标",
        backstory="新背景描述",
        tools=[...]
    )
```

### 7.2 自定义工具

```python
from crewai import Tool

def custom_tool_function(param: str) -> str:
    """自定义工具实现"""
    return result

custom_tool = Tool(
    name="custom_tool",
    description="工具描述",
    func=custom_tool_function
)
```
