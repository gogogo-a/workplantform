"""
用户信息控制器
"""
from fastapi import APIRouter, HTTPException
from internal.dto.request import (
    RegisterRequest,
    LoginRequest,
    EmailLoginRequest,
    GetUserInfoRequest,
    UpdateUserInfoRequest,
    GetUserInfoListRequest,
    AbleUsersRequest,
    SendEmailCodeRequest
)
from internal.service.orm.user_info_sever import user_info_service
from api.v1.response_control import json_response
from log import logger

router = APIRouter(prefix="/api/v1/user", tags=["用户管理"])


@router.post("/register")
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


@router.post("/login")
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


@router.post("/email-login")
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


@router.post("/info")
async def get_user_info(req: GetUserInfoRequest):
    """获取用户信息"""
    try:
        logger.info(f"获取用户信息请求: {req.uuid}")
        message, user_info, ret = await user_info_service.get_user_info(req.uuid)
        
        if user_info:
            return json_response(message, ret, user_info.model_dump(mode='json'))
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取用户信息接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/update")
async def update_user_info(req: UpdateUserInfoRequest):
    """更新用户信息"""
    try:
        logger.info(f"更新用户信息请求: {req.uuid}")
        message, ret = await user_info_service.update_user_info(req)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"更新用户信息接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/list")
async def get_user_info_list(req: GetUserInfoListRequest):
    """获取用户列表"""
    try:
        logger.info(f"获取用户列表请求: page={req.page}, page_size={req.page_size}")
        message, user_list, ret = await user_info_service.get_user_info_list(
            req.owner_id, req.page, req.page_size
        )
        return json_response(message, ret, user_list)
        
    except Exception as e:
        logger.error(f"获取用户列表接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/delete")
async def delete_users(req: AbleUsersRequest):
    """批量删除用户"""
    try:
        logger.info(f"删除用户请求: {len(req.uuid_list)} 个")
        message, ret = await user_info_service.delete_users(req.uuid_list)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"删除用户接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/set-admin")
async def set_admin(req: AbleUsersRequest):
    """批量设置管理员"""
    try:
        logger.info(f"设置管理员请求: {len(req.uuid_list)} 个, is_admin={req.is_admin}")
        message, ret = await user_info_service.set_admin(req.uuid_list, req.is_admin)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"设置管理员接口异常: {str(e)}", exc_info=True)
        return json_response("系统错误", -1)


@router.post("/send-email-code")
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

