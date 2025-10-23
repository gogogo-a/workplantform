"""
用户相关请求模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class RegisterRequest(BaseModel):
    """注册请求"""
    nickname: str = Field(..., min_length=2, max_length=50, description="昵称")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    confirm_password: str = Field(..., min_length=6, description="确认密码")
    captcha: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")


class LoginRequest(BaseModel):
    """登录请求"""
    nickname: str = Field(..., description="昵称")
    password: str = Field(..., description="密码")


class EmailLoginRequest(BaseModel):
    """邮箱验证码登录请求"""
    email: EmailStr = Field(..., description="邮箱")
    captcha: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")


class GetUserInfoRequest(BaseModel):
    """获取用户信息请求"""
    uuid: str = Field(..., description="用户UUID")


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求"""
    uuid: str = Field(..., description="用户UUID")
    nickname: Optional[str] = Field(None, min_length=2, max_length=50, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: Optional[int] = Field(None, description="性别，0.男，1.女")
    birthday: Optional[str] = Field(None, description="生日")


class GetUserInfoListRequest(BaseModel):
    """获取用户列表请求"""
    owner_id: Optional[str] = Field(None, description="拥有者ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class AbleUsersRequest(BaseModel):
    """批量操作用户请求"""
    uuid_list: List[str] = Field(..., description="用户UUID列表")
    is_admin: Optional[bool] = Field(None, description="是否设置为管理员")


class SendEmailCodeRequest(BaseModel):
    """发送邮箱验证码请求"""
    email: EmailStr = Field(..., description="邮箱")

