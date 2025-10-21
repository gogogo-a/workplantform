"""
统一模型管理器
集中管理所有类型模型的选择、初始化和配置
"""
from typing import Any, Union, Optional
import logging

from .llm_model_list import (
    LLM_MODELS, 
    LLAMA_3_2, 
    DEEPSEEK_CHAT,
    get_llm_model, 
    list_llm_models
)
from .embedding_model_list import (
    EMBEDDING_MODELS,
    BGE_LARGE_ZH_V1_5,
    BGE_BASE_ZH_V1_5,
    get_embedding_model,
    list_embedding_models
)
from .reranker_model_list import (
    RERANKER_MODELS,
    BGE_RERANKER_V2_M3,
    BGE_RERANKER_LARGE,
    get_reranker_model,
    list_reranker_models
)
from .base_model import LLMModelConfig, EmbeddingModelConfig, RerankerModelConfig

from pkg.constants.constants import OLLAMA_BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器 - 统一管理所有模型"""
    
    @staticmethod
    def select_llm_model(model_name: str, model_type: Optional[str] = None) -> Any:
        """
        选择并初始化 LLM 模型
        
        Args:
            model_name: 模型名称 (如 "llama3.2", "deepseek-chat")
            model_type: 模型类型 ("local" 或 "cloud")，可选，用于验证
            
        Returns:
            LLM 实例
        """
        # 获取模型配置
        config = get_llm_model(model_name)
        
        # 如果提供了 model_type，验证是否匹配
        if model_type is not None and config.model_type != model_type:
            raise ValueError(
                f"模型 '{model_name}' 的类型是 '{config.model_type}'，"
                f"但请求的类型是 '{model_type}'"
            )
        
        # 根据模型类型和提供商初始化模型
        if config.model_type == "local" and config.provider == "ollama":
            from langchain_community.llms import Ollama
            llm = Ollama(
                base_url=OLLAMA_BASE_URL,
                model=config.model_path,
                temperature=config.temperature,
                timeout=config.timeout,
                num_predict=config.max_tokens
            )
            logger.info(f"✓ 已选择本地模型: {model_name} (type: {config.model_type})")
            print(f"✓ 已选择本地模型: {model_name} (type: {config.model_type})")
            return llm
            
        elif config.model_type == "cloud" and config.provider == "deepseek":
            if not DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
            
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=config.model_path,
                openai_api_key=DEEPSEEK_API_KEY,
                openai_api_base=DEEPSEEK_BASE_URL,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            logger.info(f"✓ 已选择云端模型: {model_name} (type: {config.model_type})")
            print(f"✓ 已选择云端模型: {model_name} (type: {config.model_type})")
            return llm
            
        else:
            raise ValueError(
                f"不支持的模型配置: provider={config.provider}, "
                f"model_type={config.model_type}"
            )
    
    @staticmethod
    def select_embedding_model(model_name: str, device: str = "cpu") -> 'SentenceTransformer':
        """
        选择并初始化 Embedding 模型
        
        Args:
            model_name: 模型名称 (如 "bge-large-zh-v1.5")
            device: 设备 (cpu/cuda/mps)
            
        Returns:
            SentenceTransformer 实例
        """
        # 获取模型配置
        config = get_embedding_model(model_name)
        
        # 初始化模型
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer(
            config.model_path,
            device=device
        )
        
        logger.info(f"✓ 已加载 Embedding 模型: {model_name}")
        logger.info(f"  维度: {config.dimension}, 最大长度: {config.max_length}")
        print(f"✓ 已加载 Embedding 模型: {model_name}")
        
        return model
    
    @staticmethod
    def select_reranker_model(model_name: str, device: str = "cpu") -> 'FlagReranker':
        """
        选择并初始化 Reranker 模型
        
        Args:
            model_name: 模型名称 (如 "bge-reranker-v2-m3")
            device: 设备 (cpu/cuda/mps)
            
        Returns:
            FlagReranker 实例
        """
        # 获取模型配置
        config = get_reranker_model(model_name)
        
        # 初始化模型
        from FlagEmbedding import FlagReranker
        
        model = FlagReranker(
            config.model_path,
            use_fp16=config.use_fp16,
            device=device
        )
        
        logger.info(f"✓ 已加载 Reranker 模型: {model_name}")
        logger.info(f"  最大长度: {config.max_length}")
        print(f"✓ 已加载 Reranker 模型: {model_name}")
        
        return model
    
    @staticmethod
    def get_model_config(model_name: str, model_type: str) -> Union[LLMModelConfig, EmbeddingModelConfig, RerankerModelConfig]:
        """
        获取模型配置
        
        Args:
            model_name: 模型名称
            model_type: 模型类型 ("llm", "embedding", "reranker")
            
        Returns:
            模型配置对象
        """
        if model_type == "llm":
            return get_llm_model(model_name)
        elif model_type == "embedding":
            return get_embedding_model(model_name)
        elif model_type == "reranker":
            return get_reranker_model(model_name)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    @staticmethod
    def list_all_models():
        """列出所有可用模型"""
        return {
            "llm": list_llm_models(),
            "embedding": list_embedding_models(),
            "reranker": list_reranker_models()
        }
    
    @staticmethod
    def list_llm_models_by_type(model_type: str):
        """
        根据类型列出 LLM 模型
        
        Args:
            model_type: 模型类型 ("local" 或 "cloud")
            
        Returns:
            List[LLMModelConfig]: 匹配类型的模型配置列表
        """
        all_models = list_llm_models()
        return [m for m in all_models if m.model_type == model_type]
    
    @staticmethod
    def get_model_info(model_name: str, model_category: str) -> dict:
        """
        获取模型的详细信息
        
        Args:
            model_name: 模型名称
            model_category: 模型类别 ("llm", "embedding", "reranker")
            
        Returns:
            dict: 模型信息字典
        """
        config = ModelManager.get_model_config(model_name, model_category)
        return config.to_dict()



# ==================== 导出统一管理器实例 ====================

model_manager = ModelManager()

