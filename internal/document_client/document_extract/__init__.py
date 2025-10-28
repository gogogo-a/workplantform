"""
文档提取模块
支持多种文件格式的内容提取

统一使用 extractor_manager 单例访问所有功能
"""
from .base_extractor import BaseExtractor
from .extractor_manager import (
    DocumentExtractorManager,
    extract_document_content,
    extract_document_from_file,
    is_supported_file
)

# 导出管理器单例（推荐使用）
extractor_manager = DocumentExtractorManager()

__all__ = [
    "BaseExtractor",
    "DocumentExtractorManager",
    "extractor_manager",
    "extract_document_content",
    "extract_document_from_file",
    "is_supported_file"
]

