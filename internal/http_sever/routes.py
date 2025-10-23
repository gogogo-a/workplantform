"""
路由表配置
类似 Gin 的路由注册方式
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.v1.user_info_controller import router as user_router
from log import logger


def setup_routes(app: FastAPI):
    """
    配置所有路由
    
    Args:
        app: FastAPI 应用实例
    """
    logger.info("正在注册路由...")
    
    # ==================== 静态文件 ====================
    # app.mount("/static/avatars", StaticFiles(directory="static/avatars"), name="avatars")
    # app.mount("/static/files", StaticFiles(directory="static/files"), name="files")
    
    # ==================== 用户相关路由 ====================
    app.include_router(user_router)
    
    # 可以继续添加其他路由
    # app.include_router(document_router)
    # app.include_router(chat_router)
    
    logger.info("✓ 路由注册完成")
    
    # 打印所有路由
    logger.info("已注册的路由:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            methods = ','.join(route.methods)
            logger.info(f"  {methods:20} {route.path}")

