"""
LLM 服务层
精简版 - 只保留核心 chat 功能
支持提示词和工具配对
支持异步对话历史总结
"""
from typing import Optional, List, Dict, Any, Callable
import asyncio
from pkg.model_list import ModelManager, LLAMA_3_2  # 默认模型配置
from pkg.agent_prompt.prompt_templates import get_prompt, SUMMARY_PROMPT
from pkg.agent_tools import (
    get_tools_info,
    get_prompt_for_tools
)
from pkg.constants.constants import MAX_TOKEN


class LLMService:
    """LLM 服务类 - 精简版"""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        auto_summary: bool = True,
        max_history_count: int = 10,
        max_history_tokens: int = MAX_TOKEN
    ):
        """
        初始化 LLM 服务
        
        Args:
            model_name: 模型名称，如果为 None 则使用 LLAMA_3_2
            model_type: 模型类型 (local/cloud)，如果为 None 则使用默认模型的类型
            system_prompt: 自定义系统提示词（可选）
            tools: 使用的工具函数列表（可选），可以直接点击跳转
                   例如: [knowledge_search, document_analyzer]
            auto_summary: 是否自动总结历史记录
            max_history_count: 历史记录最大条数（默认10条）
            max_history_tokens: 历史记录最大token数（默认从配置读取）
        """
        # 如果没有指定模型，使用默认配置
        if model_name is None:
            model_name = LLAMA_3_2.name
            model_type = LLAMA_3_2.model_type
        elif model_type is None:
            # 如果只指定了 model_name，从配置中获取 model_type
            from pkg.model_list import get_llm_model
            config = get_llm_model(model_name)
            model_type = config.model_type
        
        self.model_name = model_name
        self.model_type = model_type
        
        # 工具配置
        self.tools = tools or []
        
        # 设置系统提示词
        if system_prompt:
            self.system_prompt = system_prompt
        elif self.tools:
            # 如果有工具但没有自定义提示词，根据工具自动选择
            prompt_template = get_prompt_for_tools(self.tools)
            self.system_prompt = get_prompt(prompt_template)
        else:
            self.system_prompt = get_prompt("default")
        
        # 历史记录管理
        self.chat_history: List[Dict[str, str]] = []
        self.auto_summary = auto_summary
        self.max_history_count = max_history_count
        self.max_history_tokens = max_history_tokens
        self._is_summarizing = False  # 总结状态标志
        self._need_summary = False  # 是否需要在下次对话前总结
        
        # 初始化模型
        self.llm = None
        self._initialize()
    
    def _initialize(self):
        """初始化模型"""
        try:
            self.llm = ModelManager.select_llm_model(self.model_name, self.model_type)
            print(f"✓ 模型已加载: {self.model_name} (type: {self.model_type})")
            if self.tools:
                tool_names = [t.__name__ for t in self.tools]
                print(f"✓ 已启用工具: {tool_names}")
        except Exception as e:
            print(f"✗ 模型初始化失败: {e}")
            raise
    
    def chat(
        self,
        user_message: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        stream: bool = True,
        use_history: bool = True,
        **kwargs
    ):
        """
        对话方法
        
        🔥 优化：自动使用内部历史记录，无需手动获取
        
        Args:
            user_message: 用户消息（简化用法）
            messages: 消息列表（高级用法，传入则忽略 user_message）
                     - 如果不包含历史，会自动添加
            context: 额外的上下文信息（如知识库检索结果）
            stream: 是否流式返回
            use_history: 是否自动使用内部历史记录（默认 True）
            **kwargs: 其他参数
        
        Yields (stream=True):
            回复片段
            
        Returns (stream=False):
            完整回复
            
        示例:
            # 简化用法（推荐）
            llm.chat("你好")
            
            # 高级用法（完全控制）
            llm.chat(messages=[{"role": "user", "content": "你好"}], use_history=False)
        
        Note:
            工具调用由 Agent 层处理，不在此方法中控制
        """
        # 🔥 关键优化：在 AI 回答前，如果需要总结，先执行总结
        if self._need_summary and not self._is_summarizing:
            print("\n⚡ 检测到需要总结历史记录，正在总结...")
            self.summarize_history()
            self._need_summary = False
        
        # 构建完整的消息列表
        full_messages = []
        
        # 添加系统提示词
        if self.system_prompt:
            full_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # 添加上下文（如知识库内容）
        if context:
            full_messages.append({
                "role": "system",
                "content": f"参考信息：\n{context}"
            })
        
        # 🔥 自动添加历史记录
        if use_history and self.chat_history:
            full_messages.extend(self.chat_history)
        
        # 添加用户消息
        if user_message and messages:
            # ❌ 不允许同时提供两个参数，避免混淆
            raise ValueError("不能同时提供 user_message 和 messages 参数，请选择其一")
        elif user_message:
            # 简化用法：直接传入字符串
            full_messages.append({
                "role": "user",
                "content": user_message
            })
        elif messages:
            # 高级用法：传入完整消息列表
            full_messages.extend(messages)
        else:
            raise ValueError("必须提供 user_message 或 messages 参数")
        
        # 格式化为 prompt
        prompt = self._format_messages(full_messages)
        
        # 生成回复
        if stream:
            return self._stream_generate(prompt, **kwargs)
        else:
            return self._generate(prompt, **kwargs)
    
    def _normalize_chunk(self, chunk) -> str:
        """
        标准化不同模型返回的 chunk 格式
        
        Args:
            chunk: 原始 chunk（可能是 str 或 AIMessageChunk）
            
        Returns:
            标准化后的字符串
        """
        # Ollama 返回字符串，ChatOpenAI 返回 AIMessageChunk
        if isinstance(chunk, str):
            return chunk
        else:
            # AIMessageChunk 对象，提取 content
            return chunk.content if hasattr(chunk, 'content') else str(chunk)
    
    def _stream_generate(self, prompt: str, **kwargs):
        """流式生成"""
        try:
            for chunk in self.llm.stream(prompt):
                yield self._normalize_chunk(chunk)
        except Exception as e:
            raise Exception(f"生成失败: {e}")
    
    def _generate(self, prompt: str, **kwargs) -> str:
        """非流式生成"""
        try:
            chunks = [self._normalize_chunk(chunk) for chunk in self.llm.stream(prompt)]
            return "".join(chunks)
        except Exception as e:
            raise Exception(f"生成失败: {e}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """格式化消息为 prompt"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        formatted.append("Assistant:")
        return "\n\n".join(formatted)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        简单估算：中文1字约1.5token，英文1词约1token
        
        Args:
            text: 文本内容
            
        Returns:
            估算的 token 数
        """
        # 简单估算方法
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + other_chars / 4)
    
    def _calculate_history_tokens(self) -> int:
        """计算历史记录的总 token 数"""
        total_tokens = 0
        for msg in self.chat_history:
            content = msg.get("content", "")
            total_tokens += self._estimate_tokens(content)
        return total_tokens
    
    def _should_summarize(self) -> bool:
        """
        判断是否需要总结历史记录
        
        Returns:
            是否需要总结
        """
        # 如果正在总结中，不再触发
        if self._is_summarizing:
            return False
        
        # 检查条数
        if len(self.chat_history) >= self.max_history_count:
            return True
        
        # 检查 token 数
        total_tokens = self._calculate_history_tokens()
        if total_tokens >= self.max_history_tokens:
            return True
        
        return False
    
    def _do_summarize(self) -> str:
        """
        执行总结的核心逻辑（提取公共代码）
        
        Returns:
            总结内容
        """
        # 构建总结 prompt
        history_text = "\n\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.chat_history
        ])
        
        summary_messages = [
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": f"请总结以下对话：\n\n{history_text}"}
        ]
        
        # 格式化并生成总结（使用 _normalize_chunk 统一处理）
        prompt = self._format_messages(summary_messages)
        summary_chunks = [
            self._normalize_chunk(chunk) 
            for chunk in self.llm.stream(prompt)
        ]
        
        return "".join(summary_chunks)
    
    async def _summarize_history_async(self):
        """
        异步总结历史记录
        在后台运行，不阻塞当前对话
        """
        if not self.chat_history or self._is_summarizing:
            return
        
        self._is_summarizing = True
        
        try:
            old_count = len(self.chat_history)
            summary = self._do_summarize()
            
            # 替换历史记录为总结
            self.chat_history = [
                {
                    "role": "assistant",
                    "content": f"[历史对话总结] {summary}"
                }
            ]
            
            print(f"\n✓ 历史记录已总结（原 {old_count} 条 -> 1 条）")
            
        except Exception as e:
            print(f"✗ 总结历史记录失败: {e}")
        finally:
            self._is_summarizing = False
    
    def summarize_history(self):
        """
        同步方式总结历史记录
        适用于同步上下文（非异步环境）
        """
        if not self.chat_history or self._is_summarizing:
            return
        
        self._is_summarizing = True
        
        try:
            old_count = len(self.chat_history)
            summary = self._do_summarize()
            
            # 替换历史记录为总结
            self.chat_history = [
                {
                    "role": "assistant",
                    "content": f"[历史对话总结] {summary}"
                }
            ]
            
            print(f"\n✓ 历史记录已总结（原 {old_count} 条 -> 1 条）")
            
        except Exception as e:
            print(f"✗ 总结历史记录失败: {e}")
        finally:
            self._is_summarizing = False
    
    def add_to_history(self, role: str, content: str):
        """
        添加消息到历史记录
        
        🔥 优化：只检查是否需要总结，不立即执行
        总结会在下次 chat() 调用时（AI回答前）自动执行
        
        Args:
            role: 角色 (user/assistant/system)
            content: 内容
        """
        self.chat_history.append({
            "role": role,
            "content": content
        })
        
        # 检查是否需要总结（只标记，不执行）
        # 只在首次超限时打印提示，避免重复
        if self.auto_summary and self._should_summarize() and not self._need_summary:
            self._need_summary = True
            print(f"📌 历史记录已达到限制（{len(self.chat_history)}条），将在下次对话前自动总结")
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取当前历史记录"""
        return self.chat_history.copy()
    
    def clear_history(self):
        """清空历史记录"""
        self.chat_history = []
        print("✓ 历史记录已清空")
    
    def get_history_stats(self) -> Dict[str, Any]:
        """获取历史记录统计信息"""
        return {
            "count": len(self.chat_history),
            "total_tokens": self._calculate_history_tokens(),
            "max_count": self.max_history_count,
            "max_tokens": self.max_history_tokens,
            "is_summarizing": self._is_summarizing
        }
    
    def get_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        tool_info = get_tools_info(self.tools) if self.tools else []
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "system_prompt": self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt,
            "tools": [t["name"] for t in tool_info],
            "tool_count": len(self.tools),
            "auto_summary": self.auto_summary,
            "history_count": len(self.chat_history)
        }
