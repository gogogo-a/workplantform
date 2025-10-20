"""
测试 MongoDB 连接和 Beanie ODM
"""
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.db.mongodb import db
from internal.model.document import DocumentModel
from internal.model.message import MessageModel
from internal.model.user_info import UserInfoModel
import uuid as uuid_module


async def test_mongodb_connection():
    """测试 MongoDB 连接"""
    print("=" * 60)
    print("测试 MongoDB 连接和 Beanie ODM")
    print("=" * 60)
    
    try:
        # 1. 连接数据库
        print("\n1️⃣ 连接 MongoDB...")
        await db.connect_db()
        
        # 2. 测试文档模型 - 创建
        print("\n2️⃣ 测试文档模型 (DocumentModel)...")
        doc = DocumentModel(
            uuid=str(uuid_module.uuid4()),
            name="测试文档.pdf",
            content="这是一个测试文档的内容，用于验证 MongoDB 和 Beanie ODM 是否正常工作。",
            page=10,
            url="/uploads/test_doc.pdf",
            size=1024000
        )
        await doc.insert()
        print(f"   ✓ 文档已创建，ID: {doc.id}, UUID: {doc.uuid}")
        
        # 3. 测试文档模型 - 查询
        print("\n3️⃣ 查询文档...")
        found_doc = await DocumentModel.find_one(DocumentModel.uuid == doc.uuid)
        if found_doc:
            print(f"   ✓ 找到文档: {found_doc.name} (页数: {found_doc.page})")
        
        # 4. 测试消息模型
        print("\n4️⃣ 测试消息模型 (MessageModel)...")
        msg = MessageModel(
            uuid=str(uuid_module.uuid4()),
            content="你好，这是一条测试消息",
            send_id="user_001",
            send_name="测试用户",
            send_avatar="https://example.com/avatar.png",
            receive_id="user_002",
            status=1
        )
        await msg.insert()
        print(f"   ✓ 消息已创建，ID: {msg.id}")
        
        # 5. 测试用户模型
        print("\n5️⃣ 测试用户模型 (UserInfoModel)...")
        user = UserInfoModel(
            uuid=str(uuid_module.uuid4()),
            nickname="测试用户",
            email="test@example.com",
            password="test123456",
            is_admin=0,
            status=0
        )
        await user.insert()
        print(f"   ✓ 用户已创建，ID: {user.id}, 昵称: {user.nickname}")
        
        # 6. 查询所有数据
        print("\n6️⃣ 统计数据...")
        doc_count = await DocumentModel.count()
        msg_count = await MessageModel.count()
        user_count = await UserInfoModel.count()
        print(f"   ✓ 文档总数: {doc_count}")
        print(f"   ✓ 消息总数: {msg_count}")
        print(f"   ✓ 用户总数: {user_count}")
        
        # 7. 更新测试
        print("\n7️⃣ 测试更新操作...")
        found_doc.page = 15
        await found_doc.save()
        updated_doc = await DocumentModel.get(found_doc.id)
        print(f"   ✓ 文档页数已更新: {doc.page} -> {updated_doc.page}")
        
        # 8. 删除测试
        print("\n8️⃣ 测试删除操作...")
        await doc.delete()
        await msg.delete()
        await user.delete()
        print("   ✓ 测试数据已清理")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！MongoDB 和 Beanie ODM 工作正常")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await db.close_db()


async def test_query_operations():
    """测试查询操作"""
    print("\n" + "=" * 60)
    print("测试高级查询操作")
    print("=" * 60)
    
    try:
        await db.connect_db()
        
        # 创建测试数据
        print("\n1️⃣ 创建测试数据...")
        users = []
        for i in range(5):
            user = UserInfoModel(
                uuid=f"test_user_{i}",
                nickname=f"用户{i}",
                email=f"user{i}@test.com",
                password="password123",
                is_admin=1 if i == 0 else 0,
                status=0
            )
            await user.insert()
            users.append(user)
        print(f"   ✓ 创建了 {len(users)} 个用户")
        
        # 条件查询
        print("\n2️⃣ 条件查询...")
        admin_users = await UserInfoModel.find(UserInfoModel.is_admin == 1).to_list()
        print(f"   ✓ 找到 {len(admin_users)} 个管理员")
        
        # 查找特定用户
        print("\n3️⃣ 查找特定用户...")
        user_0 = await UserInfoModel.find_one(UserInfoModel.nickname == "用户0")
        if user_0:
            print(f"   ✓ 找到用户: {user_0.nickname} ({user_0.email})")
        
        # 排序查询
        print("\n4️⃣ 排序查询...")
        sorted_users = await UserInfoModel.find_all().sort(
            -UserInfoModel.created_at
        ).to_list()
        print(f"   ✓ 按创建时间倒序: 第一个用户是 {sorted_users[0].nickname}")
        
        # 清理测试数据
        print("\n5️⃣ 清理测试数据...")
        for user in users:
            await user.delete()
        print("   ✓ 测试数据已清理")
        
        print("\n" + "=" * 60)
        print("✅ 查询操作测试通过")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 查询测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close_db()


def main():
    """主函数"""
    print("\n🚀 开始 MongoDB 测试\n")
    
    # 运行基础测试
    asyncio.run(test_mongodb_connection())
    
    # 运行查询测试
    asyncio.run(test_query_operations())
    
    print("\n✅ 所有测试完成！\n")


if __name__ == "__main__":
    main()

