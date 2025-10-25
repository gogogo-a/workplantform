"""
用户相关请求模型 (RESTful 风格)
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """注册请求 - POST /users"""
    nickname: str = Field(..., min_length=2, max_length=50, description="昵称")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    confirm_password: str = Field(..., min_length=6, description="确认密码")
    captcha: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")


class LoginRequest(BaseModel):
    """登录请求 - POST /users/login"""
    nickname: str = Field(..., description="昵称")
    password: str = Field(..., description="密码")


class EmailLoginRequest(BaseModel):
    """邮箱验证码登录请求 - POST /users/email-login"""
    email: EmailStr = Field(..., description="邮箱")
    captcha: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求 - PATCH /users/{id}"""
    uuid: str = Field(..., description="用户UUID")
    nickname: Optional[str] = Field(None, min_length=2, max_length=50, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: Optional[int] = Field(None, description="性别，0.男，1.女")
    birthday: Optional[str] = Field(None, description="生日")


class SendEmailCodeRequest(BaseModel):
    """发送邮箱验证码请求 - POST /users/email-code"""
    email: EmailStr = Field(..., description="邮箱")


class SetAdminRequest(BaseModel):
    """设置管理员请求 - PATCH /users/set-admin"""
    user_id: str = Field(..., description="用户UUID")
    is_admin: bool = Field(..., description="是否为管理员，true:设置为管理员，false:取消管理员")
