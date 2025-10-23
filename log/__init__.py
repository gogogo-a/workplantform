"""
日志模块

强大的日志系统，基于 loguru：
- JSON 格式记录
- 自动记录调用位置
- 双输出（控制台 + 文件）
- 自动日志轮转
- 结构化字段
- 多级别日志

使用示例：
    from log import logger
    
    logger.info("用户登录", user_id=123)
    logger.error("操作失败", error="数据库连接失败")
    
    # 带上下文
    request_logger = logger.with_context(request_id="abc")
    request_logger.info("处理请求")
"""

from .logger import (
    logger,
    debug,
    info,
    warning,
    warn,
    error,
    fatal,
    critical,
    exception
)

__all__ = [
    "logger",
    "debug",
    "info",
    "warning",
    "warn",
    "error",
    "fatal",
    "critical",
    "exception"
]

