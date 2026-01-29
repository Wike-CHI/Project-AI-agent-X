# AI Companion Backend - FastAPI Application

## 快速启动 (Windows)

### 1. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量文件
copy .env.example .env

# 编辑 .env (可选，如果你有 API Key)
notepad .env
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 数据库 (可选)

默认使用内存存储，无需安装数据库。

### 启用 Qdrant (向量数据库)

1. 下载 Qdrant: https://github.com/qdrant/qdrant/releases
2. 解压运行 `qdrant.exe`
3. 在 `.env` 中设置:
   ```
   QDRANT_ENABLED=true
   ```

### 启用 Neo4j (图数据库)

1. 下载 Neo4j Desktop: https://neo4j.com/download/
2. 创建本地数据库，设置密码
3. 在 `.env` 中设置:
   ```
   NEO4J_ENABLED=true
   NEO4J_PASSWORD=你的密码
   ```

---

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   ├── core/             # 配置和安全
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic 模式
│   ├── services/         # 业务逻辑
│   ├── agents/           # AI 智能体
│   ├── rag/              # RAG 相关
│   ├── memory/           # 记忆管理
│   └── crews/            # CrewAI 团队
├── tests/                # 测试文件
├── .env.example          # 环境变量示例
├── requirements.txt      # Python 依赖
└── Dockerfile            # Docker 配置 (可选)
```

## 技术栈

- **FastAPI**: Web 框架
- **CrewAI**: 多智能体框架
- **Agno**: 学习记忆框架
- **LlamaIndex**: RAG 框架
- **Qdrant**: 向量数据库 (可选)
- **Neo4j**: 图数据库 (可选)
- **SQLModel**: ORM

## License

MIT
