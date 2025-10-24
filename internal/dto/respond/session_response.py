"""
会话响应模型
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SessionResponse(BaseModel):
    """会话响应"""
    uuid: str = Field(..., description="会话UUID")
    user_id: str = Field(..., description="用户ID")
    name: str = Field(..., description="会话名称")
    last_message: str = Field(..., description="最后一条消息")
    create_at: datetime = Field(..., description="创建时间")
    update_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True  # Pydantic v2


class SessionListResponse(BaseModel):
    """会话列表响应"""
    total: int = Field(..., description="总会话数量")
    sessions: List[SessionResponse] = Field(..., description="会话列表")

