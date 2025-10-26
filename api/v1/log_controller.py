"""
日志查询 API 控制器
"""
from fastapi import APIRouter, Query, Request
from typing import Optional
from internal.service.json_load.log_sever import log_service
from api.v1.response_controller import json_response
from log import logger

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("/errors", summary="获取错误日志")
async def get_error_logs(
    request: Request,
    date: Optional[str] = Query(None, description="日期（格式：YYYY-MM-DD），不提供则返回今天的日志"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量（用于分页）")
):
    """
    获取错误日志
    
    **参数：**
    - **date**: 日期（格式：YYYY-MM-DD），可选，默认今天
    - **limit**: 返回的最大日志条数，默认 100
    - **offset**: 偏移量，用于分页，默认 0
    
    **返回：**
    ```json
    {
        "code": 200,
        "message": "成功",
        "data": {
            "date": "2025-10-26",
            "total": 150,
            "count": 100,
            "offset": 0,
            "logs": [
                {
                    "timestamp": "2025-10-26T10:30:45.123456",
                    "level": "ERROR",
                    "message": "错误信息",
                    "record": {...}
                }
            ]
        }
    }
    ```
    
    **示例：**
    ```bash
    # 获取今天的错误日志
    curl "http://localhost:8000/logs/errors"
    
    # 获取指定日期的错误日志
    curl "http://localhost:8000/logs/errors?date=2025-10-25"
    
    # 分页查询
    curl "http://localhost:8000/logs/errors?limit=50&offset=100"
    ```
    """
    try:
        logger.info(f"查询错误日志: date={date}, limit={limit}, offset={offset}")
        
        # 调用服务层
        result = log_service.get_error_logs(date, limit, offset)
        
        return json_response("成功", 0, result)
    
    except Exception as e:
        logger.error(f"获取错误日志失败: {e}", exc_info=True)
        return json_response(f"获取错误日志失败: {str(e)}", -1)


@router.get("/dates", summary="获取可用的日志日期")
async def get_available_log_dates(request: Request):
    """
    获取所有可用的日志日期
    
    **返回：**
    ```json
    {
        "code": 200,
        "message": "成功",
        "data": {
            "dates": [
                "2025-10-26",
                "2025-10-25",
                "2025-10-24"
            ]
        }
    }
    ```
    
    **示例：**
    ```bash
    curl "http://localhost:8000/logs/dates"
    ```
    """
    try:
        logger.info("查询可用的日志日期")
        
        dates = log_service.get_available_dates()
        
        return json_response("成功", 0, {"dates": dates})
    
    except Exception as e:
        logger.error(f"获取可用日期失败: {e}", exc_info=True)
        return json_response(f"获取可用日期失败: {str(e)}", -1)


@router.get("/statistics", summary="获取错误日志统计信息")
async def get_error_statistics(request: Request):
    """
    获取错误日志统计信息（总错误数、今日错误数、错误率、最近错误）
    
    **返回：**
    ```json
    {
        "code": 200,
        "message": "成功",
        "data": {
            "total_errors": 1523,
            "today_errors": 45,
            "error_rate": 2.95,
            "today_date": "2025-10-26",
            "recent_errors": [
                {
                    "timestamp": "2025-10-26T15:30:45.123456",
                    "level": "ERROR",
                    "message": "错误信息",
                    "record": {
                        "level": "ERROR",
                        "message": "详细错误信息",
                        "file": "module.py",
                        "line": 123,
                        "function": "function_name"
                    }
                }
            ],
            "available_dates": ["2025-10-26", "2025-10-25", "2025-10-24"],
            "error_level_stats": {
                "ERROR": 30,
                "CRITICAL": 10,
                "WARNING": 5
            },
            "error_hour_stats": {
                "10:00": 5,
                "11:00": 8,
                "12:00": 12
            }
        }
    }
    ```
    
    **字段说明：**
    - **total_errors**: 所有历史错误总数
    - **today_errors**: 今日错误数
    - **error_rate**: 错误率（今日错误数占总错误数的百分比）
    - **recent_errors**: 今日最新的10条错误
    - **today_date**: 今天的日期
    - **available_dates**: 所有可用的日志日期
    - **error_level_stats**: 今日错误级别分布
    - **error_hour_stats**: 今日错误时间分布（按小时）
    
    **示例：**
    ```bash
    # 获取错误统计信息
    curl "http://localhost:8000/logs/statistics"
    ```
    """
    try:
        logger.info("查询错误日志统计信息")
        
        stats = log_service.get_error_statistics()
        
        return json_response("成功", 0, stats)
    
    except Exception as e:
        logger.error(f"获取错误统计信息失败: {e}", exc_info=True)
        return json_response(f"获取错误统计信息失败: {str(e)}", -1)

