"""
无人系统云端 RAG 应用主程序
基于 FastAPI + LangChain + MongoDB + Milvus + Kafka + Redis
使用 Beanie ODM 进行 MongoDB 对象映射
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from internal.db.mongodb import init_mongodb, close_mongodb
from internal.db.milvus import milvus_client  # 直接导入全局单例实例
from internal.db.redis import redis_client  # 直接导入全局单例实例
from internal.http_sever.app import create_app
from log import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化所有连接，关闭时清理资源
    """
    logger.info("=" * 80)
    logger.info("🚀 RAG Platform 启动中...")
    logger.info("=" * 80)
    
    try:
        # ==================== 初始化 MongoDB ====================
        logger.info("📦 正在连接 MongoDB...")
        await init_mongodb()
        logger.info("✓ MongoDB 连接成功")
        
        # ==================== 初始化 Milvus ====================
        # 直接使用导入的全局单例实例，无需重新实例化
        logger.info("🔍 正在连接 Milvus...")
        milvus_client.connect()
        logger.info("✓ Milvus 连接成功")
        
        # ==================== 初始化 Redis ====================
        # 直接使用导入的全局单例实例，无需重新实例化
        logger.info("⚡ 正在连接 Redis...")
        redis_client.connect()
        if redis_client.ping():
            logger.info("✓ Redis 连接成功")
        else:
            logger.warning("⚠️  Redis 连接失败")
        
        logger.info("=" * 80)
        logger.info("✅ 所有服务启动完成")
        logger.info("=" * 80)
        logger.info("📡 API 服务地址: http://0.0.0.0:8000")
        logger.info("📚 API 文档地址: http://localhost:8000/docs")
        logger.info("=" * 80)
        
        yield  # 应用运行期间
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}", exc_info=True)
        raise
    
    finally:
        # ==================== 清理资源 ====================
        logger.info("=" * 80)
        logger.info("🛑 RAG Platform 关闭中...")
        logger.info("=" * 80)
        
        try:
            await close_mongodb()
            logger.info("✓ MongoDB 连接已关闭")
        except Exception as e:
            logger.error(f"关闭 MongoDB 失败: {e}")
        
        try:
            milvus_client.disconnect()
            logger.info("✓ Milvus 连接已关闭")
        except Exception as e:
            logger.error(f"关闭 Milvus 失败: {e}")
        
        logger.info("=" * 80)
        logger.info("👋 应用已关闭")
        logger.info("=" * 80)


# 创建应用实例
app = create_app()
app.router.lifespan_context = lifespan


if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
