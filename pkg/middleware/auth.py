"""
认证中间件
验证JWT Token并提取用户信息
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from pkg.utils.jwt_utils import verify_token
from log import logger


security = HTTPBearer()


# 不需要认证的路径白名单 (path, method) 或 path (所有方法)
# 格式: 
#   - 字符串: 精确匹配路径（任何HTTP方法）
#   - 元组 (path, method): 精确匹配路径和方法
AUTH_WHITELIST = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    ("/users", "POST"),        # 用户注册 (POST /users)
    ("/users/login", "POST"),   # 用户登录 (POST /users/login)
    ("/users/email-login", "POST"),  # 邮箱登录 (POST /users/email-login)
    ("/users/email-code", "POST"),   # 发送邮箱验证码 (POST /users/email-code)
]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT 认证中间件 - 全局应用"""
    
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"JWT中间件: 处理请求 {request.method} {request.url.path}")
        
        # OPTIONS 请求（CORS 预检）直接放行
        if request.method == "OPTIONS":
            logger.debug(f"JWT中间件: OPTIONS请求，跳过认证")
            return await call_next(request)
        
        # 检查是否在白名单中（精确匹配）
        path = request.url.path
        method = request.method
        is_whitelisted = False
        
        for whitelist_item in AUTH_WHITELIST:
            if isinstance(whitelist_item, tuple):
                # (path, method) 元组：精确匹配路径和方法
                whitelist_path, whitelist_method = whitelist_item
                if path == whitelist_path and method == whitelist_method:
                    is_whitelisted = True
                    logger.debug(f"JWT中间件: 匹配白名单 ({whitelist_path}, {whitelist_method})")
                    break
            else:
                # 字符串：精确匹配路径（任何方法）
                if path == whitelist_item:
                    is_whitelisted = True
                    logger.debug(f"JWT中间件: 匹配白名单 {whitelist_item}")
                    break
        
        logger.debug(f"JWT中间件: {method} {path} 在白名单中: {is_whitelisted}")
        
        if is_whitelisted:
            logger.debug(f"JWT中间件: 跳过认证（白名单）")
            return await call_next(request)
        
        # 验证 token
        logger.debug(f"JWT中间件: 开始验证token...")
        user = await get_current_user(request)
        
        if not user:
            # 如果没有有效token，返回401
            logger.warning(f"JWT中间件: 未授权访问 {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "code": -1,
                    "message": "未授权：请提供有效的认证Token"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 将用户信息存储到 request.state 中
        request.state.user = user
        admin_flag = "👑管理员" if user.get('is_admin') == 1 else ""
        logger.info(f"JWT中间件: 用户 {user.get('user_id')} ({user.get('nickname')}{admin_flag}) 访问 {request.url.path}")
        
        # 继续处理请求
        response = await call_next(request)
        return response


async def get_current_user(request: Request) -> Optional[dict]:
    """
    从请求中提取并验证JWT Token，返回用户信息
    
    Args:
        request: FastAPI Request对象
        
    Returns:
        dict: 用户信息 {"user_id": "xxx", "nickname": "xxx", "is_admin": 0/1}
        None: 如果没有token或token无效
    """
    try:
        # 从请求头获取Authorization
        authorization: str = request.headers.get("Authorization")
        
        if not authorization:
            logger.debug("未找到Authorization请求头")
            return None
        
        # 检查格式是否为 "Bearer <token>"
        if not authorization.startswith("Bearer "):
            logger.warning(f"Authorization格式错误: {authorization[:20]}...")
            return None
        
        # 提取token
        token = authorization.replace("Bearer ", "")
        logger.debug(f"提取到token: {token[:20]}...{token[-20:]}")
        
        # 验证token
        payload = verify_token(token)
        
        if payload:
            is_admin_text = "管理员" if payload.get('is_admin') == 1 else "普通用户"
            logger.debug(f"Token验证成功: user_id={payload.get('user_id')}, nickname={payload.get('nickname')}, 身份={is_admin_text}")
            return payload
        else:
            logger.warning("Token验证失败: verify_token返回None")
            return None
            
    except Exception as e:
        logger.error(f"Token解析异常: {e}", exc_info=True)
        return None


def get_user_from_request(request: Request) -> dict:
    """
    从request.state中获取用户信息（用于全局中间件模式）
    
    Args:
        request: FastAPI Request对象
        
    Returns:
        dict: 用户信息 {"user_id": "xxx", "nickname": "xxx", "is_admin": 0/1}
        
    Raises:
        HTTPException: 如果用户信息不存在
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权：用户信息不存在"
        )
    
    return request.state.user

