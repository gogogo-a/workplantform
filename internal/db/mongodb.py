"""
MongoDB 数据库连接配置
使用 Beanie ODM 和 Motor 异步驱动
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from pkg.constants.constants import MONGODB_URL, MONGODB_DATABASE

class MongoDB:
    """MongoDB 配置类"""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """连接到 MongoDB 数据库"""
        from internal.model.document import DocumentModel
        from internal.model.message import MessageModel
        from internal.model.user_info import UserInfoModel
        
        # MongoDB 连接 URL
        url = MONGODB_URL
        database_name = MONGODB_DATABASE
        
        try:
            # 创建 Motor 客户端
            cls.client = AsyncIOMotorClient(url)
            
            # 测试连接
            await cls.client.admin.command('ping')
            print("✓ MongoDB 连接成功！")
            
            # 初始化 Beanie，注册所有文档模型
            await init_beanie(
                database=cls.client[database_name],
                document_models=[
                    DocumentModel,
                    MessageModel,
                    UserInfoModel
                ]
            )
            print(f"✓ Beanie ODM 初始化成功！")
            print(f"✓ 数据库: {database_name}")
            print(f"✓ 集合: documents, messages, users")
            
        except Exception as e:
            print(f"✗ MongoDB 连接失败: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """关闭数据库连接"""
        if cls.client:
            cls.client.close()
            print("MongoDB 连接已关闭")


# 全局数据库实例
db = MongoDB()
