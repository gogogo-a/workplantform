"""
会话模型
用于存储用户的对话会话信息
使用 Beanie ODM 映射到 MongoDB
"""
from datetime import datetime
from beanie import Document
from pydantic import Field
import uuid as uuid_module


class SessionModel(Document):
    """会话模型类 - 使用 Beanie ODM"""
    
    uuid: str = Field(
        default_factory=lambda: str(uuid_module.uuid4()),
        description="会话唯一ID"
    )
    user_id: str = Field(..., description="用户ID")
    create_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Settings:
        name = "session"  # MongoDB 集合名称

