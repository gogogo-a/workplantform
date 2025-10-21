"""
文档处理服务
负责文档加载、分割、清理、向量化、存储到 MongoDB 和 Milvus
完整流程：文档 -> MongoDB(获取UUID) -> 分割 -> 向量化 -> Milvus
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import re

# 文档加载器
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器 - 负责文档的完整处理流程（MongoDB + Milvus）"""
    
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader,
    }
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
        embedding_service = None,
        milvus_client = None
    ):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠（字符数）
            separators: 分割符列表
            embedding_service: Embedding 服务实例
            milvus_client: Milvus 客户端实例
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_service = embedding_service
        self.milvus_client = milvus_client
        # MongoDB 模型将在需要时导入（避免循环导入）
        
        # 默认分割符（针对中文优化）
        if separators is None:
            separators = [
                "\n\n",  # 段落
                "\n",    # 换行
                "。",    # 句号
                "！",    # 感叹号
                "？",    # 问号
                "；",    # 分号
                "，",    # 逗号
                " ",     # 空格
                ""       # 字符
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        logger.info(f"文档处理器已初始化")
        logger.info(f"  分块大小: {chunk_size}")
        logger.info(f"  分块重叠: {chunk_overlap}")
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            List[Dict]: 文档内容列表
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            extension = path.suffix.lower()
            
            if extension not in self.SUPPORTED_EXTENSIONS:
                raise ValueError(
                    f"不支持的文件类型: {extension}. "
                    f"支持的类型: {list(self.SUPPORTED_EXTENSIONS.keys())}"
                )
            
            # 选择对应的加载器
            loader_class = self.SUPPORTED_EXTENSIONS[extension]
            loader = loader_class(str(path))
            
            # 加载文档
            documents = loader.load()
            
            logger.info(f"✓ 成功加载文档: {path.name}")
            logger.info(f"  页数/段落数: {len(documents)}")
            
            # 转换为字典格式
            result = []
            for doc in documents:
                result.append({
                    "content": doc.page_content,
                    "metadata": {
                        **doc.metadata,
                        "source": str(path),
                        "filename": path.name,
                        "extension": extension
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"✗ 加载文档失败: {e}")
            raise
    
    def split_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        分割文本为块
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            List[Dict]: 文本块列表
        """
        try:
            # 清理文本
            text = self.clean_text(text)
            
            # 分割文本
            chunks = self.text_splitter.split_text(text)
            
            # 构建结果
            result = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "content": chunk,
                    "metadata": {
                        **(metadata or {}),
                        "chunk_index": i,
                        "chunk_count": len(chunks),
                        "chunk_size": len(chunk)
                    }
                }
                result.append(chunk_data)
            
            logger.info(f"✓ 文本分割完成: {len(chunks)} 个块")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ 文本分割失败: {e}")
            raise
    
    def process_document(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        处理文档：加载 + 分割
        
        Args:
            file_path: 文档路径
            
        Returns:
            List[Dict]: 处理后的文本块列表
        """
        try:
            # 加载文档
            documents = self.load_document(file_path)
            
            # 分割每个文档
            all_chunks = []
            for doc in documents:
                chunks = self.split_text(
                    text=doc["content"],
                    metadata=doc["metadata"]
                )
                all_chunks.extend(chunks)
            
            logger.info(f"✓ 文档处理完成")
            logger.info(f"  总块数: {len(all_chunks)}")
            
            return all_chunks
            
        except Exception as e:
            logger.error(f"✗ 文档处理失败: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        # text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:，。！？；：、""''（）【】《》]', '', text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def batch_process_documents(
        self,
        file_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量处理文档
        
        Args:
            file_paths: 文档路径列表
            
        Returns:
            List[Dict]: 所有文档的文本块列表
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self.process_document(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"处理文档 {file_path} 失败: {e}")
                continue
        
        logger.info(f"✓ 批量处理完成")
        logger.info(f"  总文档数: {len(file_paths)}")
        logger.info(f"  总块数: {len(all_chunks)}")
        
        return all_chunks
    
    def get_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取文档块统计信息
        
        Args:
            chunks: 文本块列表
            
        Returns:
            Dict: 统计信息
        """
        if not chunks:
            return {}
        
        chunk_sizes = [len(chunk["content"]) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }
    
    async def add_documents_to_mongodb(
        self,
        file_paths: List[str],
        url_prefix: str = "",
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        步骤 1: 将文档保存到 MongoDB，获取 UUID
        
        Args:
            file_paths: 文档路径列表
            url_prefix: 文档 URL 前缀
            extra_metadata: 额外的元数据
            
        Returns:
            List[Dict]: 文档信息列表，每个包含 uuid、file_path、content 等
        """
        from internal.model.document import DocumentModel
        
        try:
            logger.info(f"开始将 {len(file_paths)} 个文档保存到 MongoDB...")
            
            documents_info = []
            
            for file_path in file_paths:
                try:
                    path = Path(file_path)
                    
                    # 加载文档内容
                    loaded_docs = self.load_document(file_path)
                    
                    # 合并所有页的内容
                    full_content = "\n\n".join([doc["content"] for doc in loaded_docs])
                    
                    # 创建 MongoDB 文档
                    doc_model = DocumentModel(
                        name=path.name,
                        content=full_content,
                        page=len(loaded_docs),
                        url=f"{url_prefix}/{path.name}" if url_prefix else str(path),
                        size=path.stat().st_size if path.exists() else 0
                    )
                    
                    # 保存到 MongoDB
                    await doc_model.insert()
                    
                    logger.info(f"✓ 文档已保存到 MongoDB: {path.name}, UUID: {doc_model.uuid}")
                    
                    # 记录文档信息
                    doc_info = {
                        "uuid": doc_model.uuid,
                        "file_path": file_path,
                        "name": path.name,
                        "content": full_content,
                        "page": len(loaded_docs),
                        "size": path.stat().st_size if path.exists() else 0,
                        "extension": path.suffix.lower()
                    }
                    
                    if extra_metadata:
                        doc_info.update(extra_metadata)
                    
                    documents_info.append(doc_info)
                    
                except Exception as e:
                    logger.error(f"✗ 保存文档 {file_path} 到 MongoDB 失败: {e}")
                    continue
            
            logger.info(f"✓ 成功保存 {len(documents_info)} 个文档到 MongoDB")
            
            return documents_info
            
        except Exception as e:
            logger.error(f"✗ 批量保存文档到 MongoDB 失败: {e}")
            raise
    
    def add_document_chunks_to_milvus(
        self,
        document_info: Dict[str, Any],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        步骤 2: 分割文档、向量化、存储到 Milvus（带 UUID）
        
        Args:
            document_info: 文档信息（包含 uuid, content 等）
            collection_name: Milvus 集合名称
            
        Returns:
            Dict: 处理结果统计
        """
        if self.embedding_service is None:
            raise ValueError("Embedding 服务未初始化，请先设置 embedding_service")
        if self.milvus_client is None:
            raise ValueError("Milvus 客户端未初始化，请先设置 milvus_client")
        
        try:
            doc_uuid = document_info["uuid"]
            content = document_info["content"]
            
            logger.info(f"开始处理文档 UUID: {doc_uuid}")
            
            # 1. 分割文本
            chunks = self.split_text(
                text=content,
                metadata={
                    "document_uuid": doc_uuid,
                    "filename": document_info.get("name", "unknown"),
                    "source": document_info.get("file_path", "unknown")
                }
            )
            
            if not chunks:
                logger.warning(f"文档 {doc_uuid} 没有生成文本块")
                return {"success": False, "message": "没有文本块"}
            
            # 2. 提取文本和构建元数据
            texts = []
            chunk_metadata = []
            
            for idx, chunk in enumerate(chunks):
                texts.append(chunk["content"])
                
                # 构建元数据，包含 document_uuid 和 chunk_id
                meta = {
                    "document_uuid": doc_uuid,
                    "chunk_id": idx,
                    "chunk_index": chunk["metadata"]["chunk_index"],
                    "chunk_count": chunk["metadata"]["chunk_count"],
                    "text": chunk["content"],  # 存储文本
                    "filename": document_info.get("name", "unknown"),
                    "source": document_info.get("file_path", "unknown")
                }
                chunk_metadata.append(meta)
            
            logger.info(f"  文档 {doc_uuid} 分割成 {len(texts)} 个文本块")
            
            # 3. 向量化
            embeddings = self.embedding_service.encode_documents(
                documents=texts,
                batch_size=32,
                normalize=True,
                show_progress=False
            )
            
            logger.info(f"  文档 {doc_uuid} 向量化完成，共 {len(embeddings)} 个向量")
            
            # 4. 存储到 Milvus
            ids = self.milvus_client.insert_vectors(
                collection_name=collection_name,
                embeddings=embeddings.tolist(),
                texts=texts,
                metadata=chunk_metadata
            )
            
            logger.info(f"✓ 文档 {doc_uuid} 已存储到 Milvus，共 {len(ids)} 个向量")
            
            return {
                "success": True,
                "document_uuid": doc_uuid,
                "total_chunks": len(texts),
                "total_vectors": len(ids)
            }
            
        except Exception as e:
            logger.error(f"✗ 处理文档失败: {e}")
            raise
    
    async def add_documents(
        self,
        file_paths: List[str],
        collection_name: str,
        url_prefix: str = "",
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        完整的文档处理流程：MongoDB -> 分割 -> 向量化 -> Milvus
        
        Args:
            file_paths: 文档路径列表
            collection_name: Milvus 集合名称
            url_prefix: 文档 URL 前缀
            extra_metadata: 额外的元数据
            
        Returns:
            Dict: 处理结果统计
        """
        try:
            logger.info(f"开始完整文档处理流程，共 {len(file_paths)} 个文档...")
            
            # 步骤 1: 保存到 MongoDB，获取 UUID
            documents_info = await self.add_documents_to_mongodb(
                file_paths=file_paths,
                url_prefix=url_prefix,
                extra_metadata=extra_metadata
            )
            
            if not documents_info:
                return {"success": False, "message": "没有文档被处理"}
            
            # 步骤 2: 逐个文档分割、向量化、存储到 Milvus
            total_chunks = 0
            total_vectors = 0
            processed_docs = []
            
            for doc_info in documents_info:
                try:
                    result = self.add_document_chunks_to_milvus(
                        document_info=doc_info,
                        collection_name=collection_name
                    )
                    
                    if result["success"]:
                        total_chunks += result["total_chunks"]
                        total_vectors += result["total_vectors"]
                        processed_docs.append(doc_info["uuid"])
                        
                except Exception as e:
                    logger.error(f"✗ 处理文档 {doc_info['uuid']} 失败: {e}")
                    continue
            
            # 统计信息
            stats = {
                "success": True,
                "total_documents": len(file_paths),
                "processed_documents": len(processed_docs),
                "document_uuids": processed_docs,
                "total_chunks": total_chunks,
                "total_vectors": total_vectors,
                "dimension": self.embedding_service.dimension,
                "collection": collection_name
            }
            
            logger.info(f"✓ 完整流程完成")
            logger.info(f"  总文档数: {stats['total_documents']}")
            logger.info(f"  处理成功: {stats['processed_documents']}")
            logger.info(f"  总文本块数: {stats['total_chunks']}")
            logger.info(f"  总向量数: {stats['total_vectors']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"✗ 完整文档处理流程失败: {e}")
            raise


# 注意：不在这里导入 embedding_service 和 milvus_client 避免循环导入
# 使用时需要手动注入依赖：
# document_processor.embedding_service = embedding_service
# document_processor.milvus_client = milvus_client
#
# 使用方式：
# 1. 完整流程：await document_processor.add_documents(file_paths, collection_name)
#    - 文档 -> MongoDB(获取UUID) -> 分割 -> 向量化 -> Milvus
#
# 2. 分步骤：
#    - 步骤 1: documents_info = await document_processor.add_documents_to_mongodb(file_paths)
#    - 步骤 2: document_processor.add_document_chunks_to_milvus(doc_info, collection_name)
#
# Milvus 存储结构：
# - document_uuid: 文档在 MongoDB 中的 UUID
# - chunk_id: 分割后的小段 ID (0, 1, 2, ...)
# - text: 文本内容
# - vector: 向量
# - metadata: filename, source, chunk_index, chunk_count 等

# 创建默认实例（依赖需要在使用前注入）
document_processor = DocumentProcessor(
    chunk_size=500,    # 500字符一块
    chunk_overlap=50,  # 50字符重叠
)

