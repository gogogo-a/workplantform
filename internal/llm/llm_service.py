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
from pkg.agent_prompt.agent_tool import (
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
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        use_tools: bool = True,
        stream: bool = True,
        **kwargs
    ):
        """
        对话方法
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            context: 额外的上下文信息（如知识库检索结果）
            use_tools: 是否使用工具
            stream: 是否流式返回
            **kwargs: 其他参数
        
        Yields (stream=True):
            回复片段
            
        Returns (stream=False):
            完整回复
        """
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
        
        # 添加用户消息
        full_messages.extend(messages)
        
        # 格式化为 prompt
        prompt = self._format_messages(full_messages)
        
        # 生成回复
        if stream:
            return self._stream_generate(prompt, **kwargs)
        else:
            return self._generate(prompt, **kwargs)
    
    def _stream_generate(self, prompt: str, **kwargs):
        """流式生成"""
        try:
            for chunk in self.llm.stream(prompt):
                # 处理不同模型返回的不同类型
                # Ollama 返回字符串，ChatOpenAI 返回 AIMessageChunk
                if isinstance(chunk, str):
                    yield chunk
                else:
                    # AIMessageChunk 对象，提取 content
                    yield chunk.content if hasattr(chunk, 'content') else str(chunk)
        except Exception as e:
            raise Exception(f"生成失败: {e}")
    
    def _generate(self, prompt: str, **kwargs) -> str:
        """非流式生成"""
        try:
            chunks = []
            for chunk in self.llm.stream(prompt):
                # 处理不同模型返回的不同类型
                if isinstance(chunk, str):
                    chunks.append(chunk)
                else:
                    # AIMessageChunk 对象，提取 content
                    chunks.append(chunk.content if hasattr(chunk, 'content') else str(chunk))
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
    
    async def _summarize_history_async(self):
        """
        异步总结历史记录
        在后台运行，不阻塞当前对话
        """
        if not self.chat_history or self._is_summarizing:
            return
        
        self._is_summarizing = True
        
        try:
            # 构建总结 prompt
            history_text = "\n\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in self.chat_history
            ])
            
            summary_messages = [
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": f"请总结以下对话：\n\n{history_text}"}
            ]
            
            # 格式化并生成总结
            prompt = self._format_messages(summary_messages)
            summary_chunks = []
            
            for chunk in self.llm.stream(prompt):
                # 处理不同模型返回的不同类型
                if isinstance(chunk, str):
                    summary_chunks.append(chunk)
                else:
                    # AIMessageChunk 对象，提取 content
                    summary_chunks.append(chunk.content if hasattr(chunk, 'content') else str(chunk))
            
            summary = "".join(summary_chunks)
            
            # 替换历史记录为总结
            self.chat_history = [
                {
                    "role": "assistant",
                    "content": f"[历史对话总结] {summary}"
                }
            ]
            
            print(f"\n✓ 历史记录已总结（原 {len(summary_chunks)} 条 -> 1 条）")
            
        except Exception as e:
            print(f"✗ 总结历史记录失败: {e}")
        finally:
            self._is_summarizing = False
    
    def add_to_history(self, role: str, content: str):
        """
        添加消息到历史记录
        
        Args:
            role: 角色 (user/assistant/system)
            content: 内容
        """
        self.chat_history.append({
            "role": role,
            "content": content
        })
        
        # 检查是否需要总结（异步执行）
        if self.auto_summary and self._should_summarize():
            # 创建异步任务，不等待完成
            asyncio.create_task(self._summarize_history_async())
    
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
