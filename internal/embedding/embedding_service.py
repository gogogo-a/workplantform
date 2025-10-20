"""
Embedding 服务
使用 bge-large-zh-v1.5 模型进行文本向量化
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """文本向量化服务（单例模式）"""
    
    _instance: Optional['EmbeddingService'] = None
    _initialized: bool = False
    
    # 支持的模型配置
    MODELS = {
        "bge-large-zh-v1.5": {
            "model_name": "BAAI/bge-large-zh-v1.5",
            "dimension": 1024,
            "max_length": 512,
            "description": "BAAI 出品，中文效果最好"
        },
        "bge-base-zh-v1.5": {
            "model_name": "BAAI/bge-base-zh-v1.5",
            "dimension": 768,
            "max_length": 512,
            "description": "速度快，效果好"
        },
        "text2vec-base-chinese": {
            "model_name": "shibing624/text2vec-base-chinese",
            "dimension": 768,
            "max_length": 512,
            "description": "轻量级中文模型"
        }
    }
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "bge-large-zh-v1.5", device: str = "cpu"):
        """
        初始化 Embedding 服务
        
        Args:
            model_name: 模型名称
            device: 设备 (cpu/cuda/mps)
        """
        # 只初始化一次
        if EmbeddingService._initialized:
            return
            
        self.model_name = model_name
        self.device = device
        self.model = None
        self.dimension = None
        self.max_length = None
        EmbeddingService._initialized = True
        logger.info(f"Embedding 服务已初始化: {model_name}")
    
    def load_model(self):
        """加载模型"""
        if self.model is not None:
            logger.info(f"模型已加载: {self.model_name}")
            return
        
        try:
            if self.model_name not in self.MODELS:
                raise ValueError(f"不支持的模型: {self.model_name}")
            
            model_config = self.MODELS[self.model_name]
            model_path = model_config["model_name"]
            
            logger.info(f"正在加载模型: {model_path}")
            logger.info(f"描述: {model_config['description']}")
            logger.info(f"维度: {model_config['dimension']}")
            logger.info(f"最大长度: {model_config['max_length']}")
            
            # 加载模型
            self.model = SentenceTransformer(model_path, device=self.device)
            self.dimension = model_config["dimension"]
            self.max_length = model_config["max_length"]
            
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
        if self.model_name not in self.MODELS:
            return {}
        
        config = self.MODELS[self.model_name]
        return {
            "model_name": self.model_name,
            "model_path": config["model_name"],
            "dimension": self.dimension or config["dimension"],
            "max_length": self.max_length or config["max_length"],
            "description": config["description"],
            "device": self.device,
            "loaded": self.model is not None
        }
    
    @classmethod
    def list_available_models(cls) -> List[dict]:
        """列出所有可用模型"""
        return [
            {
                "name": name,
                **config
            }
            for name, config in cls.MODELS.items()
        ]


# 创建全局单例实例
embedding_service = EmbeddingService(model_name="bge-large-zh-v1.5")

