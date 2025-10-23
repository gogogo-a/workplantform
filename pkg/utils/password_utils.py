"""
密码加密和验证工具
使用 bcrypt 进行安全的密码哈希
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    加密密码
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码哈希（字符串格式）
    
    Example:
        >>> hashed = hash_password("my_password")
        >>> print(hashed)
        '$2b$12$...'
    """
    # 将密码转为字节
    password_bytes = password.encode('utf-8')
    
    # 生成盐并哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # 返回字符串格式
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        password: 明文密码
        hashed_password: 加密后的密码哈希
        
    Returns:
        bool: 密码是否匹配
    
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    try:
        # 将密码和哈希转为字节
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # 验证密码
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"密码验证失败: {e}")
        return False

