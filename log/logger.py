"""
强大的日志单例对象

特性：
1. JSON 格式记录
2. 自动记录调用位置（func, file, line）
3. 双输出（控制台 + 文件）
4. 自动日志轮转
5. 结构化字段
6. 多级别日志（Debug, Info, Warn, Error, Fatal）
7. 调用栈回溯

使用示例：
    from log.logger import logger
    
    logger.debug("开发调试信息")
    logger.info("用户登录成功", user_id=123)
    logger.warning("Redis 连接缓慢", latency_ms=500)
    logger.error("用户不存在", user_id=999)
    logger.fatal("配置文件加载失败")  # 会退出程序
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from loguru import logger as _logger


class Logger:
    """日志单例类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志配置（只执行一次）"""
        if self._initialized:
            return
        
        # 移除默认的 handler
        _logger.remove()
        
        # 获取项目根目录的 json_log 文件夹
        project_root = Path(__file__).parent.parent
        log_base_dir = project_root / "json_log"
        log_base_dir.mkdir(exist_ok=True)
        
        # ==================== 控制台输出配置 ====================
        # 彩色、易读的格式（开发调试用）
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        _logger.add(
            sys.stderr,
            format=console_format,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # ==================== 文件输出配置（JSON 格式）====================
        
        # 使用 serialize=True，loguru 会自动将 record 转换为 JSON
        # NDJSON 格式：每行一个 JSON 对象（Newline Delimited JSON）
        
        # 所有级别的日志
        # 路径格式：json_log/25_10_23_log/app.json
        _logger.add(
            str(log_base_dir / "{time:YY_MM_DD_log}" / "app.json"),
            format="{message}",  # 简单格式，实际内容由序列化处理
            level="DEBUG",
            rotation="00:00",  # 每天午夜轮转
            retention="30 days",  # 保留 30 天
            compression="zip",  # 压缩旧日志为 app.json.zip
            encoding="utf-8",
            serialize=True,  # 自动 JSON 序列化（NDJSON 格式）
            backtrace=True,
            diagnose=True,
            enqueue=True  # 异步写入，避免阻塞
        )
        
        # Error 及以上级别单独记录
        # 路径格式：json_log/25_10_23_log/error.json
        _logger.add(
            str(log_base_dir / "{time:YY_MM_DD_log}" / "error.json"),
            format="{message}",
            level="ERROR",
            rotation="00:00",
            retention="90 days",  # 错误日志保留更久
            compression="zip",  # 压缩旧日志为 error.json.zip
            encoding="utf-8",
            serialize=True,  # 自动 JSON 序列化（NDJSON 格式）
            backtrace=True,
            diagnose=True,
            enqueue=True
        )
        
        self._initialized = True
        self._logger = _logger
        
        # 记录日志系统启动
        self._logger.info("日志系统已初始化", log_dir=str(log_base_dir))
    
    def _add_context(self, **kwargs):
        """添加上下文信息到日志"""
        return self._logger.bind(**kwargs)
    
    def debug(self, msg: str, **kwargs):
        """Debug 级别 - 开发调试"""
        self._logger.bind(**kwargs).debug(msg)
    
    def info(self, msg: str, **kwargs):
        """Info 级别 - 普通信息"""
        self._logger.bind(**kwargs).info(msg)
    
    def warning(self, msg: str, **kwargs):
        """Warning 级别 - 警告（非致命）"""
        self._logger.bind(**kwargs).warning(msg)
    
    def warn(self, msg: str, **kwargs):
        """warning 的别名"""
        self.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        """Error 级别 - 错误（业务/系统）"""
        self._logger.bind(**kwargs).error(msg)
    
    def fatal(self, msg: str, **kwargs):
        """Fatal 级别 - 致命错误（会退出程序）"""
        self._logger.bind(**kwargs).critical(msg)
        sys.exit(1)
    
    def critical(self, msg: str, **kwargs):
        """Critical 级别 - 严重错误（不退出程序）"""
        self._logger.bind(**kwargs).critical(msg)
    
    def exception(self, msg: str, **kwargs):
        """
        记录异常信息（自动捕获调用栈）
        
        示例:
            try:
                risky_operation()
            except Exception as e:
                logger.exception("操作失败", operation="risky_operation")
        """
        self._logger.bind(**kwargs).exception(msg)
    
    def with_context(self, **kwargs):
        """
        创建带上下文的日志记录器
        
        示例:
            request_logger = logger.with_context(request_id="abc123", user_id=456)
            request_logger.info("处理请求")
            request_logger.error("请求失败")
        """
        return self._logger.bind(**kwargs)
    
    @property
    def raw(self):
        """获取原始 loguru logger 对象（用于高级用法）"""
        return self._logger


# ==================== 创建全局单例对象 ====================
logger = Logger()


# ==================== 便捷函数（可选）====================
def debug(msg: str, **kwargs):
    """快捷函数：Debug 日志"""
    logger.debug(msg, **kwargs)


def info(msg: str, **kwargs):
    """快捷函数：Info 日志"""
    logger.info(msg, **kwargs)


def warning(msg: str, **kwargs):
    """快捷函数：Warning 日志"""
    logger.warning(msg, **kwargs)


def warn(msg: str, **kwargs):
    """快捷函数：Warn 日志"""
    logger.warn(msg, **kwargs)


def error(msg: str, **kwargs):
    """快捷函数：Error 日志"""
    logger.error(msg, **kwargs)


def fatal(msg: str, **kwargs):
    """快捷函数：Fatal 日志（会退出程序）"""
    logger.fatal(msg, **kwargs)


def critical(msg: str, **kwargs):
    """快捷函数：Critical 日志"""
    logger.critical(msg, **kwargs)


def exception(msg: str, **kwargs):
    """快捷函数：Exception 日志"""
    logger.exception(msg, **kwargs)


# ==================== 示例用法 ====================
if __name__ == "__main__":
    # 基础日志
    logger.debug("这是调试信息")
    logger.info("用户登录成功", user_id=123, username="test")
    logger.warning("Redis 连接缓慢", latency_ms=500, host="localhost")
    logger.error("用户不存在", user_id=999)
    
    # 带上下文的日志
    request_logger = logger.with_context(request_id="abc123", ip="192.168.1.1")
    request_logger.info("开始处理请求")
    request_logger.info("请求处理完成", duration_ms=150)
    
    # 异常日志
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("除零错误", operation="division")
    
    # Fatal 日志（注释掉，因为会退出程序）
    # logger.fatal("配置文件加载失败", config_path="/etc/app.conf")
    
    print("\n✓ 日志示例已记录，请查看 log/ 目录")

