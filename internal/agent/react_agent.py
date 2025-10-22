"""
ReAct Agent 实现
基于 Reasoning + Acting 框架的智能代理
"""
import re
from typing import Dict, List, Callable, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ReActAgent:
    """ReAct 框架的 Agent 实现"""
    
    def __init__(
        self,
        llm_service,
        tools: Dict[str, Callable],
        max_iterations: int = 5,
        verbose: bool = True
    ):
        """
        初始化 ReAct Agent
        
        Args:
            llm_service: LLM 服务实例
            tools: 工具字典 {tool_name: tool_function}
            max_iterations: 最大迭代次数
            verbose: 是否打印详细信息
        """
        self.llm = llm_service
        self.tools = tools
        self.max_iterations = max_iterations
        self.verbose = verbose
    
    def _parse_action(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        解析 LLM 输出中的 Action
        
        Args:
            text: LLM 输出文本
            
        Returns:
            (action_name, action_input) 或 (None, None)
        """
        # 匹配 Action: tool_name("参数") 或 tool_name("参数", 数字)
        # 支持中英文引号
        action_pattern = r'Action:\s*(\w+)\s*\([""\'"]([^""\'"\)]+)[""\'"](?:\s*,\s*(\d+))?\)'
        match = re.search(action_pattern, text)
        
        if match:
            tool_name = match.group(1)
            query = match.group(2)
            top_k = int(match.group(3)) if match.group(3) else 5
            
            if self.verbose:
                print(f"[解析] 工具: {tool_name}, 查询: {query}, top_k: {top_k}")
            
            return tool_name, f"{query}|||{top_k}"  # 用|||分隔参数
        
        # 匹配 Action: None
        if re.search(r'Action:\s*None', text, re.IGNORECASE):
            return None, None
        
        return None, None
    
    def _extract_thought(self, text: str) -> str:
        """提取 Thought 内容"""
        match = re.search(r'Thought:\s*(.+?)(?=\n(?:Action|Answer|$))', text, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_answer(self, text: str) -> Optional[str]:
        """提取 Answer 内容"""
        match = re.search(r'Answer:\s*(.+)', text, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入（格式: "query|||top_k"）
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return f"错误: 未知工具 '{tool_name}'"
        
        try:
            # 解析参数
            parts = tool_input.split("|||")
            query = parts[0]
            top_k = int(parts[1]) if len(parts) > 1 else 5
            
            # 执行工具
            result = self.tools[tool_name](query=query, top_k=top_k)
            
            # 格式化结果
            if isinstance(result, dict):
                if result.get("success"):
                    context = result.get("context", "")
                    count = result.get("count", 0)
                    return f"成功检索到 {count} 个相关文档片段：\n\n{context}"
                else:
                    message = result.get("message", "检索失败")
                    return f"检索失败: {message}"
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return f"工具执行失败: {str(e)}"
    
    def run(self, question: str, stream: bool = False) -> str:
        """
        运行 ReAct Agent
        
        Args:
            question: 用户问题
            stream: 是否流式输出
            
        Returns:
            最终答案
        """
        conversation = []
        current_input = f"用户问题: {question}\n\n请按照 Thought-Action 的格式回答（如果需要工具，系统会返回 Observation）。"
        last_action = None  # 记录上一次的 Action，用于检测重复
        has_observation = False  # 标记是否已经收到 Observation
        
        for iteration in range(self.max_iterations):
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"第 {iteration + 1} 轮推理")
                print(f"{'='*60}")
            
            # 1. LLM 生成 Thought 和 Action
            messages = [{"role": "user", "content": current_input}]
            
            response = ""
            if stream:
                print("\n🤔 ", end='', flush=True)
                for chunk in self.llm.chat(messages, stream=True):
                    # 检查是否包含 "Observation:"，如果有则立即停止
                    if "Observation:" in (response + chunk):
                        # 只保留 Observation: 之前的部分
                        remaining = (response + chunk).split("Observation:")[0]
                        if remaining != response:
                            stop_chunk = remaining[len(response):]
                            print(stop_chunk, end='', flush=True)
                            response += stop_chunk
                        print()
                        if self.verbose:
                            print("\n⚠️  检测到 LLM 尝试生成 Observation，已停止")
                        break
                    print(chunk, end='', flush=True)
                    response += chunk
                else:
                    print()
            else:
                for chunk in self.llm.chat(messages, stream=False):
                    response += chunk
                    # 非流式也要检查
                    if "Observation:" in response:
                        response = response.split("Observation:")[0]
                        break
            
            if self.verbose and not stream:
                print(f"\nLLM 输出:\n{response}")
            
            # 2. 检查是否有 Answer
            answer = self._extract_answer(response)
            if answer:
                if self.verbose:
                    print(f"\n✅ 找到最终答案")
                return answer
            
            # 3. 解析 Action
            tool_name, tool_input = self._parse_action(response)
            
            # 4. 检测重复 Action（防止循环）
            current_action = f"{tool_name}:{tool_input}" if tool_name else None
            if current_action and current_action == last_action and has_observation:
                if self.verbose:
                    print("\n⚠️  检测到重复 Action，已经有 Observation，强制要求给出 Answer")
                current_input = f"""{response}

⚠️ 警告：你已经执行过这个查询并收到了结果。不要重复查询！
请直接基于之前的 Observation 给出 Answer。

现在请给出最终答案（Answer:）"""
                continue
            
            # 5. 如果已有 Observation 但又要 Action，强制要求 Answer
            if has_observation and tool_name:
                if self.verbose:
                    print("\n⚠️  已有 Observation 但仍想执行 Action，强制要求 Answer")
                current_input = f"""{response}

⚠️ 你已经从工具获取了信息（Observation），现在必须基于这些信息回答问题。
不要再次执行 Action！请直接给出 Answer。

格式：
Thought: [基于之前的 Observation 分析]
Answer: [你的答案]"""
                continue
            
            # 6. 如果 Action 是 None，要求 LLM 给出答案
            if tool_name is None:
                thought = self._extract_thought(response)
                if "Action: None" in response or "Action:None" in response:
                    if self.verbose:
                        print("\n📌 LLM 决定不使用工具，直接回答")
                    current_input = f"{response}\n\n请直接给出 Answer。"
                    continue
                else:
                    # 没有找到有效的 Action，提示 LLM
                    if self.verbose:
                        print("\n⚠️  未找到有效的 Action，提示 LLM")
                    current_input = f"{response}\n\n请明确指定 Action（格式: Action: knowledge_search(\"查询内容\", 5) 或 Action: None）"
                    continue
            
            # 7. 执行工具
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"🔧 执行工具: {tool_name}")
                print(f"{'='*60}")
                print(f"   查询: {tool_input.split('|||')[0]}")
                print(f"   Top-K: {tool_input.split('|||')[1] if len(tool_input.split('|||')) > 1 else 5}")
            
            observation = self._execute_tool(tool_name, tool_input)
            
            # 记录已执行的 Action 和标记已有 Observation
            last_action = current_action
            has_observation = True
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"📊 工具执行结果（Observation）")
                print(f"{'='*60}")
                print(f"观察内容总长度: {len(observation)} 字符")
                # 显示前500个字符（增加显示长度）
                if len(observation) > 500:
                    print(f"\n{observation[:500]}...")
                    print(f"\n[... 还有 {len(observation) - 500} 个字符]")
                else:
                    print(f"\n{observation}")
            
            # 8. 构建下一轮输入 - 强制要求只使用 Observation 内容
            current_input = f"""{response}

Observation: {observation}

❗❗❗ 重要指令 ❗❗❗
1. 你**必须**只使用上面 Observation 中的具体内容来回答
2. **禁止**使用你自己的知识或编造内容
3. 如果 Observation 中有具体的文字，请**直接引用或转述**这些文字
4. 不要说"包括：1. 成绩优异 2. 品德良好"这种笼统的话，要说 Observation 里的具体内容

现在请给出答案（必须包含 Observation 中的具体内容）：
Thought: [我从 Observation 中看到了哪些具体内容]
Answer: [根据 Observation 中的具体文字回答，引用原文]"""
            
            # 调试：显示发送给 LLM 的完整内容长度
            if self.verbose:
                print(f"\n[调试] 发送给 LLM 的内容总长度: {len(current_input)} 字符")
                print(f"[调试] 其中 Observation 长度: {len(observation)} 字符")
                # 显示 Observation 的前200字符，确认内容确实包含了
                obs_preview = observation[:200] if len(observation) > 200 else observation
                print(f"[调试] Observation 前200字符:\n{obs_preview}...")
        
        # 达到最大迭代次数
        return "抱歉，我无法在规定步骤内完成推理。请重新提问或简化问题。"


def create_react_agent(llm_service, tools_dict: Dict[str, Callable]) -> ReActAgent:
    """
    创建 ReAct Agent
    
    Args:
        llm_service: LLM 服务实例
        tools_dict: 工具字典
        
    Returns:
        ReActAgent 实例
    """
    return ReActAgent(
        llm_service=llm_service,
        tools=tools_dict,
        max_iterations=5,
        verbose=True
    )

