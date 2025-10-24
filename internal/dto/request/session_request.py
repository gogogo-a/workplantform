"""
会话相关请求模型 (RESTful 风格)
"""
from pydantic import BaseModel, Field
from typing import Optional


class UpdateSessionRequest(BaseModel):
    """更新会话请求 - PATCH /sessions/{id}"""
    uuid: str = Field(..., description="会话UUID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="会话名称")
    last_message: Optional[str] = Field(None, description="最后一条消息")

