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
  - 流式对话（`stream_chat`）
  - 非流式对话（`chat`）
  
- ✅ **高级功能**
  - 系统 Prompt 管理
  - 工具调用能力（Tool Use）
  - 自动聊天历史总结
    - 触发条件：消息数 >= 10 或 token 数超过阈值
    - 全异步执行
    - 自动替换历史记录

#### 2.2 Prompt 管理（`pkg/agent_prompt/`）
- ✅ **多场景 Prompt 模板**
  - `DEFAULT_PROMPT`: 通用对话
  - `RAG_PROMPT`: 基于知识库的问答
  - `CODE_PROMPT`: 代码生成与解释
  - `DOCUMENT_PROMPT`: 文档分析
  - `SUMMARY_PROMPT`: 聊天历史总结
  
- ✅ **工具定义**（`agent_tool.py`）
  - `knowledge_search`: 知识库搜索
  - `document_analyzer`: 文档分析
  - `code_executor`: 代码执行
  - IDE 可点击跳转

#### 2.3 Embedding 服务（`internal/embedding/embedding_service.py`）
- ✅ **文本向量化**
  - 基于 `sentence-transformers` 
  - 支持文档批量编码（`encode_documents`）
  - 支持查询编码（`encode_query`，带归一化）
  - 单例模式，避免重复加载
  - 支持 CPU/GPU 切换

#### 2.4 Reranker 服务（`internal/reranker/reranker_service.py`）
- ✅ **检索结果重排序**
  - 基于 `FlagEmbedding` 的 BGE Reranker
  - 语义相关性二次评分
  - 支持自定义分数阈值
  - Logits 输出（-100 到 +10，分数越高越相关）

#### 2.5 文档处理服务（`internal/document/document_processor.py`）
- ✅ **多格式文档支持**
  - `.txt`、`.pdf`、`.docx` 格式
  - 基于 LangChain 的文档加载器
  
- ✅ **文档处理流程**
  - `add_documents_to_mongodb`: 保存原始文档到 MongoDB，生成 UUID
  - `add_document_chunks_to_milvus`: 文档分割、向量化、存储到 Milvus
  - `add_documents`: 完整的文档入库流程编排
  - 可配置 chunk_size（默认500）和 chunk_overlap（默认50）

#### 2.6 RAG 检索服务（`internal/rag/rag_service.py`）
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
  - `test/test_rag.py`: RAG 完整流程测试（对比 Reranker 效果）
  - `test/test_async_summary.py`: 聊天历史总结测试
  - `test/test_full_rag_qa.py`: **完整的 RAG QA 演示**

- ✅ **交互式 QA Demo**（`test/test_full_rag_qa.py`）
  - 真实文档处理（.docx）
  - MongoDB + Milvus 双重存储
  - 实时向量检索
  - Reranker 重排序
  - 流式 LLM 对话
  - 显示检索到的文档片段

### 4. 开发环境

- ✅ **完整的依赖管理**
  - `requirements.txt`: 所有 Python 依赖
  - `.gitignore`: Git 忽略规则
  - `.env` 环境变量配置（MongoDB、Milvus、API Keys）

- ✅ **Docker 部署**
  - `milvus/docker-compose.yml`: Milvus 生态一键部署
    - Milvus 向量数据库
    - MinIO 对象存储
    - Attu 可视化管理界面（http://localhost:8000）

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
- ⏳ **Redis 集成**（`internal/db/redis.py`）
  - 热点数据缓存
  - 多轮对话历史存储
  - 用户会话管理
  - 检索结果缓存

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

创建 `.env` 文件：

```bash
# MongoDB
MONGODB_URL=mongodb://root:rootpassword@localhost:27017/
MONGODB_DATABASE=rag_platform

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=root
MILVUS_PASSWORD=rootpassword
MILVUS_DB_NAME=rag_platform

# DeepSeek API（可选）
DEEPSEEK_API_KEY=your_api_key
```

### 3. 启动 Milvus

```bash
cd milvus
docker-compose up -d

# 访问 Attu 可视化界面
# http://localhost:8000
```

### 4. 运行 RAG QA 演示

```bash
# 首次运行：处理文档并存储
python test/test_full_rag_qa.py

# 后续运行：注释掉文档处理步骤
# 在 test_full_rag_qa.py 中注释掉：
# success = await process_and_store_documents(doc_folder, collection_name)
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
│   │   └── redis.py        # Redis 缓存（计划中）
│   ├── model/              # 数据模型 ✅
│   │   ├── document.py     # 文档模型
│   │   ├── message.py      # 消息模型
│   │   └── user_info.py    # 用户模型
│   ├── llm/                # LLM 服务 ✅
│   │   └── llm_service.py  # 统一 LLM 接口
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
│   ├── test_rag.py
│   ├── test_async_summary.py
│   └── test_full_rag_qa.py   # 完整 RAG QA 演示
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

### 1. 模型配置
- 所有模型配置统一在 `pkg/model_list/` 中管理
- 使用 `ModelManager` 进行模型选择和初始化
- 避免硬编码模型名称

### 2. 数据库操作
- MongoDB 使用 Beanie ODM 异步操作
- Milvus 集合需要先 `flush()` 再 `load()` 才能搜索
- 向量维度必须与 Embedding 模型输出一致（1024维）

### 3. RAG 检索
- Reranker 分数阈值默认为 `-100.0`（因为是 logits）
- 去重阈值为 `0.02`（相似度 98%）
- 建议检索 Top-15，Rerank 后返回 Top-5

### 4. 性能优化
- Embedding 和 Reranker 服务使用单例模式
- 向量检索使用 COSINE 相似度
- 大文档建议 chunk_size=500, chunk_overlap=50
