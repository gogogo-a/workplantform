"""
Agent 工具基础类
"""
from typing import Dict, Callable, Any


class AgentTool:
    """工具基础类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        prompt_template: str = "default",
        is_admin: bool = False
    ):
        self.name = name
        self.description = description
        self.func = func
        self.prompt_template = prompt_template
        self.is_admin = is_admin
    
    def execute(self, *args, **kwargs) -> Any:
        """执行工具"""
        return self.func(*args, **kwargs)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template,
            "is_admin": self.is_admin
        }

