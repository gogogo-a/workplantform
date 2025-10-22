"""
消息模型
用于存储多轮对话的消息记录
使用 Beanie ODM 映射到 MongoDB
"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class MessageModel(Document):
    """消息模型类 - 使用 Beanie ODM"""
    
    uuid: str = Field(..., description="消息uuid")
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    send_id: str = Field(..., description="发送者uuid")
    send_name: str = Field(..., description="发送者昵称")
    send_avatar: str = Field(..., description="发送者头像")
    receive_id: str = Field(..., description="接受者uuid")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[str] = Field(None, description="文件大小")
    status: int = Field(..., description="状态，0.未发送，1.已发送")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    send_at: Optional[datetime] = Field(None, description="发送时间")
    
    class Settings:
        name = "message"  # MongoDB 集合名称
