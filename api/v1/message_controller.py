"""
消息管理 API 控制器 (RESTful 风格)
集成 Agent + RAG 检索
统一流式返回
"""
from fastapi import APIRouter, Query, Path
from fastapi.responses import StreamingResponse
from internal.dto.request import SendMessageRequest
from internal.service.orm.message_sever import message_service
from api.v1.response_controller import json_response
from log import logger
import json as json_module

router = APIRouter(prefix="/messages", tags=["消息管理"])


@router.post("", summary="发送消息并获取 AI 回复（统一流式返回）")
async def send_message(req: SendMessageRequest):
    """
    发送消息并自动获取 AI 智能回复（统一流式返回）
    
    
    
    **参数：**
    - **content**: 消息内容（必填）
    - **user_id**: 用户ID（必填）
    - **session_id**: 会话ID（可选，不提供则创建新会话）
    - **send_name**: 发送者昵称（默认"用户"）
    - **send_avatar**: 发送者头像URL
    - **file_type**: 文件类型（text/image/file）
    - **file_name**: 文件名
    - **file_size**: 文件大小
    - **show_thinking**: 是否显示思考过程（默认 False）
    
    **返回格式：**
    统一使用 SSE（Server-Sent Events）流式返回
    
    **SSE 事件类型：**
    - `session_created`: 会话创建
    - `user_message_saved`: 用户消息保存完成
    - `thought`: Agent 思考过程（仅 show_thinking=True）
    - `action`: Agent 执行动作（仅 show_thinking=True）
    - `observation`: 观察结果（仅 show_thinking=True）
    - `answer_chunk`: 最终答案片段（流式输出）
    - `ai_message_saved`: AI 消息保存完成
    - `done`: 完成
    - `error`: 错误
    
    **show_thinking 参数说明：**
    - `show_thinking=False`（默认）：只返回答案片段，隐藏思考过程
    - `show_thinking=True`：显示完整思考过程（Thought → Action → Observation → Answer）
    
    **使用示例（Python）：**
    ```python
    import requests
    
    # 不显示思考过程
    response = requests.post(
        "http://localhost:8000/messages",
        json={
            "content": "你好",
            "user_id": "user_001",
            "show_thinking": False  # 只看答案
        },
        stream=True
    )
    
    # 显示思考过程
    response = requests.post(
        "http://localhost:8000/messages",
        json={
            "content": "什么是 RAG？",
            "user_id": "user_001",
            "show_thinking": True  # 显示推理过程
        },
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
    ```
    """
    try:
        logger.info(f"收到发送消息请求: user={req.user_id}, session={req.session_id}, show_thinking={req.show_thinking}")
        
        async def event_generator():
            """SSE 事件生成器（在 Controller 层格式化）"""
            try:
                async for event in message_service.send_message_stream(
                    content=req.content,
                    user_id=req.user_id,
                    send_name=req.send_name,
                    send_avatar=req.send_avatar,
                    session_id=req.session_id,
                    file_type=req.file_type,
                    file_name=req.file_name,
                    file_size=req.file_size,
                    show_thinking=req.show_thinking
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
