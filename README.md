# AI Companion - Personal Digital Nervous System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![React Native](https://img.shields.io/badge/React%20Native-0.75.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A personal AI companion powered by multi-agent architecture**

</div>

## 快速启动 (Windows)

### 后端 (FastAPI)

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制环境变量
copy .env.example .env

# 4. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端 (React Native Desktop)

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm start

# 3. 新终端运行 Windows 端
npm run windows
```

---

## 项目结构

```
Project-AI-agent-X/
├── backend/                 # FastAPI 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 配置和安全
│   │   ├── models/         # 数据模型
│   │   ├── agents/         # AI 智能体
│   │   ├── rag/            # RAG 相关
│   │   ├── memory/         # 记忆管理
│   │   └── crews/          # CrewAI 团队
│   ├── tests/              # 测试
│   └── requirements.txt
├── frontend/               # React Native 前端
│   ├── src/
│   │   ├── screens/        # 页面 (Home, Chat, Memory, Settings)
│   │   ├── services/       # API 服务
│   │   ├── store/          # 状态管理
│   │   └── navigation/     # 导航
│   └── package.json
└── docs/                   # 文档
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 多智能体 | CrewAI + Agno |
| RAG | LlamaIndex |
| 前端 | React Native Desktop |
| 数据库 | SQLite (默认) / Qdrant + Neo4j (可选) |
| LLM | OpenAI / Claude / 通义千问 (多模型) |

## API 文档

启动后端后访问: http://localhost:8000/docs

## 数据库 (可选)

默认使用内存存储，无需安装。

如需启用持久化存储：

- **Qdrant**: 下载 https://github.com/qdrant/qdrant/releases
- **Neo4j**: 下载 https://neo4j.com/download/

详见 [docs/本地数据库安装指南.md](docs/本地数据库安装指南.md)

## 文档

- [产品需求文档](docs/产品文档/产品需求文档PRD.md)
- [技术架构](docs/技术文档/项目架构总览.md)
- [API设计](docs/技术文档/API接口设计.md)
- [CrewAI多智能体](docs/技术文档/CrewAI多智能体架构设计.md)
- [RAG系统](docs/技术文档/RAG数据处理系统设计.md)
- [记忆存储](docs/技术文档/记忆存储系统设计.md)

## License

MIT
