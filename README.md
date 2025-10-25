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

### 3. 🌟 **流式 AI 对话系统**（真正的实时流式）✅ 🆕

#### 3.1 核心特性
- ✅ **Token-by-Token 流式输出**
  - LLM 生成一个 token，客户端立即收到
  - 不是假流式（分块输出完整答案）
  - 真正的实时体验
  
- ✅ **Agent 推理过程可视化**
  - `show_thinking=true`: 显示完整推理过程
  - `show_thinking=false`: 只显示最终答案
  - 实时展示：Thought → Action → Observation → Answer

- ✅ **技术实现**：回调机制 + 异步队列
  ```python
  # Agent 生成 token 时调用回调
  callback("llm_chunk", token)
      ↓
  # 放入队列
  event_queue.put((event_type, content))
      ↓
  # Service 异步读取队列
  async for event in queue:
      yield {"event": "...", "data": {...}}
      ↓
  # Controller 格式化为 SSE
  yield f"event: answer_chunk\ndata: {json}\n\n"
      ↓
  # 客户端实时接收
  response.iter_lines()
  ```

#### 3.2 SSE（Server-Sent Events）支持
- ✅ **标准 SSE 格式**
  - `Content-Type: text/event-stream`
  - 单向推送（服务器 → 客户端）
  - 自动重连机制
  
- ✅ **事件类型**
  - `session_created`: 会话创建
  - `user_message_saved`: 用户消息已保存
  - `thought`: Agent 思考过程
  - `action`: Agent 执行动作
  - `observation`: 工具执行结果
  - `answer_chunk`: 答案片段（实时输出）
  - `ai_message_saved`: AI 回复已保存
  - `done`: 完成
  - `error`: 错误

#### 3.3 使用示例
```python
# Python 客户端
import requests

response = requests.post(
    "http://localhost:8000/messages",
    json={
        "content": "什么是 RAG 技术？",
        "user_id": "user_001",
        "show_thinking": True  # 显示思考过程
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('event: '):
            event_type = line_str.replace('event: ', '').strip()
        elif line_str.startswith('data: '):
            event_data = json.loads(line_str.replace('data: ', ''))
            
            if event_type == 'thought':
                print(f"💭 {event_data['content']}")
            elif event_type == 'action':
                print(f"🔧 {event_data['content']}")
            elif event_type == 'answer_chunk':
                print(event_data['content'], end='', flush=True)
```

```javascript
// JavaScript 客户端（浏览器）
const eventSource = new EventSource('/messages?...');

eventSource.addEventListener('thought', (e) => {
    const data = JSON.parse(e.data);
    console.log('💭 思考:', data.content);
});

eventSource.addEventListener('answer_chunk', (e) => {
    const data = JSON.parse(e.data);
    document.getElementById('answer').innerHTML += data.content;
});

eventSource.addEventListener('done', (e) => {
    eventSource.close();
});
```

### 4. 测试与演示

- ✅ **完整测试套件**
  - `test/test_mongodb.py`: MongoDB CRUD 测试
  - `test/test_milvus.py`: Milvus 连接和检索测试
  - `test/test_redis.py`: Redis 操作测试 🆕
  - `test/test_rag.py`: RAG 完整流程测试（对比 Reranker 效果）
  - `test/test_summary_mechanism.py`: 延迟总结机制测试 🆕
  - `test/test_chat_service.py`: ChatService 完整测试 🆕
  - `test/test_full_rag_qa.py`: **完整的 RAG QA 演示（ChatService + Agent 架构）** 🆕
  - `test/test_user_api.py`: 用户管理 API 测试 🆕
  - `test/test_document_api.py`: 文档管理 API 测试 🆕
  - `test/test_session_api.py`: 会话管理 API 测试 🆕
  - `test/test_message_api.py`: **流式消息 API 测试**（支持思考过程显示）🆕 🌟

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

- ✅ **流式 AI 对话测试**（`test/test_message_api.py`）🆕 🌟
  - **3种测试模式**：
    1. 自动测试（流式，隐藏思考过程）
    2. 交互式聊天（流式，隐藏思考过程）
    3. 交互式聊天（流式，显示思考过程）⭐
  - **实时推理展示**：看到 Agent 的完整思考过程
  - **真正的流式**：LLM 生成一个字符，立即显示
  - **Agent + RAG 集成**：与 `test_full_rag_qa.py` 完全一致

### 5. 工具与服务

#### 5.1 密码加密（`pkg/utils/password_utils.py`）✅ 🆕
- ✅ **bcrypt 密码哈希**
  - `hash_password()`: 密码加密
  - `verify_password()`: 密码验证
  - 安全的盐值生成

#### 5.2 JWT 认证（`pkg/utils/jwt_utils.py`）✅ 🆕
- ✅ **Token 管理**
  - `create_token()`: 创建 JWT token
  - `verify_token()`: 验证和解析 token
  - 过期时间控制
  - SECRET_KEY 从环境变量加载

#### 5.3 邮件服务（`pkg/utils/email_service.py`）✅ 🆕
- ✅ **验证码发送**
  - `send_verification_code()`: 发送邮箱验证码
  - `verify_code()`: 验证验证码
  - Redis 存储（5分钟过期）
  - SMTP TLS 支持
  - 邮件模板

#### 5.4 文档处理工具（`pkg/utils/document_utils.py`）✅ 🆕
- ✅ **文档加载**
  - 自动检测文件类型
  - 支持 PDF、DOCX、TXT、Markdown
  - `load_documents()`: 批量加载
  
- ✅ **文档分割**
  - `split_documents()`: 智能分块
  - 可配置 chunk_size 和 overlap
  - 保留文档元数据

- ✅ **文本清理**
  - `clean_text()`: 去除特殊字符
  - 统一空白符处理

#### 5.5 日志系统（`log/logger.py`）✅ 🆕
- ✅ **Loguru 集成**
  - JSON 格式输出（NDJSON）
  - 自动记录调用位置
  - Stack trace 支持
  - 双输出（控制台 + 文件）
  - 自动日志轮转（按日期）
  - 结构化字段（Debug, Info, Warn, Error, Fatal）
  - 日志目录：`json_log/YY_MM_DD_log/*.json`

### 6. FastAPI Web 服务 ✅ 🆕

#### 6.1 应用入口（`main.py`）
- ✅ **服务器启动**
  - MongoDB、Redis、Milvus 初始化
  - 文档处理器启动
  - FastAPI 应用配置
  - uvicorn 服务器

#### 6.2 路由管理（`internal/http_server/routes.py`）
- ✅ **统一路由注册**
  - 用户管理路由
  - 文档管理路由
  - 会话管理路由
  - 消息管理路由
  - 自动打印所有路由

#### 6.3 响应控制器（`api/v1/response_controller.py`）
- ✅ **统一响应格式**
  - `json_response()`: 标准 JSON 响应
  - 自动错误处理
  - 状态码映射

#### 6.4 DTO（数据传输对象）
- ✅ **Request DTOs**（`internal/dto/request/`）
  - `user_request.py`: 用户相关请求
  - `message_request.py`: 消息相关请求（含 `show_thinking`）
  - `session_request.py`: 会话相关请求
  - Pydantic 验证

- ✅ **Response DTOs**（`internal/dto/respond/`）
  - `user_response.py`: 用户信息响应
  - `document_response.py`: 文档响应
  - `session_response.py`: 会话响应
  - `message_response.py`: 消息响应
  - 自动序列化

### 7. 开发环境与配置

- ✅ **完整的依赖管理**
  - `requirements.txt`: 所有 Python 依赖
  - `.gitignore`: Git 忽略规则
  - `env_template.txt`: 环境变量模板
  - `bcrypt`, `PyJWT`, `email-validator` 等新增依赖

- ✅ **环境配置**（`pkg/constants/constants.py`）
  - **统一配置管理**: 所有配置从 `.env` 加载
  - **智能设备选择**: 自动检测 CUDA/MPS/CPU
  - **HuggingFace 离线模式**: 避免联网检查 🆕
    - `TRANSFORMERS_OFFLINE=1`
    - `HF_HUB_OFFLINE=1`
  - **Redis 配置**: Host、Port、DB、Password 🆕
  - **邮件服务配置**: SMTP 服务器、端口、认证 🆕
  - **JWT 配置**: SECRET_KEY、过期时间 🆕
  - **导入顺序优化**: 确保环境变量在库导入前设置 🆕

- ✅ **Docker 部署**
  - `milvus/docker-compose.yml`: Milvus 生态一键部署
    - Milvus 向量数据库
    - MinIO 对象存储
    - Attu 可视化管理界面（http://localhost:8000）
  - `mongodb/docker-compose.yml`: MongoDB 部署 🆕
  - Redis 部署（推荐 Docker）
  - Kafka 部署（`Kafka/docker-compose.yml`）🆕

---

## 🎯 架构亮点 🆕

### 1. 🌟 真正的流式 AI 对话实现（核心创新）

#### 1.1 技术挑战
传统的流式实现存在以下问题：
- ❌ **假流式**：先生成完整答案，再分块输出
- ❌ **无法展示思考过程**：用户看不到 Agent 的推理过程
- ❌ **异步困境**：Agent 是同步代码，API 是异步代码

#### 1.2 解决方案：回调 + 队列 + 异步生成器

```
┌─────────────────────────────────────────────────────────┐
│  第 1 层：LLM 流式生成（同步）                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  LLMService.chat(stream=True)                     │  │
│  │    → yield "RAG"                                  │  │
│  │    → yield " 是"                                  │  │
│  │    → yield " 检索"                                 │  │
│  └───────────────┬───────────────────────────────────┘  │
└──────────────────┼──────────────────────────────────────┘
                   │ token
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 2 层：ReActAgent 回调（同步）                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ReActAgent.__init__(callback=callback_fn)        │  │
│  │                                                    │  │
│  │  def run(question, stream=True):                  │  │
│  │      for chunk in llm.chat(..., stream=True):    │  │
│  │          if self.callback:                        │  │
│  │              self.callback("llm_chunk", chunk) ━━━│━━━━┐
│  └───────────────────────────────────────────────────┘  │    │
└─────────────────────────────────────────────────────────┘    │
                                                                │
                   ┌────────────────────────────────────────────┘
                   │ callback
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 3 层：队列传递（线程安全）                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  import queue                                     │  │
│  │  event_queue = queue.Queue()                      │  │
│  │                                                    │  │
│  │  def callback(event_type, content):               │  │
│  │      event_queue.put((event_type, content)) ━━━━━━│━━━━┐
│  └───────────────────────────────────────────────────┘  │   │
└─────────────────────────────────────────────────────────┘   │
                                                               │
                   ┌───────────────────────────────────────────┘
                   │ put
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 4 层：异步后台任务（asyncio）                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  # 在后台线程运行同步 Agent                         │  │
│  │  async def run_agent():                           │  │
│  │      return await asyncio.to_thread(              │  │
│  │          lambda: agent.run(message, stream=True)  │  │
│  │      )                                            │  │
│  │                                                    │  │
│  │  agent_task = asyncio.create_task(run_agent()) ━━│━━━━┐
│  └───────────────────────────────────────────────────┘  │  │
└─────────────────────────────────────────────────────────┘  │
                                                              │
                   ┌──────────────────────────────────────────┘
                   │ 后台运行
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 5 层：异步生成器（Service 层）                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  async def _generate_ai_reply_stream(...):        │  │
│  │      while not agent_task.done() or               │  │
│  │            not event_queue.empty():               │  │
│  │          try:                                     │  │
│  │              event_type, content =                │  │
│  │                  event_queue.get_nowait()  ◀━━━━━━│━━━ 实时读取
│  │              yield {                              │  │
│  │                  "event": "answer_chunk",         │  │
│  │                  "data": {"content": content}     │  │
│  │              } ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│━━━━┐
│  │          except queue.Empty:                      │  │  │
│  │              await asyncio.sleep(0.01)            │  │  │
│  └───────────────────────────────────────────────────┘  │  │
└─────────────────────────────────────────────────────────┘  │
                                                              │
                   ┌──────────────────────────────────────────┘
                   │ yield
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 6 层：SSE 格式化（Controller 层）                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  async def event_generator():                     │  │
│  │      async for event_dict in                      │  │
│  │          message_service.send_message_stream(...):│  │
│  │          event_type = event_dict["event"]         │  │
│  │          event_data = event_dict["data"]          │  │
│  │          yield f"event: {event_type}\n"           │  │
│  │          yield f"data: {json.dumps(event_data)}\n"│  │
│  │          yield "\n"  # SSE 分隔符 ━━━━━━━━━━━━━━━━│━━━━┐
│  │                                                    │  │  │
│  │  return StreamingResponse(                        │  │  │
│  │      event_generator(),                           │  │  │
│  │      media_type="text/event-stream"               │  │  │
│  │  ) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│━━━━┤
│  └───────────────────────────────────────────────────┘  │  │
└─────────────────────────────────────────────────────────┘  │
                                                              │
                   ┌──────────────────────────────────────────┘
                   │ HTTP Stream
                   ▼
┌─────────────────────────────────────────────────────────┐
│  第 7 层：客户端接收（实时显示）                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  response = requests.post(..., stream=True)       │  │
│  │                                                    │  │
│  │  for line in response.iter_lines():               │  │
│  │      if line.startswith('event: '):               │  │
│  │          event_type = line.replace('event: ', '') │  │
│  │      elif line.startswith('data: '):              │  │
│  │          data = json.loads(line.replace(...))     │  │
│  │          if event_type == 'answer_chunk':         │  │
│  │              print(data['content'], end='') ━━━━━━│━━━ 实时打印！
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

#### 1.3 关键技术点

1. **回调机制（Callback）**
   - `ReActAgent` 接收 `callback` 函数
   - LLM 每生成一个 token，立即调用 `callback("llm_chunk", token)`
   - 实现：`internal/agent/react_agent.py`

2. **线程安全队列（queue.Queue）**
   - 同步代码（Agent）向队列写入
   - 异步代码（Service）从队列读取
   - 跨线程通信的桥梁

3. **后台任务（asyncio.to_thread）**
   - 将同步的 `agent.run()` 放到后台线程
   - 不阻塞异步事件循环
   - 实现：`asyncio.create_task(asyncio.to_thread(agent.run))`

4. **异步生成器（AsyncGenerator）**
   - 使用 `yield` 实时产出事件
   - 使用 `queue.get_nowait()` 非阻塞读取
   - 实现：`async def _generate_ai_reply_stream() -> AsyncGenerator[Dict, None]`

5. **SSE（Server-Sent Events）**
   - 标准的 HTTP 流式协议
   - 格式：`event: <type>\ndata: <json>\n\n`
   - `Content-Type: text/event-stream`

#### 1.4 核心代码片段

```python
# internal/agent/react_agent.py
class ReActAgent:
    def __init__(self, llm_service, tools, callback: Optional[Callable] = None):
        self.callback = callback
    
    def run(self, question: str, stream: bool = False) -> str:
        for chunk in self.llm_service.chat(stream=True):
            if self.callback:
                self.callback("llm_chunk", chunk)  # 🔥 关键：每个 token 都回调

# internal/service/orm/message_sever.py
async def _generate_ai_reply_stream(self, ...):
    event_queue = queue.Queue()  # 🔥 线程安全队列
    
    def callback(event_type, content):
        event_queue.put((event_type, content))  # 🔥 写入队列
    
    agent = ReActAgent(..., callback=callback)
    
    # 🔥 后台运行同步 Agent
    agent_task = asyncio.create_task(
        asyncio.to_thread(lambda: agent.run(message, stream=True))
    )
    
    # 🔥 实时读取队列并 yield
    while not agent_task.done() or not event_queue.empty():
        try:
            event_type, content = event_queue.get_nowait()
            yield {"event": "answer_chunk", "data": {"content": content}}
        except queue.Empty:
            await asyncio.sleep(0.01)
```

#### 1.5 优势
- ✅ **真正的实时**：LLM 生成一个字符，客户端立即收到
- ✅ **思考过程可视化**：`show_thinking=true` 可以看到 Agent 推理
- ✅ **性能优异**：非阻塞，支持并发
- ✅ **易于扩展**：只需添加新的 `callback` 事件类型

### 2. 分层架构 - 单一职责原则
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

### 3. 简化 API - 降低使用难度
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

### 4. 智能历史管理
- **延迟总结**：不阻塞当前对话，在下次对话前执行
- **自动同步**：历史记录自动保存到 Redis
- **可控粒度**：`save_only_answer=True` 只保存问答，自动清理中间推理
- **Session 隔离**：多用户、多会话互不干扰

### 5. 环境变量优化
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

## 🌟 核心优势与特色

### 1. 🚀 真正的实时流式对话
- **Token-by-Token 流式输出**
  - LLM 生成一个 token，客户端立即显示
  - 不是假流式（先生成完再分块输出）
  - 用户体验接近 ChatGPT 官方体验
  
- **Agent 推理过程可视化**
  - `show_thinking=true` 可以实时看到 AI 的思考过程
  - Thought → Action → Observation → Answer 完整展示
  - 帮助理解 AI 如何推理和使用工具

- **技术创新**
  - 回调机制 + 线程安全队列 + 异步生成器
  - 完美解决同步 Agent 与异步 API 的集成难题
  - 支持 SSE（Server-Sent Events）标准协议

### 2. 🧠 智能 ReAct Agent
- **真实工具调用**
  - 不伪造 Observation，强制使用真实工具返回结果
  - 防止 LLM 编造答案，保证准确性
  - 检测重复 Action 并强制给出 Answer

- **知识库 RAG 集成**
  - 自动调用 `knowledge_search` 工具检索文档
  - 向量检索 + Reranker 重排序 + 智能去重
  - 可溯源，返回引用文档的 UUID 和名称

- **灵活配置**
  - 可选是否显示思考过程
  - 可选是否启用 Agent（支持普通对话）
  - 最大推理轮数可配置（防止死循环）

### 3. 📚 企业级 RAG 检索
- **三阶段检索流程**
  1. **向量检索**：Milvus 高性能向量数据库，毫秒级响应
  2. **Reranker 重排序**：BGE Reranker 语义相关性二次评分
  3. **智能去重**：过滤相似度 ≥ 98% 的重复文档

- **高质量 Embedding**
  - BGE-large-zh-v1.5（1024 维）
  - 针对中文优化，检索准确率高
  - 支持离线模式（HuggingFace 本地缓存）

- **灵活的文档管理**
  - MongoDB 存储文档元数据和原始内容
  - Milvus 存储向量和分块数据
  - 支持 PDF、DOCX、TXT、Markdown

### 4. 🎯 分层架构设计
- **单一职责原则**
  - Controller 层：处理 HTTP 请求
  - Service 层：业务逻辑
  - LLM 层：模型调用
  - Agent 层：工具编排
  - 各层职责清晰，易于测试和维护

- **统一 API 设计**
  - `ChatService.chat()` 统一入口
  - 支持普通对话和 Agent 对话
  - 自动管理 Session、Redis、历史记录
  - 降低使用难度，提高开发效率

- **依赖注入**
  - 避免循环依赖
  - 方便单元测试
  - 易于扩展和替换组件

### 5. 💾 智能历史管理
- **自动总结机制**
  - 每 10 条消息（可配置）自动触发总结
  - 累积总结：总结 A → 总结 B（包含 A）→ 总结 C（包含 B）
  - 有效压缩上下文，节省 Token

- **Redis 持久化**
  - 会话历史自动同步到 Redis
  - 支持多用户、多会话隔离
  - 可配置过期时间

- **可控历史粒度**
  - `save_only_answer=True`：只保存问答（简洁）
  - `save_only_answer=False`：保存完整推理过程（调试）

### 6. 🔐 完整的用户系统
- **安全认证**
  - bcrypt 密码加密（不可逆）
  - JWT Token 认证
  - 全局中间件统一鉴权
  - 白名单机制（支持路径 + 方法精确匹配）

- **多种登录方式**
  - 昵称 + 密码登录
  - 邮箱验证码登录
  - 邮箱验证码注册

- **权限管理**
  - 管理员/普通用户角色
  - 管理后台（用户管理、文档管理）
  - 基于 Token 的用户身份识别

### 7. 🎨 现代化前端界面
- **炫酷视觉效果**
  - 暗色主题 + 霓虹色彩（蓝、紫、粉）
  - Canvas 粒子背景（动态连接、自动移动）
  - 流畅动画（淡入、滑动、发光效果）
  - 毛玻璃效果 + 渐变按钮
  - 大屏设计风格，科技感十足

- **实时流式体验**
  - Token-by-Token 实时显示
  - 思考过程可视化（可选）
  - 文件上传（拖拽、多文件）
  - 消息操作（复制、重新生成）

- **Vue 3 技术栈**
  - Composition API + `<script setup>`
  - Pinia 状态管理
  - Vue Router 路由守卫
  - Element Plus 组件库

### 8. 🛠️ 完善的开发体验
- **统一模型管理**
  - `ModelManager` 集中管理所有模型
  - 支持 LLM、Embedding、Reranker
  - 避免硬编码，使用配置常量
  - 易于切换和扩展模型

- **环境变量管理**
  - `.env` 统一配置
  - `env_template.txt` 模板文件
  - 智能设备选择（CUDA/MPS/CPU/AUTO）
  - HuggingFace 离线模式支持

- **完整的测试套件**
  - 数据库测试（MongoDB、Milvus、Redis）
  - RAG 完整流程测试
  - API 接口测试（用户、文档、会话、消息）
  - 交互式 Demo（`test_full_rag_qa.py`、`test_message_api.py`）

- **详细的日志系统**
  - Loguru 日志框架
  - JSON 格式输出（NDJSON）
  - 自动记录调用位置和 Stack Trace
  - 双输出（控制台 + 文件）
  - 按日期自动轮转

### 9. ⚡ 异步处理架构
- **FastAPI 异步框架**
  - 完全异步，高并发性能
  - 非阻塞 I/O
  - 支持数千并发连接

- **Beanie ODM 异步数据库**
  - MongoDB 异步操作
  - 类似 SQLAlchemy 的 ORM 体验
  - 支持复杂查询和聚合

- **后台任务处理**
  - `asyncio.create_task()` 异步任务
  - 会话名称自动生成（后台任务）
  - 历史总结自动触发（后台任务）
  - 不阻塞主请求，用户无感知

### 10. 🔄 Kafka 异步文档处理（已实现）
- **消息队列架构**
  - 文档上传后发送到 Kafka
  - 异步 Embedding 和向量化
  - 任务状态实时更新

- **解耦设计**
  - 文档上传和处理分离
  - 支持大批量文档处理
  - 失败重试机制

- **可扩展**
  - 多个 Consumer 并行处理
  - 支持分布式部署
  - 消息持久化保证可靠性

### 11. 📦 开箱即用
- **Docker 一键部署**
  - Milvus + MinIO + Attu 可视化
  - MongoDB 容器化部署
  - Redis 容器化部署
  - Kafka 容器化部署

- **详细文档**
  - README 完整的使用指南
  - API 开发文档（`API_DEVELOPMENT_GUIDE.md`）
  - 代码注释清晰
  - 架构图和流程图

- **低门槛**
  - 环境配置简单（`.env` 文件）
  - 依赖清晰（`requirements.txt`）
  - 测试脚本齐全
  - 支持离线运行（本地模型）

---

## ⚠️ 当前限制与不足

### 1. 文档处理限制
- ❌ **文件格式支持有限**
  - ✅ 支持：`.pdf`、`.docx`、`.txt`、`.md`
  - ❌ 不支持：`.pptx`、`.xlsx`、`.csv`、`.html`、`.rtf` 等
  - 建议：使用文档转换工具预处理为支持的格式

- ❌ **图片内容无法识别**
  - 当前只能处理文本内容，图片、图表、公式会被跳过
  - 无多模态大模型（如 GPT-4V）集成
  - 建议：对于包含重要图表的文档，手动添加文字描述

- ⚠️ **PDF 处理限制**
  - 扫描版 PDF（图片 PDF）无法识别文字
  - 复杂排版可能导致文本提取混乱
  - 建议：使用 OCR 工具预处理或转换为可编辑的 PDF

### 2. 功能限制
- ❌ **无网络搜索工具**
  - Agent 无法访问互联网获取实时信息
  - 只能基于知识库内的文档回答问题
  - 建议：定期更新知识库文档

- ❌ **无联网 API 调用**
  - 不支持调用外部 API（如天气、股票、新闻等）
  - 无法获取实时数据
  - 计划：集成搜索引擎 API（如 Google Search API、Bing Search API）

- ⚠️ **历史总结机制的信息损失**
  - 采用累积总结：总结A → 总结B（包含A） → 总结C（包含B）
  - 多次总结可能丢失细节信息
  - 当前阈值：每 10 条消息触发一次总结
  - 建议：重要对话定期导出备份

### 3. 性能限制
- ⚠️ **大文件处理速度慢**
  - 超过 10MB 的文档 Embedding 需要较长时间
  - 建议：使用 Kafka 异步处理（已实现但需部署）

- ⚠️ **并发限制**
  - 单个 LLM 调用是串行的
  - 大量并发请求可能导致响应延迟
  - 建议：部署多个 LLM 实例进行负载均衡

### 4. 多模态与多语言
- ❌ **不支持图片理解**
  - 无 Vision 模型集成
  - 无法分析图表、图片、手写内容
  - 计划：集成 GPT-4V、Claude 3 等多模态模型

- ⚠️ **英文支持较弱**
  - Embedding 模型优化为中文（BGE-large-zh-v1.5）
  - 英文文档检索效果可能不佳
  - 建议：使用多语言模型（如 `multilingual-e5-large`）

### 5. 安全与权限
- ⚠️ **JWT 认证较简单**
  - 使用全局中间件 + 白名单机制
  - 无 Token 刷新机制（Refresh Token）
  - 无 IP 白名单或访问频率限制
  - 建议：生产环境需加强安全策略

- ⚠️ **文档权限管理简单**
  - 当前所有用户共享知识库
  - 无文档级别的访问控制
  - 计划：实现基于角色的文档权限（RBAC）

### 6. 监控与运维
- ❌ **无系统监控**
  - 缺少性能监控（响应时间、错误率）
  - 缺少资源监控（CPU、内存、GPU）
  - 建议：集成 Prometheus + Grafana

- ❌ **无日志分析**
  - 日志以 JSON 格式存储，但无可视化分析
  - 建议：使用 ELK Stack（Elasticsearch + Logstash + Kibana）

### 7. 扩展性
- ⚠️ **单机部署**
  - 当前架构适合中小规模应用
  - 无分布式部署方案
  - 计划：Kubernetes 编排 + 微服务化

---

## 🚧 计划中功能

### 第一阶段：API 层和前端 ✅

#### 1. FastAPI RESTful API（`api/v1/`）✅ 🆕

##### 1.1 用户管理 API（`user_info_controller.py`）✅
- ✅ `POST /users`: 用户注册（邮箱验证码）
- ✅ `POST /users/login`: 用户登录（昵称+密码）
- ✅ `POST /users/email-login`: 邮箱验证码登录
- ✅ `GET /users/{user_id}`: 获取用户信息
- ✅ `PATCH /users/{user_id}`: 更新用户信息
- ✅ `GET /users`: 获取用户列表（分页）
- ✅ `DELETE /users/{user_id_list}`: 批量删除用户
- ✅ `PATCH /users/set-admin`: 设置管理员
- ✅ `POST /users/email-code`: 发送邮箱验证码

##### 1.2 文档管理 API（`document_controller.py`）✅
- ✅ `POST /documents`: 高级文档上传
  - 保存到 MongoDB 和 Milvus
  - 自动向量化和分块
  - 支持全文检索
- ✅ `GET /documents`: 获取文档列表（分页、关键词搜索）
- ✅ `GET /documents/{document_id}`: 获取文档详情
- ✅ `DELETE /documents/{document_id}`: 删除文档

##### 1.3 会话管理 API（`session_controller.py`）✅
- ✅ `GET /sessions`: 获取会话列表（分页）
- ✅ `GET /sessions/{session_id}`: 获取会话详情
- ✅ `PATCH /sessions/{session_id}`: 更新会话（名称、最后消息）

##### 1.4 消息管理 API（`message_controller.py`）✅ 🌟
- ✅ `POST /messages`: **流式 AI 对话**（SSE）
  - **真正的流式输出**（Token-by-Token）
  - **Agent + RAG 检索**（自动调用知识库）
  - **思考过程可选**（`show_thinking` 参数）
  - **自动创建会话**（不提供 `session_id` 时）
  - **实时推理展示**（Thought → Action → Observation → Answer）
- ✅ `GET /messages/{session_id}`: 获取会话的所有消息（分页）

#### 2. 统一响应格式 ✅
```python
# 标准 JSON 响应
{
    "code": 200,        # 0: 成功, -1: 失败, 200/400/500: HTTP 状态码
    "message": "成功",
    "data": { ... }     # 业务数据
}

# SSE 流式响应（POST /messages）
event: session_created
data: {"session_id": "xxx", "session_name": "xxx"}

event: thought
data: {"content": "用户询问 RAG，需要检索知识库"}

event: action
data: {"content": "knowledge_search(\"RAG\", 3)"}

event: observation
data: {"content": "找到3条相关文档..."}

event: answer_chunk
data: {"content": "RAG"}

event: done
data: {"session_id": "xxx"}
```

#### 2. 前端界面 ✅ 🆕 🌟
- ✅ **Vue 3 现代化界面**（`web/plantform_vue/`）
  - 基于 Vue 3 + Vite + Element Plus
  - 采用 Composition API 和 `<script setup>` 语法
  - Pinia 状态管理 + Vue Router 路由
  
- ✅ **炫酷视觉效果**
  - 🎨 暗色主题 + 霓虹色彩（蓝、紫、粉）
  - ✨ Canvas 粒子背景（动态连接、自动移动）
  - 💫 流畅动画（淡入、滑动、发光效果）
  - 🔮 毛玻璃效果 + 渐变按钮
  - 大屏设计风格，科技感十足
  
- ✅ **登录注册系统**
  - 双登录方式：昵称+密码 / 邮箱验证码
  - 邮箱验证码注册
  - 60秒验证码倒计时
  - 表单验证和错误提示
  
- ✅ **聊天对话界面**
  - 📱 左侧：会话列表（创建、切换会话）
  - 💬 中间：聊天区域（流式显示 AI 回复）
  - ⌨️ 底部：消息输入框（Enter 发送，Shift+Enter 换行）
  - 🧠 思考过程可视化（可选显示 Agent 推理过程）
  - 📎 文件上传（支持拖拽、多文件）
  - 🔄 消息操作（复制、重新生成）
  - ⚡ 真正的 Token-by-Token 流式输出
  
- ✅ **管理后台**（仅管理员可见）
  - 👥 用户管理：查看、搜索、删除用户，设置管理员
  - 📄 文档管理：上传、查看、删除知识库文档
  - 🔍 分页和搜索功能
  - 📊 数据统计展示
  
- ✅ **权限控制**
  - 基于 Vue Router 的路由守卫
  - 登录状态检查
  - 管理员权限验证
  - 自动跳转和重定向
  
- ✅ **开发规范**
  - 组件化、模块化开发
  - 公共组件（`components/public/`）
  - 页面专属组件（`components/{page}/`）
  - 清晰的目录结构
  - 详细的开发文档

### 第二阶段：高级功能

#### 1. 网络搜索与外部工具 🆕 ⏳
- ⏳ **搜索引擎集成**
  - Google Search API / Bing Search API
  - DuckDuckGo 搜索
  - 实时信息获取（新闻、天气、股票等）
  - Agent 工具：`web_search(query, max_results=5)`

- ⏳ **外部 API 调用**
  - 天气查询 API
  - 计算器 API
  - 翻译 API
  - 自定义 API 集成框架

#### 2. 多模态与文档格式扩展 🆕 ⏳
- ⏳ **多模态大模型集成**
  - GPT-4V（OpenAI Vision）
  - Claude 3（Anthropic）
  - Qwen-VL（通义千问 Vision）
  - 图片理解、图表分析、OCR

- ⏳ **扩展文件格式支持**
  - ✅ 当前支持：`.pdf`、`.docx`、`.txt`、`.md`
  - ⏳ 计划支持：
    - `.pptx`（PowerPoint）
    - `.xlsx`、`.csv`（Excel）
    - `.html`（网页）
    - `.rtf`（富文本）
    - `.epub`（电子书）

- ⏳ **OCR 文字识别**
  - 扫描版 PDF 识别
  - 图片文字提取
  - 手写文字识别
  - 集成 Tesseract OCR 或 PaddleOCR

#### 3. 溯源系统
- ⏳ **答案溯源**
  - 在生成的答案中插入角标 [1][2]
  - 点击角标显示原始文档片段
  - 高亮显示匹配内容
  - 支持跳转到原始文档

#### 4. 缓存与会话管理
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

#### 5. 异步处理优化
- ⏳ **Kafka 消息队列**（`internal/Kafka/`）
  - 文档上传后异步触发 Embedding
  - 大批量文档处理队列
  - 任务状态追踪
  - 失败重试机制

### 第三阶段：企业级特性

#### 1. 安全增强 🆕 ⏳
- ⏳ **增强认证机制**
  - Token 刷新机制（Refresh Token）
  - 多设备登录管理
  - IP 白名单
  - 访问频率限制（Rate Limiting）

- ⏳ **权限管理系统**
  - 基于角色的访问控制（RBAC）
  - 文档级别权限控制
  - API 权限细粒度管理
  - 操作审计日志

#### 2. 性能优化
- ⏳ **检索性能提升**
  - Milvus 分区和分片
  - 向量索引优化（IVF_FLAT → HNSW）
  - 批量检索优化
  - 结果缓存策略

- ⏳ **并发处理**
  - 异步文档处理
  - 并发 Embedding
  - 流式结果返回

#### 3. 多模型支持
- ⏳ 集成更多 LLM 模型
  - 通义千问（Qwen）
  - ChatGPT（GPT-4）
  - 文心一言（ERNIE）
  - Claude

#### 4. 高级 RAG 技术
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

#### 5. 监控与日志 🆕 ⏳
- ⏳ **系统监控**
  - 检索性能监控（Prometheus + Grafana）
  - Token 消耗统计
  - API 调用统计
  - 错误日志收集
  - 资源监控（CPU、内存、GPU）

- ⏳ **日志分析**
  - ELK Stack（Elasticsearch + Logstash + Kibana）
  - 日志可视化
  - 异常检测
  - 性能分析

### 第四阶段：部署与交付

#### 1. 分布式与扩展性 🆕 ⏳
- ⏳ **微服务化**
  - 服务拆分（认证、文档、对话、检索）
  - 服务注册与发现（Consul / Eureka）
  - 服务间通信（gRPC / RESTful）
  - 负载均衡（Nginx / HAProxy）

- ⏳ **分布式部署**
  - Kubernetes 编排
  - 多副本部署
  - 自动扩缩容（HPA）
  - 服务网格（Istio）

#### 2. 容器化与自动化 ⏳
- ⏳ **完整 Docker 化**
  - 所有服务的 Docker 镜像
  - Docker Compose 一键部署
  - 多阶段构建优化

- ⏳ **CI/CD 流程**
  - GitHub Actions / GitLab CI
  - 自动化测试（单元测试 + 集成测试）
  - 自动化部署（蓝绿部署 / 滚动更新）
  - 版本管理和回滚

#### 3. 生产环境优化 ⏳
- ⏳ **高可用架构**
  - 多活部署
  - 数据备份与恢复
  - 灾难恢复方案
  - 故障自动切换

- ⏳ **性能调优**
  - 数据库索引优化
  - 缓存策略优化
  - 连接池优化
  - 异步任务队列

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

### 5. 启动 API 服务器 🆕

```bash
# 启动 FastAPI 服务器
python main.py

# 服务器将在 http://localhost:8000 启动
# 访问 API 文档：http://localhost:8000/docs
```

### 6. 测试 API 接口 🆕

```bash
# 测试用户管理 API
python test/test_user_api.py

# 测试文档管理 API
python test/test_document_api.py

# 测试会话管理 API
python test/test_session_api.py

# 测试流式消息 API（推荐）⭐
python test/test_message_api.py
# 选择模式:
#   1. 自动测试
#   2. 交互式聊天（隐藏思考过程）
#   3. 交互式聊天（显示思考过程）⭐
```

### 7. 运行 RAG QA 演示（本地测试）

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

### 8. 启动前端界面 🆕 ⭐

```bash
# 进入前端目录
cd web/plantform_vue

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev

# 前端将在 http://localhost:5173 启动
# 自动打开浏览器访问
```

**前端功能体验**：
1. 📱 **登录注册**：
   - 访问 `/login` 或 `/register`
   - 使用邮箱验证码注册新账户
   - 昵称+密码登录 或 邮箱验证码登录

2. 💬 **智能对话**：
   - 登录后自动跳转到 `/chat`
   - 创建新会话或选择已有会话
   - 输入问题，体验实时流式 AI 回复
   - 可选显示 AI 思考过程
   - 上传文档到知识库

3. 🛠️ **管理后台**（管理员）：
   - 访问 `/admin/users` 管理用户
   - 访问 `/admin/documents` 管理文档
   - 搜索、删除、设置权限

**前端构建部署**：
```bash
# 构建生产版本
npm run build

# 预览构建产物
npm run preview

# 部署：将 dist/ 目录部署到 Nginx/CDN
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
├── api/                    # API 路由 ✅ 🆕
│   └── v1/
│       ├── user_info_controller.py   # 用户管理 API
│       ├── document_controller.py    # 文档管理 API
│       ├── session_controller.py     # 会话管理 API
│       ├── message_controller.py     # 消息管理 API（流式）
│       ├── response_controller.py    # 统一响应格式
│       └── __init__.py
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
│   ├── dto/                # 数据传输对象 ✅ 🆕
│   │   ├── request/        # 请求 DTO
│   │   │   ├── user_request.py
│   │   │   ├── message_request.py
│   │   │   ├── session_request.py
│   │   │   └── __init__.py
│   │   └── respond/        # 响应 DTO
│   │       ├── user_response.py
│   │       ├── document_response.py
│   │       ├── session_response.py
│   │       ├── message_response.py
│   │       └── __init__.py
│   ├── service/            # 业务逻辑层 ✅ 🆕
│   │   └── orm/
│   │       ├── user_info_sever.py    # 用户管理服务
│   │       ├── document_sever.py     # 文档管理服务
│   │       ├── session_sever.py      # 会话管理服务
│   │       └── message_sever.py      # 消息管理服务（流式）
│   ├── http_sever/         # HTTP 服务 ✅ 🆕
│   │   ├── app.py          # FastAPI 应用工厂
│   │   └── routes.py       # 路由注册
│   ├── llm/                # LLM 服务 ✅
│   │   └── llm_service.py  # 统一 LLM 接口（简化 API）🆕
│   ├── chat_service/       # 会话服务 ✅ 🆕
│   │   ├── chat_service.py # ChatService（Session + Redis + Agent）
│   │   └── __init__.py
│   ├── agent/              # ReAct Agent ✅ 🆕
│   │   ├── react_agent.py  # ReAct Agent 实现（支持回调）
│   │   └── __init__.py
│   ├── embedding/          # Embedding 服务 ✅
│   │   └── embedding_service.py
│   ├── reranker/           # Reranker 服务 ✅
│   │   └── reranker_service.py
│   ├── document/           # 文档处理 ✅
│   │   └── document_processor.py
│   ├── rag/                # RAG 服务 ✅
│   │   └── rag_service.py
│   ├── document_client/    # 文档处理客户端 ✅ 🆕
│   │   ├── config.toml     # 配置文件
│   │   ├── config_loader.py
│   │   ├── document_processor.py
│   │   ├── message_client.py
│   │   ├── channel/        # 内存队列
│   │   └── Kafka/          # Kafka 客户端
│   └── Kafka/              # Kafka 部署 ✅ 🆕
│       └── docker-compose.yml
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
│   ├── utils/              # 工具函数 ✅ 🆕
│   │   ├── password_utils.py       # 密码加密
│   │   ├── jwt_utils.py            # JWT 认证
│   │   ├── email_service.py        # 邮件服务
│   │   ├── document_utils.py       # 文档处理
│   │   └── __init__.py
│   └── constants/          # 全局常量
│       └── constants.py
├── log/                    # 日志系统 ✅ 🆕
│   ├── logger.py           # Loguru 日志配置
│   └── json_log/           # JSON 日志目录（按日期）
├── test/                   # 测试文件 ✅
│   ├── test_mongodb.py
│   ├── test_milvus.py
│   ├── test_redis.py         # Redis 测试 🆕
│   ├── test_rag.py
│   ├── test_summary_mechanism.py # 延迟总结机制测试 🆕
│   ├── test_chat_service.py  # ChatService 测试 🆕
│   ├── test_full_rag_qa.py   # 完整 RAG QA 演示（ChatService + Agent）🆕
│   ├── test_user_api.py      # 用户 API 测试 🆕
│   ├── test_document_api.py  # 文档 API 测试 🆕
│   ├── test_session_api.py   # 会话 API 测试 🆕
│   ├── test_message_api.py   # 流式消息 API 测试 🆕 ⭐
│   ├── test_password_utils.py # 密码工具测试 🆕
│   ├── test_jwt_utils.py     # JWT 工具测试 🆕
│   └── test_email_service.py # 邮件服务测试 🆕
├── milvus/                 # Milvus 部署 ✅
│   └── docker-compose.yml
├── mongodb/                # MongoDB 部署 ✅ 🆕
│   └── docker-compose.yml
├── web/                    # 前端项目 ✅ 🆕 ⭐
│   └── plantform_vue/      # Vue 3 前端
│       ├── public/         # 静态资源
│       ├── src/
│       │   ├── api/        # API 封装
│       │   │   ├── request.js         # Axios 封装
│       │   │   ├── user.js            # 用户 API
│       │   │   ├── document.js        # 文档 API
│       │   │   ├── session.js         # 会话 API
│       │   │   ├── message.js         # 消息 API（SSE）
│       │   │   └── index.js
│       │   ├── assets/     # 资源文件
│       │   │   ├── css/
│       │   │   │   └── global.css     # 全局样式
│       │   │   ├── img/
│       │   │   └── js/
│       │   ├── components/ # 组件
│       │   │   ├── public/            # 公共组件
│       │   │   │   ├── ParticleBackground.vue  # 粒子背景
│       │   │   │   ├── AppHeader.vue           # 导航栏
│       │   │   │   ├── LoadingSpinner.vue      # 加载动画
│       │   │   │   └── EmptyState.vue          # 空状态
│       │   │   ├── chat/              # 聊天组件
│       │   │   │   ├── SessionList.vue         # 会话列表
│       │   │   │   ├── ChatMessage.vue         # 聊天消息
│       │   │   │   └── MessageInput.vue        # 消息输入
│       │   │   ├── login/             # 登录组件
│       │   │   │   ├── LoginForm.vue           # 登录表单
│       │   │   │   └── RegisterForm.vue        # 注册表单
│       │   │   └── admin/             # 管理组件
│       │   ├── router/     # 路由
│       │   │   └── index.js           # 路由配置
│       │   ├── store/      # 状态管理
│       │   │   ├── user.js            # 用户状态
│       │   │   ├── chat.js            # 聊天状态
│       │   │   └── index.js
│       │   ├── views/      # 页面视图
│       │   │   ├── chat/
│       │   │   │   └── ChatView.vue            # 聊天页面
│       │   │   ├── login/
│       │   │   │   ├── LoginView.vue           # 登录页面
│       │   │   │   └── RegisterView.vue        # 注册页面
│       │   │   └── admin/
│       │   │       ├── AdminLayout.vue         # 管理布局
│       │   │       ├── UserManagement.vue      # 用户管理
│       │   │       └── DocumentManagement.vue  # 文档管理
│       │   ├── App.vue     # 根组件
│       │   └── main.js     # 应用入口
│       ├── .env.development  # 开发环境配置
│       ├── .env.production   # 生产环境配置
│       ├── index.html      # HTML 入口
│       ├── package.json    # 项目依赖
│       ├── vite.config.js  # Vite 配置
│       └── README.md       # 前端文档
├── main.py                 # 应用入口（FastAPI）✅ 🆕
├── requirements.txt        # Python 依赖 ✅
├── .env                    # 环境变量配置
├── .gitignore              # Git 忽略规则 ✅
├── API_DEVELOPMENT_GUIDE.md # API 开发指南 🆕
└── README.md               # 本文件
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
