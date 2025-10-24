"""
消息响应模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageResponse(BaseModel):
    """消息响应"""
    uuid: str = Field(..., description="消息UUID")
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    send_type: int = Field(..., description="发送者类型，0.用户，1.AI，2.系统")
    send_id: str = Field(..., description="发送者UUID")
    send_name: str = Field(..., description="发送者昵称")
    send_avatar: str = Field(..., description="发送者头像")
    receive_id: str = Field(..., description="接受者UUID")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[str] = Field(None, description="文件大小")
    status: int = Field(..., description="状态，0.未发送，1.已发送")
    created_at: datetime = Field(..., description="创建时间")
    send_at: Optional[datetime] = Field(None, description="发送时间")
    
    class Config:
        from_attributes = True  # Pydantic v2


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    user_message: MessageResponse = Field(..., description="用户消息")
    ai_message: Optional[MessageResponse] = Field(None, description="AI回复消息")
    session_id: str = Field(..., description="会话ID")
    session_name: str = Field(..., description="会话名称")


class MessageListResponse(BaseModel):
    """消息列表响应"""
    total: int = Field(..., description="总消息数量")
    messages: List[MessageResponse] = Field(..., description="消息列表")

