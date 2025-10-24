"""
文档服务业务逻辑层
处理文档的上传、查询、删除等业务
"""
import os
import uuid as uuid_module
from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import UploadFile
from pymilvus import Collection

from internal.model.document import DocumentModel
from internal.db.milvus import milvus_client
from internal.document_client.document_processor import document_processor
from internal.document_client.config_loader import config
from log import logger


class DocumentService:
    """文档服务类"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.collection_name = config.get('milvus.collection_name', 'documents')
    
    async def upload_document(self, file: UploadFile):
        """
        上传文档并异步处理
        
        Args:
            file: 上传的文件
            
        Returns:
            tuple: (message, ret, data) - message: 提示信息, ret: 返回码(0成功/-1失败), data: 文档信息
        """
        try:
            # 1. 生成唯一文件名
            file_uuid = str(uuid_module.uuid4())
            file_extension = Path(file.filename).suffix
            new_filename = f"{file_uuid}{file_extension}"
            file_path = self.upload_dir / new_filename
            
            # 2. 保存文件
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            file_size = len(content)
            logger.info(f"文件已保存: {file.filename} → {file_path}, 大小: {file_size} bytes")
            
            # 3. 保存文档信息到 MongoDB
            doc_model = DocumentModel(
                uuid=file_uuid,
                name=file.filename,
                content="",  # 内容将在后台处理时填充
                page=0,
                url=f"/uploads/{new_filename}",
                size=file_size
            )
            await doc_model.insert()
            
            logger.info(f"文档已保存到 MongoDB: {file_uuid}")
            
            # 4. 提交到 Kafka 异步处理（Embedding）
            task = {
                "task_type": "file",
                "file_path": str(file_path),
                "document_uuid": file_uuid,
                "metadata": {
                    "filename": file.filename,
                    "source": "api_upload"
                }
            }
            
            submit_success = document_processor.submit_task(task)
            
            if not submit_success:
                logger.error(f"任务提交失败: {file_uuid}")
                data = {
                    "uuid": file_uuid,
                    "name": file.filename,
                    "status": "failed"
                }
                return "文档保存成功，但处理任务提交失败", -1, data
            
            logger.info(f"文档处理任务已提交: {file_uuid}")
            
            data = {
                "uuid": file_uuid,
                "name": file.filename,
                "status": "processing",
                "message": "文档已提交处理，后台正在进行 Embedding"
            }
            return "上传成功", 0, data
            
        except Exception as e:
            logger.error(f"上传文档失败: {e}", exc_info=True)
            return f"上传失败: {str(e)}", -1, None
    
    async def get_document_detail(self, document_uuid: str):
        """
        获取文档详情
        
        Args:
            document_uuid: 文档UUID
            
        Returns:
            tuple: (message, ret, data) - message: 提示信息, ret: 返回码, data: 文档详细信息
        """
        try:
            # 1. 从 MongoDB 获取文档基本信息
            doc = await DocumentModel.find_one(DocumentModel.uuid == document_uuid)
            
            if not doc:
                return "文档不存在", -2, None
            
            # 2. 从 Milvus 获取 chunk_count
            chunk_count = await self._get_chunk_count_from_milvus(document_uuid)
            
            data = {
                "uuid": doc.uuid,
                "name": doc.name,
                "size": doc.size,
                "page": doc.page,
                "url": doc.url,
                "uploaded_at": doc.create_at.isoformat() if doc.create_at else None,
                "chunk_count": chunk_count
            }
            return "查询成功", 0, data
            
        except Exception as e:
            logger.error(f"获取文档详情失败: {e}", exc_info=True)
            return f"查询失败: {str(e)}", -1, None
    
    async def delete_document(self, document_uuid: str):
        """
        删除文档（MongoDB + Milvus + 物理文件）
        
        Args:
            document_uuid: 文档UUID
            
        Returns:
            tuple: (message, ret) - message: 提示信息, ret: 返回码
        """
        try:
            # 1. 查询文档
            doc = await DocumentModel.find_one(DocumentModel.uuid == document_uuid)
            
            if not doc:
                return "文档不存在", -2
            
            # 2. 删除 MongoDB 记录
            await doc.delete()
            logger.info(f"MongoDB 文档已删除: {document_uuid}")
            
            # 3. 删除 Milvus 向量数据
            deleted_count = self._delete_from_milvus(document_uuid)
            logger.info(f"Milvus 向量已删除: {document_uuid}, 数量: {deleted_count}")
            
            # 4. 删除物理文件
            file_path = Path(doc.url.lstrip('/'))
            if file_path.exists():
                file_path.unlink()
                logger.info(f"物理文件已删除: {file_path}")
            
            return f"文档已删除（包含 {deleted_count} 个向量块）", 0
            
        except Exception as e:
            logger.error(f"删除文档失败: {e}", exc_info=True)
            return f"删除失败: {str(e)}", -1
    
    async def get_document_list(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        keyword: Optional[str] = None
    ):
        """
        获取文档列表（分页 + 搜索）
        
        Args:
            page: 页码
            page_size: 每页数量
            keyword: 搜索关键词
            
        Returns:
            tuple: (message, ret, data) - message: 提示信息, ret: 返回码, data: 文档列表
        """
        try:
            # 1. 构建查询条件
            skip = (page - 1) * page_size
            
            if keyword:
                # 使用名称模糊搜索
                query = {"name": {"$regex": keyword, "$options": "i"}}
                total = await DocumentModel.find(query).count()
                docs = await DocumentModel.find(query).skip(skip).limit(page_size).to_list()
            else:
                total = await DocumentModel.count()
                docs = await DocumentModel.find_all().skip(skip).limit(page_size).to_list()
            
            # 2. 为每个文档获取 chunk_count（从 Milvus）
            document_list = []
            for doc in docs:
                chunk_count = await self._get_chunk_count_from_milvus(doc.uuid)
                document_list.append({
                    "uuid": doc.uuid,
                    "name": doc.name,
                    "uploaded_at": doc.create_at.isoformat() if doc.create_at else None,
                    "chunk_count": chunk_count
                })
            
            data = {
                "total": total,
                "page": page,
                "page_size": page_size,
                "documents": document_list
            }
            return "查询成功", 0, data
            
        except Exception as e:
            logger.error(f"获取文档列表失败: {e}", exc_info=True)
            return f"查询失败: {str(e)}", -1, None
    
    async def _get_chunk_count_from_milvus(self, document_uuid: str) -> int:
        """
        从 Milvus 查询指定文档的 chunk 数量
        
        Args:
            document_uuid: 文档UUID
            
        Returns:
            int: chunk 数量
        """
        try:
            existing_collections = milvus_client.list_collections()
            if self.collection_name not in existing_collections:
                return 0
            
            collection = Collection(self.collection_name)
            collection.load()
            
            # 查询该文档的所有向量记录（document_uuid 在 metadata 中）
            expr = f'metadata["document_uuid"] == "{document_uuid}"'
            results = collection.query(
                expr=expr,
                output_fields=["id"],
                limit=10000
            )
            
            return len(results)
            
        except Exception as e:
            logger.warning(f"从 Milvus 查询 chunk_count 失败: {e}")
            return 0
    
    def _delete_from_milvus(self, document_uuid: str) -> int:
        """
        从 Milvus 删除指定文档的所有向量
        
        Args:
            document_uuid: 文档UUID
            
        Returns:
            int: 删除的向量数量
        """
        try:
            existing_collections = milvus_client.list_collections()
            if self.collection_name not in existing_collections:
                return 0
            
            collection = Collection(self.collection_name)
            collection.load()
            
            # 先查询该文档有多少条记录（document_uuid 在 metadata 中）
            expr = f'metadata["document_uuid"] == "{document_uuid}"'
            count_results = collection.query(
                expr=expr,
                output_fields=["id"],
                limit=10000
            )
            
            count = len(count_results)
            
            # 删除
            if count > 0:
                collection.delete(expr)
                collection.flush()
            
            return count
            
        except Exception as e:
            logger.error(f"从 Milvus 删除向量失败: {e}", exc_info=True)
            return 0


# 导出单例
document_service = DocumentService()

