# API 开发规范文档

## 📋 目录
1. [项目架构](#项目架构)
2. [分层设计](#分层设计)
3. [RESTful API 设计规范](#restful-api-设计规范)
4. [统一响应格式](#统一响应格式)
5. [开发流程](#开发流程)
6. [代码规范](#代码规范)
7. [示例代码](#示例代码)

---

## 🏗️ 项目架构

```
plantform/
├── api/v1/                      # API 控制器层
│   ├── user_info_controller.py  # 用户管理接口
│   ├── document_controller.py   # 文档管理接口
│   └── response_controller.py   # 统一响应工具
├── internal/
│   ├── dto/                     # 数据传输对象
│   │   ├── request/             # 请求模型
│   │   └── respond/             # 响应模型
│   ├── service/orm/             # 业务逻辑层
│   │   ├── user_info_sever.py   # 用户业务逻辑
│   │   └── document_sever.py    # 文档业务逻辑
│   ├── model/                   # MongoDB 数据模型
│   ├── db/                      # 数据库连接
│   └── http_sever/              # HTTP 服务器配置
└── test/                        # 测试文件
```

---

## 🎯 分层设计

### 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  API 层 (Controller)                                         │
│  - 接收 HTTP 请求                                             │
│  - 参数验证                                                   │
│  - 调用 Service 层                                            │
│  - 返回统一格式响应                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  业务逻辑层 (Service)                                         │
│  - 处理业务逻辑                                               │
│  - 数据库操作（MongoDB、Milvus、Redis）                       │
│  - 返回: (message, ret, data)                                │
│    - message: str (提示信息)                                  │
│    - ret: int (0:成功, -1:服务器错误, -2:客户端错误)           │
│    - data: Any (数据，可选)                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  数据访问层 (Model + DB)                                      │
│  - MongoDB (Beanie ODM)                                      │
│  - Milvus (向量数据库)                                        │
│  - Redis (缓存)                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 RESTful API 设计规范

### HTTP 方法使用规范

| HTTP 方法 | 操作 | 幂等性 | 使用场景 |
|-----------|------|--------|----------|
| **GET** | 查询 | ✅ 是 | 获取资源列表、获取单个资源详情 |
| **POST** | 创建 | ❌ 否 | 创建新资源、复杂查询（带 Body） |
| **PUT** | 完整更新 | ✅ 是 | 完整替换资源 |
| **PATCH** | 部分更新 | ✅ 是 | 部分更新资源字段 |
| **DELETE** | 删除 | ✅ 是 | 删除资源 |

### URL 设计规范

#### 基本原则

1. **使用名词复数形式**
   ```
   ✅ /api/v1/users
   ✅ /api/v1/documents
   ❌ /api/v1/user
   ❌ /api/v1/getUser
   ```

2. **资源层级清晰**
   ```
   ✅ /api/v1/users/{user_id}
   ✅ /api/v1/users/{user_id}/documents
   ❌ /api/v1/getUserDocuments
   ```

3. **使用连字符（kebab-case）**
   ```
   ✅ /api/v1/user-profiles
   ❌ /api/v1/userProfiles
   ❌ /api/v1/user_profiles
   ```

#### 标准端点设计

| 操作 | HTTP 方法 | 路径 | 说明 |
|------|-----------|------|------|
| 获取列表 | GET | `/resources` | 获取资源列表（支持分页、过滤） |
| 获取详情 | GET | `/resources/{id}` | 获取单个资源详情 |
| 创建资源 | POST | `/resources` | 创建新资源 |
| 完整更新 | PUT | `/resources/{id}` | 完整更新资源 |
| 部分更新 | PATCH | `/resources/{id}` | 部分更新资源 |
| 删除资源 | DELETE | `/resources/{id}` | 删除资源 |

### 查询参数规范

#### GET 请求参数

```
# 分页
GET /api/v1/documents?page=1&page_size=10

# 过滤
GET /api/v1/documents?keyword=test&status=active

# 排序
GET /api/v1/documents?sort=created_at&order=desc

# 字段筛选
GET /api/v1/documents?fields=id,name,created_at
```

#### 路径参数

```python
# 资源 ID
GET /api/v1/documents/{document_id}

# 嵌套资源
GET /api/v1/users/{user_id}/documents/{document_id}
```

### 实际应用示例

#### 用户管理 API

```
POST   /api/v1/users              # 注册用户
POST   /api/v1/users/login        # 用户登录
GET    /api/v1/users              # 获取用户列表
GET    /api/v1/users/{id}         # 获取用户详情
PATCH  /api/v1/users/{id}         # 更新用户信息
DELETE /api/v1/users/{id}         # 删除用户
POST   /api/v1/users/email-code   # 发送邮箱验证码
```

#### 文档管理 API

```
POST   /api/v1/documents          # 上传文档
GET    /api/v1/documents          # 获取文档列表
GET    /api/v1/documents/{id}     # 获取文档详情
PATCH  /api/v1/documents/{id}     # 更新文档信息
DELETE /api/v1/documents/{id}     # 删除文档
GET    /api/v1/documents/{id}/chunks  # 获取文档分块
```

### HTTP 状态码规范

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| **200** | OK | 成功响应（GET、PUT、PATCH、DELETE） |
| **201** | Created | 创建成功（POST） |
| **204** | No Content | 删除成功且无返回内容 |
| **400** | Bad Request | 请求参数错误、验证失败 |
| **401** | Unauthorized | 未认证 |
| **403** | Forbidden | 无权限 |
| **404** | Not Found | 资源不存在 |
| **409** | Conflict | 资源冲突（如用户名已存在） |
| **500** | Internal Server Error | 服务器错误 |

### RESTful vs 非 RESTful 对比

| 操作 | 非 RESTful | RESTful |
|------|-----------|---------|
| 获取用户列表 | POST /getUserList | GET /users?page=1 |
| 获取用户详情 | POST /getUserInfo | GET /users/{id} |
| 创建用户 | POST /createUser | POST /users |
| 更新用户 | POST /updateUser | PATCH /users/{id} |
| 删除用户 | POST /deleteUser | DELETE /users/{id} |

---

## 📦 统一响应格式

### Response 结构

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### Code 码规范

| Code | 说明 | Service 层 ret | 使用场景 |
|------|------|----------------|----------|
| 200  | 成功 | 0              | 操作成功 |
| 400  | 客户端错误 | -2        | 参数错误、验证失败 |
| 404  | 资源不存在 | -2        | 数据不存在 |
| 500  | 服务器错误 | -1        | 系统异常 |

### json_response 函数

```python
def json_response(
    message: str,
    ret: int = 0,
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """
    统一响应格式
    
    Args:
        message: 响应消息
        ret: 返回码 (0:成功, -1:服务器错误, -2:客户端错误)
        data: 响应数据（可选）
        status_code: HTTP 状态码
    
    Returns:
        JSONResponse
    """
```

**自动映射规则：**
- `ret = 0`  → `code = 200` (成功)
- `ret = -1` → `code = 500` (服务器错误)
- `ret = -2` → `code = 400` (客户端错误)

---

## 🔄 开发流程

### 步骤 1: 定义 DTO (数据传输对象)

#### Request DTO (`internal/dto/request/`)

```python
# example_request.py
from pydantic import BaseModel, Field
from typing import Optional

class CreateItemRequest(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
```

#### Response DTO (`internal/dto/respond/`)

```python
# example_response.py
from pydantic import BaseModel, Field
from datetime import datetime

class ItemResponse(BaseModel):
    """项目响应"""
    id: str = Field(..., description="项目ID")
    name: str = Field(..., description="项目名称")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### 步骤 2: 实现 Service 层

```python
# internal/service/orm/example_sever.py
from internal.model.item import ItemModel
from log import logger

class ExampleService:
    """示例业务服务"""
    
    async def create_item(self, name: str, description: str = None):
        """
        创建项目
        
        Args:
            name: 项目名称
            description: 项目描述
            
        Returns:
            tuple: (message, ret, data)
        """
        try:
            # 1. 业务逻辑验证
            existing = await ItemModel.find_one(ItemModel.name == name)
            if existing:
                return "项目名称已存在", -2, None
            
            # 2. 创建数据
            item = ItemModel(name=name, description=description)
            await item.insert()
            
            # 3. 返回结果
            data = {
                "id": item.id,
                "name": item.name,
                "created_at": item.created_at
            }
            return "创建成功", 0, data
            
        except Exception as e:
            logger.error(f"创建项目失败: {e}", exc_info=True)
            return f"创建失败: {str(e)}", -1, None
    
    async def get_item(self, item_id: str):
        """
        获取项目详情
        
        Returns:
            tuple: (message, ret, data)
        """
        try:
            item = await ItemModel.find_one(ItemModel.id == item_id)
            
            if not item:
                return "项目不存在", -2, None
            
            data = {
                "id": item.id,
                "name": item.name,
                "created_at": item.created_at
            }
            return "查询成功", 0, data
            
        except Exception as e:
            logger.error(f"查询项目失败: {e}", exc_info=True)
            return f"查询失败: {str(e)}", -1, None

# 导出单例
example_service = ExampleService()
```

### 步骤 3: 实现 Controller 层

```python
# api/v1/example_controller.py
from fastapi import APIRouter, Query
from internal.service.orm.example_sever import example_service
from internal.dto.request import CreateItemRequest
from api.v1.response_controller import json_response
from log import logger

router = APIRouter(prefix="/item", tags=["项目管理"])


@router.post("/create", summary="创建项目")
async def create_item(req: CreateItemRequest):
    """创建项目"""
    try:
        logger.info(f"创建项目请求: {req.name}")
        
        # 调用 Service 层
        message, ret, data = await example_service.create_item(
            name=req.name,
            description=req.description
        )
        
        # 返回响应
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"创建项目接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("/detail", summary="获取项目详情")
async def get_item(item_id: str = Query(..., description="项目ID")):
    """获取项目详情"""
    try:
        logger.info(f"获取项目详情: {item_id}")
        
        message, ret, data = await example_service.get_item(item_id)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取项目详情接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)
```

### 步骤 4: 注册路由

```python
# internal/http_sever/routes.py
from api.v1.example_controller import router as example_router

def setup_routes(app: FastAPI):
    app.include_router(example_router)
```

---

## 📝 代码规范

### 1. 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | 小写+下划线 | `user_info_controller.py` |
| 类名 | 大驼峰 | `UserInfoService` |
| 函数名 | 小写+下划线 | `get_user_info()` |
| 常量 | 大写+下划线 | `MAX_RETRY_COUNT` |
| 变量 | 小写+下划线 | `user_id` |

### 2. Service 层返回值规范

**✅ 正确示例：**

```python
# 成功（有数据）
return "操作成功", 0, {"id": 123, "name": "张三"}

# 成功（无数据）
return "删除成功", 0, None

# 客户端错误
return "用户不存在", -2, None

# 服务器错误
return f"数据库错误: {str(e)}", -1, None
```

**❌ 错误示例：**

```python
# 不要返回 Dict
return {"success": True, "message": "成功"}

# 不要返回不一致的结构
return "成功", {"data": ...}
```

### 3. Controller 层规范

```python
@router.post("/xxx")
async def xxx(req: XxxRequest):
    try:
        # 1. 记录日志
        logger.info(f"接口请求: {req}")
        
        # 2. 调用 Service（接收3个返回值）
        message, ret, data = await service.method(req)
        
        # 3. 返回响应
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        # 4. 异常处理
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)
```

### 4. 日志规范

```python
# 使用统一的 logger
from log import logger

# INFO: 记录正常流程
logger.info(f"用户登录: {username}")

# WARNING: 记录警告信息
logger.warning(f"登录失败次数过多: {username}")

# ERROR: 记录错误（带堆栈）
logger.error(f"数据库连接失败: {e}", exc_info=True)
```

### 5. DateTime 序列化规范

**在 Service 层处理：**

```python
# ❌ 错误：直接返回 datetime 对象
return "成功", 0, {
    "created_at": doc.create_at  # datetime 对象
}

# ✅ 正确：转换为字符串
return "成功", 0, {
    "created_at": doc.create_at.isoformat()  # 字符串
}
```

**或在 Response DTO 中配置：**

```python
class ItemResponse(BaseModel):
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

## 📚 示例代码

### 完整示例：用户注册

#### 1. Request DTO

```python
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
```

#### 2. Service 层

```python
async def register(self, req: RegisterRequest):
    try:
        # 检查用户是否存在
        existing = await UserModel.find_one(UserModel.username == req.username)
        if existing:
            return "用户名已存在", -2, None
        
        # 创建用户
        user = UserModel(
            username=req.username,
            password=hash_password(req.password)
        )
        await user.insert()
        
        # 生成 token
        token = create_token({"user_id": user.id})
        
        data = {
            "user_id": user.id,
            "username": user.username,
            "token": token
        }
        return "注册成功", 0, data
        
    except Exception as e:
        logger.error(f"注册失败: {e}", exc_info=True)
        return f"注册失败: {str(e)}", -1, None
```

#### 3. Controller 层

```python
@router.post("/register")
async def register(req: RegisterRequest):
    try:
        logger.info(f"用户注册: {req.username}")
        message, ret, data = await user_service.register(req)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"注册接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)
```

#### 4. 响应示例

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": "abc123",
    "username": "zhangsan",
    "token": "eyJhbGc..."
  }
}
```

---

## ✅ 检查清单

开发新接口时，请确保：

- [ ] DTO 定义完整（Request + Response）
- [ ] Service 层返回 `(message, ret, data)` 格式
- [ ] Controller 层正确解包 Service 返回值
- [ ] 使用 `json_response(message, ret, data)` 返回
- [ ] 添加日志记录（info + error）
- [ ] DateTime 对象正确序列化
- [ ] 异常处理完整
- [ ] 在 `routes.py` 中注册路由
- [ ] 编写测试用例

---

## 🚀 快速开发模板

### RESTful API 模板

```python
# === Service 层 ===
async def method_name(self, param1, param2):
    try:
        # 业务逻辑
        # ...
        
        return "操作成功", 0, data
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return f"操作失败: {str(e)}", -1, None

# === Controller 层 ===
from fastapi import APIRouter, Query, Path

router = APIRouter(prefix="/resources", tags=["资源管理"])

# GET /resources - 获取列表
@router.get("")
async def get_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100)
):
    try:
        logger.info(f"获取列表: page={page}, page_size={page_size}")
        message, ret, data = await service.get_list(page, page_size)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)

# GET /resources/{id} - 获取详情
@router.get("/{resource_id}")
async def get_detail(
    resource_id: str = Path(..., description="资源ID")
):
    try:
        logger.info(f"获取详情: {resource_id}")
        message, ret, data = await service.get_detail(resource_id)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)

# POST /resources - 创建资源
@router.post("")
async def create(req: CreateRequest):
    try:
        logger.info(f"创建资源: {req}")
        message, ret, data = await service.create(req)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)

# PATCH /resources/{id} - 更新资源
@router.patch("/{resource_id}")
async def update(
    resource_id: str = Path(..., description="资源ID"),
    req: UpdateRequest = None
):
    try:
        req.id = resource_id
        logger.info(f"更新资源: {resource_id}")
        message, ret, data = await service.update(req)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)

# DELETE /resources/{id} - 删除资源
@router.delete("/{resource_id}")
async def delete(
    resource_id: str = Path(..., description="资源ID")
):
    try:
        logger.info(f"删除资源: {resource_id}")
        message, ret = await service.delete(resource_id)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return json_response("系统错误", -1)
```

---

## 📞 联系与支持

如有疑问，请参考：
- 现有代码: `api/v1/user_info_controller.py`
- 现有代码: `api/v1/document_controller.py`

遵循此规范，确保代码风格统一，易于维护！

