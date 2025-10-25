"""
文档模型
用于存储上传的文档信息
使用 Beanie ODM 映射到 MongoDB
"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
import uuid as uuid_module


class DocumentModel(Document):
    """文档模型类 - 使用 Beanie ODM"""
    
    uuid: str = Field(default_factory=lambda: str(uuid_module.uuid4()))
    name: str = Field(..., description="文档名称")
    content: str = Field(default="", description="文档内容")
    page: int = Field(default=0, description="文档页数")
    url: str = Field(..., description="文档URL")
    size: int = Field(..., description="文档大小(字节)")
    status: int = Field(default=0, description="文档状态")  # 0.未处理，1.处理中，2.处理完成，3.处理失败
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "documents"  # MongoDB 集合名称
