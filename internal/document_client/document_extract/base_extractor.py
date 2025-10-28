"""
文档提取器基类
定义统一的文档提取接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import os
from log import logger


class BaseExtractor(ABC):
    """文档提取器基类"""
    
    def __init__(self):
        """初始化提取器"""
        self.supported_extensions = self.get_supported_extensions()
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 扩展名列表（小写，带点，如 ['.pdf', '.txt']）
        """
        pass
    
    @abstractmethod
    def extract_from_file(self, file_path: str) -> str:
        """
        从文件路径提取内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 提取的文本内容
        """
        pass
    
    def extract_from_bytes(self, file_bytes: bytes, filename: str) -> str:
        """
        从字节流提取内容（默认实现：创建临时文件）
        
        Args:
            file_bytes: 文件字节流
            filename: 文件名（用于确定扩展名）
            
        Returns:
            str: 提取的文本内容
        """
        # 获取文件扩展名
        extension = Path(filename).suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(
                f"不支持的文件类型: {extension}. "
                f"支持的类型: {self.supported_extensions}"
            )
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            # 从临时文件提取
            content = self.extract_from_file(tmp_path)
            return content
        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def can_handle(self, file_path_or_name: str) -> bool:
        """
        检查是否可以处理该文件
        
        Args:
            file_path_or_name: 文件路径或文件名
            
        Returns:
            bool: 是否支持
        """
        extension = Path(file_path_or_name).suffix.lower()
        return extension in self.supported_extensions
    
    def validate_file(self, file_path: str) -> None:
        """
        验证文件是否存在且格式支持
        
        Args:
            file_path: 文件路径
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not self.can_handle(file_path):
            raise ValueError(
                f"不支持的文件类型: {path.suffix}. "
                f"支持的类型: {self.supported_extensions}"
            )
    
    def get_name(self) -> str:
        """
        获取提取器名称
        
        Returns:
            str: 提取器名称
        """
        return self.__class__.__name__

