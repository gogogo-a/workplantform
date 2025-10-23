"""
文档处理工具函数
提供文档加载、分割、清理等功能
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from log import logger


# 支持的文件类型映射
SUPPORTED_LOADERS = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}


def load_document(file_path: str) -> List[Dict[str, Any]]:
    """
    加载文档
    
    Args:
        file_path: 文档路径
        
    Returns:
        List[Dict]: 文档内容列表，每个包含 content 和 metadata
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension not in SUPPORTED_LOADERS:
            raise ValueError(
                f"不支持的文件类型: {extension}. "
                f"支持的类型: {list(SUPPORTED_LOADERS.keys())}"
            )
        
        # 选择对应的加载器
        loader_class = SUPPORTED_LOADERS[extension]
        loader = loader_class(str(path))
        
        # 加载文档
        documents = loader.load()
        
        logger.info(f"✓ 文档加载成功: {path.name}, 页数: {len(documents)}")
        
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
        logger.error(f"✗ 文档加载失败: {e}", exc_info=True)
        raise


def clean_text(text: str) -> str:
    """
    清理文本
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    text = text.strip()
    
    return text


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separators: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    分割文本为块
    
    Args:
        text: 文本内容
        chunk_size: 分块大小（字符数）
        chunk_overlap: 分块重叠（字符数）
        separators: 分割符列表（可选）
        metadata: 元数据（可选）
        
    Returns:
        List[Dict]: 文本块列表，每个包含 content 和 metadata
    """
    try:
        # 清理文本
        text = clean_text(text)
        
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
        
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        # 分割文本
        chunks = text_splitter.split_text(text)
        
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
        logger.error(f"✗ 文本分割失败: {e}", exc_info=True)
        raise


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件基本信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict: 文件信息（name, size, extension 等）
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    return {
        "name": path.name,
        "path": str(path),
        "extension": path.suffix.lower(),
        "size": path.stat().st_size,
        "exists": True
    }


def is_supported_file(file_path: str) -> bool:
    """
    检查文件类型是否支持
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否支持
    """
    extension = Path(file_path).suffix.lower()
    return extension in SUPPORTED_LOADERS


if __name__ == "__main__":
    # 测试代码
    print("=" * 80)
    print("文档工具函数测试")
    print("=" * 80)
    
    # 测试文本分割
    test_text = """
    这是第一段测试文本。这段文本会被分割成多个块。
    
    这是第二段测试文本。我们使用递归字符分割器。
    
    这是第三段测试文本。支持中文分割。
    """
    
    chunks = split_text(test_text, chunk_size=50, chunk_overlap=10)
    print(f"\n文本分割结果: {len(chunks)} 个块")
    for i, chunk in enumerate(chunks):
        print(f"  块 {i}: {chunk['content'][:30]}... ({chunk['metadata']['chunk_size']} 字符)")
    
    # 测试文件检查
    print(f"\n支持的文件类型: {list(SUPPORTED_LOADERS.keys())}")
    print(f"test.pdf 是否支持: {is_supported_file('test.pdf')}")
    print(f"test.mp4 是否支持: {is_supported_file('test.mp4')}")

