"""
Re-ranker 服务
用于对检索结果进行二次排序，提高相关性
"""
from FlagEmbedding import FlagReranker
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RerankerService:
    """Re-ranker 服务（单例模式）"""
    
    _instance: Optional['RerankerService'] = None
    _initialized: bool = False
    
    # 支持的模型配置
    MODELS = {
        "bge-reranker-v2-m3": {
            "model_name": "BAAI/bge-reranker-v2-m3",
            "description": "多语言 Reranker，支持中英文",
            "max_length": 8192
        },
        "bge-reranker-large": {
            "model_name": "BAAI/bge-reranker-large",
            "description": "大型中文 Reranker",
            "max_length": 512
        },
        "bge-reranker-base": {
            "model_name": "BAAI/bge-reranker-base",
            "description": "基础中文 Reranker",
            "max_length": 512
        }
    }
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "bge-reranker-v2-m3", device: str = "cpu"):
        """
        初始化 Reranker 服务
        
        Args:
            model_name: 模型名称
            device: 设备 (cpu/cuda/mps)
        """
        # 只初始化一次
        if RerankerService._initialized:
            return
        
        self.model_name = model_name
        self.device = device
        self.model = None
        self.max_length = None
        RerankerService._initialized = True
        logger.info(f"Reranker 服务已初始化: {model_name}")
    
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
            
            logger.info(f"正在加载 Reranker 模型: {model_path}")
            logger.info(f"描述: {model_config['description']}")
            logger.info(f"最大长度: {model_config['max_length']}")
            
            # 加载模型
            self.model = FlagReranker(
                model_path,
                use_fp16=False,  # CPU 不支持 fp16
                device=self.device
            )
            self.max_length = model_config["max_length"]
            
            logger.info(f"✓ Reranker 模型加载成功: {self.model_name}")
            logger.info(f"✓ 使用设备: {self.device}")
            
        except Exception as e:
            logger.error(f"✗ Reranker 模型加载失败: {e}")
            raise Exception(f"加载 Reranker 模型失败: {e}")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表，每个文档需包含 'text' 字段
            top_k: 返回前 k 个结果，None 表示返回全部
            score_threshold: 分数阈值，低于此分数的文档将被过滤
            
        Returns:
            List[Dict]: 重排序后的文档列表（添加了 rerank_score 字段）
        """
        # 确保模型已加载
        if self.model is None:
            self.load_model()
        
        if not documents:
            return []
        
        try:
            # 提取文本
            texts = [doc.get('text', '') for doc in documents]
            
            # 构建查询-文档对
            pairs = [[query, text] for text in texts]
            
            # 计算 rerank 分数
            scores = self.model.compute_score(pairs)
            
            # 如果是单个文档，scores 是标量
            if not isinstance(scores, list):
                scores = [scores]
            
            # 添加 rerank 分数到文档
            reranked_docs = []
            for doc, score in zip(documents, scores):
                doc_copy = doc.copy()
                doc_copy['rerank_score'] = float(score)
                
                # 应用分数阈值
                if score >= score_threshold:
                    reranked_docs.append(doc_copy)
            
            # 按分数降序排序
            reranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 截取 top_k
            if top_k is not None:
                reranked_docs = reranked_docs[:top_k]
            
            logger.info(f"✓ Rerank 完成")
            logger.info(f"  原始文档数: {len(documents)}")
            logger.info(f"  过滤后: {len(reranked_docs)}")
            if reranked_docs:
                logger.info(f"  最高分: {reranked_docs[0]['rerank_score']:.4f}")
                logger.info(f"  最低分: {reranked_docs[-1]['rerank_score']:.4f}")
            
            return reranked_docs
            
        except Exception as e:
            logger.error(f"✗ Rerank 失败: {e}")
            raise
    
    def rerank_simple(
        self,
        query: str,
        texts: List[str],
        top_k: Optional[int] = None
    ) -> List[tuple]:
        """
        简单的重排序（只返回文本和分数）
        
        Args:
            query: 查询文本
            texts: 文本列表
            top_k: 返回前 k 个结果
            
        Returns:
            List[tuple]: [(text, score), ...] 按分数降序
        """
        if self.model is None:
            self.load_model()
        
        if not texts:
            return []
        
        try:
            # 构建查询-文档对
            pairs = [[query, text] for text in texts]
            
            # 计算分数
            scores = self.model.compute_score(pairs)
            
            # 如果是单个文档，scores 是标量
            if not isinstance(scores, list):
                scores = [scores]
            
            # 组合文本和分数
            results = list(zip(texts, scores))
            
            # 按分数降序排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            # 截取 top_k
            if top_k is not None:
                results = results[:top_k]
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Rerank 失败: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        if self.model_name not in self.MODELS:
            return {}
        
        config = self.MODELS[self.model_name]
        return {
            "model_name": self.model_name,
            "model_path": config["model_name"],
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
reranker_service = RerankerService(model_name="bge-reranker-v2-m3")

