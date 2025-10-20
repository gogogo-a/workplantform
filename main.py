"""
无人系统云端 RAG 应用主程序
基于 FastAPI + LangChain + MongoDB + Milvus + Kafka + Redis
使用 Beanie ODM 进行 MongoDB 对象映射
"""
import asyncio
from internal.db.mongodb import db


async def main():
    """主函数"""
    print("=" * 50)
    print("无人系统云端 RAG 应用启动中...")
    print("=" * 50)
    
    try:
        # 连接数据库并初始化 Beanie
        await db.connect_db()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
    finally:
        # 关闭数据库连接
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(main())
