"""
Redis 客户端（单例模式）
提供缓存、会话、消息队列等功能
"""
import redis
import json
import logging
from typing import Any, Optional, Dict, List, Union

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 确保只初始化一次
        if RedisClient._initialized:
            return
        
        # 从 constants 导入配置
        from pkg.constants.constants import (
            REDIS_HOST, 
            REDIS_PORT, 
            REDIS_DB, 
            REDIS_PASSWORD
        )
        
        self.client: Optional[redis.Redis] = None
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.db = REDIS_DB
        self.password = REDIS_PASSWORD if REDIS_PASSWORD else None
        self.decode_responses = True  # 自动解码为字符串
        
        RedisClient._initialized = True
        logger.info(f"Redis 客户端已初始化: {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """
        连接到 Redis
        
        Returns:
            bool: 是否连接成功
        """
        try:
            if self.client is not None:
                logger.info("Redis 已经连接")
                return True
            
            # 创建 Redis 连接
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # 测试连接
            self.client.ping()
            logger.info(f"✓ Redis 连接成功: {self.host}:{self.port}")
            return True
            
        except redis.ConnectionError as e:
            logger.error(f"✗ Redis 连接失败: {e}")
            self.client = None
            return False
        except Exception as e:
            logger.error(f"✗ Redis 连接异常: {e}")
            self.client = None
            return False
    
    def disconnect(self):
        """断开 Redis 连接"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                logger.info("✓ Redis 连接已断开")
        except Exception as e:
            logger.error(f"✗ 断开 Redis 连接失败: {e}")
    
    def _ensure_connected(self):
        """确保已连接"""
        if self.client is None:
            raise ConnectionError("Redis 未连接，请先调用 connect()")
    
    # ==================== 基本操作 ====================
    
    def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        设置键值对
        
        Args:
            key: 键
            value: 值（会自动序列化 dict/list 为 JSON）
            ex: 过期时间（秒）
            px: 过期时间（毫秒）
            nx: 只在键不存在时设置
            xx: 只在键存在时设置
            
        Returns:
            bool: 是否设置成功
        """
        try:
            self._ensure_connected()
            
            # 如果值是 dict 或 list，序列化为 JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
            
        except Exception as e:
            logger.error(f"✗ Redis SET 失败 ({key}): {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取值
        
        Args:
            key: 键
            default: 默认值（键不存在时返回）
            
        Returns:
            值（自动尝试解析 JSON）
        """
        try:
            self._ensure_connected()
            value = self.client.get(key)
            
            if value is None:
                return default
            
            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"✗ Redis GET 失败 ({key}): {e}")
            return default
    
    def delete(self, *keys: str) -> int:
        """
        删除一个或多个键
        
        Args:
            *keys: 键列表
            
        Returns:
            int: 删除的键数量
        """
        try:
            self._ensure_connected()
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"✗ Redis DELETE 失败: {e}")
            return 0
    
    def exists(self, *keys: str) -> int:
        """
        检查键是否存在
        
        Args:
            *keys: 键列表
            
        Returns:
            int: 存在的键数量
        """
        try:
            self._ensure_connected()
            return self.client.exists(*keys)
        except Exception as e:
            logger.error(f"✗ Redis EXISTS 失败: {e}")
            return 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 键
            seconds: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            self._ensure_connected()
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"✗ Redis EXPIRE 失败 ({key}): {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间
        
        Args:
            key: 键
            
        Returns:
            int: 剩余秒数（-1=永久，-2=不存在）
        """
        try:
            self._ensure_connected()
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"✗ Redis TTL 失败 ({key}): {e}")
            return -2
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的所有键
        
        Args:
            pattern: 模式（如 "user:*"）
            
        Returns:
            List[str]: 键列表
        """
        try:
            self._ensure_connected()
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"✗ Redis KEYS 失败: {e}")
            return []
    
    # ==================== Hash 操作 ====================
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """
        设置 Hash 字段
        
        Args:
            name: Hash 名称
            key: 字段名
            value: 字段值
            
        Returns:
            int: 新增字段数量
        """
        try:
            self._ensure_connected()
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return self.client.hset(name, key, value)
        except Exception as e:
            logger.error(f"✗ Redis HSET 失败 ({name}.{key}): {e}")
            return 0
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """
        获取 Hash 字段值
        
        Args:
            name: Hash 名称
            key: 字段名
            default: 默认值
            
        Returns:
            字段值
        """
        try:
            self._ensure_connected()
            value = self.client.hget(name, key)
            
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"✗ Redis HGET 失败 ({name}.{key}): {e}")
            return default
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        获取 Hash 所有字段
        
        Args:
            name: Hash 名称
            
        Returns:
            Dict: 所有字段
        """
        try:
            self._ensure_connected()
            data = self.client.hgetall(name)
            
            # 尝试解析 JSON 值
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Redis HGETALL 失败 ({name}): {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """
        删除 Hash 字段
        
        Args:
            name: Hash 名称
            *keys: 字段名列表
            
        Returns:
            int: 删除的字段数量
        """
        try:
            self._ensure_connected()
            return self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"✗ Redis HDEL 失败 ({name}): {e}")
            return 0
    
    def hexists(self, name: str, key: str) -> bool:
        """
        检查 Hash 字段是否存在
        
        Args:
            name: Hash 名称
            key: 字段名
            
        Returns:
            bool: 是否存在
        """
        try:
            self._ensure_connected()
            return bool(self.client.hexists(name, key))
        except Exception as e:
            logger.error(f"✗ Redis HEXISTS 失败 ({name}.{key}): {e}")
            return False
    
    # ==================== List 操作 ====================
    
    def lpush(self, name: str, *values: Any) -> int:
        """
        从列表左侧推入元素
        
        Args:
            name: 列表名称
            *values: 值列表
            
        Returns:
            int: 列表长度
        """
        try:
            self._ensure_connected()
            
            # 序列化复杂对象
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(v)
            
            return self.client.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"✗ Redis LPUSH 失败 ({name}): {e}")
            return 0
    
    def rpush(self, name: str, *values: Any) -> int:
        """
        从列表右侧推入元素
        
        Args:
            name: 列表名称
            *values: 值列表
            
        Returns:
            int: 列表长度
        """
        try:
            self._ensure_connected()
            
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(v)
            
            return self.client.rpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"✗ Redis RPUSH 失败 ({name}): {e}")
            return 0
    
    def lpop(self, name: str) -> Any:
        """
        从列表左侧弹出元素
        
        Args:
            name: 列表名称
            
        Returns:
            弹出的元素
        """
        try:
            self._ensure_connected()
            value = self.client.lpop(name)
            
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"✗ Redis LPOP 失败 ({name}): {e}")
            return None
    
    def rpop(self, name: str) -> Any:
        """
        从列表右侧弹出元素
        
        Args:
            name: 列表名称
            
        Returns:
            弹出的元素
        """
        try:
            self._ensure_connected()
            value = self.client.rpop(name)
            
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"✗ Redis RPOP 失败 ({name}): {e}")
            return None
    
    def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表范围内的元素
        
        Args:
            name: 列表名称
            start: 起始索引
            end: 结束索引（-1 表示最后）
            
        Returns:
            List: 元素列表
        """
        try:
            self._ensure_connected()
            values = self.client.lrange(name, start, end)
            
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Redis LRANGE 失败 ({name}): {e}")
            return []
    
    def llen(self, name: str) -> int:
        """
        获取列表长度
        
        Args:
            name: 列表名称
            
        Returns:
            int: 列表长度
        """
        try:
            self._ensure_connected()
            return self.client.llen(name)
        except Exception as e:
            logger.error(f"✗ Redis LLEN 失败 ({name}): {e}")
            return 0
    
    # ==================== Set 操作 ====================
    
    def sadd(self, name: str, *values: Any) -> int:
        """
        向集合添加元素
        
        Args:
            name: 集合名称
            *values: 值列表
            
        Returns:
            int: 添加的元素数量
        """
        try:
            self._ensure_connected()
            
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(v)
            
            return self.client.sadd(name, *serialized_values)
        except Exception as e:
            logger.error(f"✗ Redis SADD 失败 ({name}): {e}")
            return 0
    
    def smembers(self, name: str) -> set:
        """
        获取集合所有成员
        
        Args:
            name: 集合名称
            
        Returns:
            set: 成员集合
        """
        try:
            self._ensure_connected()
            values = self.client.smembers(name)
            
            result = set()
            for v in values:
                try:
                    result.add(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.add(v)
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Redis SMEMBERS 失败 ({name}): {e}")
            return set()
    
    def sismember(self, name: str, value: Any) -> bool:
        """
        检查元素是否在集合中
        
        Args:
            name: 集合名称
            value: 值
            
        Returns:
            bool: 是否存在
        """
        try:
            self._ensure_connected()
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return bool(self.client.sismember(name, value))
        except Exception as e:
            logger.error(f"✗ Redis SISMEMBER 失败 ({name}): {e}")
            return False
    
    def srem(self, name: str, *values: Any) -> int:
        """
        从集合删除元素
        
        Args:
            name: 集合名称
            *values: 值列表
            
        Returns:
            int: 删除的元素数量
        """
        try:
            self._ensure_connected()
            
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(v)
            
            return self.client.srem(name, *serialized_values)
        except Exception as e:
            logger.error(f"✗ Redis SREM 失败 ({name}): {e}")
            return 0
    
    # ==================== 高级功能 ====================
    
    def incr(self, key: str, amount: int = 1) -> int:
        """
        递增计数器
        
        Args:
            key: 键
            amount: 递增量
            
        Returns:
            int: 递增后的值
        """
        try:
            self._ensure_connected()
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"✗ Redis INCR 失败 ({key}): {e}")
            return 0
    
    def decr(self, key: str, amount: int = 1) -> int:
        """
        递减计数器
        
        Args:
            key: 键
            amount: 递减量
            
        Returns:
            int: 递减后的值
        """
        try:
            self._ensure_connected()
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"✗ Redis DECR 失败 ({key}): {e}")
            return 0
    
    def flushdb(self) -> bool:
        """
        清空当前数据库
        
        ⚠️  危险操作！
        
        Returns:
            bool: 是否成功
        """
        try:
            self._ensure_connected()
            self.client.flushdb()
            logger.warning("⚠️  Redis 当前数据库已清空")
            return True
        except Exception as e:
            logger.error(f"✗ Redis FLUSHDB 失败: {e}")
            return False
    
    def ping(self) -> bool:
        """
        测试连接
        
        Returns:
            bool: 是否连接正常
        """
        try:
            self._ensure_connected()
            return self.client.ping()
        except Exception as e:
            logger.error(f"✗ Redis PING 失败: {e}")
            return False
    
    def info(self) -> Dict[str, Any]:
        """
        获取 Redis 服务器信息
        
        Returns:
            Dict: 服务器信息
        """
        try:
            self._ensure_connected()
            return self.client.info()
        except Exception as e:
            logger.error(f"✗ Redis INFO 失败: {e}")
            return {}


# 创建全局单例实例
redis_client = RedisClient()

