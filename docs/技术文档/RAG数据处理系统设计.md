# RAG 数据处理系统设计文档

## 1. 系统概述

基于 LlamaIndex 实现 RAG (Retrieval-Augmented Generation) 数据处理系统，为智能体提供知识检索和上下文增强能力。

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG 数据处理架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    数据源层                              │   │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│   │  │ 用户对话 │ │ 文档    │ │ 知识库  │ │ 日程事件 │       │   │
│   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    数据处理层                             │   │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│   │  │ 文本加载器   │ │ 文本分割器  │ │ 元数据提取器│        │   │
│   │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    索引构建层                             │   │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│   │  │ 向量索引    │ │ 树形索引    │ │ 关键词索引  │        │   │
│   │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    检索层                                 │   │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│   │  │ 向量检索    │ │ 混合检索    │ │ 重排序      │        │   │
│   │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    输出层                                 │   │
│   │  ┌─────────────┐ ┌─────────────┐                        │   │
│   │  │ 上下文构建  │ │ 答案生成    │                        │   │
│   │  └─────────────┘ └─────────────┘                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2. LlamaIndex 集成

### 2.1 核心组件

```python
# backend/src/pdns/rag/manager.py

from llama_index.core import (
    VectorStoreIndex,
    Settings,
    PromptTemplate,
    get_response_synthesizer
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class RAGManager:
    """RAG 管理器 - LlamaIndex 核心"""

    def __init__(self, config: Settings):
        self.config = config
        self._init_embedder()
        self._init_llm()
        self.indices = {}

    def _init_embedder(self):
        """初始化嵌入模型"""
        self.embedder = HuggingFaceEmbedding(
            model_name=self.config.embedding_model,
            device=self.config.embedding_device
        )
        Settings.embed_model = self.embedder

    def _init_llm(self):
        """初始化 LLM"""
        from llama_index.llms.ollama import Ollama
        self.llm = Ollama(
            model=self.config.llm_model,
            base_url=self.config.llm_base_url,
            temperature=self.config.llm_temperature
        )
        Settings.llm = self.llm
```

## 3. 数据源处理

### 3.1 文本加载器

```python
# backend/src/pdns/rag/loaders.py

from llama_index.core import SimpleDirectoryReader
from llama_index.core.readers import StringIterableReader

class DocumentLoader:
    """文档加载器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    async def load_from_directory(
        self,
        extensions: List[str] = [".md", ".txt", ".pdf", ".docx"]
    ) -> List[Document]:
        """从目录加载文档"""
        reader = SimpleDirectoryReader(
            input_dir=str(self.data_dir),
            file_extractor=self._get_extractors(extensions)
        )
        return reader.load_data()

    async def load_from_text(self, text: str, metadata: dict = None) -> Document:
        """从文本加载"""
        reader = StringIterableReader()
        return reader.load_data([text], metadata=metadata)

    def _get_extractors(self, extensions: List[str]) -> dict:
        """获取文件提取器"""
        extractors = {}
        if ".pdf" in extensions:
            from llama_index.core.readers import PDFReader
            extractors[".pdf"] = PDFReader()
        if ".docx" in extensions:
            from llama_index.core.readers import DocxReader
            extractors[".docx"] = DocxReader()
        return extractors
```

### 3.2 文本分割器

```python
from llama_index.core.node_parser import SentenceSplitter

class TextSplitter:
    """文本分割器"""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split(self, documents: List[Document]) -> List[TextNode]:
        """分割文档"""
        return self.splitter.get_nodes_from_documents(documents)
```

## 4. 索引构建

### 4.1 向量索引

```python
# backend/src/pdns/rag/indices.py

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore

class VectorIndexBuilder:
    """向量索引构建器"""

    def __init__(self, qdrant_store: QdrantVectorStore):
        self.qdrant_store = qdrant_store

    def build_from_documents(
        self,
        documents: List[Document],
        index_name: str
    ) -> VectorStoreIndex:
        """从文档构建向量索引"""
        storage_context = StorageContext.from_defaults(
            vector_store=self.qdrant_store
        )

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )

        return index

    def build_empty(self, index_name: str) -> VectorStoreIndex:
        """创建空索引"""
        return VectorStoreIndex.from_vector_store(
            self.qdrant_store,
            show_progress=True
        )
```

### 4.2 自定义索引

```python
class KnowledgeBaseIndex:
    """知识库专用索引"""

    def __init__(self, rag_manager: RAGManager):
        self.rag = rag_manager

    async def create_user_knowledge_index(
        self,
        user_id: str,
        documents: List[Document]
    ) -> str:
        """为用户创建知识库索引"""

        # 添加用户标识到元数据
        for doc in documents:
            doc.metadata["user_id"] = user_id
            doc.metadata["source_type"] = "user_knowledge"

        # 构建索引
        index = self.rag.build_from_documents(
            documents,
            index_name=f"user_{user_id}_knowledge"
        )

        return index.index_id

    async def create_conversation_index(
        self,
        user_id: str,
        conversation_id: str,
        messages: List[dict]
    ) -> str:
        """为对话创建索引"""
        # 将对话消息转为文档
        docs = [
            Document(
                text=msg["content"],
                metadata={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "role": msg["role"],
                    "timestamp": msg.get("timestamp")
                }
            )
            for msg in messages
        ]

        return await self.create_user_knowledge_index(user_id, docs)
```

## 5. 检索系统

### 5.1 向量检索器

```python
# backend/src/pdns/rag/retriever.py

from llama_index.core.retrievers import (
    VectorIndexRetriever,
    BM25Retriever,
    EnsembleRetriever
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

class HybridRetriever:
    """混合检索器 - 向量 + 关键词"""

    def __init__(
        self,
        vector_index: VectorStoreIndex,
        bm25_index: BM25Retriever = None
    ):
        self.vector_retriever = VectorIndexRetriever(
            index=vector_index,
            similarity_top_k=5
        )

        self.bm25_retriever = BM25Retriever.from_defaults(
            index=vector_index,
            similarity_top_k=5
        ) if bm25_index else None

    def get_ensemble_retriever(self) -> EnsembleRetriever:
        """获取集成检索器"""
        retrievers = [self.vector_retriever]
        if self.bm25_retriever:
            retrievers.append(self.bm25_retriever)

        return EnsembleRetriever(
            retrievers=retrievers,
            similarity_top_k=10
        )

    def get_query_engine(
        self,
        retriever=None,
        postprocessors=None
    ) -> RetrieverQueryEngine:
        """获取查询引擎"""
        retriever = retriever or self.get_ensemble_retriever()

        response_synthesizer = get_response_synthesizer()

        return RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=postprocessors or []
        )
```

### 5.2 重排序

```python
from llama_index.core.postprocessor import SimilarityPostprocessor, RerankPostprocessor

class Reranker:
    """重排序处理器"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 3
    ) -> List[Document]:
        """重排序文档"""
        # 准备输入
        pairs = [(query, doc.text) for doc in documents]

        # 计算相关性分数
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        )

        with torch.no_grad():
            scores = self.model(**inputs).logits.squeeze(-1)

        # 排序并返回 top_k
        sorted_indices = scores.argsort(descending=True)[:top_k]

        return [documents[i] for i in sorted_indices]
```

## 6. 上下文构建

### 6.1 上下文管理器

```python
# backend/src/pdns/rag/context.py

class ContextBuilder:
    """上下文构建器"""

    def __init__(self, rag_manager: RAGManager):
        self.rag = rag_manager

    async def build_context(
        self,
        query: str,
        user_id: str,
        conversation_history: List[dict] = None,
        max_context_length: int = 4096
    ) -> str:
        """构建检索增强上下文"""

        # 1. 检索相关知识
        knowledge = await self._retrieve_knowledge(query, user_id)

        # 2. 检索对话历史
        history = self._format_history(conversation_history)

        # 3. 检索用户偏好
        preferences = await self._retrieve_preferences(user_id)

        # 4. 合并上下文
        context_parts = [
            "=== 用户知识 ===",
            knowledge,
            "\n=== 对话历史 ===",
            history,
            "\n=== 用户偏好 ===",
            preferences
        ]

        context = "\n".join(context_parts)

        # 5. 截断到最大长度
        return self._truncate_context(context, max_context_length)

    async def _retrieve_knowledge(
        self,
        query: str,
        user_id: str
    ) -> str:
        """检索用户知识"""
        # 使用 Qdrant 检索
        results = await self.rag.retrieve(
            query=query,
            filters={"user_id": user_id},
            top_k=5
        )

        return "\n".join([
            f"- {result.content}"
            for result in results
        ])

    def _format_history(
        self,
        history: List[dict],
        max_turns: int = 5
    ) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"

        recent = history[-max_turns:]
        return "\n".join([
            f"用户: {msg.get('user', '')}\n助手: {msg.get('assistant', '')}"
            for msg in recent
        ])

    async def _retrieve_preferences(self, user_id: str) -> str:
        """检索用户偏好"""
        # 从关系数据库获取
        return "偏好信息"

    def _truncate_context(
        self,
        context: str,
        max_length: int
    ) -> str:
        """截断上下文"""
        if len(context) <= max_length:
            return context

        # 保留开头和用户查询部分
        return context[:max_length] + "\n...(内容截断)"
```

## 7. 文件结构

```
backend/src/pdns/rag/
├── __init__.py
├── manager.py            # RAG管理器
├── loaders.py            # 文档加载器
├── splitter.py           # 文本分割器
├── indices.py            # 索引构建
├── retriever.py          # 检索器
├── postprocessor.py      # 后处理器
└── context.py            # 上下文构建

data/
├── documents/            # 原始文档
├── indices/              # 索引存储
└── cache/                # 模型缓存
```

## 8. 使用示例

### 8.1 基础 RAG 查询

```python
async def rag_query_example():
    rag_manager = RAGManager(settings)

    # 加载文档
    loader = DocumentLoader(data_dir)
    documents = await loader.load_from_directory()

    # 构建索引
    index = rag_manager.build_from_documents(documents)

    # 查询
    query_engine = index.as_query_engine()
    response = query_engine.query("用户的历史偏好是什么？")

    return response
```

### 8.2 带检索增强的对话

```python
async def augmented_chat(
    rag: RAGManager,
    user_id: str,
    message: str,
    history: List[dict]
):
    # 构建上下文
    context_builder = ContextBuilder(rag)
    context = await context_builder.build_context(
        query=message,
        user_id=user_id,
        conversation_history=history
    )

    # 构建提示词
    prompt = f"""
    基于以下上下文回答用户问题。如果上下文中没有相关信息，
    请说明你不知道。

    上下文:
    {context}

    用户问题: {message}
    """

    # 调用 LLM
    response = await rag.llm.agenerate([prompt])

    return response
```
