"""
文档响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentMetadata(BaseModel):
    """文档元数据"""
    uuid: str = Field(..., description="文档UUID")
    name: str = Field(..., description="文档名称")
    uploaded_at: datetime = Field(..., description="上传时间")
    chunk_count: int = Field(default=0, description="文本块数量")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentDetailResponse(BaseModel):
    """文档详情响应"""
    uuid: str = Field(..., description="文档UUID")
    name: str = Field(..., description="文档名称")
    size: int = Field(..., description="文件大小(字节)")
    page: int = Field(default=0, description="文档页数")
    url: str = Field(..., description="文档访问URL")
    uploaded_at: datetime = Field(..., description="上传时间")
    chunk_count: int = Field(default=0, description="文本块数量")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total: int = Field(..., description="文档总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    documents: List[DocumentMetadata] = Field(..., description="文档列表")


class UploadDocumentResponse(BaseModel):
    """上传文档响应"""
    uuid: str = Field(..., description="文档UUID")
    name: str = Field(..., description="文档名称")
    status: str = Field(default="processing", description="处理状态: processing/completed/failed")
    message: str = Field(default="文档已提交处理", description="提示信息")

