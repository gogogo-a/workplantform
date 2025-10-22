"""
Embedding 服务
使用 bge-large-zh-v1.5 模型进行文本向量化
"""
# 🔥 关键：必须先导入 constants，设置 HuggingFace 离线模式
from pkg.constants.constants import RUNNING_MODE

from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import numpy as np
import logging

from pkg.model_list import (
    get_embedding_model, 
    list_embedding_models, 
    ModelManager,
    BGE_LARGE_ZH_V1_5  # 默认模型配置
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """文本向量化服务（单例模式）"""
    
    _instance: Optional['EmbeddingService'] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        初始化 Embedding 服务
        
        Args:
            model_name: 模型名称，如果为 None 则使用 BGE_LARGE_ZH_V1_5
            device: 设备 (cpu/cuda/mps)，如果为 None 则使用环境变量 RUNNING_MODE
        """
        # 只初始化一次
        if EmbeddingService._initialized:
            return
        
        # 如果没有指定模型，使用默认配置
        if model_name is None:
            model_name = BGE_LARGE_ZH_V1_5.name
        
        # 如果没有指定设备，使用环境变量
        if device is None:
            device = RUNNING_MODE
            
        self.model_name = model_name
        self.device = device
        self.model = None
        self.model_config = None
        self.dimension = None
        self.max_length = None
        EmbeddingService._initialized = True
        logger.info(f"Embedding 服务已初始化: {model_name}, 设备: {device}")
    
    def load_model(self):
        """加载模型"""
        if self.model is not None:
            logger.info(f"模型已加载: {self.model_name}")
            return
        
        try:
            # 从统一配置中获取模型配置
            self.model_config = get_embedding_model(self.model_name)
            
            logger.info(f"正在加载模型: {self.model_config.model_path}")
            logger.info(f"描述: {self.model_config.description}")
            logger.info(f"维度: {self.model_config.dimension}")
            logger.info(f"最大长度: {self.model_config.max_length}")
            
            # 使用统一管理器加载模型
            self.model = ModelManager.select_embedding_model(self.model_name, self.device)
            self.dimension = self.model_config.dimension
            self.max_length = self.model_config.max_length
            
            logger.info(f"✓ 模型加载成功: {self.model_name}")
            logger.info(f"✓ 使用设备: {self.device}")
            
        except Exception as e:
            logger.error(f"✗ 模型加载失败: {e}")
            raise Exception(f"加载 Embedding 模型失败: {e}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        文本向量化
        
        Args:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            normalize: 是否归一化（使用 COSINE 时建议 True）
            show_progress: 是否显示进度条
            
        Returns:
            np.ndarray: 向量数组
        """
        # 确保模型已加载
        if self.model is None:
            self.load_model()
        
        try:
            # 转换为列表
            if isinstance(texts, str):
                texts = [texts]
                single_text = True
            else:
                single_text = False
            
            # 对于 BGE 模型，查询文本需要添加前缀
            if "bge" in self.model_name.lower():
                # 检查是否已经有前缀
                processed_texts = []
                for text in texts:
                    if not text.startswith("为这个句子生成表示以用于检索相关文章："):
                        processed_texts.append(f"为这个句子生成表示以用于检索相关文章：{text}")
                    else:
                        processed_texts.append(text)
                texts = processed_texts
            
            # 编码
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            
            # 如果是单个文本，返回一维数组
            if single_text:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"✗ 文本编码失败: {e}")
            raise
    
    def encode_query(
        self,
        query: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        查询文本向量化（针对搜索优化）
        
        Args:
            query: 查询文本
            normalize: 是否归一化
            
        Returns:
            np.ndarray: 查询向量
        """
        if self.model is None:
            self.load_model()
        
        try:
            # BGE 模型的查询需要添加特殊前缀
            if "bge" in self.model_name.lower():
                query = f"为这个句子生成表示以用于检索相关文章：{query}"
            
            embedding = self.model.encode(
                query,
                normalize_embeddings=normalize,
                convert_to_numpy=True
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"✗ 查询编码失败: {e}")
            raise
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        文档向量化（不添加查询前缀）
        
        Args:
            documents: 文档列表
            batch_size: 批处理大小
            normalize: 是否归一化
            show_progress: 是否显示进度
            
        Returns:
            np.ndarray: 文档向量数组
        """
        if self.model is None:
            self.load_model()
        
        try:
            # 文档不需要添加前缀，直接编码
            embeddings = self.model.encode(
                documents,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"✗ 文档编码失败: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        try:
            if self.model_config is None:
                self.model_config = get_embedding_model(self.model_name)
            
            return {
                "model_name": self.model_name,
                "model_path": self.model_config.model_path,
                "dimension": self.dimension or self.model_config.dimension,
                "max_length": self.max_length or self.model_config.max_length,
                "description": self.model_config.description,
                "device": self.device,
                "loaded": self.model is not None
            }
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def list_available_models(cls) -> List[dict]:
        """列出所有可用模型"""
        return [config.to_dict() for config in list_embedding_models()]


# 创建全局单例实例（使用默认模型 BGE_LARGE_ZH_V1_5）
embedding_service = EmbeddingService()

