"""
Milvus 向量数据库连接
使用单例模式管理连接
"""
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from typing import Optional, List, Dict, Any
import logging

from pkg.constants.constants import (
    MILVUS_HOST,
    MILVUS_PORT,
    MILVUS_USER,
    MILVUS_PASSWORD,
    MILVUS_DB_NAME
)

logger = logging.getLogger(__name__)


class Milvus:
    """Milvus 向量数据库单例类"""
    
    _instance: Optional['Milvus'] = None
    _initialized: bool = False
    _connection_alias: str = "default"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化（只执行一次）"""
        if not Milvus._initialized:
            self.host = MILVUS_HOST
            self.port = MILVUS_PORT
            self.user = MILVUS_USER
            self.password = MILVUS_PASSWORD
            self.db_name = MILVUS_DB_NAME
            self.collections: Dict[str, Collection] = {}
            Milvus._initialized = True
            logger.info("Milvus 实例已初始化")
    
    def connect(self):
        """
        连接到 Milvus 数据库
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 检查是否已连接
            if connections.has_connection(self._connection_alias):
                logger.info(f"Milvus 已连接到 {self.host}:{self.port}")
                return True
            
            # 直接连接（Milvus 2.x 会使用默认数据库）
            connections.connect(
                alias=self._connection_alias,
                host=self.host,
                port=str(self.port),
                user=self.user,
                password=self.password
            )
            
            logger.info(f"✓ 成功连接到 Milvus: {self.host}:{self.port}")
            
            # 验证连接
            version = utility.get_server_version()
            logger.info(f"✓ Milvus 版本: {version}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 连接 Milvus 失败: {e}")
            raise Exception(f"Milvus 连接失败: {e}")
    
    def disconnect(self):
        """断开 Milvus 连接"""
        try:
            if connections.has_connection(self._connection_alias):
                connections.disconnect(self._connection_alias)
                logger.info("✓ Milvus 连接已断开")
        except Exception as e:
            logger.error(f"✗ 断开 Milvus 连接失败: {e}")
    
    def create_collection(
        self,
        collection_name: str,
        dimension: int = 1536,
        description: str = "",
        index_type: str = "IVF_FLAT",
        metric_type: str = "L2",
        auto_id: bool = True
    ) -> Collection:
        """
        创建集合（Collection）
        
        Args:
            collection_name: 集合名称
            dimension: 向量维度（默认 1536，OpenAI embedding 维度）
            description: 集合描述
            index_type: 索引类型
            metric_type: 相似度度量类型（L2/IP/COSINE）
            auto_id: 是否自动生成 ID
            
        Returns:
            Collection: 创建的集合对象
        """
        try:
            # 检查集合是否已存在
            if utility.has_collection(collection_name):
                logger.info(f"集合 '{collection_name}' 已存在")
                collection = Collection(collection_name)
                self.collections[collection_name] = collection
                return collection
            
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=auto_id),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            
            # 创建 schema
            schema = CollectionSchema(
                fields=fields,
                description=description or f"Collection for {collection_name}"
            )
            
            # 创建集合
            collection = Collection(
                name=collection_name,
                schema=schema,
                using=self._connection_alias
            )
            
            # 创建索引
            index_params = {
                "metric_type": metric_type,
                "index_type": index_type,
                "params": {"nlist": 1024}
            }
            
            collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info(f"✓ 集合 '{collection_name}' 创建成功")
            logger.info(f"  - 维度: {dimension}")
            logger.info(f"  - 索引类型: {index_type}")
            logger.info(f"  - 度量类型: {metric_type}")
            
            self.collections[collection_name] = collection
            return collection
            
        except Exception as e:
            logger.error(f"✗ 创建集合 '{collection_name}' 失败: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        获取集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Collection: 集合对象，不存在则返回 None
        """
        try:
            if collection_name in self.collections:
                return self.collections[collection_name]
            
            if utility.has_collection(collection_name):
                collection = Collection(collection_name)
                self.collections[collection_name] = collection
                return collection
            
            logger.warning(f"集合 '{collection_name}' 不存在")
            return None
            
        except Exception as e:
            logger.error(f"✗ 获取集合 '{collection_name}' 失败: {e}")
            return None
    
    def drop_collection(self, collection_name: str):
        """
        删除集合
        
        Args:
            collection_name: 集合名称
        """
        try:
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                if collection_name in self.collections:
                    del self.collections[collection_name]
                logger.info(f"✓ 集合 '{collection_name}' 已删除")
            else:
                logger.warning(f"集合 '{collection_name}' 不存在")
        except Exception as e:
            logger.error(f"✗ 删除集合 '{collection_name}' 失败: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            List[str]: 集合名称列表
        """
        try:
            collections = utility.list_collections()
            return collections
        except Exception as e:
            logger.error(f"✗ 列出集合失败: {e}")
            return []
    
    def insert_vectors(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        插入向量数据
        
        Args:
            collection_name: 集合名称
            embeddings: 向量列表
            texts: 文本列表
            metadata: 元数据列表
            
        Returns:
            List[int]: 插入的 ID 列表
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                raise Exception(f"集合 '{collection_name}' 不存在")
            
            # 准备数据
            if metadata is None:
                metadata = [{}] * len(embeddings)
            
            data = [
                embeddings,
                texts,
                metadata
            ]
            
            # 插入数据
            mr = collection.insert(data)
            collection.flush()
            
            logger.info(f"✓ 成功插入 {len(embeddings)} 条向量到 '{collection_name}'")
            return mr.primary_keys
            
        except Exception as e:
            logger.error(f"✗ 插入向量失败: {e}")
            raise
    
    def search_vectors(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        top_k: int = 10,
        metric_type: str = "COSINE",
        output_fields: Optional[List[str]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        搜索向量
        
        Args:
            collection_name: 集合名称
            query_embeddings: 查询向量列表
            top_k: 返回 top K 个结果
            metric_type: 度量类型（L2/IP/COSINE），应与创建索引时一致
            output_fields: 需要返回的字段
            
        Returns:
            List[List[Dict]]: 搜索结果
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                raise Exception(f"集合 '{collection_name}' 不存在")
            
            # 加载集合到内存
            collection.load()
            
            # 设置搜索参数
            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": 10}
            }
            
            if output_fields is None:
                output_fields = ["text", "metadata"]
            
            # 执行搜索
            results = collection.search(
                data=query_embeddings,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=output_fields
            )
            
            # 格式化结果
            formatted_results = []
            for hits in results:
                hit_list = []
                for hit in hits:
                    hit_dict = {
                        "id": hit.id,
                        "distance": hit.distance,
                        "score": 1.0 / (1.0 + hit.distance)  # 转换为相似度分数
                    }
                    # 添加输出字段
                    for field in output_fields:
                        hit_dict[field] = hit.entity.get(field)
                    hit_list.append(hit_dict)
                formatted_results.append(hit_list)
            
            logger.info(f"✓ 在 '{collection_name}' 中搜索到 {len(formatted_results)} 组结果")
            return formatted_results
            
        except Exception as e:
            logger.error(f"✗ 搜索向量失败: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Dict: 统计信息
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return {}
            
            collection.flush()
            stats = {
                "name": collection_name,
                "num_entities": collection.num_entities,
                "description": collection.description
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"✗ 获取集合统计信息失败: {e}")
            return {}


# 创建全局单例实例
milvus_client = Milvus()

