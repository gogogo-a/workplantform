"""
Reranker 模型列表
定义所有可用的重排序模型
"""
from .base_model import RerankerModelConfig


# ==================== BGE Reranker 系列模型 ====================

BGE_RERANKER_V2_M3 = RerankerModelConfig(
    name="bge-reranker-v2-m3",
    model_path="BAAI/bge-reranker-v2-m3",
    description="多语言 Reranker，支持中英文",
    provider="baai",
    model_type="local",
    max_length=8192,
    use_fp16=False
)

BGE_RERANKER_LARGE = RerankerModelConfig(
    name="bge-reranker-large",
    model_path="BAAI/bge-reranker-large",
    description="大型中文 Reranker",
    provider="baai",
    model_type="local",
    max_length=512,
    use_fp16=False
)

BGE_RERANKER_BASE = RerankerModelConfig(
    name="bge-reranker-base",
    model_path="BAAI/bge-reranker-base",
    description="基础中文 Reranker",
    provider="baai",
    model_type="local",
    max_length=512,
    use_fp16=False
)


# ==================== 模型字典（用于查找）====================

RERANKER_MODELS = {
    "bge-reranker-v2-m3": BGE_RERANKER_V2_M3,
    "bge-reranker-large": BGE_RERANKER_LARGE,
    "bge-reranker-base": BGE_RERANKER_BASE,
}


# ==================== 辅助函数 ====================

def get_reranker_model(model_name: str) -> RerankerModelConfig:
    """
    获取 Reranker 模型配置
    
    Args:
        model_name: 模型名称
        
    Returns:
        RerankerModelConfig: 模型配置对象
        
    Raises:
        ValueError: 如果模型不存在
    """
    if model_name not in RERANKER_MODELS:
        available = ", ".join(RERANKER_MODELS.keys())
        raise ValueError(f"未找到 Reranker 模型 '{model_name}'。可用模型: {available}")
    return RERANKER_MODELS[model_name]


def list_reranker_models():
    """列出所有可用的 Reranker 模型"""
    return list(RERANKER_MODELS.values())

