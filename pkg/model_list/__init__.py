"""
模型列表模块
统一导出所有模型配置和管理器
"""

# 导出基础模型配置类
from .base_model import (
    BaseModelConfig,
    LLMModelConfig,
    EmbeddingModelConfig,
    RerankerModelConfig
)

# 导出 LLM 模型
from .llm_model_list import (
    LLAMA_3_2,
    DEEPSEEK_CHAT,
    LLM_MODELS,
    get_llm_model,
    list_llm_models
)

# 导出 Embedding 模型
from .embedding_model_list import (
    BGE_LARGE_ZH_V1_5,
    BGE_BASE_ZH_V1_5,
    TEXT2VEC_BASE_CHINESE,
    EMBEDDING_MODELS,
    get_embedding_model,
    list_embedding_models
)

# 导出 Reranker 模型
from .reranker_model_list import (
    BGE_RERANKER_V2_M3,
    BGE_RERANKER_LARGE,
    BGE_RERANKER_BASE,
    RERANKER_MODELS,
    get_reranker_model,
    list_reranker_models
)

# 导出统一管理器
from .model_manager import (
    ModelManager,
    model_manager,
)

__all__ = [
    # 基础类
    "BaseModelConfig",
    "LLMModelConfig",
    "EmbeddingModelConfig",
    "RerankerModelConfig",
    
    # LLM 模型
    "LLAMA_3_2",
    "DEEPSEEK_CHAT",
    "LLM_MODELS",
    "get_llm_model",
    "list_llm_models",
    
    # Embedding 模型
    "BGE_LARGE_ZH_V1_5",
    "BGE_BASE_ZH_V1_5",
    "TEXT2VEC_BASE_CHINESE",
    "EMBEDDING_MODELS",
    "get_embedding_model",
    "list_embedding_models",
    
    # Reranker 模型
    "BGE_RERANKER_V2_M3",
    "BGE_RERANKER_LARGE",
    "BGE_RERANKER_BASE",
    "RERANKER_MODELS",
    "get_reranker_model",
    "list_reranker_models",
    
    # 统一管理器
    "ModelManager",
    "model_manager",
]

