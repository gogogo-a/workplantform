"""
请求模型
"""
from .user_request import (
    RegisterRequest,
    LoginRequest,
    EmailLoginRequest,
    GetUserInfoRequest,
    UpdateUserInfoRequest,
    GetUserInfoListRequest,
    AbleUsersRequest,
    SendEmailCodeRequest
)

__all__ = [
    'RegisterRequest',
    'LoginRequest',
    'EmailLoginRequest',
    'GetUserInfoRequest',
    'UpdateUserInfoRequest',
    'GetUserInfoListRequest',
    'AbleUsersRequest',
    'SendEmailCodeRequest'
]

