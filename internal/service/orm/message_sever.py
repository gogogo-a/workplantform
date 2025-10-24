"""
消息管理业务逻辑（模块化设计）
参考 test_full_rag_qa.py 的 AI 回答流程
集成 Agent + RAG 检索
"""
from typing import Tuple, Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime
import uuid as uuid_module

from internal.model.message import MessageModel
from internal.model.session import SessionModel
from internal.db.redis import redis_client
from internal.db.milvus import milvus_client
from internal.chat_service.chat_service import ChatService
from internal.rag.rag_service import rag_service
from pkg.model_list import DEEPSEEK_CHAT
from pkg.agent_prompt.prompt_templates import AGENT_RAG_PROMPT
from pkg.agent_prompt.agent_tool import knowledge_search
from log import logger


class MessageService:
    """消息管理服务（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化 RAG 服务"""
        if self._initialized:
            return
        
        # 初始化 RAG 服务
        self._init_rag_service()
        self._initialized = True
    
    def _init_rag_service(self):
        """初始化 RAG 检索服务"""
        try:
            # 连接 Milvus（如果还没连接）
            from pymilvus import connections
            if not connections.has_connection("default"):
                logger.info("连接 Milvus...")
                milvus_client.connect()
            
            # 设置 collection name
            collection_name = "rag_documents"  # 默认集合名
            rag_service.collection_name = collection_name
            
            # 初始化 RAG 服务
            logger.info(f"初始化 RAG 检索服务: collection={collection_name}")
            rag_service.initialize()
            
            logger.info("✓ RAG 服务初始化成功")
            
        except Exception as e:
            logger.warning(f"RAG 服务初始化失败: {e}，将在没有 RAG 的情况下运行")
    
    # ==================== 私有辅助函数（模块化）====================
    
    async def _create_or_get_session(
        self, 
        session_id: Optional[str], 
        user_id: str, 
        content: str
    ) -> Tuple[str, str]:
        """
        创建或获取会话
        
        Args:
            session_id: 会话ID（可选）
            user_id: 用户ID
            content: 消息内容（用于生成会话名称）
            
        Returns:
            (session_id, session_name)
        """
        try:
            if session_id:
                # 查找现有会话
                session = await SessionModel.find_one(SessionModel.uuid == session_id)
                if session:
                    logger.info(f"使用现有会话: {session_id}")
                    return session.uuid, session.name
                else:
                    logger.warning(f"会话不存在，将创建新会话: {session_id}")
            
            # 创建新会话
            # 会话名称：消息前10个字符，超过则加"..."
            session_name = content[:10] + ("..." if len(content) > 10 else "")
            
            new_session = SessionModel(
                uuid=str(uuid_module.uuid4()),
                user_id=user_id,
                name=session_name,
                last_message=content
            )
            await new_session.insert()
            
            logger.info(f"创建新会话: {new_session.uuid}, 名称: {session_name}")
            return new_session.uuid, session_name
            
        except Exception as e:
            logger.error(f"创建/获取会话失败: {e}", exc_info=True)
            raise
    
    async def _save_user_message(
        self,
        session_id: str,
        content: str,
        user_id: str,
        send_name: str,
        send_avatar: str,
        file_type: Optional[str] = None,
        file_name: Optional[str] = None,
        file_size: Optional[str] = None
    ) -> MessageModel:
        """
        保存用户消息到数据库
        
        Returns:
            MessageModel: 保存的消息对象
        """
        try:
            message = MessageModel(
                uuid=str(uuid_module.uuid4()),
                session_id=session_id,
                content=content,
                send_type=0,  # 0.用户
                send_id=user_id,
                send_name=send_name,
                send_avatar=send_avatar,
                receive_id="system",  # AI系统
                file_type=file_type,
                file_name=file_name,
                file_size=file_size,
                status=1,  # 1.已发送
                send_at=datetime.now()
            )
            await message.insert()
            
            logger.info(f"用户消息已保存: {message.uuid}, session: {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"保存用户消息失败: {e}", exc_info=True)
            raise
    
    async def _get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话的所有历史消息（用于 AI 处理）
        
        Returns:
            List[Dict]: 格式化的历史消息列表 [{"role": "user/assistant", "content": "..."}]
        """
        try:
            # 查询所有消息，按时间升序
            messages = await MessageModel.find(
                MessageModel.session_id == session_id
            ).sort(MessageModel.created_at).to_list()
            
            # 转换为 ChatService 需要的格式
            history = []
            for msg in messages:
                role = "user" if msg.send_type == 0 else "assistant"
                history.append({
                    "role": role,
                    "content": msg.content
                })
            
            logger.info(f"获取会话历史: session={session_id}, 共 {len(history)} 条消息")
            return history
            
        except Exception as e:
            logger.error(f"获取会话历史失败: {e}", exc_info=True)
            return []
    
    async def _generate_ai_reply(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        history: List[Dict[str, Any]],
        stream: bool = False
    ) -> str:
        """
        生成 AI 回复（使用 ChatService + Agent + RAG）
        参考 test_full_rag_qa.py 的实现
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            history: 历史记录
            stream: 是否流式返回
            
        Returns:
            str: AI 回复内容（非流式）或空字符串（流式，内容通过 yield 返回）
        """
        try:
            logger.info(f"开始生成 AI 回复（Agent + RAG）: session={session_id}, stream={stream}")
            
            # 初始化 ChatService（与 test_full_rag_qa.py 完全一致）
            chat_service = ChatService(
                session_id=session_id,
                user_id=user_id,
                model_name=DEEPSEEK_CHAT.name,
                model_type=DEEPSEEK_CHAT.model_type,
                system_prompt=AGENT_RAG_PROMPT,  # 使用 Agent RAG 提示词
                tools=[knowledge_search],  # 传递 RAG 工具
                auto_summary=True,  # 启用自动总结
                max_history_count=10  # 保持最近10条历史
            )
            
            # 🔥 加载历史记录时添加上下文分隔（排除最后一条，因为是当前用户消息）
            if len(history) > 1:
                # 添加历史对话标记
                chat_service.add_to_history("system", "--- 以下是历史对话记录---")
                for msg in history[:-1]:
                    chat_service.add_to_history(msg['role'], msg['content'])
                # 添加当前问题标记
                chat_service.add_to_history("system", "--- 以上是历史对话，以下是用户当前的新问题 ---")
                logger.info(f"已加载 {len(history)-1} 条历史记录")
            
            # 准备 Agent 工具
            agent_tools = {
                "knowledge_search": knowledge_search
            }
            
            # 调用 AI 生成回复（与 test_full_rag_qa.py 一致）
            logger.info(f"调用 ChatService.chat() 生成回复...")
            ai_reply = chat_service.chat(
                user_message=user_message,
                use_agent=True,  # 启用 Agent
                agent_tools=agent_tools,  # 传递工具
                save_only_answer=True,  # 只保存问答，不保存思考过程
                max_iterations=5,  # 最大迭代次数
                verbose=True,  # 显示推理过程
                stream=stream  # 流式或非流式
            )
            
            logger.info(f"AI 回复生成成功: {len(ai_reply) if isinstance(ai_reply, str) else 'streaming'}")
            return ai_reply
            
        except Exception as e:
            logger.error(f"生成 AI 回复失败: {e}", exc_info=True)
            return "抱歉，我现在无法回答您的问题，请稍后再试。"
    
    async def _generate_ai_reply_stream(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        history: List[Dict[str, Any]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """生成 AI 回复（真正的流式）- 使用回调机制"""
        import asyncio
        import queue
        
        try:
            from internal.chat_service.chat_service import ChatService
            from internal.agent.react_agent import ReActAgent
            
            chat_service = ChatService(
                session_id=session_id,
                user_id=user_id,
                model_name=DEEPSEEK_CHAT.name,
                model_type=DEEPSEEK_CHAT.model_type,
                system_prompt=AGENT_RAG_PROMPT,
                tools=[knowledge_search],
                auto_summary=True,
                max_history_count=10
            )
            
            # 🔥 加载历史记录时添加上下文分隔
            if len(history) > 1:
                # 添加历史对话标记
                chat_service.add_to_history("system", "--- 以下是历史对话记录---")
                for msg in history[:-1]:
                    chat_service.add_to_history(msg['role'], msg['content'])
                # 添加当前问题标记
                chat_service.add_to_history("system", "--- 以上是历史对话，以下是用户当前的新问题 ---")
            
            # 创建事件队列
            event_queue = queue.Queue()
            
            # 定义回调函数
            def callback(event_type, content):
                event_queue.put((event_type, content))
            
            # 创建 Agent 并传入回调
            agent = ReActAgent(
                llm_service=chat_service.llm_service,
                tools={"knowledge_search": knowledge_search},
                max_iterations=5,
                verbose=False,
                callback=callback
            )
            
            # 在后台线程运行 Agent
            async def run_agent():
                return await asyncio.to_thread(lambda: agent.run(user_message, stream=True))
            
            # 启动 Agent 任务
            agent_task = asyncio.create_task(run_agent())
            
            # 实时读取队列并yield事件
            current_line = ""
            in_answer = False
            
            while not agent_task.done() or not event_queue.empty():
                try:
                    event_type, content = event_queue.get_nowait()
                    
                    if event_type == "llm_chunk":
                        current_line += content
                        
                        # 检测事件类型
                        if '\n' in current_line:
                            lines = current_line.split('\n')
                            for line in lines[:-1]:
                                line = line.strip()
                                if line.startswith('Thought:'):
                                    yield {
                                        "event": "thought",
                                        "data": {"content": line.replace('Thought:', '').strip()}
                                    }
                                elif line.startswith('Action:'):
                                    yield {
                                        "event": "action",
                                        "data": {"content": line.replace('Action:', '').strip()}
                                    }
                                elif line.startswith('Answer:'):
                                    in_answer = True
                                    answer_start = line.replace('Answer:', '').strip()
                                    if answer_start:
                                        yield {
                                            "event": "answer_chunk",
                                            "data": {"content": answer_start}
                                        }
                            current_line = lines[-1]
                        
                        # 🔥 实时检测 Answer: 开头（即使没有换行符）
                        if not in_answer and 'Answer:' in current_line:
                            in_answer = True
                            # 提取 Answer: 后面的内容
                            answer_part = current_line.split('Answer:', 1)[1]
                            if answer_part.strip():
                                yield {
                                    "event": "answer_chunk",
                                    "data": {"content": answer_part}
                                }
                            current_line = ""  # 清空已处理的内容
                        # 如果在 Answer 部分，实时输出
                        elif in_answer and content not in ['\n', '\r\n']:
                            yield {
                                "event": "answer_chunk",
                                "data": {"content": content}
                            }
                
                except queue.Empty:
                    await asyncio.sleep(0.01)  # 等待新事件
            
            # 🔥 循环结束后，检查是否有遗留的 Answer 内容
            if current_line.strip() and not in_answer:
                if 'Answer:' in current_line:
                    answer_part = current_line.split('Answer:', 1)[1].strip()
                    if answer_part:
                        yield {
                            "event": "answer_chunk",
                            "data": {"content": answer_part}
                        }
            
            # 等待 Agent 完成
            result = await agent_task
            logger.info(f"Agent 完成: {len(result)} 字符")
            
        except Exception as e:
            logger.error(f"生成 AI 回复失败: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {"content": str(e)}
            }
    
    async def _save_ai_message(
        self,
        session_id: str,
        content: str,
        receive_id: str
    ) -> MessageModel:
        """
        保存 AI 消息到数据库
        
        Returns:
            MessageModel: 保存的消息对象
        """
        try:
            message = MessageModel(
                uuid=str(uuid_module.uuid4()),
                session_id=session_id,
                content=content,
                send_type=1,  # 1.AI
                send_id="system",
                send_name="AI助手",
                send_avatar="",
                receive_id=receive_id,
                status=1,  # 1.已发送
                send_at=datetime.now()
            )
            await message.insert()
            
            logger.info(f"AI 消息已保存: {message.uuid}, session: {session_id}")
            
            # 同时保存到 Redis（缓存最后一条 AI 消息）
            try:
                key = f"session:{session_id}:last_ai_message"
                redis_client.set(key, content, ex=3600)  # 1小时过期
                logger.info(f"AI 消息已缓存到 Redis: {key}")
            except Exception as e:
                logger.warning(f"缓存 AI 消息到 Redis 失败: {e}")
            
            return message
            
        except Exception as e:
            logger.error(f"保存 AI 消息失败: {e}", exc_info=True)
            raise
    
    async def _update_session_last_message(self, session_id: str, message: str):
        """
        更新会话的最后一条消息
        """
        try:
            session = await SessionModel.find_one(SessionModel.uuid == session_id)
            if session:
                session.last_message = message
                session.update_at = datetime.now()
                await session.save()
                logger.info(f"会话最后消息已更新: {session_id}")
            else:
                logger.warning(f"会话不存在，无法更新: {session_id}")
                
        except Exception as e:
            logger.error(f"更新会话最后消息失败: {e}", exc_info=True)
    
    # ==================== 公共接口 ====================
    
    async def send_message_stream(
        self,
        content: str,
        user_id: str,
        send_name: str,
        send_avatar: str,
        session_id: Optional[str] = None,
        file_type: Optional[str] = None,
        file_name: Optional[str] = None,
        file_size: Optional[str] = None,
        show_thinking: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        发送消息（统一流式返回）
        
        Args:
            show_thinking: 是否显示思考过程（Thought/Action/Observation）
        
        Yields:
            Dict: 包含事件类型和数据的字典
                - event: 事件类型
                - data: 事件数据
        
        事件类型：
            - session_created: 会话创建
            - user_message_saved: 用户消息保存完成
            - thought: Agent 思考（仅当 show_thinking=True）
            - action: Agent 动作（仅当 show_thinking=True）
            - observation: 观察结果（仅当 show_thinking=True）
            - answer_chunk: 最终答案片段
            - ai_message_saved: AI 消息保存完成
            - done: 完成
            - error: 错误
        """
        try:
            logger.info(f"收到消息发送请求（流式）: user={user_id}, session={session_id}")
            
            # 1. 创建或获取会话
            session_id, session_name = await self._create_or_get_session(
                session_id, user_id, content
            )
            
            yield {
                "event": "session_created",
                "data": {
                    "session_id": session_id,
                    "session_name": session_name
                }
            }
            
            # 2. 保存用户消息
            user_msg = await self._save_user_message(
                session_id, content, user_id, send_name, send_avatar,
                file_type, file_name, file_size
            )
            
            yield {
                "event": "user_message_saved",
                "data": {
                    "uuid": user_msg.uuid,
                    "content": user_msg.content
                }
            }
            
            # 3. 获取会话历史
            history = await self._get_session_history(session_id)
            
            # 4. 流式生成 AI 回复
            ai_reply_full = ""
            async for event_dict in self._generate_ai_reply_stream(session_id, user_id, content, history):
                event_type = event_dict.get("event", "message")
                event_data = event_dict.get("data", {})
                event_content = event_data.get("content", "")
                
                # 根据 show_thinking 参数决定是否输出思考过程
                if event_type == "thought":
                    if show_thinking:  # 只有启用时才输出
                        yield event_dict
                elif event_type == "action":
                    if show_thinking:  # 只有启用时才输出
                        yield event_dict
                elif event_type == "observation":
                    if show_thinking:  # 只有启用时才输出
                        yield event_dict
                elif event_type == "answer_chunk":
                    ai_reply_full += event_content
                    yield event_dict
                elif event_type == "debug":
                    if show_thinking:  # 只有启用时才输出
                        yield event_dict
                elif event_type == "error":
                    yield event_dict
            
            # 5. 保存 AI 消息
            if ai_reply_full:
                ai_msg = await self._save_ai_message(session_id, ai_reply_full, user_id)
                
                yield {
                    "event": "ai_message_saved",
                    "data": {
                        "uuid": ai_msg.uuid,
                        "content": ai_msg.content
                    }
                }
                
                # 6. 更新会话最后消息
                await self._update_session_last_message(session_id, ai_reply_full)
            
            yield {
                "event": "done",
                "data": {
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"发送消息失败（流式）: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {
                    "message": f"发送失败: {str(e)}"
                }
            }
    
    async def get_session_messages(
        self,
        session_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[str, int, Optional[Dict[str, Any]]]:
        """
        获取会话的所有消息
        
        Args:
            session_id: 会话ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            (message, ret, data)
        """
        try:
            logger.info(f"获取会话消息: session={session_id}, page={page}, page_size={page_size}")
            
            # 查询消息
            query = MessageModel.find(MessageModel.session_id == session_id)
            
            # 排序：按创建时间升序
            query = query.sort(MessageModel.created_at)
            
            # 分页
            skip = (page - 1) * page_size
            messages = await query.skip(skip).limit(page_size).to_list()
            
            # 总数
            total = await MessageModel.find(MessageModel.session_id == session_id).count()
            
            # 转换为字典格式
            messages_data = []
            for msg in messages:
                messages_data.append({
                    "uuid": msg.uuid,
                    "session_id": msg.session_id,
                    "content": msg.content,
                    "send_type": msg.send_type,
                    "send_id": msg.send_id,
                    "send_name": msg.send_name,
                    "send_avatar": msg.send_avatar,
                    "receive_id": msg.receive_id,
                    "file_type": msg.file_type,
                    "file_name": msg.file_name,
                    "file_size": msg.file_size,
                    "status": msg.status,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "send_at": msg.send_at.isoformat() if msg.send_at else None
                })
            
            data = {
                "total": total,
                "messages": messages_data
            }
            
            logger.info(f"获取会话消息成功: session={session_id}, 共 {total} 条消息")
            return "获取成功", 0, data
            
        except Exception as e:
            logger.error(f"获取会话消息失败: {e}", exc_info=True)
            return f"获取失败: {str(e)}", -1, None


# 创建单例实例
message_service = MessageService()
