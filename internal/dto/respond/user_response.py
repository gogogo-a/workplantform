"""
用户相关响应模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    uuid: str
    nickname: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[int] = None
    birthday: Optional[str] = None
    created_at: datetime
    is_admin: int = 0
    status: int = 0
    token: Optional[str] = None  # 登录/注册时返回
    
    class Config:
        from_attributes = True  # Pydantic v2

