"""
用户信息模型
用于存储用户基本信息和权限
使用 Beanie ODM 映射到 MongoDB
"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class UserInfoModel(Document):
    """用户信息模型类 - 使用 Beanie ODM"""
    
    uuid: str = Field(..., description="用户唯一id")
    nickname: str = Field(..., description="昵称")
    email: Optional[str] = Field(None, description="邮箱")
    avatar: str = Field(
        default="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
        description="头像"
    )
    gender: Optional[int] = Field(None, description="性别，0.男，1.女")
    password: str = Field(..., description="密码")
    birthday: Optional[str] = Field(None, description="生日")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    is_admin: int = Field(default=0, description="是否是管理员，0.不是，1.是")
    status: int = Field(default=0, description="状态，0.正常，1.禁用")
    
    class Settings:
        name = "user_info"  # MongoDB 集合名称
