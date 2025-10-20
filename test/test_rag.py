"""
测试 RAG 完整流程
包括文档处理、向量化、存储、检索
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.rag.rag_service import rag_service
from internal.embedding.embedding_service import embedding_service
from internal.document.document_processor import document_processor


def test_embedding_service():
    """测试 Embedding 服务"""
    print("=" * 80)
    print("测试 Embedding 服务")
    print("=" * 80)
    
    try:
        # 加载模型
        print("\n加载 Embedding 模型...")
        embedding_service.load_model()
        
        # 获取模型信息
        info = embedding_service.get_model_info()
        print(f"\n模型信息:")
        print(f"  名称: {info['model_name']}")
        print(f"  路径: {info['model_path']}")
        print(f"  维度: {info['dimension']}")
        print(f"  最大长度: {info['max_length']}")
        print(f"  设备: {info['device']}")
        
        # 测试编码
        test_texts = [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的核心技术",
            "深度学习推动了AI的快速发展"
        ]
        
        print(f"\n测试文本编码...")
        embeddings = embedding_service.encode_documents(
            documents=test_texts,
            normalize=True,
            show_progress=False
        )
        
        print(f"✓ 编码完成")
        print(f"  文本数: {len(test_texts)}")
        print(f"  向量形状: {embeddings.shape}")
        print(f"  向量维度: {embeddings.shape[1]}")
        
        # 测试查询编码
        query = "什么是人工智能？"
        print(f"\n测试查询编码: {query}")
        query_embedding = embedding_service.encode_query(query)
        print(f"✓ 查询向量形状: {query_embedding.shape}")
        
        print("\n✅ Embedding 服务测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Embedding 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_processor():
    """测试文档处理"""
    print("\n" + "=" * 80)
    print("测试文档处理")
    print("=" * 80)
    
    try:
        # 创建测试文本文件
        test_file = os.path.join(project_root, "test_document.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""人工智能简介

人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。

机器学习是人工智能的核心技术之一。通过让计算机从数据中学习规律，
机器学习使得计算机能够在没有明确编程的情况下完成特定任务。

深度学习是机器学习的一个分支，它基于人工神经网络。近年来，
深度学习在图像识别、语音识别、自然语言处理等领域取得了突破性进展，
极大地推动了人工智能的发展。

应用领域包括：
1. 计算机视觉：图像识别、目标检测、人脸识别
2. 自然语言处理：机器翻译、文本生成、情感分析
3. 语音识别：语音转文字、语音助手
4. 推荐系统：个性化推荐、内容筛选

未来展望：人工智能将继续在各个领域发挥重要作用，
推动社会进步和科技发展。""")
        
        print(f"\n处理文档: {test_file}")
        
        # 处理文档
        chunks = document_processor.process_document(test_file)
        
        print(f"\n✓ 文档处理完成")
        print(f"  文本块数: {len(chunks)}")
        
        # 显示前几个块
        print(f"\n前 3 个文本块:")
        for i, chunk in enumerate(chunks[:3], 1):
            content = chunk["content"][:100] + "..." if len(chunk["content"]) > 100 else chunk["content"]
            print(f"\n  块 {i}:")
            print(f"    长度: {len(chunk['content'])} 字符")
            print(f"    内容: {content}")
        
        # 统计信息
        stats = document_processor.get_stats(chunks)
        print(f"\n文档统计:")
        print(f"  总块数: {stats['total_chunks']}")
        print(f"  平均大小: {stats['avg_chunk_size']:.0f} 字符")
        print(f"  最小块: {stats['min_chunk_size']} 字符")
        print(f"  最大块: {stats['max_chunk_size']} 字符")
        
        # 清理测试文件
        os.remove(test_file)
        
        print("\n✅ 文档处理测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 文档处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_service():
    """测试完整 RAG 服务"""
    print("\n" + "=" * 80)
    print("测试 RAG 服务")
    print("=" * 80)
    
    try:
        # 初始化 RAG 服务
        print("\n初始化 RAG 服务...")
        rag_service.initialize()
        
        # 创建多个测试文档
        test_files = []
        
        # 文档 1: AI 基础
        doc1 = os.path.join(project_root, "test_ai_basics.txt")
        with open(doc1, "w", encoding="utf-8") as f:
            f.write("""人工智能基础知识

人工智能（AI）的定义：
人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。

AI 的三个层次：
1. 弱人工智能（ANI）：擅长于单个方面的人工智能，如语音识别、图像识别
2. 强人工智能（AGI）：在各方面都能和人类媲美的人工智能
3. 超人工智能（ASI）：在所有领域都比人类强的人工智能

核心技术包括机器学习、深度学习、自然语言处理、计算机视觉等。""")
        test_files.append(doc1)
        
        # 文档 2: 机器学习
        doc2 = os.path.join(project_root, "test_ml.txt")
        with open(doc2, "w", encoding="utf-8") as f:
            f.write("""机器学习详解

机器学习的定义：
机器学习是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。

机器学习的分类：
1. 监督学习：从标注数据中学习预测模型
   - 分类问题：预测离散的类别标签
   - 回归问题：预测连续的数值
   
2. 无监督学习：从无标注数据中学习数据的内在结构
   - 聚类：将相似的数据分组
   - 降维：减少数据的特征数量
   
3. 强化学习：通过与环境交互来学习最优策略

常用算法包括线性回归、逻辑回归、决策树、随机森林、支持向量机、神经网络等。""")
        test_files.append(doc2)
        
        # 文档 3: FastAPI
        doc3 = os.path.join(project_root, "test_fastapi.txt")
        with open(doc3, "w", encoding="utf-8") as f:
            f.write("""FastAPI 框架介绍

FastAPI 是什么：
FastAPI 是一个用于构建 API 的现代、快速（高性能）的 web 框架，
使用 Python 3.6+ 并基于标准的 Python 类型提示。

主要特点：
1. 快速：可与 NodeJS 和 Go 比肩的极高性能
2. 高效：提高开发速度约 200% 至 300%
3. 更少的错误：减少约 40% 的人为错误
4. 智能：极佳的编辑器支持，自动补全
5. 简单：设计的易于使用和学习
6. 简短：减少代码重复
7. 健壮：生产可用级别的代码，自动生成交互式文档

核心依赖：
- Starlette：负责 web 部分
- Pydantic：负责数据部分
- Uvicorn：ASGI 服务器

适用场景：构建 RESTful API、微服务、后端服务等。""")
        test_files.append(doc3)
        
        print(f"\n添加 {len(test_files)} 个测试文档到 RAG 系统...")
        
        # 添加文档
        result = rag_service.add_documents(test_files)
        
        print(f"\n✓ 文档添加完成")
        print(f"  总文档数: {result['total_documents']}")
        print(f"  总文本块数: {result['total_chunks']}")
        print(f"  总向量数: {result['total_vectors']}")
        print(f"  向量维度: {result['dimension']}")
        
        # 测试搜索 - 使用更有对比性的查询
        test_queries = [
            {
                "query": "FastAPI 框架的主要特点是什么？",
                "expected": "test_fastapi.txt",
                "description": "精确查询测试（期望返回 FastAPI 文档）"
            },
            {
                "query": "如何进行机器学习分类？",
                "expected": "test_ml.txt", 
                "description": "语义查询测试（期望返回机器学习文档）"
            }
        ]
        
        print(f"\n" + "=" * 80)
        print("测试向量检索 vs Reranker 对比")
        print("=" * 80)
        
        for test_case in test_queries:
            query = test_case["query"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            print(f"\n{'='*80}")
            print(f"📝 测试用例: {description}")
            print(f"🔍 查询: {query}")
            print(f"🎯 期望来源: {expected}")
            print(f"{'='*80}")
            
            # 1. 不使用 Reranker（获取更多候选）
            print(f"\n{'─'*80}")
            print("📊 阶段 1: 向量检索（召回 Top 9 候选文档）")
            print(f"{'─'*80}")
            
            results_vector_only = rag_service.search(query, top_k=9, use_reranker=False)
            
            print(f"\n向量检索结果:")
            print(f"{'序号':<6} {'来源':<25} {'向量分数':<12} {'内容预览'}")
            print("-" * 80)
            
            for i, result in enumerate(results_vector_only, 1):
                filename = result['metadata'].get('filename', '未知')[:23]
                score = result['vector_score']
                content = result['text'][:40].replace('\n', ' ') + "..."
                
                # 标记是否是期望文档
                marker = "✓" if expected in filename else " "
                print(f"{marker} #{i:<4} {filename:<25} {score:<12.4f} {content}")
            
            # 2. 使用 Reranker（重排序 Top 3）
            print(f"\n{'─'*80}")
            print("🔥 阶段 2: Reranker 重排序（精选 Top 3）")
            print(f"{'─'*80}")
            
            results_with_rerank = rag_service.search(query, top_k=3, use_reranker=True)
            
            print(f"\nReranker 重排序结果:")
            print(f"{'序号':<6} {'来源':<25} {'Rerank分数':<14} {'向量分数':<12} {'排名变化'}")
            print("-" * 90)
            
            for i, result in enumerate(results_with_rerank, 1):
                filename = result['metadata'].get('filename', '未知')[:23]
                rerank_score = result.get('rerank_score', 0)
                vector_score = result['vector_score']
                
                # 找到原始排名
                original_rank = None
                for j, orig in enumerate(results_vector_only, 1):
                    if orig['id'] == result['id']:
                        original_rank = j
                        break
                
                rank_change = ""
                if original_rank:
                    if original_rank == i:
                        rank_change = "保持"
                    elif original_rank > i:
                        rank_change = f"↑ 上升 {original_rank - i} 位"
                    else:
                        rank_change = f"↓ 下降 {i - original_rank} 位"
                
                # 标记是否是期望文档
                marker = "✓" if expected in filename else " "
                print(f"{marker} #{i:<4} {filename:<25} {rerank_score:<14.4f} {vector_score:<12.4f} {rank_change}")
            
            # 3. 对比分析
            print(f"\n{'─'*80}")
            print("📈 效果对比分析")
            print(f"{'─'*80}")
            
            # 检查 Top 1 是否正确
            top1_vector = results_vector_only[0]['metadata'].get('filename', '')
            top1_rerank = results_with_rerank[0]['metadata'].get('filename', '')
            
            vector_correct = expected in top1_vector
            rerank_correct = expected in top1_rerank
            
            print(f"\nTop 1 结果:")
            print(f"  向量检索: {top1_vector:<30} {'✓ 正确' if vector_correct else '✗ 错误'}")
            print(f"  Reranker:  {top1_rerank:<30} {'✓ 正确' if rerank_correct else '✗ 错误'}")
            
            if rerank_correct and not vector_correct:
                print(f"\n  💡 Reranker 成功纠正了向量检索的排序！")
            elif rerank_correct and vector_correct:
                print(f"\n  ✓ 两种方法都返回了正确结果")
            
            # 显示被淘汰的文档
            vector_ids = {r['id'] for r in results_vector_only[:3]}
            rerank_ids = {r['id'] for r in results_with_rerank}
            eliminated = vector_ids - rerank_ids
            
            if eliminated:
                print(f"\n  🚫 被 Reranker 淘汰的低质量文档:")
                for result in results_vector_only[:3]:
                    if result['id'] in eliminated:
                        filename = result['metadata'].get('filename', '未知')
                        print(f"     - {filename} (向量分数: {result['vector_score']:.4f})")
            
            print()
        
        # 测试获取上下文
        print(f"\n" + "=" * 80)
        print("测试生成 LLM 上下文")
        print("=" * 80)
        
        query = "介绍一下机器学习的分类"
        print(f"\n查询: {query}")
        
        context = rag_service.get_context_for_query(query, top_k=3, max_context_length=1000)
        print(f"\n生成的上下文 ({len(context)} 字符):")
        print("-" * 80)
        print(context)
        
        # 获取统计信息
        print(f"\n" + "=" * 80)
        print("集合统计信息")
        print("=" * 80)
        
        stats = rag_service.get_collection_stats()
        print(f"\n集合名称: {stats.get('name', 'N/A')}")
        print(f"实体数: {stats.get('num_entities', 0)}")
        print(f"Embedding 模型: {stats.get('embedding_model', 'N/A')}")
        print(f"向量维度: {stats.get('dimension', 0)}")
        
        # 清理测试文件
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
        
        print("\n✅ RAG 服务测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ RAG 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 清理测试文件
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
        
        return False


def main():
    """主测试函数"""
    print("\n🚀 开始测试 RAG 完整流程\n")
    
    all_passed = True
    
    # 测试 Embedding 服务
    if not test_embedding_service():
        all_passed = False
        print("\n⚠️  Embedding 测试失败，终止后续测试")
        return
    
    # 测试文档处理
    if not test_document_processor():
        all_passed = False
    
    # 测试 RAG 服务
    if not test_rag_service():
        all_passed = False
    
    # 总结
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 80)
    
    print("\n💡 使用说明:")
    print("1. 准备文档（支持 .txt, .pdf, .docx）")
    print("2. 使用 rag_service.add_documents([file_paths]) 添加文档")
    print("3. 使用 rag_service.search(query, use_reranker=True) 检索相关内容")
    print("4. 使用 rag_service.get_context_for_query(query) 获取 LLM 上下文")
    print("\n📊 推荐配置:")
    print("  - Embedding 模型: bge-large-zh-v1.5 (1024维)")
    print("  - Reranker 模型: bge-reranker-v2-m3 (二次排序)")
    print("  - Metric Type: COSINE")
    print("  - 分块大小: 500 字符")
    print("  - 分块重叠: 50 字符")
    print("  - Top K: 3-5 个结果")
    print("\n🔥 Reranker 优势:")
    print("  - 提高检索精度，淘汰不相关文档")
    print("  - 减少噪声，提升 LLM 上下文质量")
    print("  - 基于语义深度理解，比向量相似度更准确\n")


if __name__ == "__main__":
    main()

