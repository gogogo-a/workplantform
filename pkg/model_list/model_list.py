"""
AI 模型配置列表和选择函数
"""
from pkg.constants.constants import OLLAMA_BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


# ==================== 模型配置列表 ====================

MODEL_LIST = [
    {
        "name": "llama3.2",
        "type": "local",
        "provider": "ollama",
        "description": "Llama 3.2 本地模型"
    },
    {
        "name": "deepseek-chat",
        "type": "cloud",
        "provider": "deepseek",
        "description": "DeepSeek Chat 云端模型"
    }
]


# ==================== 模型选择函数 ====================

def select_model(model_name: str, model_type: str):
    """
    根据模型名称和类型选择并初始化模型
    
    Args:
        model_name: 模型名称，如 "llama3.2" 或 "deepseek-chat"
        model_type: 模型类型，"local" 或 "cloud"
    
    Returns:
        LLM实例
    """
    # 匹配模型
    if model_type == "local":
        if model_name == "llama3.2":
            # 本地 Ollama 模型
            from langchain_community.llms import Ollama
            llm = Ollama(
                base_url=OLLAMA_BASE_URL,
                model=model_name,
                temperature=0.3,
                timeout=120,  # 增加超时时间
                num_predict=2048  # 限制输出长度
            )
            print(f"✓ 已选择本地模型: {model_name}")
            return llm
        else:
            raise ValueError(f"不支持的本地模型: {model_name}")
    
    elif model_type == "cloud":
        if model_name == "deepseek-chat":
            # DeepSeek 云端模型
            if not DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
            
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model_name,
                openai_api_key=DEEPSEEK_API_KEY,
                openai_api_base=DEEPSEEK_BASE_URL,
                temperature=0.3
            )
            print(f"✓ 已选择云端模型: {model_name}")
            return llm
        else:
            raise ValueError(f"不支持的云端模型: {model_name}")
    
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def get_available_models():
    """获取可用的模型列表"""
    return MODEL_LIST
