"""
Agent 工具系统
定义可用的工具和工具与提示词的配对关系
"""
from typing import Dict, List, Callable, Any


# ==================== 工具定义 ====================

class AgentTool:
    """工具类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        prompt_template: str = "default"
    ):
        self.name = name
        self.description = description
        self.func = func
        self.prompt_template = prompt_template
    
    def execute(self, *args, **kwargs) -> Any:
        """执行工具"""
        return self.func(*args, **kwargs)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template
        }


# ==================== 工具函数定义 ====================

def knowledge_search(query: str, top_k: int = 5, use_reranker: bool = True) -> Dict[str, Any]:
    """
    知识库搜索工具
    从向量数据库中检索相关知识（RAG）
    
    Args:
        query: 搜索查询
        top_k: 返回结果数量
        use_reranker: 是否使用重排序
        
    Returns:
        Dict: 包含搜索结果和上下文的字典
            - success: 是否成功
            - results: 搜索结果列表
            - context: 格式化的上下文文本
            - count: 结果数量
    """
    try:
        # 延迟导入，避免循环依赖
        from internal.rag.rag_service import rag_service
        
        print(f"[工具] 知识库搜索: {query} (Top {top_k})")
        
        # 执行 RAG 检索
        search_results = rag_service.search(
            query=query,
            top_k=top_k,
            use_reranker=use_reranker
        )
        
        if not search_results:
            print(f"[工具] 未找到相关文档")
            return {
                "success": False,
                "results": [],
                "context": "",
                "count": 0,
                "message": "知识库中未找到相关信息"
            }
        
        # 构建上下文（增加长度限制，确保返回完整内容）
        context = rag_service.get_context_for_query(
            query=query,
            top_k=top_k,
            max_context_length=10000,  # 增加到 10000 字符，确保完整内容
            use_reranker=use_reranker
        )
        
        print(f"[工具] 找到 {len(search_results)} 个相关文档片段")
        print(f"[工具] 上下文长度: {len(context)} 字符")
        
        return {
            "success": True,
            "results": search_results,
            "context": context,
            "count": len(search_results),
            "message": f"成功检索到 {len(search_results)} 个相关文档片段"
        }
        
    except Exception as e:
        print(f"[工具] 知识库搜索失败: {e}")
        return {
            "success": False,
            "results": [],
            "context": "",
            "count": 0,
            "message": f"搜索失败: {str(e)}"
        }

# 提示词模板
knowledge_search.prompt_template = "rag"
knowledge_search.description = "从知识库检索相关信息（RAG检索），用于回答需要参考文档的问题"




# ==================== 工具助手函数 ====================

def get_tool_info(tool_func: Callable) -> Dict:
    """
    获取工具信息
    
    Args:
        tool_func: 工具函数
        
    Returns:
        工具信息字典
    """
    return {
        "name": tool_func.__name__,
        "description": getattr(tool_func, "description", tool_func.__doc__ or "无描述"),
        "prompt_template": getattr(tool_func, "prompt_template", "default")
    }


def get_tools_info(tools: List[Callable]) -> List[Dict]:
    """
    批量获取工具信息
    
    Args:
        tools: 工具函数列表
        
    Returns:
        工具信息列表
    """
    return [get_tool_info(tool) for tool in tools]


def get_prompt_for_tools(tools: List[Callable]) -> str:
    """
    根据工具列表获取合适的提示词模板
    
    Args:
        tools: 工具函数列表
        
    Returns:
        提示词模板名称
    """
    if not tools:
        return "default"
    
    # 返回第一个工具的提示词模板
    first_tool = tools[0]
    return getattr(first_tool, "prompt_template", "default")


# ==================== 导出所有工具 ====================

ALL_TOOLS = [
    knowledge_search,
]


def list_all_tools() -> List[Dict]:
    """列出所有可用工具"""
    return get_tools_info(ALL_TOOLS)

