"""
聊天服务（上层封装）
负责：
1. Session 和 User 管理
2. Redis 历史记录持久化
3. 调用底层 LLMService
4. 封装 Agent 交互（统一入口）
"""
from typing import Optional, List, Dict, Any, Callable
import json
from internal.llm.llm_service import LLMService
from internal.db.redis import redis_client
from pkg.constants.constants import MAX_TOKEN


class ChatService:
    """
    聊天服务 - 上层封装
    管理会话、用户、历史记录持久化
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        auto_summary: bool = True,
        max_history_count: int = 10,
        max_history_tokens: int = MAX_TOKEN,
        redis_expire_seconds: int = 3600,
        use_redis: bool = True
    ):
        """
        初始化聊天服务
        
        Args:
            session_id: 会话ID（必填）
            user_id: 用户ID（必填）
            model_name: 模型名称
            model_type: 模型类型 (local/cloud)
            system_prompt: 系统提示词
            tools: 工具列表
            auto_summary: 是否自动总结
            max_history_count: 最大历史记录条数
            max_history_tokens: 最大历史记录token数
            redis_expire_seconds: Redis 过期时间（秒，默认1小时）
            use_redis: 是否使用 Redis 持久化
        """
        self.session_id = session_id
        self.user_id = user_id
        self.use_redis = use_redis
        self.redis_expire_seconds = redis_expire_seconds
        self._redis_key = self._get_redis_key()
        
        # 初始化底层 LLM 服务（纯粹的 LLM 调用）
        self.llm_service = LLMService(
            model_name=model_name,
            model_type=model_type,
            system_prompt=system_prompt,
            tools=tools,
            auto_summary=auto_summary,
            max_history_count=max_history_count,
            max_history_tokens=max_history_tokens
        )
        
        # 如果启用 Redis，初始化并加载历史记录
        if self.use_redis:
            self._init_redis()
        
        print(f"✓ ChatService 已初始化")
        print(f"  Session: {self.session_id}")
        print(f"  User: {self.user_id}")
        print(f"  Redis: {'启用' if self.use_redis else '禁用'}")
    
    def _get_redis_key(self) -> str:
        """
        生成 Redis 键
        格式：user_history:{user_id}:{session_id}
        
        按照 redis_key 文件的规范
        """
        return f"user_history:{self.user_id}:{self.session_id}"
    
    def _init_redis(self):
        """初始化 Redis 并加载历史记录"""
        try:
            # 连接 Redis（如果还没连接）
            if not redis_client.client or not redis_client.ping():
                redis_client.connect()
            
            # 从 Redis 加载历史记录
            self._load_history_from_redis()
            
            print(f"  Redis 键: {self._redis_key}")
            print(f"  过期时间: {self.redis_expire_seconds}秒")
            print(f"  已加载历史: {len(self.llm_service.chat_history)}条")
            
        except Exception as e:
            print(f"⚠️  Redis 初始化失败: {e}")
            print(f"  将继续使用内存模式（不持久化）")
            self.use_redis = False
    
    def _save_history_to_redis(self):
        """保存历史记录到 Redis"""
        if not self.use_redis:
            return
        
        try:
            history = self.llm_service.get_history()
            
            # 构建存储数据（包含元信息）
            data = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "history": history,
                "count": len(history)
            }
            
            # 保存到 Redis（自动序列化为 JSON）
            redis_client.set(
                self._redis_key,
                data,
                ex=self.redis_expire_seconds
            )
            
        except Exception as e:
            print(f"⚠️  保存到 Redis 失败: {e}")
    
    def _load_history_from_redis(self):
        """从 Redis 加载历史记录"""
        if not self.use_redis:
            return
        
        try:
            # 从 Redis 获取数据
            data = redis_client.get(self._redis_key)
            
            if data:
                # redis_client 会自动解析 JSON
                if isinstance(data, dict):
                    history = data.get("history", [])
                    # 恢复历史记录到 LLMService
                    self.llm_service.chat_history = history
                elif isinstance(data, list):
                    # 兼容旧格式（直接是列表）
                    self.llm_service.chat_history = data
            
        except Exception as e:
            print(f"⚠️  从 Redis 加载失败: {e}")
            self.llm_service.chat_history = []
    
    def chat(
        self,
        user_message: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        stream: bool = True,
        auto_add_to_history: bool = True,
        **kwargs
    ):
        """
        对话（自动管理历史记录和持久化）
        
        🔥 优化：完全自动化的对话流程
        1. 自动使用内部历史记录
        2. 自动添加用户消息和 AI 回复到历史
        3. 自动同步到 Redis
        4. 自动处理总结
        
        Args:
            user_message: 用户消息（简化用法，推荐）
            messages: 消息列表（高级用法，用于完全控制）
            context: 额外上下文
            stream: 是否流式返回
            auto_add_to_history: 是否自动添加到历史记录（默认 True）
            **kwargs: 其他参数
            
        Yields/Returns:
            LLM 回复
            
        示例:
            # ✅ 简化用法（推荐）
            for chunk in chat_service.chat("你好"):
                print(chunk, end="")
            
            # ✅ 高级用法（完全控制，不自动添加历史）
            response = chat_service.chat(
                messages=[{"role": "user", "content": "你好"}],
                auto_add_to_history=False
            )
        
        Note:
            工具调用由 Agent 层处理，不在此方法中控制
        """
        # 提取用户消息（用于历史记录）
        extracted_user_message = None
        if user_message:
            extracted_user_message = user_message
        elif messages and auto_add_to_history:
            # 从 messages 中提取最后一条用户消息
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    extracted_user_message = msg.get("content")
                    break
        
        # 🔥 关键优化：只传递其中一个参数给底层 LLM
        # 避免参数冲突
        if user_message:
            # 简化用法：只传 user_message
            result_generator = self.llm_service.chat(
                user_message=user_message,
                context=context,
                stream=stream,
                use_history=True,  # 🔥 自动使用内部历史
                **kwargs
            )
        else:
            # 高级用法：传 messages（不传 user_message）
            result_generator = self.llm_service.chat(
                messages=messages,
                context=context,
                stream=stream,
                use_history=True,  # 🔥 自动使用内部历史
                **kwargs
            )
        
        # 如果需要自动添加到历史
        if auto_add_to_history and extracted_user_message:
            # 先添加用户消息
            self.add_to_history("user", extracted_user_message)
            
            if stream:
                # 流式返回：需要收集完整回复后再添加
                def response_generator():
                    full_response = ""
                    try:
                        for chunk in result_generator:
                            full_response += chunk
                            yield chunk
                    finally:
                        # 添加 AI 回复到历史（即使出错也会执行）
                        if full_response:
                            self.add_to_history("assistant", full_response)
                
                return response_generator()
            else:
                # 非流式：直接添加完整回复
                response = result_generator
                self.add_to_history("assistant", response)
                return response
        else:
            # 不自动添加历史，直接返回
            return result_generator
    
    def add_to_history(self, role: str, content: str):
        """
        添加消息到历史记录（并持久化到 Redis）
        
        🔥 优化：只会标记是否需要总结，不会立即执行
        真正的总结发生在下次 chat() 调用时
        
        Args:
            role: 角色 (user/assistant/system)
            content: 内容
        """
        # 添加到底层 LLMService（可能会标记需要总结）
        self.llm_service.add_to_history(role, content)
        
        # 持久化到 Redis
        self._save_history_to_redis()
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取历史记录"""
        return self.llm_service.get_history()
    
    def clear_history(self):
        """清空历史记录（包括 Redis）"""
        # 清空底层服务的历史
        self.llm_service.clear_history()
        
        # 删除 Redis 中的记录
        if self.use_redis:
            try:
                redis_client.delete(self._redis_key)
                print("✓ 历史记录已清空（包括 Redis）")
            except Exception as e:
                print(f"✓ 历史记录已清空（Redis 清除失败: {e}）")
    
    def reload_history(self):
        """从 Redis 重新加载历史记录"""
        if self.use_redis:
            self._load_history_from_redis()
            print(f"✓ 已从 Redis 重新加载历史记录: {len(self.llm_service.chat_history)}条")
        else:
            print("⚠️  Redis 未启用，无法重新加载")
    
    def get_history_stats(self) -> Dict[str, Any]:
        """获取历史记录统计信息"""
        stats = self.llm_service.get_history_stats()
        
        # 添加会话信息
        stats["session_id"] = self.session_id
        stats["user_id"] = self.user_id
        stats["redis_enabled"] = self.use_redis
        
        if self.use_redis:
            stats["redis_key"] = self._redis_key
            stats["redis_expire_seconds"] = self.redis_expire_seconds
            
            # 检查 Redis 中是否存在
            try:
                exists = redis_client.exists(self._redis_key)
                stats["redis_exists"] = bool(exists)
                
                if exists:
                    ttl = redis_client.ttl(self._redis_key)
                    stats["redis_ttl"] = ttl
            except:
                stats["redis_exists"] = False
        
        return stats
    
    def get_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        info = self.llm_service.get_info()
        
        # 添加 ChatService 层的信息
        info["chat_service"] = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "redis_enabled": self.use_redis,
            "redis_key": self._redis_key if self.use_redis else None,
            "redis_expire_seconds": self.redis_expire_seconds if self.use_redis else None
        }
        
        return info
    
    def update_redis_expire(self, seconds: int):
        """
        更新 Redis 过期时间
        
        Args:
            seconds: 新的过期时间（秒）
        """
        if not self.use_redis:
            print("⚠️  Redis 未启用")
            return
        
        try:
            self.redis_expire_seconds = seconds
            
            # 如果键存在，更新过期时间
            if redis_client.exists(self._redis_key):
                redis_client.expire(self._redis_key, seconds)
                print(f"✓ Redis 过期时间已更新: {seconds}秒")
            else:
                print("⚠️  Redis 键不存在，将在下次保存时生效")
                
        except Exception as e:
            print(f"✗ 更新过期时间失败: {e}")
    
    def get_redis_info(self) -> Dict[str, Any]:
        """获取 Redis 相关信息"""
        if not self.use_redis:
            return {"enabled": False}
        
        info = {
            "enabled": True,
            "key": self._redis_key,
            "expire_seconds": self.redis_expire_seconds,
            "exists": False,
            "ttl": -2
        }
        
        try:
            exists = redis_client.exists(self._redis_key)
            info["exists"] = bool(exists)
            
            if exists:
                ttl = redis_client.ttl(self._redis_key)
                info["ttl"] = ttl
                
                # 获取数据大小（估算）
                data = redis_client.get(self._redis_key)
                if data:
                    info["data_size"] = len(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def chat_with_agent(
        self,
        question: str,
        agent_tools: Optional[Dict[str, Callable]] = None,
        save_only_answer: bool = True,
        max_iterations: int = 5,
        verbose: bool = True
    ) -> str:
        """
        使用 Agent 进行对话（ReAct 框架）
        
        🔥 优化：完全自动化的 Agent 对话流程
        1. 自动创建 Agent
        2. Agent 执行推理和工具调用
        3. 自动保存历史记录（只保存问答或完整过程）
        4. 自动同步到 Redis
        
        Args:
            question: 用户问题
            agent_tools: Agent 可用的工具字典 {tool_name: tool_function}
            save_only_answer: 是否只保存最终答案（默认 True，推荐）
                            True: 只保存 question 和 answer
                            False: 保存所有 Thought、Action、Observation
            max_iterations: Agent 最大推理轮数
            verbose: 是否打印详细的推理过程
            
        Returns:
            最终答案
            
        示例:
            # ✅ 简单用法（推荐）
            from pkg.agent_prompt.agent_tool import knowledge_search
            
            answer = chat_service.chat_with_agent(
                question="奖学金评定标准是什么？",
                agent_tools={"knowledge_search": knowledge_search}
            )
            
            # ✅ 保留完整思考过程（用于调试）
            answer = chat_service.chat_with_agent(
                question="奖学金评定标准是什么？",
                agent_tools={"knowledge_search": knowledge_search},
                save_only_answer=False  # 保留所有 Thought、Action、Observation
            )
        """
        if not agent_tools:
            raise ValueError("agent_tools 不能为空，请提供至少一个工具")
        
        # 导入 ReActAgent（延迟导入避免循环依赖）
        from internal.agent.react_agent import ReActAgent
        
        # 🔥 关键：记录历史长度，用于后续控制
        history_start_length = len(self.llm_service.chat_history)
        
        # 创建 Agent（Agent 不再处理历史记录，由 ChatService 统一管理）
        agent = ReActAgent(
            llm_service=self.llm_service,
            tools=agent_tools,
            max_iterations=max_iterations,
            verbose=verbose
        )
        
        # 运行 Agent（会自动调用 llm_service，产生中间历史）
        answer = agent.run(question, stream=verbose)
        
        # 🔥 ChatService 统一处理历史记录
        if save_only_answer:
            # ✅ 只保存问答（清除所有中间过程）
            self.llm_service.chat_history = self.llm_service.chat_history[:history_start_length]
            
            # 添加简洁的问答对
            self.add_to_history("user", question)
            self.add_to_history("assistant", answer)
            
            if verbose:
                cleaned_count = len(self.llm_service.chat_history) - history_start_length - 2
                print(f"\n💾 ChatService：只保存问答（清除了 {cleaned_count} 条中间过程）")
        else:
            # ❌ 保留所有思考过程
            # Agent 已经添加了所有中间历史到 llm_service
            # 我们需要额外保存问答到 ChatService 的 Redis
            self.add_to_history("user", question)
            self.add_to_history("assistant", answer)
            
            if verbose:
                total_count = len(self.llm_service.chat_history) - history_start_length
                print(f"\n💾 ChatService：保留完整思考过程（共 {total_count} 条）")
        
        # 自动同步到 Redis（add_to_history 已经调用了 _save_history_to_redis）
        # 无需额外操作
        
        return answer

