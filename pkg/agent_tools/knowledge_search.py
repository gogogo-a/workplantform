"""
知识库搜索工具
从向量数据库中检索相关知识（RAG）
"""
from typing import Dict, Any


def knowledge_search(query: str, top_k: int = 5, use_reranker: bool = True, user_permission: int = 0) -> Dict[str, Any]:
    """
    知识库搜索工具
    从向量数据库中检索相关知识（RAG），根据用户权限过滤文档
    
    Args:
        query: 搜索查询
        top_k: 返回结果数量
        use_reranker: 是否使用重排序
        user_permission: 用户权限（0=普通用户，1=管理员）
        
    Returns:
        Dict: 包含搜索结果和上下文的字典
            - success: 是否成功
            - results: 搜索结果列表
            - context: 格式化的上下文文本
            - count: 结果数量
            - documents: 文档元信息列表（uuid, name）
    """
    try:
        # 延迟导入，避免循环依赖
        from internal.rag.rag_service import rag_service
        
        print(f"[工具] 知识库搜索: {query} (Top {top_k}, user_permission={user_permission})")
        
        # 执行 RAG 检索（只调用一次，传递用户权限）
        search_results = rag_service.search(
            query=query,
            top_k=top_k,
            use_reranker=use_reranker,
            user_permission=user_permission  # 🔥 传递用户权限
        )
        
        if not search_results:
            print(f"[工具] 未找到相关文档")
            return {
                "success": False,
                "results": [],
                "context": "",
                "count": 0,
                "documents": [],
                "message": "知识库中未找到相关信息"
            }
        
        # 🔥 手动构建上下文，避免重复调用 search()
        context_parts = []
        current_length = 0
        max_context_length = 10000
        
        for i, result in enumerate(search_results, 1):
            text = result["text"]
            source = result["metadata"].get("filename", "未知来源")
            
            # 添加分数信息
            score_info = ""
            if "rerank_score" in result:
                score_info = f" (Rerank分数: {result['rerank_score']:.4f})"
            
            # 格式化引用
            part = f"[文档{i} - {source}{score_info}]\n{text}\n"
            part_length = len(part)
            
            # 检查长度限制
            if current_length + part_length > max_context_length:
                break
            
            context_parts.append(part)
            current_length += part_length
        
        context = "\n".join(context_parts)
        
        # 🔥 提取文档元信息（去重后的）
        documents_info = []
        seen_docs = set()  # 用于去重
        
        for result in search_results:
            metadata = result.get("metadata", {})
            doc_uuid = metadata.get("document_uuid", "")
            doc_name = metadata.get("filename", "未知文档")
            
            # 基于 document_uuid 去重
            if doc_uuid and doc_uuid not in seen_docs:
                seen_docs.add(doc_uuid)
                documents_info.append({
                    "uuid": doc_uuid,
                    "name": doc_name
                })
        
        print(f"[工具] 找到 {len(search_results)} 个相关文档片段")
        print(f"[工具] 涉及 {len(documents_info)} 个不同文档")
        print(f"[工具] 上下文长度: {len(context)} 字符")
        
        return {
            "success": True,
            "results": search_results,
            "context": context,
            "count": len(search_results),
            "documents": documents_info,  # 新增：文档元信息列表
            "message": f"成功检索到 {len(search_results)} 个相关文档片段"
        }
        
    except Exception as e:
        print(f"[工具] 知识库搜索失败: {e}")
        return {
            "success": False,
            "results": [],
            "context": "",
            "count": 0,
            "documents": [],
            "message": f"搜索失败: {str(e)}"
        }


# 工具元信息
knowledge_search.prompt_template = "rag"
knowledge_search.description = "从知识库检索相关信息（RAG检索），用于回答需要参考文档的问题"
knowledge_search.is_admin = False  # 所有用户可用

