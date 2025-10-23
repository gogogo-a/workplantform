"""
JWT Token 工具
用于生成和验证 JWT token
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pkg.constants.constants import SECRET_KEY


def create_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    生成 JWT Token
    
    Args:
        data: 要编码的数据（通常包含 user_id, username 等）
        expires_delta: 过期时间（默认 24 小时）
    
    Returns:
        str: JWT token
    
    Example:
        >>> token = create_token({"user_id": 1, "username": "zhangsan"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24*30)
    
    to_encode.update({"exp": expire})
    
    # 生成 token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证 JWT Token
    
    Args:
        token: JWT token
    
    Returns:
        Optional[Dict]: 解码后的数据，如果验证失败返回 None
    
    Example:
        >>> token = create_token({"user_id": 1})
        >>> payload = verify_token(token)
        >>> print(payload)
        {'user_id': 1, 'exp': 1234567890}
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Token 已过期
        return None
    except jwt.InvalidTokenError:
        # Token 无效
        return None


