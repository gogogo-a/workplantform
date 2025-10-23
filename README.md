# 无人系统云端 RAG 应用

基于**检索增强生成（RAG）**技术的企业级智能问答系统，专注于无人系统领域的知识库构建与智能检索。

---

## 📋 项目概述

本项目旨在构建一套高性能的云端知识库问答系统，通过 RAG 技术实现：
- 📚 大规模文档的智能检索
- 🤖 精准的 AI 问答
- 🔍 可溯源的答案生成
- ⚡ 高性能的向量检索

---

## ✅ 已完成功能

### 1. 核心基础架构

#### 1.1 数据库层
- ✅ **MongoDB 集成**
  - 基于 Beanie ODM 的异步文档映射
  - 单例连接模式，支持连接池
  - 数据模型：`DocumentModel`（文档）、`MessageModel`（消息）、`UserInfoModel`（用户）
  - 完整的 CRUD 操作支持

- ✅ **Milvus 向量数据库**
  - 单例连接管理
  - 支持集合创建、删除、查询
  - COSINE 相似度检索
  - Docker Compose 一键部署（包含 MinIO、Attu 可视化工具）
  - 1024维向量存储

#### 1.2 统一模型管理系统
- ✅ **模型配置架构**
  - 基于继承的模型配置基类（`BaseModelConfig`）
  - 分类管理：LLM、Embedding、Reranker
  - 统一的 `ModelManager` 管理器
  - 支持本地模型（`type: "local"`）和云端模型（`type: "cloud"`）

- ✅ **已集成模型**
  - **LLM**: Ollama Llama 3.2（本地）、DeepSeek Chat（云端）
  - **Embedding**: BGE-large-zh-v1.5（1024维）、BGE-base-zh-v1.5、Text2vec-base-chinese
  - **Reranker**: BGE-reranker-v2-m3、BGE-reranker-large、BGE-reranker-base

### 2. 核心服务层

#### 2.1 LLM 服务（`internal/llm/llm_service.py`）
- ✅ **模型调用**
  - 统一的 LLM 接口，支持本地和云端模型切换
  - 简化 API：支持 `user_message`（推荐）和 `messages`（高级用法）
  - 自动历史记录管理（`use_history=True`）
  - 流式和非流式对话支持
  
- ✅ **高级功能**
  - 系统 Prompt 管理
  - 工具调用能力（Tool Use）
  - 延迟总结机制：在下次对话前自动执行总结
    - 触发条件：消息数 >= 10 或 token 数超过阈值
    - 同步执行（`summarize_history()`）
    - 自动替换历史记录
  - 参数验证：禁止同时传递 `user_message` 和 `messages`

#### 2.2 ChatService 会话服务（`internal/chat_service/chat_service.py`）🆕
- ✅ **统一会话管理**
  - Session 和 User 管理
  - Redis 历史记录持久化（可配置过期时间）
  - 自动历史记录管理
  - 自动 Redis 同步
  
- ✅ **Agent 集成**
  - 统一的 `chat()` 方法，支持普通对话和 Agent 对话
  - 通过 `use_agent=True` 启用 ReAct Agent
  - 自动创建 ReAct Agent
  - 可控历史粒度（`save_only_answer`）
    - `True`: 只保存问答（推荐，简洁）
    - `False`: 保存完整思考过程（调试用）
  - 自动清理中间推理步骤
  
- ✅ **简化 API**
  ```python
  # ✅ 普通对话
  for chunk in chat_service.chat("你好"):
      print(chunk, end="")
  
  # ✅ Agent 对话（1 行，全自动）
  answer = chat_service.chat(
      user_message="你的问题",
      use_agent=True,
      agent_tools={"knowledge_search": knowledge_search},
      save_only_answer=True  # 只保存问答
  )
  ```

#### 2.3 ReAct Agent（`internal/agent/react_agent.py`）🆕
- ✅ **真正的 ReAct 框架**
  - Thought → Action → Observation 循环
  - 真实工具调用（非伪造）
  - 防止循环和重复 Action
  - 强制使用 Observation 内容（禁止编造）
  
- ✅ **智能控制**
  - 自动检测 LLM 生成 Observation 并截断
  - 检测重复 Action 并强制给出 Answer
  - 最多 5 轮推理（可配置）
  - 详细的调试输出

#### 2.4 Redis 缓存服务（`internal/db/redis.py`）🆕
- ✅ **单例连接管理**
  - 自动连接和重连
  - 连接池支持
  
- ✅ **完整的 CRUD 操作**
  - 基础操作：`get`, `set`, `delete`, `exists`
  - 过期管理：`expire`, `ttl`
  - Hash 操作：`hset`, `hget`, `hgetall`
  - List 操作：`lpush`, `rpush`, `lpop`, `rpop`, `lrange`
  - Set 操作：`sadd`, `srem`, `smembers`, `scard`
  - Sorted Set 操作：`zadd`, `zrange`, `zrem`
  - Pub/Sub：`publish`, `subscribe`

#### 2.5 Session 模型（`internal/model/session.py`）🆕
- ✅ **会话管理**
  - `SessionModel`: 会话模型（uuid, user_id, create_at, update_at）
  - `MessageModel`: 新增 `session_id` 字段，关联会话
  - 支持多会话管理

#### 2.6 Prompt 管理（`pkg/agent_prompt/`）
- ✅ **多场景 Prompt 模板**
  - `DEFAULT_PROMPT`: 通用对话
  - `RAG_PROMPT`: 基于知识库的问答
  - `AGENT_RAG_PROMPT`: ReAct Agent 专用 Prompt 🆕
  - `CODE_PROMPT`: 代码生成与解释
  - `DOCUMENT_PROMPT`: 文档分析
  - `SUMMARY_PROMPT`: 聊天历史总结
  
- ✅ **工具定义**（`agent_tool.py`）
  - `knowledge_search`: 知识库搜索（已实现）
  - IDE 可点击跳转

#### 2.7 Embedding 服务（`internal/embedding/embedding_service.py`）
- ✅ **文本向量化**
  - 基于 `sentence-transformers` 
  - 支持文档批量编码（`encode_documents`）
  - 支持查询编码（`encode_query`，带归一化）
  - 单例模式，避免重复加载
  - 智能设备选择（CPU/CUDA/MPS）
  - HuggingFace 离线模式支持 🆕

#### 2.8 Reranker 服务（`internal/reranker/reranker_service.py`）
- ✅ **检索结果重排序**
  - 基于 `FlagEmbedding` 的 BGE Reranker
  - 语义相关性二次评分
  - 支持自定义分数阈值（默认 -100.0）
  - Logits 输出（-100 到 +10，分数越高越相关）
  - 智能设备选择（CPU/CUDA/MPS）
  - HuggingFace 离线模式支持 🆕

#### 2.9 文档处理服务（`internal/document/document_processor.py`）
- ✅ **多格式文档支持**
  - `.txt`、`.pdf`、`.docx` 格式
  - 基于 LangChain 的文档加载器
  
- ✅ **文档处理流程**
  - `add_documents_to_mongodb`: 保存原始文档到 MongoDB，生成 UUID
  - `add_document_chunks_to_milvus`: 文档分割、向量化、存储到 Milvus
  - `add_documents`: 完整的文档入库流程编排
  - 可配置 chunk_size（默认500）和 chunk_overlap（默认50）
  - 依赖注入设计，避免循环依赖

#### 2.10 RAG 检索服务（`internal/rag/rag_service.py`）
- ✅ **智能检索流程**
  1. **向量检索**: 在 Milvus 中检索 Top-K 候选文档
  2. **Reranker 重排序**: 语义相关性二次评分（可选）
  3. **智能去重**: 过滤相似度 >= 98% 的重复文档
  4. **上下文生成**: 格式化为 LLM 可用的上下文

- ✅ **检索特性**
  - 支持元数据过滤
  - 可配置检索数量（默认5个）
  - Reranker 可开关
  - 自动去重，保证结果多样性

### 3. 测试与演示

- ✅ **完整测试套件**
  - `test/test_mongodb.py`: MongoDB CRUD 测试
  - `test/test_milvus.py`: Milvus 连接和检索测试
  - `test/test_redis.py`: Redis 操作测试 🆕
  - `test/test_rag.py`: RAG 完整流程测试（对比 Reranker 效果）
  - `test/test_summary_mechanism.py`: 延迟总结机制测试 🆕
  - `test/test_chat_service.py`: ChatService 完整测试 🆕
  - `test/test_full_rag_qa.py`: **完整的 RAG QA 演示（ChatService + Agent 架构）** 🆕

- ✅ **交互式 RAG QA Demo**（`test/test_full_rag_qa.py`）
  - **ChatService 架构**: Session 管理 + Redis 持久化
  - **ReAct Agent**: 真实工具调用，完整推理过程
  - **智能检索**: 向量匹配 + Reranker + 去重
  - **历史管理**: 可选保存完整思考过程或只保存问答
  - **交互命令**: `history`（查看历史）、`clear`（清空）、`exit`（退出）
  - 真实文档处理（.docx）
  - MongoDB + Milvus 双重存储
  - 实时向量检索
  - 流式 LLM 对话

### 4. 开发环境与配置

- ✅ **完整的依赖管理**
  - `requirements.txt`: 所有 Python 依赖
  - `.gitignore`: Git 忽略规则
  - `env_template.txt`: 环境变量模板

- ✅ **环境配置**（`pkg/constants/constants.py`）
  - **统一配置管理**: 所有配置从 `.env` 加载
  - **智能设备选择**: 自动检测 CUDA/MPS/CPU
  - **HuggingFace 离线模式**: 避免联网检查 🆕
    - `TRANSFORMERS_OFFLINE=1`
    - `HF_HUB_OFFLINE=1`
  - **Redis 配置**: Host、Port、DB、Password 🆕
  - **导入顺序优化**: 确保环境变量在库导入前设置 🆕

- ✅ **Docker 部署**
  - `milvus/docker-compose.yml`: Milvus 生态一键部署
    - Milvus 向量数据库
    - MinIO 对象存储
    - Attu 可视化管理界面（http://localhost:8000）
  - Redis 部署（推荐 Docker）

---

## 🎯 架构亮点 🆕

### 1. 分层架构 - 单一职责原则
```
┌─────────────────────────────────────────────────┐
│             ChatService（会话层）                 │
│  - Session 管理                                  │
│  - Redis 持久化                                  │
│  - Agent 编排                                    │
│  - 历史记录粒度控制                               │
└──────────────┬──────────────────────────────────┘
               │
        ┌──────┴───────┐
        ▼              ▼
┌─────────────┐  ┌─────────────┐
│ LLMService  │  │ ReActAgent  │
│ - 模型调用   │  │ - 工具调用   │
│ - Prompt    │  │ - 推理循环   │
│ - 历史管理   │  │ - 强制约束   │
└─────────────┘  └─────────────┘
```

**优势**：
- ✅ 各层职责清晰，易于测试和维护
- ✅ ChatService 统一入口，屏蔽底层复杂性
- ✅ LLMService 专注对话，Agent 专注工具调用
- ✅ Session、Redis、历史记录由 ChatService 统一管理

### 2. 简化 API - 降低使用难度
```python
# ❌ 旧方式（7+ 行，容易出错）
llm = LLMService(...)
agent = create_react_agent(llm, tools)
answer = agent.run(question)
llm.add_to_history("user", question)
llm.add_to_history("assistant", answer)
chat_service._save_history_to_redis()

# ✅ 新方式（统一的 chat 方法）
# 普通对话
for chunk in chat_service.chat("你好"):
    print(chunk, end="")

# Agent 对话（1 行，全自动）
answer = chat_service.chat(
    user_message="问题",
    use_agent=True,
    agent_tools={"knowledge_search": knowledge_search}
)
```

### 3. 智能历史管理
- **延迟总结**：不阻塞当前对话，在下次对话前执行
- **自动同步**：历史记录自动保存到 Redis
- **可控粒度**：`save_only_answer=True` 只保存问答，自动清理中间推理
- **Session 隔离**：多用户、多会话互不干扰

### 4. 环境变量优化
```python
# 🔥 关键：constants.py 必须最先导入
from pkg.constants.constants import RUNNING_MODE  # 设置环境变量

from sentence_transformers import SentenceTransformer  # HuggingFace 库
```

**优势**：
- ✅ 自动设置 `TRANSFORMERS_OFFLINE` 和 `HF_HUB_OFFLINE`
- ✅ 避免 HuggingFace 库联网检查
- ✅ 智能设备选择（CUDA/MPS/CPU）
- ✅ 统一配置管理，易于部署

---

## 🚧 计划中功能

### 第一阶段：API 层和前端

#### 1. FastAPI 路由（`api/v1/`）
- ⏳ **文档管理 API**
  - `POST /api/v1/documents/upload`: 文档上传
  - `GET /api/v1/documents`: 文档列表
  - `DELETE /api/v1/documents/{id}`: 删除文档
  - `GET /api/v1/documents/{id}/chunks`: 查看文档分块

- ⏳ **问答 API**
  - `POST /api/v1/chat`: 流式对话接口
  - `POST /api/v1/search`: 向量检索接口
  - `GET /api/v1/chat/history`: 聊天历史
  - `DELETE /api/v1/chat/clear`: 清空历史

- ⏳ **用户管理 API**
  - `POST /api/v1/auth/login`: 用户登录
  - `POST /api/v1/auth/register`: 用户注册
  - `GET /api/v1/users/me`: 获取当前用户信息

#### 2. 前端界面
- ⏳ Web UI（React/Vue）
  - 文档上传界面
  - 实时问答界面（流式显示）
  - 聊天历史管理
  - 文档管理界面

### 第二阶段：高级功能

#### 1. 溯源系统
- ⏳ **答案溯源**
  - 在生成的答案中插入角标 [1][2]
  - 点击角标显示原始文档片段
  - 高亮显示匹配内容
  - 支持跳转到原始文档

#### 2. 缓存与会话管理
- ✅ **Redis 集成**（`internal/db/redis.py`）🆕
  - 单例连接管理
  - 完整的 CRUD 操作
  - 多轮对话历史存储
  - 用户会话管理（Session + User）
  - 自动过期管理
  
- ⏳ **高级缓存策略**
  - 热点数据缓存
  - 检索结果缓存
  - 缓存预热

#### 3. 异步处理优化
- ⏳ **Kafka 消息队列**（`internal/Kafka/`）
  - 文档上传后异步触发 Embedding
  - 大批量文档处理队列
  - 任务状态追踪
  - 失败重试机制

### 第三阶段：企业级特性

#### 1. 性能优化
- ⏳ **检索性能提升**
  - Milvus 分区和分片
  - 向量索引优化（IVF_FLAT → HNSW）
  - 批量检索优化
  - 结果缓存策略

- ⏳ **并发处理**
  - 异步文档处理
  - 并发 Embedding
  - 流式结果返回

#### 2. 多模型支持
- ⏳ 集成更多 LLM 模型
  - 通义千问（Qwen）
  - ChatGPT（GPT-4）
  - 文心一言（ERNIE）
  - Claude

#### 3. 高级 RAG 技术
- ⏳ **混合检索**
  - 向量检索 + 关键词检索（BM25）
  - 融合排序

- ⏳ **查询优化**
  - 查询改写（Query Rewrite）
  - 查询扩展（Query Expansion）
  - HyDE（假设性文档 Embedding）

- ⏳ **上下文压缩**
  - LLMLingua 上下文压缩
  - 动态 chunk 选择

#### 4. 监控与日志
- ⏳ **系统监控**
  - 检索性能监控
  - Token 消耗统计
  - API 调用统计
  - 错误日志收集

#### 5. 权限与安全
- ⏳ **用户权限系统**
  - 基于角色的访问控制（RBAC）
  - 文档权限管理
  - API 鉴权（JWT）

### 第四阶段：部署与交付

- ⏳ **完整 Docker 化**
  - 所有服务的 Docker 镜像
  - Docker Compose 一键部署
  - Kubernetes 编排支持

- ⏳ **CI/CD 流程**
  - 自动化测试
  - 自动化部署
  - 版本管理

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层（计划中）                         │
│                    Web UI / Mobile App                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API 层（FastAPI - 计划中）                 │
│          /chat  /search  /documents  /auth                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       核心服务层 ✅                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ LLM Service │  │ RAG Service  │  │ Doc Processor│       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Embedding  │  │   Reranker   │  │ Prompt Mgmt  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       模型管理层 ✅                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           统一模型管理器（ModelManager）                │   │
│  │  LLM Models | Embedding Models | Reranker Models    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据存储层                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ MongoDB  │  │  Milvus  │  │  Redis   │  │  Kafka   │   │
│  │    ✅     │  │    ✅     │  │   ⏳     │  │   ⏳     │   │
│  │  文档数据  │  │  向量数据  │  │  缓存    │  │  消息队列 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3.9 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制模板并创建 `.env` 文件：

```bash
cp env_template.txt .env
```

然后编辑 `.env`，主要配置项：

```bash
# ==================== AI 模型配置 ====================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 运行模式（控制 Embedding 和 Reranker 的设备）
RUNNING_MODE=cpu  # 可选: cpu, cuda, mps, gpu, auto

# HuggingFace 模型配置（避免联网检查）🆕
TRANSFORMERS_OFFLINE=1  # 使用本地缓存
HF_HUB_OFFLINE=1        # 禁用在线检查
# HF_ENDPOINT=https://hf-mirror.com  # 可选：使用镜像

# ==================== 数据库配置 ====================
# MongoDB
MONGODB_URL=mongodb://root:rootpassword@localhost:27017/
MONGODB_DATABASE=rag_platform

# Milvus 向量数据库
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=root
MILVUS_PASSWORD=rootpassword
MILVUS_DB_NAME=rag_platform

# Redis 缓存 🆕
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 可选

# ==================== 其他配置 ====================
# Token 限制配置（用于聊天历史总结）
MAX_TOKEN_LIMIT_FOR_SUMMARY=6400
```

### 3. 启动数据库服务

```bash
# 启动 Milvus（向量数据库）
cd milvus
docker-compose up -d

# 访问 Attu 可视化界面
# http://localhost:8000

# 启动 Redis（缓存服务）🆕
docker run -d --name redis -p 6379:6379 redis:latest

# 或者使用持久化
docker run -d --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:latest redis-server --appendonly yes
```

### 4. 下载模型（首次运行）🆕

```bash
# Ollama 模型
ollama pull llama3.2

# HuggingFace 模型（会自动下载到 ~/.cache/huggingface/）
# 首次运行时会自动下载，或者手动：
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-zh-v1.5')"
python -c "from FlagEmbedding import FlagReranker; FlagReranker('BAAI/bge-reranker-v2-m3')"

# 下载完成后，在 .env 中设置离线模式
TRANSFORMERS_OFFLINE=1
HF_HUB_OFFLINE=1
```

### 5. 运行 RAG QA 演示

```bash
# 首次运行：处理文档并存储
python test/test_full_rag_qa.py

# 后续运行：注释掉文档处理步骤
# 在 test_full_rag_qa.py 的 main() 函数中注释掉：
# success = await process_and_store_documents(doc_folder, collection_name)

# 交互式命令：
# - 输入问题进行提问
# - 'history': 查看历史记录
# - 'clear': 清空历史
# - 'exit' 或 'quit': 退出
```

---

## 📊 Rerank 分数说明

BGE Reranker 输出的是 **logits**（未归一化分数）：

- **范围**: 通常在 `-10` 到 `+10` 之间
- **规则**: **分数越高，相关性越强**
- **示例**:
  ```
  -0.39  ← 最相关（最高分）
  -1.08  ← 第二相关
  -4.02  ← 第三相关
  -6.12  ← 相关性较低
  ```

---

## 📁 项目结构

```
plantform/
├── api/                    # API 路由（计划中）
│   └── v1/
├── internal/               # 核心业务逻辑 ✅
│   ├── db/                 # 数据库连接
│   │   ├── mongodb.py      # MongoDB（Beanie ODM）✅
│   │   ├── milvus.py       # Milvus 向量数据库 ✅
│   │   ├── milvus_config.py # Milvus 优化配置 ✅
│   │   └── redis.py        # Redis 缓存 ✅ 🆕
│   ├── model/              # 数据模型 ✅
│   │   ├── document.py     # 文档模型
│   │   ├── message.py      # 消息模型（带 session_id）🆕
│   │   ├── session.py      # 会话模型 🆕
│   │   └── user_info.py    # 用户模型
│   ├── llm/                # LLM 服务 ✅
│   │   └── llm_service.py  # 统一 LLM 接口（简化 API）🆕
│   ├── chat_service/       # 会话服务 ✅ 🆕
│   │   ├── chat_service.py # ChatService（Session + Redis + Agent）
│   │   └── __init__.py
│   ├── agent/              # ReAct Agent ✅ 🆕
│   │   ├── react_agent.py  # ReAct Agent 实现
│   │   └── __init__.py
│   ├── embedding/          # Embedding 服务 ✅
│   │   └── embedding_service.py
│   ├── reranker/           # Reranker 服务 ✅
│   │   └── reranker_service.py
│   ├── document/           # 文档处理 ✅
│   │   └── document_processor.py
│   ├── rag/                # RAG 服务 ✅
│   │   └── rag_service.py
│   └── Kafka/              # Kafka 消息队列（计划中）
├── pkg/                    # 公共组件 ✅
│   ├── model_list/         # 统一模型管理
│   │   ├── base_model.py           # 基础模型类
│   │   ├── llm_model_list.py       # LLM 模型配置
│   │   ├── embedding_model_list.py # Embedding 模型配置
│   │   ├── reranker_model_list.py  # Reranker 模型配置
│   │   └── model_manager.py        # 模型管理器
│   ├── agent_prompt/       # Prompt 管理
│   │   ├── prompt_templates.py     # Prompt 模板
│   │   └── agent_tool.py           # 工具定义
│   └── constants/          # 全局常量
│       └── constants.py
├── test/                   # 测试文件 ✅
│   ├── test_mongodb.py
│   ├── test_milvus.py
│   ├── test_redis.py         # Redis 测试 🆕
│   ├── test_rag.py
│   ├── test_summary_mechanism.py # 延迟总结机制测试 🆕
│   ├── test_chat_service.py  # ChatService 测试 🆕
│   └── test_full_rag_qa.py   # 完整 RAG QA 演示（ChatService + Agent）🆕
├── milvus/                 # Milvus 部署 ✅
│   └── docker-compose.yml
├── main.py                 # 应用入口
├── requirements.txt        # Python 依赖 ✅
├── .env                    # 环境变量配置
├── .gitignore              # Git 忽略规则 ✅
└── READEME.md              # 本文件
```

---

## 🔧 常用命令

### 数据库管理

```bash
# 查看 Milvus 集合
docker exec milvus milvus_cli list collections

# 连接 MongoDB
mongosh mongodb://root:rootpassword@localhost:27017/
```

### 模型管理

```bash
# 查看已下载的 Ollama 模型
ollama list

# 拉取 Ollama 模型
ollama pull llama3.2

# 运行 Ollama 模型测试
ollama run llama3.2
```

---

## 📝 开发注意事项

### 1. 模型配置 🆕
- 所有模型配置统一在 `pkg/model_list/` 中管理
- 使用 `ModelManager` 进行模型选择和初始化
- 避免硬编码模型名称，使用配置常量（如 `BGE_LARGE_ZH_V1_5.name`）
- **导入顺序**：确保 `constants.py` 在 HuggingFace 库之前导入
- **离线模式**：设置 `TRANSFORMERS_OFFLINE=1` 和 `HF_HUB_OFFLINE=1`

### 2. 架构设计 🆕
- **LLMService**: 简化 API，支持 `user_message`（推荐）和 `messages`（高级）
- **ChatService**: 统一入口，自动管理 Session、Redis、历史记录
- **ReAct Agent**: 由 ChatService 创建和管理，不直接使用
- **统一的 chat() 方法**: 支持普通对话和 Agent 对话
- **推荐用法**：
  ```python
  # ✅ 推荐：使用 ChatService 统一 API
  # 普通对话
  for chunk in chat_service.chat("你好"):
      print(chunk, end="")
  
  # Agent 对话（工具调用）
  answer = chat_service.chat(
      user_message="问题",
      use_agent=True,
      agent_tools={"knowledge_search": knowledge_search},
      save_only_answer=True  # 只保存问答
  )
  
  # ❌ 不推荐：直接使用 Agent
  # agent = create_react_agent(llm, tools)
  # answer = agent.run(question)
  ```

### 3. 数据库操作
- MongoDB 使用 Beanie ODM 异步操作
- Milvus 集合需要先 `flush()` 再 `load()` 才能搜索
- 向量维度必须与 Embedding 模型输出一致（1024维）
- Redis 使用单例模式，自动连接管理

### 4. RAG 检索
- Reranker 分数阈值默认为 `-100.0`（因为是 logits）
- 去重阈值为 `0.02`（相似度 98%）
- 建议检索 Top-15，Rerank 后返回 Top-5
- `knowledge_search` 工具的 `max_context_length` 已增至 10000

### 5. 性能优化
- Embedding 和 Reranker 服务使用单例模式
- 向量检索使用 COSINE 相似度
- 大文档建议 chunk_size=500, chunk_overlap=50
- 智能设备选择：自动检测 CUDA/MPS，或手动设置 `RUNNING_MODE`

### 6. 历史记录管理 🆕
- **ChatService 自动管理**：无需手动调用 `add_to_history` 或 `sync_to_redis`
- **延迟总结**：在下次对话前执行，不阻塞当前对话
- **可控粒度**：`save_only_answer=True` 只保存问答（推荐，简洁）
- **Session 隔离**：每个 Session 独立的历史记录和 Redis 键

### 7. 代码重用与 DRY 🆕
- 避免重复代码：使用 `_normalize_chunk()` 统一处理不同模型返回值
- 参数验证：禁止同时传递冲突参数（如 `user_message` 和 `messages`）
- 依赖注入：使用参数传递依赖（如 `document_processor`），避免循环导入
