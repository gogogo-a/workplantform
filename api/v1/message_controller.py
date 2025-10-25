"""
消息管理 API 控制器 (RESTful 风格)
集成 Agent + RAG 检索
统一流式返回
支持文件上传
"""
from fastapi import APIRouter, Query, Path, Request, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from internal.dto.request import SendMessageRequest
from internal.service.orm.message_sever import message_service
from api.v1.response_controller import json_response
from pkg.middleware.auth import get_user_from_request
from pkg.utils.document_utils import parse_document_content
from log import logger
import json as json_module
from typing import Optional

# 使用全局JWT中间件，不需要路由级别的dependencies
router = APIRouter(
    prefix="/messages", 
    tags=["消息管理"]
)


@router.post("", summary="发送消息并获取 AI 回复（统一流式返回，支持文件上传）")
async def send_message(
    request: Request,
    content: str = Form(..., description="消息内容"),
    session_id: Optional[str] = Form(None, description="会话ID（可选）"),
    send_name: Optional[str] = Form(None, description="发送者昵称（可选）"),
    send_avatar: Optional[str] = Form(None, description="发送者头像URL（可选）"),
    show_thinking: str = Form("false", description="是否显示思考过程"),
    file: Optional[UploadFile] = File(None, description="上传的文件（可选，支持 .pdf/.docx/.txt）")
):
    """
    发送消息并自动获取 AI 智能回复（统一流式返回，支持文件上传）
    
    ⚠️ 调试模式：临时打印所有接收到的参数
    
    **参数：**
    - **content**: 消息内容（必填）
    - **session_id**: 会话ID（可选，不提供则创建新会话）
    - **send_name**: 发送者昵称（可选，使用token中的昵称）
    - **send_avatar**: 发送者头像URL（可选）
    - **show_thinking**: 是否显示思考过程（默认 False）
    - **file**: 上传的文件（可选，支持 .pdf/.docx/.txt）
    
    **文件上传说明：**
    如果上传了文件，系统会：
    1. 解析文件内容（支持 PDF、Word、TXT）
    2. 在消息中添加文件类型提示："这是我上传的 xxx 文件..."
    3. 将文件内容保存到消息的 extra_data 中
    4. AI 会基于文件内容回答问题
    
    **返回格式：**
    统一使用 SSE（Server-Sent Events）流式返回
    
    **SSE 事件类型：**
    - `session_created`: 会话创建
    - `user_message_saved`: 用户消息保存完成
    - `thought`: Agent 思考过程（仅 show_thinking=True）
    - `action`: Agent 执行动作（仅 show_thinking=True）
    - `observation`: 观察结果（仅 show_thinking=True）
    - `answer_chunk`: 最终答案片段（流式输出）
    - `documents`: 检索到的文档列表（包含 uuid 和 name，已去重）
    - `ai_message_saved`: AI 消息保存完成
    - `done`: 完成
    - `error`: 错误
    
    **使用示例（Python - 不带文件）：**
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8000/messages",
        data={
            "content": "你好",
            "show_thinking": "false"
        },
        headers={"Authorization": "Bearer <token>"},
        stream=True
    )
    ```
    
    **使用示例（Python - 带文件）：**
    ```python
    import requests
    
    with open("document.pdf", "rb") as f:
        response = requests.post(
            "http://localhost:8000/messages",
            data={
                "content": "请总结这个文档的主要内容",
                "show_thinking": "true"
            },
            files={"file": ("document.pdf", f, "application/pdf")},  # 注意：字段名是 'file'
            headers={"Authorization": "Bearer <token>"},
            stream=True
        )
    ```
    """
    try:
        # 🔥 调试：打印所有接收到的参数
        logger.info(f"📥 接收到的参数: content={content}, session_id={session_id}, show_thinking={show_thinking}, has_file={file is not None}")
        if file:
            logger.info(f"📎 文件信息: filename={file.filename}, content_type={file.content_type}")
        
        # 验证必填参数
        if not content:
            logger.error("❌ content 参数缺失或为空")
            return json_response("消息内容不能为空", -1)
        
        # 从全局中间件中获取用户信息
        logger.debug(f"开始获取用户信息, request.state: {hasattr(request.state, 'user')}")
        try:
            current_user = get_user_from_request(request)
            logger.debug(f"用户信息获取成功: {current_user}")
        except Exception as auth_error:
            logger.error(f"获取用户信息失败: {auth_error}", exc_info=True)
            raise
        
        user_id = current_user.get("user_id")
        user_nickname = current_user.get("nickname", "用户")
        
        # 🔥 Controller 层职责：文件解析
        file_content = None
        file_type = None
        file_name = None
        file_size = None
        enhanced_content = content
        
        # 处理文件上传
        if file:
            logger.info(f"检测到文件上传: {file.filename}, content_type={file.content_type}")
            
            try:
                # 1. 读取文件
                file_bytes = await file.read()
                file_size = str(len(file_bytes))
                file_name = file.filename
                
                # 2. 解析文件内容（Controller 层职责）
                file_content = parse_document_content(file_bytes, file_name)
                
                # 3. 确定文件类型
                if file_name.endswith('.pdf'):
                    file_type = 'pdf'
                elif file_name.endswith(('.docx', '.doc')):
                    file_type = 'docx'
                elif file_name.endswith('.txt'):
                    file_type = 'txt'
                else:
                    file_type = 'file'
                
                # 4. 构建增强内容（包含文件提示）
                enhanced_content = f"""这是我上传的 {file_type.upper()} 文件（文件名：{file_name}）：

{file_content}

---

我的问题：{content}"""
                
                logger.info(f"文件解析成功: type={file_type}, size={file_size}, content_length={len(file_content)}")
                
            except Exception as e:
                logger.error(f"文件解析失败: {e}", exc_info=True)
                return json_response(f"文件解析失败: {str(e)}", -1)
        
        logger.info(f"收到发送消息请求: user={user_id}, nickname={user_nickname}, session={session_id}, show_thinking={show_thinking}, has_file={file is not None}")
        
        async def event_generator():
            """SSE 事件生成器（在 Controller 层格式化）"""
            try:
                async for event in message_service.send_message_stream(
                    content=content,  # 🔥 原始用户问题（保存到数据库）
                    user_id=user_id,
                    send_name=send_name or user_nickname,
                    send_avatar=send_avatar or "",
                    session_id=session_id,
                    file_type=file_type,
                    file_name=file_name,
                    file_size=file_size,
                    file_content=file_content,  # 🔥 文件内容（保存到 extra_data）
                    show_thinking=show_thinking,
                    enhanced_content=enhanced_content  # 🔥 增强内容（发给 AI）
                ):
                    # 格式化为 SSE 格式
                    event_type = event.get("event", "message")
                    event_data = event.get("data", {})
                    
                    # SSE 格式: event: <type>\ndata: <json>\n\n
                    yield f"event: {event_type}\n"
                    yield f"data: {json_module.dumps(event_data, ensure_ascii=False)}\n\n"
                    
            except Exception as e:
                logger.error(f"流式生成失败: {e}", exc_info=True)
                yield f"event: error\n"
                yield f"data: {json_module.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("/{session_id}", summary="获取会话的所有消息")
async def get_session_messages(
    session_id: str = Path(..., description="会话UUID"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页数量")
):
    """
    获取会话的所有消息（按时间升序）
    
    - **session_id**: 会话UUID
    - **page**: 页码（从1开始，默认1）
    - **page_size**: 每页数量（默认50，最大200）
    
    返回：
    - total: 总消息数
    - messages: 消息列表
      - uuid: 消息UUID
      - session_id: 会话ID
      - content: 消息内容
      - send_type: 发送者类型（0.用户，1.AI，2.系统）
      - send_id: 发送者UUID
      - send_name: 发送者昵称
      - send_avatar: 发送者头像
      - receive_id: 接受者UUID
      - file_type: 文件类型
      - file_name: 文件名
      - file_size: 文件大小
      - status: 状态（0.未发送，1.已发送）
      - extra_data: 额外数据（仅AI消息有，包含思考过程和检索文档）
        - documents: 检索到的文档列表 [{"uuid": "...", "name": "..."}]
        - thoughts: 思考过程列表（仅当发送时启用了 show_thinking）
        - actions: 执行动作列表（仅当发送时启用了 show_thinking）
        - observations: 观察结果列表（仅当发送时启用了 show_thinking）
      - created_at: 创建时间
      - send_at: 发送时间
    """
    try:
        logger.info(f"收到获取会话消息请求: session={session_id}, page={page}, page_size={page_size}")
        
        message, ret, data = await message_service.get_session_messages(
            session_id=session_id,
            page=page,
            page_size=page_size
        )
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取会话消息失败: {e}", exc_info=True)
        return json_response("系统错误", -1)
