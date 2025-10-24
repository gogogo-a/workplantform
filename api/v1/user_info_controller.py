"""
用户信息控制器 (RESTful 风格)
"""
from fastapi import APIRouter, Query, Path
from internal.dto.request import (
    RegisterRequest,
    LoginRequest,
    EmailLoginRequest,
    UpdateUserInfoRequest,
    SendEmailCodeRequest
)
from internal.service.orm.user_info_sever import user_info_service
from api.v1.response_controller import json_response
from log import logger

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", summary="用户注册")
async def register(req: RegisterRequest):
    """
    用户注册
    
    需要提供: 昵称、邮箱、密码、确认密码、邮箱验证码
    """
    try:
        logger.info(f"用户注册请求: {req.nickname} - {req.email}")
        message, user_info, ret = await user_info_service.register(req)
        
        if user_info:
            return json_response(message, ret, user_info.model_dump(mode='json'))
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"注册接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/login", summary="用户登录")
async def login(req: LoginRequest):
    """
    用户登录（昵称+密码）
    
    需要提供: 昵称、密码
    """
    try:
        logger.info(f"用户登录请求: {req.nickname}")
        message, user_info, ret = await user_info_service.login(req)
        
        if user_info:
            return json_response(message, ret, user_info.model_dump(mode='json'))
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"登录接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/email-login", summary="邮箱验证码登录")
async def email_login(req: EmailLoginRequest):
    """
    邮箱验证码登录
    
    需要提供: 邮箱、验证码
    """
    try:
        logger.info(f"邮箱登录请求: {req.email}")
        message, user_info, ret = await user_info_service.email_login(req)
        
        if user_info:
            return json_response(message, ret, user_info.model_dump(mode='json'))
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"邮箱登录接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("", summary="获取用户列表")
async def get_user_list(
    owner_id: str = Query(default=None, description="拥有者ID"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量")
):
    """
    获取用户列表
    
    - **owner_id**: 拥有者ID（可选）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        logger.info(f"获取用户列表请求: page={page}, page_size={page_size}")
        message, user_list, ret = await user_info_service.get_user_info_list(
            owner_id, page, page_size
        )
        return json_response(message, ret, user_list)
        
    except Exception as e:
        logger.error(f"获取用户列表接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("/{user_id}", summary="获取用户详情")
async def get_user_info(
    user_id: str = Path(..., description="用户UUID")
):
    """
    获取用户详情
    
    - **user_id**: 用户UUID
    """
    try:
        logger.info(f"获取用户信息请求: {user_id}")
        message, user_info, ret = await user_info_service.get_user_info(user_id)
        
        if user_info:
            return json_response(message, ret, user_info.model_dump(mode='json'))
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取用户信息接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.patch("/{user_id}", summary="更新用户信息")
async def update_user_info(
    user_id: str = Path(..., description="用户UUID"),
    req: UpdateUserInfoRequest = None
):
    """
    更新用户信息
    
    - **user_id**: 用户UUID
    - **req**: 更新的用户信息
    """
    try:
        # 将路径参数的 user_id 设置到 req 中
        req.uuid = user_id
        logger.info(f"更新用户信息请求: {user_id}")
        message, ret = await user_info_service.update_user_info(req)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"更新用户信息接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: str = Path(..., description="用户UUID")
):
    """
    删除单个用户
    
    - **user_id**: 用户UUID
    """
    try:
        logger.info(f"删除用户请求: {user_id}")
        message, ret = await user_info_service.delete_users([user_id])
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"删除用户接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/email-code", summary="发送邮箱验证码")
async def send_email_code(req: SendEmailCodeRequest):
    """
    发送邮箱验证码
    
    需要提供: 邮箱
    """
    try:
        logger.info(f"发送验证码请求: {req.email}")
        message, ret = user_info_service.send_email_code(req.email)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"发送验证码接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)
