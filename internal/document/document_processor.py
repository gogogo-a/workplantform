"""
文档处理服务
负责文档加载、分割、清理
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
    """文档处理器"""
    
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
        separators: Optional[List[str]] = None
    ):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠（字符数）
            separators: 分割符列表
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
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


# 创建默认实例
document_processor = DocumentProcessor(
    chunk_size=500,    # 500字符一块
    chunk_overlap=50   # 50字符重叠
)

