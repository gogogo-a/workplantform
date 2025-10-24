"""
文档管理 API 控制器 (RESTful 风格)
提供文档上传、删除、查询、列表等接口
"""
from fastapi import APIRouter, UploadFile, File, Query, Path

from internal.service.orm.document_sever import document_service
from api.v1.response_controller import json_response
from log import logger

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.post("", summary="上传文档")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档并自动进行 Embedding 处理
    
    - **file**: 文档文件（支持 .pdf, .docx, .txt）
    
    处理流程：
    1. 保存文件到本地
    2. 记录到 MongoDB
    3. 提交到 Kafka 进行异步 Embedding
    4. 存储向量到 Milvus（后台处理）
    """
    try:
        logger.info(f"收到上传请求: {file.filename}, 类型: {file.content_type}")
        
        # 验证文件类型
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_ext = file.filename[file.filename.rfind('.'):].lower()
        
        if file_ext not in allowed_extensions:
            return json_response(
                f"不支持的文件类型: {file_ext}，支持的类型: {', '.join(allowed_extensions)}",
                -2
            )
        
        # 调用业务逻辑
        message, ret, data = await document_service.upload_document(file)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"上传文档失败: {e}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("", summary="获取文档列表")
async def get_document_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(default=None, description="搜索关键词（文档名称）")
):
    """
    获取文档列表（分页 + 搜索）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（最大100）
    - **keyword**: 搜索关键词（可选，模糊匹配文档名称）
    
    返回每个文档的元数据：
    - uuid: 文档唯一标识
    - name: 文档名称
    - uploaded_at: 上传时间
    - chunk_count: 文本块数量（从 Milvus 查询）
    """
    try:
        logger.info(f"收到文档列表请求: page={page}, page_size={page_size}, keyword={keyword}")
        message, ret, data = await document_service.get_document_list(
            page=page,
            page_size=page_size,
            keyword=keyword
        )
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}", exc_info=True)
        return json_response("系统错误", -1)


@router.get("/{document_id}", summary="获取文档详情")
async def get_document_detail(
    document_id: str = Path(..., description="文档UUID")
):
    """
    获取文档详情
    
    - **document_id**: 文档UUID
    
    返回文档的完整信息：
    - uuid: 文档唯一标识
    - name: 文档名称
    - size: 文件大小（字节）
    - page: 文档页数
    - url: 文档访问URL
    - uploaded_at: 上传时间
    - chunk_count: 文本块数量（从 Milvus 查询）
    """
    try:
        logger.info(f"收到文档详情请求: {document_id}")
        message, ret, data = await document_service.get_document_detail(document_id)
        
        if data:
            return json_response(message, ret, data)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"获取文档详情失败: {e}", exc_info=True)
        return json_response("系统错误", -1)


@router.delete("/{document_id}", summary="删除文档")
async def delete_document(
    document_id: str = Path(..., description="文档UUID")
):
    """
    删除文档（包括 MongoDB 记录、Milvus 向量、物理文件）
    
    - **document_id**: 文档UUID
    """
    try:
        logger.info(f"收到删除请求: {document_id}")
        message, ret = await document_service.delete_document(document_id)
        return json_response(message, ret)
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}", exc_info=True)
        return json_response("系统错误", -1)
