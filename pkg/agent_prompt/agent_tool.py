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

def knowledge_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    知识库搜索工具
    从向量数据库中检索相关知识
    
    Args:
        query: 搜索查询
        top_k: 返回结果数量
    """
    # TODO: 实际实现时连接 Milvus 进行向量搜索
    print(f"[工具] 知识库搜索: {query} (Top {top_k})")
    return [
        {
            "content": f"知识片段关于: {query}",
            "source": "示例文档",
            "score": 0.95
        }
    ]

# 提示词模板
knowledge_search.prompt_template = "rag"
knowledge_search.description = "从知识库检索相关信息"


def document_analyzer(doc_path: str) -> Dict:
    """
    文档分析工具
    分析文档内容并提取关键信息
    
    Args:
        doc_path: 文档路径
    """
    # TODO: 实际实现时处理文档
    print(f"[工具] 文档分析: {doc_path}")
    return {
        "summary": "文档摘要",
        "keywords": ["关键词1", "关键词2"],
        "sections": 3
    }

# 提示词模板
document_analyzer.prompt_template = "document"
document_analyzer.description = "分析文档内容"


def code_executor(code: str, language: str = "python") -> Dict:
    """
    代码执行工具
    执行代码并返回结果
    
    Args:
        code: 代码内容
        language: 编程语言
    """
    # TODO: 实际实现时在沙箱环境执行代码
    print(f"[工具] 代码执行: {language}")
    return {
        "status": "success",
        "output": "执行结果",
        "error": None
    }

# 提示词模板
code_executor.prompt_template = "code"
code_executor.description = "执行代码片段"


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
    document_analyzer,
    code_executor
]


def list_all_tools() -> List[Dict]:
    """列出所有可用工具"""
    return get_tools_info(ALL_TOOLS)

