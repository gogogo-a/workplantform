"""
统一响应格式控制
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """响应数据模型"""
    code: int
    message: str
    data: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": {"id": 1, "name": "示例"}
            }
        }


def json_response(
    message: str,
    ret: int = 0,
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """
    统一 JSON 响应格式
    
    Args:
        message: 响应消息
        ret: 返回码 (0: 成功, -1: 服务器错误, -2: 客户端错误)
        data: 响应数据（可选）
        status_code: HTTP 状态码（默认 200）
    
    Returns:
        JSONResponse: 格式化的 JSON 响应
    
    Examples:
        >>> # 成功响应（带数据）
        >>> return json_response("查询成功", ret=0, data={"user": "张三"})
        
        >>> # 成功响应（无数据）
        >>> return json_response("操作成功", ret=0)
        
        >>> # 客户端错误
        >>> return json_response("参数错误", ret=-2)
        
        >>> # 服务器错误
        >>> return json_response("服务器内部错误", ret=-1)
    """
    if ret == 0:
        # 成功响应
        if data is not None:
            response_data = {
                "code": 200,
                "message": message,
                "data": data
            }
        else:
            response_data = {
                "code": 200,
                "message": message
            }
        return JSONResponse(content=response_data, status_code=status_code)
    
    elif ret == -2:
        # 客户端错误（如参数错误、验证失败等）
        response_data = {
            "code": 400,
            "message": message
        }
        return JSONResponse(content=response_data, status_code=status_code)
    
    elif ret == -1:
        # 服务器错误
        response_data = {
            "code": 500,
            "message": message
        }
        return JSONResponse(content=response_data, status_code=status_code)
    
    else:
        # 未知错误码，默认为服务器错误
        response_data = {
            "code": 500,
            "message": f"未知错误码: {ret}"
        }
        return JSONResponse(content=response_data, status_code=500)


def success_response(message: str = "操作成功", data: Any = None) -> JSONResponse:
    """
    成功响应快捷方法
    
    Args:
        message: 响应消息
        data: 响应数据
    
    Returns:
        JSONResponse
    """
    return json_response(message=message, ret=0, data=data)


def error_response(message: str = "操作失败", error_type: str = "client") -> JSONResponse:
    """
    错误响应快捷方法
    
    Args:
        message: 错误消息
        error_type: 错误类型 ("client" 客户端错误 / "server" 服务器错误)
    
    Returns:
        JSONResponse
    """
    ret = -2 if error_type == "client" else -1
    return json_response(message=message, ret=ret)


def client_error_response(message: str = "请求参数错误") -> JSONResponse:
    """
    客户端错误响应快捷方法
    
    Args:
        message: 错误消息
    
    Returns:
        JSONResponse
    """
    return json_response(message=message, ret=-2)


def server_error_response(message: str = "服务器内部错误") -> JSONResponse:
    """
    服务器错误响应快捷方法
    
    Args:
        message: 错误消息
    
    Returns:
        JSONResponse
    """
    return json_response(message=message, ret=-1)


# 常用响应示例
class CommonResponses:
    """常用响应消息"""
    
    # 成功响应
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    QUERY_SUCCESS = "查询成功"
    
    # 客户端错误
    PARAM_ERROR = "参数错误"
    NOT_FOUND = "资源不存在"
    UNAUTHORIZED = "未授权"
    FORBIDDEN = "禁止访问"
    ALREADY_EXISTS = "资源已存在"
    VALIDATION_ERROR = "数据验证失败"
    
    # 服务器错误
    SERVER_ERROR = "服务器内部错误"
    DATABASE_ERROR = "数据库错误"
    NETWORK_ERROR = "网络错误"
    SERVICE_UNAVAILABLE = "服务不可用"


# 使用示例
"""
from api.v1.response_control import (
    json_response, 
    success_response, 
    client_error_response,
    server_error_response,
    CommonResponses
)

@app.get("/api/v1/user/{user_id}")
async def get_user(user_id: int):
    try:
        user = await get_user_from_db(user_id)
        if user:
            return success_response(
                message=CommonResponses.QUERY_SUCCESS,
                data=user
            )
        else:
            return client_error_response(
                message=CommonResponses.NOT_FOUND
            )
    except Exception as e:
        return server_error_response(
            message=f"{CommonResponses.DATABASE_ERROR}: {str(e)}"
        )
"""

