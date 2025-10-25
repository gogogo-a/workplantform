"""
请求模型 (RESTful 风格)
"""
from .user_request import (
    RegisterRequest,
    LoginRequest,
    EmailLoginRequest,
    UpdateUserInfoRequest,
    SendEmailCodeRequest,
    SetAdminRequest
)
from .session_request import (
    UpdateSessionRequest
)
from .message_request import (
    SendMessageRequest
)

__all__ = [
    'RegisterRequest',
    'LoginRequest',
    'EmailLoginRequest',
    'UpdateUserInfoRequest',
    'SendEmailCodeRequest',
    'SetAdminRequest',
    'UpdateSessionRequest',
    'SendMessageRequest'
]
