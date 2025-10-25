# RAG 平台 API 接口文档

> 版本：v1.0  
> 基础路径：`http://localhost:8000`  
> 响应格式：JSON  
> 文档更新时间：2025-10-24

---

## 📋 目录

- [1. 用户管理 API](#1-用户管理-api)
- [2. 文档管理 API](#2-文档管理-api)
- [3. 会话管理 API](#3-会话管理-api)
- [4. 消息管理 API](#4-消息管理-api)
- [5. 通用响应格式](#5-通用响应格式)
- [6. 错误码说明](#6-错误码说明)

---

## 1. 用户管理 API

基础路径：`/users`

### 1.1 用户注册

**接口描述：** 用户注册，需要邮箱验证码

**请求方式：** `POST /users`

**请求头：**
```http
Content-Type: application/json
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| nickname | string | 是 | 昵称 | 长度 2-50 字符 |
| email | string | 是 | 邮箱地址 | 必须是有效的邮箱格式 |
| password | string | 是 | 密码 | 最短 6 位 |
| confirm_password | string | 是 | 确认密码 | 最短 6 位，需与 password 一致 |
| captcha | string | 是 | 邮箱验证码 | 6 位数字 |

**请求示例：**
```json
{
  "nickname": "张三",
  "email": "zhangsan@example.com",
  "password": "123456",
  "confirm_password": "123456",
  "captcha": "123456"
}
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码（0=成功, -1=失败） |
| message | string | 响应消息 |
| data | object | 用户信息对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 用户唯一标识 |
| nickname | string | 昵称 |
| email | string | 邮箱 |
| avatar | string | 头像 URL |
| gender | integer | 性别（0=男, 1=女） |
| birthday | string | 生日 |
| role | integer | 角色（0=普通用户, 1=管理员） |
| created_at | string | 创建时间（ISO 8601 格式） |

**成功响应示例：**
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "nickname": "张三",
    "email": "zhangsan@example.com",
    "avatar": "",
    "gender": 0,
    "birthday": "",
    "role": 0,
    "created_at": "2025-10-24T10:30:00Z"
  }
}
```

**失败响应示例：**
```json
{
  "code": -1,
  "message": "验证码错误"
}
```

---

### 1.2 用户登录

**接口描述：** 使用昵称和密码登录

**请求方式：** `POST /users/login`

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nickname | string | 是 | 昵称 |
| password | string | 是 | 密码 |

**请求示例：**
```json
{
  "nickname": "张三",
  "password": "123456"
}
```

**响应参数：** 同 [1.1 用户注册](#11-用户注册)

---

### 1.3 邮箱验证码登录

**接口描述：** 使用邮箱和验证码登录

**请求方式：** `POST /users/email-login`

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| email | string | 是 | 邮箱地址 | 必须是有效的邮箱格式 |
| captcha | string | 是 | 邮箱验证码 | 6 位数字 |

**请求示例：**
```json
{
  "email": "zhangsan@example.com",
  "captcha": "123456"
}
```

**响应参数：** 同 [1.1 用户注册](#11-用户注册)

---

### 1.4 获取用户列表

**接口描述：** 分页获取用户列表

**请求方式：** `GET /users`

**Query 参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| owner_id | string | 否 | 拥有者ID（过滤） | null | - |
| page | integer | 否 | 页码 | 1 | >= 1 |
| page_size | integer | 否 | 每页数量 | 10 | 1-100 |

**请求示例：**
```http
GET /users?page=1&page_size=10
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 数据对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| total | integer | 总用户数 |
| users | array | 用户列表（每个元素结构同 1.1 的 data） |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 100,
    "users": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "nickname": "张三",
        "email": "zhangsan@example.com",
        "avatar": "",
        "gender": 0,
        "birthday": "",
        "role": 0,
        "created_at": "2025-10-24T10:30:00Z"
      }
    ]
  }
}
```

---

### 1.5 获取用户详情

**接口描述：** 根据用户 UUID 获取用户详细信息

**请求方式：** `GET /users/{user_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户 UUID |

**请求示例：**
```http
GET /users/550e8400-e29b-41d4-a716-446655440000
```

**响应参数：** 同 [1.1 用户注册](#11-用户注册)

---

### 1.6 更新用户信息

**接口描述：** 更新用户的部分信息

**请求方式：** `PATCH /users/{user_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户 UUID |

**请求体参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| nickname | string | 否 | 昵称 | 长度 2-50 字符 |
| email | string | 否 | 邮箱地址 | 必须是有效的邮箱格式 |
| avatar | string | 否 | 头像 URL | - |
| gender | integer | 否 | 性别 | 0=男, 1=女 |
| birthday | string | 否 | 生日 | - |

**请求示例：**
```json
{
  "nickname": "李四",
  "avatar": "https://example.com/avatar.jpg"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "更新成功"
}
```

---

### 1.7 删除单个用户

**接口描述：** 删除指定用户

**请求方式：** `DELETE /users/{user_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户 UUID |

**请求示例：**
```http
DELETE /users/550e8400-e29b-41d4-a716-446655440000
```

**响应示例：**
```json
{
  "code": 200,
  "message": "删除成功: 1 个用户"
}
```

---

### 1.8 批量删除用户

**接口描述：** 批量删除多个用户

**请求方式：** `DELETE /users/{user_id_list}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id_list | string | 是 | 用户UUID列表（逗号分隔） |

**请求示例：**
```http
DELETE /users/550e8400-e29b-41d4-a716-446655440000,550e8400-e29b-41d4-a716-446655440001
```

**响应示例：**
```json
{
  "code": 200,
  "message": "删除成功: 2 个用户"
}
```

**注意事项：**
- 多个UUID之间用逗号分隔
- 会批量删除所有指定的用户
- 操作不可逆，请谨慎使用

---

### 1.9 设置管理员

**接口描述：** 设置或取消用户的管理员权限

**请求方式：** `PATCH /users/set-admin`

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户UUID |
| is_admin | boolean | 是 | 是否为管理员（true=设置，false=取消） |

**请求示例：**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_admin": true
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "设置管理员成功: 1 个用户"
}
```

**注意事项：**
- `is_admin: true` - 设置为管理员
- `is_admin: false` - 取消管理员权限
- 需要当前用户具有管理员权限

---

### 1.10 发送邮箱验证码

**接口描述：** 向指定邮箱发送验证码（用于注册或登录）

**请求方式：** `POST /users/email-code`

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| email | string | 是 | 邮箱地址 | 必须是有效的邮箱格式 |

**请求示例：**
```json
{
  "email": "zhangsan@example.com"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "验证码发送成功，请查收邮件"
}
```

**注意事项：**
- 验证码有效期 5 分钟
- 同一邮箱 1 分钟内只能发送 1 次
- 验证码存储在 Redis 中

---

## 2. 文档管理 API

基础路径：`/documents`

### 2.1 上传文档

**接口描述：** 上传文档并自动进行 Embedding 处理（异步）

**请求方式：** `POST /documents`

**请求头：**
```http
Content-Type: multipart/form-data
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| file | File | 是 | 文档文件 | 支持 .pdf, .docx, .txt |

**请求示例（cURL）：**
```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/document.pdf"
```

**请求示例（Python）：**
```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/documents', files=files)
    print(response.json())
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 文档信息对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 文档唯一标识 |
| name | string | 文档名称 |
| size | integer | 文件大小（字节） |
| url | string | 文档访问 URL |
| uploaded_at | string | 上传时间 |

**响应示例：**
```json
{
  "code": 0,
  "message": "文档上传成功，正在后台处理",
  "data": {
    "uuid": "650e8400-e29b-41d4-a716-446655440001",
    "name": "技术文档.pdf",
    "size": 1048576,
    "url": "/uploads/650e8400-e29b-41d4-a716-446655440001.pdf",
    "uploaded_at": "2025-10-24T11:00:00Z"
  }
}
```

**处理流程：**
1. 保存文件到本地
2. 记录到 MongoDB
3. 提交到 Kafka 进行异步 Embedding
4. 存储向量到 Milvus（后台处理）

---

### 2.2 获取文档列表

**接口描述：** 分页获取文档列表，支持关键词搜索

**请求方式：** `GET /documents`

**Query 参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| page | integer | 否 | 页码 | 1 | >= 1 |
| page_size | integer | 否 | 每页数量 | 10 | 1-100 |
| keyword | string | 否 | 搜索关键词（文档名） | null | 模糊匹配 |

**请求示例：**
```http
GET /documents?page=1&page_size=10&keyword=技术文档
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 数据对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| total | integer | 总文档数 |
| documents | array | 文档列表（见下表） |

**documents 数组元素结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 文档唯一标识 |
| name | string | 文档名称 |
| uploaded_at | string | 上传时间 |
| chunk_count | integer | 文本块数量（从 Milvus 查询） |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 50,
    "documents": [
      {
        "uuid": "650e8400-e29b-41d4-a716-446655440001",
        "name": "技术文档.pdf",
        "uploaded_at": "2025-10-24T11:00:00Z",
        "chunk_count": 120
      },
      {
        "uuid": "650e8400-e29b-41d4-a716-446655440002",
        "name": "用户手册.docx",
        "uploaded_at": "2025-10-24T10:30:00Z",
        "chunk_count": 85
      }
    ]
  }
}
```

---

### 2.3 获取文档详情

**接口描述：** 获取文档的完整信息

**请求方式：** `GET /documents/{document_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| document_id | string | 是 | 文档 UUID |

**请求示例：**
```http
GET /documents/650e8400-e29b-41d4-a716-446655440001
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 文档详细信息（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 文档唯一标识 |
| name | string | 文档名称 |
| size | integer | 文件大小（字节） |
| page | integer | 文档页数 |
| url | string | 文档访问 URL |
| uploaded_at | string | 上传时间 |
| chunk_count | integer | 文本块数量（从 Milvus 查询） |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "uuid": "650e8400-e29b-41d4-a716-446655440001",
    "name": "技术文档.pdf",
    "size": 1048576,
    "page": 50,
    "url": "/uploads/650e8400-e29b-41d4-a716-446655440001.pdf",
    "uploaded_at": "2025-10-24T11:00:00Z",
    "chunk_count": 120
  }
}
```

---

### 2.4 删除文档

**接口描述：** 删除文档（包括 MongoDB 记录、Milvus 向量、物理文件）

**请求方式：** `DELETE /documents/{document_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| document_id | string | 是 | 文档 UUID |

**请求示例：**
```http
DELETE /documents/650e8400-e29b-41d4-a716-446655440001
```

**响应示例：**
```json
{
  "code": 0,
  "message": "文档删除成功"
}
```

**注意事项：**
- 删除操作会同时删除：
  - MongoDB 中的文档记录
  - Milvus 中的所有向量数据
  - 本地存储的物理文件

---

## 3. 会话管理 API

基础路径：`/sessions`

### 3.1 获取会话列表

**接口描述：** 获取用户的会话列表（分页）

**请求方式：** `GET /sessions`

**Query 参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| user_id | string | 是 | 用户 ID | - | - |
| page | integer | 否 | 页码 | 1 | >= 1 |
| page_size | integer | 否 | 每页数量 | 20 | 1-100 |

**请求示例：**
```http
GET /sessions?user_id=550e8400-e29b-41d4-a716-446655440000&page=1&page_size=20
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 数据对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| total | integer | 总会话数 |
| sessions | array | 会话列表（见下表） |

**sessions 数组元素结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 会话唯一标识 |
| user_id | string | 用户 ID |
| name | string | 会话名称 |
| last_message | string | 最后一条消息 |
| create_at | string | 创建时间 |
| update_at | string | 更新时间 |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 15,
    "sessions": [
      {
        "uuid": "750e8400-e29b-41d4-a716-446655440010",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "RAG 技术讨论",
        "last_message": "RAG 是检索增强生成技术...",
        "create_at": "2025-10-24T09:00:00Z",
        "update_at": "2025-10-24T11:30:00Z"
      },
      {
        "uuid": "750e8400-e29b-41d4-a716-446655440011",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "向量数据库",
        "last_message": "Milvus 是一个开源向量数据库...",
        "create_at": "2025-10-23T15:00:00Z",
        "update_at": "2025-10-23T16:20:00Z"
      }
    ]
  }
}
```

---

### 3.2 获取会话详情

**接口描述：** 获取会话的完整信息

**请求方式：** `GET /sessions/{session_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 UUID |

**请求示例：**
```http
GET /sessions/750e8400-e29b-41d4-a716-446655440010
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 会话详细信息（结构同 3.1 的 sessions 元素） |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "uuid": "750e8400-e29b-41d4-a716-446655440010",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "RAG 技术讨论",
    "last_message": "RAG 是检索增强生成技术...",
    "create_at": "2025-10-24T09:00:00Z",
    "update_at": "2025-10-24T11:30:00Z"
  }
}
```

---

### 3.3 更新会话信息

**接口描述：** 更新会话的部分信息

**请求方式：** `PATCH /sessions/{session_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 UUID |

**请求体参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| name | string | 否 | 会话名称 | 长度 1-100 字符 |
| last_message | string | 否 | 最后一条消息 | - |

**请求示例：**
```json
{
  "name": "RAG 技术深度讨论"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "更新成功"
}
```

---

## 4. 消息管理 API

基础路径：`/messages`

### 4.1 发送消息并获取 AI 回复（流式）

**接口描述：** 发送消息并自动获取 AI 智能回复（统一流式返回，支持 Agent + RAG）

**请求方式：** `POST /messages`

**请求头：**
```http
Content-Type: application/json
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 约束 | 默认值 |
|--------|------|------|------|------|--------|
| content | string | 是 | 消息内容 | 最短 1 字符 | - |
| user_id | string | 是 | 用户 ID | - | - |
| session_id | string | 否 | 会话 ID | 不提供则创建新会话 | null |
| send_name | string | 否 | 发送者昵称 | - | "用户" |
| send_avatar | string | 否 | 发送者头像 URL | - | "" |
| file_type | string | 否 | 文件类型 | text/image/file | null |
| file_name | string | 否 | 文件名 | - | null |
| file_size | string | 否 | 文件大小 | - | null |
| show_thinking | boolean | 否 | 是否显示思考过程 | - | false |

**请求示例（隐藏思考过程）：**
```json
{
  "content": "你好",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "750e8400-e29b-41d4-a716-446655440010",
  "show_thinking": false
}
```

**请求示例（显示思考过程）：**
```json
{
  "content": "什么是 RAG 技术？",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "show_thinking": true
}
```

**响应格式：** SSE（Server-Sent Events）流式响应

**响应头：**
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**SSE 事件类型：**

| 事件类型 | 触发条件 | 数据结构 | 说明 |
|----------|----------|----------|------|
| `session_created` | 创建新会话时 | `{"session_id": "...", "session_name": "..."}` | 会话创建成功 |
| `user_message_saved` | 用户消息保存后 | `{"uuid": "...", "content": "..."}` | 用户消息已保存到数据库 |
| `thought` | Agent 思考时 | `{"content": "..."}` | 仅当 `show_thinking=true` |
| `action` | Agent 执行动作时 | `{"content": "..."}` | 仅当 `show_thinking=true` |
| `observation` | 工具返回结果时 | `{"content": "..."}` | 仅当 `show_thinking=true` |
| `answer_chunk` | AI 生成答案片段 | `{"content": "..."}` | 实时输出，每个 token |
| `ai_message_saved` | AI 消息保存后 | `{"uuid": "...", "content": "..."}` | AI 回复已保存到数据库 |
| `done` | 对话完成 | `{"session_id": "..."}` | 流式输出结束 |
| `error` | 发生错误 | `{"message": "..."}` | 错误信息 |

**SSE 响应格式：**
```
event: session_created
data: {"session_id": "750e8400-e29b-41d4-a716-446655440010", "session_name": "什么是 RAG..."}

event: user_message_saved
data: {"uuid": "850e8400-e29b-41d4-a716-446655440020", "content": "什么是 RAG 技术？"}

event: thought
data: {"content": "用户询问 RAG 技术，需要检索知识库获取权威信息"}

event: action
data: {"content": "knowledge_search(\"RAG 技术\", 5)"}

event: observation
data: {"content": "成功检索到 5 个相关文档片段：\n\n1. RAG（Retrieval-Augmented Generation）是检索增强生成技术..."}

event: answer_chunk
data: {"content": "RAG"}

event: answer_chunk
data: {"content": "（"}

event: answer_chunk
data: {"content": "Retrieval"}

event: answer_chunk
data: {"content": "-Augmented"}

event: answer_chunk
data: {"content": " Generation"}

event: answer_chunk
data: {"content": "）"}

event: answer_chunk
data: {"content": "是"}

event: answer_chunk
data: {"content": "检索"}

event: answer_chunk
data: {"content": "增强"}

event: answer_chunk
data: {"content": "生成"}

event: answer_chunk
data: {"content": "技术"}

event: answer_chunk
data: {"content": "..."}

event: ai_message_saved
data: {"uuid": "850e8400-e29b-41d4-a716-446655440021", "content": "RAG（Retrieval-Augmented Generation）是检索增强生成技术..."}

event: done
data: {"session_id": "750e8400-e29b-41d4-a716-446655440010"}
```

**客户端示例（Python）：**

**示例 1：隐藏思考过程**
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/messages",
    json={
        "content": "你好",
        "user_id": "user_001",
        "show_thinking": False
    },
    stream=True
)

print("AI 回复：", end='')
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('event: '):
            event_type = line_str.replace('event: ', '').strip()
        elif line_str.startswith('data: '):
            event_data = json.loads(line_str.replace('data: ', ''))
            
            # 只显示答案片段
            if event_type == 'answer_chunk':
                print(event_data['content'], end='', flush=True)

print()  # 换行
```

**示例 2：显示思考过程**
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/messages",
    json={
        "content": "什么是 RAG 技术？",
        "user_id": "user_001",
        "show_thinking": True
    },
    stream=True
)

current_event = None
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('event: '):
            current_event = line_str.replace('event: ', '').strip()
        elif line_str.startswith('data: '):
            event_data = json.loads(line_str.replace('data: ', ''))
            
            # 显示不同类型的事件
            if current_event == 'thought':
                print(f"\n💭 思考: {event_data['content']}")
            elif current_event == 'action':
                print(f"🔧 动作: {event_data['content']}")
            elif current_event == 'observation':
                print(f"👀 观察: {event_data['content'][:100]}...")
            elif current_event == 'answer_chunk':
                print(event_data['content'], end='', flush=True)
            elif current_event == 'done':
                print("\n✅ 完成")
```

**客户端示例（JavaScript/浏览器）：**
```javascript
const eventSource = new EventSource('/messages?...');

// 监听 answer_chunk 事件
eventSource.addEventListener('answer_chunk', (e) => {
    const data = JSON.parse(e.data);
    document.getElementById('answer').innerHTML += data.content;
});

// 监听 thought 事件
eventSource.addEventListener('thought', (e) => {
    const data = JSON.parse(e.data);
    console.log('💭 思考:', data.content);
});

// 监听 done 事件
eventSource.addEventListener('done', (e) => {
    eventSource.close();
    console.log('✅ 完成');
});

// 监听 error 事件
eventSource.addEventListener('error', (e) => {
    const data = JSON.parse(e.data);
    console.error('❌ 错误:', data.message);
    eventSource.close();
});
```

**注意事项：**
1. **流式输出**：响应是实时流式的，客户端需要使用 SSE 或 stream 方式接收
2. **show_thinking 参数**：
   - `false`（默认）：只返回 `answer_chunk`，隐藏思考过程
   - `true`：返回完整的 Agent 推理过程（Thought → Action → Observation → Answer）
3. **自动创建会话**：如果不提供 `session_id`，系统会自动创建新会话
4. **Agent + RAG**：系统会自动调用 ReAct Agent，必要时检索知识库
5. **真正的流式**：每个 token 生成后立即发送，不是假流式

---

### 4.2 获取会话的所有消息

**接口描述：** 获取指定会话的所有消息（分页）

**请求方式：** `GET /messages/{session_id}`

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 UUID |

**Query 参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 | 约束 |
|--------|------|------|------|--------|------|
| page | integer | 否 | 页码 | 1 | >= 1 |
| page_size | integer | 否 | 每页数量 | 50 | 1-200 |

**请求示例：**
```http
GET /messages/750e8400-e29b-41d4-a716-446655440010?page=1&page_size=50
```

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码 |
| message | string | 响应消息 |
| data | object | 数据对象（见下表） |

**data 对象结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| total | integer | 总消息数 |
| messages | array | 消息列表（见下表） |

**messages 数组元素结构：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 消息唯一标识 |
| session_id | string | 会话 ID |
| content | string | 消息内容 |
| send_type | integer | 发送者类型（0=用户, 1=AI, 2=系统） |
| send_id | string | 发送者 UUID |
| send_name | string | 发送者昵称 |
| send_avatar | string | 发送者头像 |
| receive_id | string | 接收者 UUID |
| file_type | string | 文件类型 |
| file_name | string | 文件名 |
| file_size | string | 文件大小 |
| status | integer | 状态（0=未发送, 1=已发送） |
| created_at | string | 创建时间 |
| send_at | string | 发送时间 |

**响应示例：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 10,
    "messages": [
      {
        "uuid": "850e8400-e29b-41d4-a716-446655440020",
        "session_id": "750e8400-e29b-41d4-a716-446655440010",
        "content": "什么是 RAG 技术？",
        "send_type": 0,
        "send_id": "550e8400-e29b-41d4-a716-446655440000",
        "send_name": "张三",
        "send_avatar": "",
        "receive_id": "system",
        "file_type": null,
        "file_name": null,
        "file_size": null,
        "status": 1,
        "created_at": "2025-10-24T11:30:00Z",
        "send_at": "2025-10-24T11:30:00Z"
      },
      {
        "uuid": "850e8400-e29b-41d4-a716-446655440021",
        "session_id": "750e8400-e29b-41d4-a716-446655440010",
        "content": "RAG（Retrieval-Augmented Generation）是检索增强生成技术...",
        "send_type": 1,
        "send_id": "system",
        "send_name": "AI助手",
        "send_avatar": "",
        "receive_id": "550e8400-e29b-41d4-a716-446655440000",
        "file_type": null,
        "file_name": null,
        "file_size": null,
        "status": 1,
        "created_at": "2025-10-24T11:30:15Z",
        "send_at": "2025-10-24T11:30:15Z"
      }
    ]
  }
}
```

---

## 5. 通用响应格式

所有非流式接口的响应都遵循以下统一格式：

```json
{
  "code": 0,
  "message": "操作成功",
  "data": {}
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码（详见下方错误码说明） |
| message | string | 响应消息，用于展示给用户 |
| data | object/array/null | 业务数据，根据接口不同而不同 |

---

## 6. 错误码说明

| 错误码 | 说明 | 常见原因 |
|--------|------|----------|
| 0 | 成功 | 请求处理成功 |
| -1 | 失败 | 一般业务错误（具体原因见 message） |
| -2 | 参数错误 | 请求参数不合法或缺失必填参数 |
| 200 | 成功 | HTTP 成功 |
| 400 | 请求错误 | 请求参数格式错误 |
| 401 | 未授权 | Token 无效或过期 |
| 403 | 禁止访问 | 无权限访问该资源 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器错误 | 服务器内部错误 |

### 常见错误响应示例

**参数错误：**
```json
{
  "code": -2,
  "message": "参数错误：邮箱格式不正确"
}
```

**资源不存在：**
```json
{
  "code": 404,
  "message": "用户不存在"
}
```

**系统错误：**
```json
{
  "code": -1,
  "message": "系统错误"
}
```

---

## 7. 附录

### 7.1 时间格式

所有时间字段均使用 ISO 8601 格式：

```
2025-10-24T11:30:00Z
```

### 7.2 UUID 格式

所有 UUID 均使用 UUID4 格式：

```
550e8400-e29b-41d4-a716-446655440000
```

### 7.3 分页说明

- `page`：页码从 1 开始
- `page_size`：每页数量，一般最大为 100（消息接口为 200）
- `total`：总记录数

### 7.4 文件大小单位

文件大小字段均使用字节（Byte）为单位。

### 7.5 SSE（Server-Sent Events）说明

SSE 是一种标准的 HTTP 流式协议，用于服务器向客户端实时推送数据。

**格式：**
```
event: <事件类型>
data: <JSON 数据>

```

**注意：**
- 每个事件块以空行结尾
- data 字段必须是 JSON 格式
- 客户端需要使用 EventSource API 或 stream 方式接收

---

## 8. 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2025-10-24 | 初始版本，包含用户、文档、会话、消息管理 API |

---

## 9. 联系方式

如有问题，请联系开发团队。

**技术支持邮箱：** support@example.com  
**项目地址：** https://github.com/example/rag-platform

---

**© 2025 RAG 平台 API 文档**

