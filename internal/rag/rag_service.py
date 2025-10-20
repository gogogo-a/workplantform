"""
RAG 服务
整合文档处理、向量化、存储、检索
"""
from typing import List, Dict, Any, Optional
import logging

from internal.document.document_processor import document_processor
from internal.embedding.embedding_service import embedding_service
from internal.db.milvus import milvus_client
from internal.reranker.reranker_service import reranker_service

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 服务类"""
    
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_model: str = "bge-large-zh-v1.5",
        reranker_model: str = "bge-reranker-v2-m3",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 5,
        use_reranker: bool = True
    ):
        """
        初始化 RAG 服务
        
        Args:
            collection_name: Milvus 集合名称
            embedding_model: Embedding 模型名称
            reranker_model: Reranker 模型名称
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
            top_k: 检索返回结果数量
            use_reranker: 是否使用 Reranker
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.reranker_model = reranker_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.use_reranker = use_reranker
        
        # 初始化组件
        self.doc_processor = document_processor
        self.embedder = embedding_service
        self.vector_db = milvus_client
        self.reranker = reranker_service if use_reranker else None
        
        logger.info(f"RAG 服务已初始化")
        logger.info(f"  集合名称: {collection_name}")
        logger.info(f"  Embedding 模型: {embedding_model}")
        logger.info(f"  Reranker 模型: {reranker_model if use_reranker else '未启用'}")
        logger.info(f"  分块大小: {chunk_size}")
    
    def initialize(self):
        """初始化所有组件"""
        try:
            # 连接 Milvus
            self.vector_db.connect()
            
            # 加载 Embedding 模型
            self.embedder.load_model()
            
            # 加载 Reranker 模型（如果启用）
            if self.use_reranker and self.reranker:
                self.reranker.load_model()
            
            # 获取模型信息
            model_info = self.embedder.get_model_info()
            dimension = model_info["dimension"]
            
            # 创建或获取集合
            collection = self.vector_db.get_collection(self.collection_name)
            if not collection:
                logger.info(f"创建新集合: {self.collection_name}")
                self.vector_db.create_collection(
                    collection_name=self.collection_name,
                    dimension=dimension,
                    description=f"RAG 文档集合 - {self.embedding_model}",
                    metric_type="COSINE"
                )
            else:
                logger.info(f"使用现有集合: {self.collection_name}")
            
            logger.info("✓ RAG 服务初始化完成")
            
        except Exception as e:
            logger.error(f"✗ RAG 服务初始化失败: {e}")
            raise
    
    def add_documents(
        self,
        file_paths: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        添加文档到向量数据库
        
        Args:
            file_paths: 文档路径列表
            metadata: 额外的元数据
            
        Returns:
            Dict: 添加结果统计
        """
        try:
            logger.info(f"开始处理 {len(file_paths)} 个文档...")
            
            # 1. 处理文档（加载 + 分割）
            all_chunks = self.doc_processor.batch_process_documents(file_paths)
            
            if not all_chunks:
                logger.warning("没有文档块需要处理")
                return {"success": False, "message": "没有文档块"}
            
            # 2. 提取文本和元数据
            texts = [chunk["content"] for chunk in all_chunks]
            chunk_metadata = []
            for chunk in all_chunks:
                meta = chunk["metadata"].copy()
                if metadata:
                    meta.update(metadata)
                chunk_metadata.append(meta)
            
            logger.info(f"共 {len(texts)} 个文本块待向量化...")
            
            # 3. 向量化
            embeddings = self.embedder.encode_documents(
                documents=texts,
                batch_size=32,
                normalize=True,
                show_progress=True
            )
            
            logger.info(f"向量化完成，共 {len(embeddings)} 个向量")
            
            # 4. 存储到 Milvus
            logger.info(f"存储到 Milvus 集合: {self.collection_name}")
            ids = self.vector_db.insert_vectors(
                collection_name=self.collection_name,
                embeddings=embeddings.tolist(),
                texts=texts,
                metadata=chunk_metadata
            )
            
            # 5. 统计信息
            stats = {
                "success": True,
                "total_documents": len(file_paths),
                "total_chunks": len(texts),
                "total_vectors": len(ids),
                "dimension": self.embedder.dimension,
                "collection": self.collection_name
            }
            
            logger.info(f"✓ 文档添加完成")
            logger.info(f"  文档数: {stats['total_documents']}")
            logger.info(f"  文本块数: {stats['total_chunks']}")
            logger.info(f"  向量数: {stats['total_vectors']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"✗ 添加文档失败: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        use_reranker: Optional[bool] = None,
        rerank_top_k: Optional[int] = None,
        rerank_score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        搜索相关文档（包含可选的 Rerank 步骤）
        
        Args:
            query: 查询文本
            top_k: 初始向量检索返回结果数量（会被 Reranker 处理）
            filter_metadata: 元数据过滤条件
            use_reranker: 是否使用 Reranker（None 表示使用默认设置）
            rerank_top_k: Rerank 后返回的结果数量（None 表示与 top_k 相同）
            rerank_score_threshold: Rerank 分数阈值
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            if top_k is None:
                top_k = self.top_k
            
            if use_reranker is None:
                use_reranker = self.use_reranker
            
            if rerank_top_k is None:
                rerank_top_k = top_k
            
            logger.info(f"搜索查询: {query[:50]}...")
            
            # 1. 向量化查询
            query_embedding = self.embedder.encode_query(
                query=query,
                normalize=True
            )
            
            # 2. 向量检索（如果使用 Reranker，检索更多候选）
            retrieval_top_k = top_k * 3 if use_reranker else top_k
            
            results = self.vector_db.search_vectors(
                collection_name=self.collection_name,
                query_embeddings=[query_embedding.tolist()],
                top_k=retrieval_top_k,
                metric_type="COSINE",
                output_fields=["text", "metadata"]
            )
            
            # 3. 格式化结果
            formatted_results = []
            if results and len(results) > 0:
                for hit in results[0]:  # 只有一个查询
                    result = {
                        "id": hit["id"],
                        "text": hit["text"],
                        "metadata": hit["metadata"],
                        "vector_score": hit["score"],
                        "distance": hit["distance"]
                    }
                    
                    # 应用元数据过滤
                    if filter_metadata:
                        match = all(
                            hit["metadata"].get(k) == v
                            for k, v in filter_metadata.items()
                        )
                        if match:
                            formatted_results.append(result)
                    else:
                        formatted_results.append(result)
            
            logger.info(f"✓ 向量检索完成，返回 {len(formatted_results)} 条候选")
            
            # 4. Rerank 步骤（如果启用）
            if use_reranker and self.reranker and formatted_results:
                logger.info(f"开始 Rerank...")
                
                reranked_results = self.reranker.rerank(
                    query=query,
                    documents=formatted_results,
                    top_k=rerank_top_k,
                    score_threshold=rerank_score_threshold
                )
                
                logger.info(f"✓ Rerank 完成，返回 {len(reranked_results)} 条结果")
                return reranked_results
            
            # 5. 不使用 Reranker，直接返回向量检索结果
            return formatted_results[:rerank_top_k]
            
        except Exception as e:
            logger.error(f"✗ 搜索失败: {e}")
            raise
    
    def get_context_for_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        max_context_length: int = 2000,
        use_reranker: Optional[bool] = None,
        rerank_score_threshold: float = 0.0
    ) -> str:
        """
        获取查询的上下文文本（用于 LLM，自动应用 Reranker）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            max_context_length: 最大上下文长度
            use_reranker: 是否使用 Reranker
            rerank_score_threshold: Rerank 分数阈值
            
        Returns:
            str: 拼接的上下文文本
        """
        try:
            # 搜索相关文档（包含 Rerank）
            results = self.search(
                query,
                top_k=top_k,
                use_reranker=use_reranker,
                rerank_score_threshold=rerank_score_threshold
            )
            
            if not results:
                return ""
            
            # 拼接上下文
            context_parts = []
            current_length = 0
            
            for i, result in enumerate(results, 1):
                text = result["text"]
                source = result["metadata"].get("filename", "未知来源")
                
                # 添加分数信息（如果有 rerank_score）
                score_info = ""
                if "rerank_score" in result:
                    score_info = f" (Rerank分数: {result['rerank_score']:.4f})"
                
                # 格式化引用
                part = f"[文档{i} - {source}{score_info}]\n{text}\n"
                part_length = len(part)
                
                # 检查长度限制
                if current_length + part_length > max_context_length:
                    break
                
                context_parts.append(part)
                current_length += part_length
            
            context = "\n".join(context_parts)
            
            logger.info(f"✓ 生成上下文，长度: {len(context)} 字符")
            
            return context
            
        except Exception as e:
            logger.error(f"✗ 获取上下文失败: {e}")
            return ""
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            stats = self.vector_db.get_collection_stats(self.collection_name)
            model_info = self.embedder.get_model_info()
            
            return {
                **stats,
                "embedding_model": model_info["model_name"],
                "dimension": model_info["dimension"]
            }
        except Exception as e:
            logger.error(f"✗ 获取统计信息失败: {e}")
            return {}


# 创建默认 RAG 服务实例
rag_service = RAGService(
    collection_name="rag_documents",
    embedding_model="bge-large-zh-v1.5",
    reranker_model="bge-reranker-v2-m3",
    chunk_size=500,
    chunk_overlap=50,
    top_k=5,
    use_reranker=True
)

