"""
测试 MongoDB 连接和 Beanie ODM - 创建测试数据
"""
import sys
import os
import asyncio
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.db.mongodb import db
from internal.model.document import DocumentModel
from internal.model.message import MessageModel
from internal.model.session import SessionModel
from internal.model.user_info import UserInfoModel
import uuid as uuid_module


async def create_test_data():
    """创建测试数据（已存在则跳过）"""
    print("=" * 80)
    print("📦 MongoDB 测试数据初始化")
    print("=" * 80)
    
    try:
        await db.connect_db()
        print("\n✅ MongoDB 连接成功")
        
        # 1. 创建用户数据
        print("\n1️⃣ 创建用户数据...")
        user_data = [
            {"uuid": "user_001", "nickname": "白总", "email": "baizong@example.com", "password": "admin123", "is_admin": 1},
            {"uuid": "user_002", "nickname": "测试用户", "email": "test@example.com", "password": "test123"},
            {"uuid": "user_003", "nickname": "访客", "email": "guest@example.com", "password": "guest123"},
        ]
        
        for data in user_data:
            existing = await UserInfoModel.find_one(UserInfoModel.uuid == data["uuid"])
            if existing:
                print(f"   ⏭️  用户已存在: {data['nickname']}")
            else:
                user = UserInfoModel(**data)
                await user.insert()
                print(f"   ✅ 创建用户: {data['nickname']} ({data['email']})")
        
        # 2. 创建会话数据
        print("\n2️⃣ 创建会话数据...")
        session_data = [
            {"uuid": "session_001", "user_id": "user_001"},
            {"uuid": "session_002", "user_id": "user_002"},
        ]
        
        for data in session_data:
            existing = await SessionModel.find_one(SessionModel.uuid == data["uuid"])
            if existing:
                print(f"   ⏭️  会话已存在: {data['uuid']}")
            else:
                session = SessionModel(**data)
                await session.insert()
                print(f"   ✅ 创建会话: {data['uuid']} (用户: {data['user_id']})")
        
        # 3. 创建消息数据
        print("\n3️⃣ 创建消息数据...")
        message_data = [
            {
                "uuid": str(uuid_module.uuid4()),
                "session_id": "session_001",
                "content": "你好，我想了解一下 RAG 技术",
                "send_id": "user_001",
                "send_name": "白总",
                "send_avatar": "https://example.com/avatar1.png",
                "receive_id": "system",
                "status": 1
            },
            {
                "uuid": str(uuid_module.uuid4()),
                "session_id": "session_001",
                "content": "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术",
                "send_id": "system",
                "send_name": "AI助手",
                "send_avatar": "https://example.com/ai.png",
                "receive_id": "user_001",
                "status": 1
            },
        ]
        
        for data in message_data:
            msg = MessageModel(**data)
            await msg.insert()
            print(f"   ✅ 创建消息: {data['content'][:20]}...")
        
        # 4. 创建文档数据
        print("\n4️⃣ 创建文档数据...")
        document_data = [
            {
                "uuid": str(uuid_module.uuid4()),
                "name": "RAG技术白皮书.pdf",
                "content": "检索增强生成（RAG）是一种结合了信息检索和文本生成的先进AI技术...",
                "page": 25,
                "url": "/uploads/rag_whitepaper.pdf",
                "size": 2048000
            },
            {
                "uuid": str(uuid_module.uuid4()),
                "name": "向量数据库指南.pdf",
                "content": "向量数据库是专门为存储和检索向量化数据设计的数据库系统...",
                "page": 18,
                "url": "/uploads/vector_db_guide.pdf",
                "size": 1536000
            },
        ]
        
        for data in document_data:
            doc = DocumentModel(**data)
            await doc.insert()
            print(f"   ✅ 创建文档: {data['name']} ({data['page']}页)")
        
        # 5. 统计数据
        print("\n5️⃣ 数据统计...")
        user_count = await UserInfoModel.count()
        session_count = await SessionModel.count()
        message_count = await MessageModel.count()
        doc_count = await DocumentModel.count()
        
        print(f"   📊 用户总数: {user_count}")
        print(f"   📊 会话总数: {session_count}")
        print(f"   📊 消息总数: {message_count}")
        print(f"   📊 文档总数: {doc_count}")
        
        print("\n" + "=" * 80)
        print("✅ 测试数据创建完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close_db()


def main():
    """主函数"""
    print("\n🚀 开始初始化 MongoDB 测试数据\n")
    asyncio.run(create_test_data())
    print("\n✨ 初始化完成！\n")


if __name__ == "__main__":
    main()

