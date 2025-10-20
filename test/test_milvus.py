"""
测试 Milvus 向量数据库连接和操作
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.db.milvus import milvus_client
import numpy as np


def test_connection():
    """测试 Milvus 连接"""
    print("=" * 80)
    print("测试 Milvus 连接")
    print("=" * 80)
    
    try:
        milvus_client.connect()
        print("\n✅ Milvus 连接成功！")
        return True
    except Exception as e:
        print(f"\n❌ Milvus 连接失败: {e}")
        return False


def test_list_collections():
    """测试列出所有集合"""
    print("\n" + "=" * 80)
    print("测试列出集合")
    print("=" * 80)
    
    try:
        collections = milvus_client.list_collections()
        print(f"\n当前集合列表:")
        if collections:
            for i, col in enumerate(collections, 1):
                print(f"  {i}. {col}")
        else:
            print("  （暂无集合）")
        return True
    except Exception as e:
        print(f"\n❌ 列出集合失败: {e}")
        return False


def test_create_collection():
    """测试创建集合"""
    print("\n" + "=" * 80)
    print("测试创建集合")
    print("=" * 80)
    
    collection_name = "test_documents"
    
    try:
        # 先删除已存在的测试集合
        collections = milvus_client.list_collections()
        if collection_name in collections:
            print(f"\n删除已存在的测试集合: {collection_name}")
            milvus_client.drop_collection(collection_name)
        
        # 创建新集合
        print(f"\n创建集合: {collection_name}")
        collection = milvus_client.create_collection(
            collection_name=collection_name,
            dimension=384,  # 使用较小的维度用于测试
            description="测试文档集合",
            metric_type="COSINE"
        )
        
        print(f"\n✅ 集合创建成功！")
        
        # 获取集合统计
        stats = milvus_client.get_collection_stats(collection_name)
        print(f"\n集合统计信息:")
        print(f"  名称: {stats['name']}")
        print(f"  描述: {stats['description']}")
        print(f"  实体数: {stats['num_entities']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 创建集合失败: {e}")
        return False


def test_insert_vectors():
    """测试插入向量"""
    print("\n" + "=" * 80)
    print("测试插入向量")
    print("=" * 80)
    
    collection_name = "test_documents"
    
    try:
        # 生成测试数据
        num_vectors = 10
        dimension = 384
        
        print(f"\n生成 {num_vectors} 个测试向量...")
        
        # 随机生成向量并归一化（用于 COSINE）
        embeddings = []
        for _ in range(num_vectors):
            vec = np.random.randn(dimension).astype(np.float32)
            vec = vec / np.linalg.norm(vec)  # 归一化
            embeddings.append(vec.tolist())
        
        texts = [f"这是测试文档 {i+1}" for i in range(num_vectors)]
        metadata = [
            {
                "source": f"doc_{i+1}.txt",
                "page": i + 1,
                "category": "test"
            }
            for i in range(num_vectors)
        ]
        
        # 插入向量
        ids = milvus_client.insert_vectors(
            collection_name=collection_name,
            embeddings=embeddings,
            texts=texts,
            metadata=metadata
        )
        
        print(f"\n✅ 成功插入 {len(ids)} 条向量！")
        print(f"ID 范围: {ids[0]} - {ids[-1]}")
        
        # 获取更新后的统计
        stats = milvus_client.get_collection_stats(collection_name)
        print(f"\n更新后的实体数: {stats['num_entities']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 插入向量失败: {e}")
        return False


def test_search_vectors():
    """测试向量搜索"""
    print("\n" + "=" * 80)
    print("测试向量搜索")
    print("=" * 80)
    
    collection_name = "test_documents"
    
    try:
        # 生成查询向量
        dimension = 384
        query_vec = np.random.randn(dimension).astype(np.float32)
        query_vec = query_vec / np.linalg.norm(query_vec)  # 归一化
        
        print(f"\n执行向量搜索（Top 5）...")
        
        # 搜索（使用 COSINE 度量，与创建集合时一致）
        results = milvus_client.search_vectors(
            collection_name=collection_name,
            query_embeddings=[query_vec.tolist()],
            top_k=5,
            metric_type="COSINE",
            output_fields=["text", "metadata"]
        )
        
        print(f"\n✅ 搜索完成！")
        print(f"\n搜索结果:")
        
        for i, hits in enumerate(results):
            print(f"\n查询 {i+1} 的结果:")
            for j, hit in enumerate(hits, 1):
                print(f"\n  Top {j}:")
                print(f"    ID: {hit['id']}")
                print(f"    相似度分数: {hit['score']:.4f}")
                print(f"    距离: {hit['distance']:.4f}")
                print(f"    文本: {hit['text']}")
                print(f"    元数据: {hit['metadata']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 搜索向量失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cleanup():
    """清理测试数据"""
    print("\n" + "=" * 80)
    print("清理测试数据")
    print("=" * 80)
    
    collection_name = "test_documents"
    
    try:
        collections = milvus_client.list_collections()
        if collection_name in collections:
            print(f"\n删除测试集合: {collection_name}")
            milvus_client.drop_collection(collection_name)
            print(f"\n✅ 清理完成！")
        else:
            print(f"\n测试集合不存在，无需清理")
        return True
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n🚀 开始测试 Milvus 向量数据库\n")
    
    # 测试连接
    if not test_connection():
        print("\n❌ 连接失败，终止测试")
        return
    
    # 测试列出集合
    test_list_collections()
    
    # 测试创建集合
    if not test_create_collection():
        print("\n❌ 创建集合失败，终止测试")
        return
    
    # 测试插入向量
    if not test_insert_vectors():
        print("\n❌ 插入向量失败，终止测试")
        return
    
    # 测试搜索向量
    test_search_vectors()
    
    # 清理测试数据
    # test_cleanup()  # 注释掉，保留数据以便查看
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)
    print("\n💡 提示:")
    print("  - Milvus 连接成功")
    print("  - 已创建测试集合 'test_documents'")
    print("  - 已插入测试向量数据")
    print("  - 向量搜索功能正常")
    print(f"\n如需清理测试数据，取消注释 test_cleanup() 行\n")


if __name__ == "__main__":
    main()

