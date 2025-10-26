"""
系统资源监控模块

定期收集系统和服务的性能指标：
- CPU、内存、GPU 使用率
- MongoDB 连接数、操作统计
- Milvus 集合统计、内存使用
- Kafka 主题信息（如果启用）
- LLM API 调用统计

监控数据保存到 json_monitor/YYYY-MM-DD_resource.json
"""

import time
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from log import logger

# 尝试导入可选的监控库
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil 未安装，无法监控 CPU/内存。安装: pip install psutil")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.debug("GPUtil 未安装，无法监控 GPU。安装: pip install gputil")


class ResourceMonitor:
    """系统资源监控器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 监控数据保存目录
        project_root = Path(__file__).parent.parent.parent
        self.monitor_dir = project_root / "json_monitor"
        self.monitor_dir.mkdir(exist_ok=True)
        
        # 监控线程
        self.monitoring = False
        self.monitor_thread = None
        self.interval = 60  # 默认每 60 秒监控一次
        
        # 统计计数器
        self.stats = {
            "llm_calls": 0,
            "llm_tokens": 0,
            "llm_errors": 0,
            "embedding_calls": 0,
            "milvus_searches": 0,
            "mongodb_queries": 0
        }
        
        self._initialized = True
        logger.info(f"资源监控器已初始化，监控目录: {self.monitor_dir}")
    
    def _get_file_path(self) -> Path:
        """
        获取资源监控数据文件路径
        
        格式: json_monitor/YY_MM_DD_monitor/resource.json
        例如: json_monitor/25_10_26_monitor/resource.json
        """
        # 使用和 json_log 相同的日期格式：YY_MM_DD_monitor
        today_dir = datetime.now().strftime("%y_%m_%d_monitor")
        monitor_subdir = self.monitor_dir / today_dir
        
        # 确保目录存在
        monitor_subdir.mkdir(exist_ok=True)
        
        # 文件名：resource.json
        return monitor_subdir / "resource.json"
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统资源指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {}
        }
        
        if PSUTIL_AVAILABLE:
            try:
                # CPU 使用率
                metrics["system"]["cpu_percent"] = psutil.cpu_percent(interval=1)
                metrics["system"]["cpu_count"] = psutil.cpu_count()
                
                # 内存使用
                mem = psutil.virtual_memory()
                metrics["system"]["memory_total_gb"] = round(mem.total / (1024**3), 2)
                metrics["system"]["memory_used_gb"] = round(mem.used / (1024**3), 2)
                metrics["system"]["memory_percent"] = mem.percent
                
                # 磁盘使用
                disk = psutil.disk_usage('/')
                metrics["system"]["disk_total_gb"] = round(disk.total / (1024**3), 2)
                metrics["system"]["disk_used_gb"] = round(disk.used / (1024**3), 2)
                metrics["system"]["disk_percent"] = disk.percent
                
            except Exception as e:
                logger.error(f"收集系统指标失败: {e}")
        
        if GPUTIL_AVAILABLE:
            try:
                # GPU 使用率
                gpus = GPUtil.getGPUs()
                if gpus:
                    metrics["system"]["gpu"] = []
                    for gpu in gpus:
                        metrics["system"]["gpu"].append({
                            "id": gpu.id,
                            "name": gpu.name,
                            "load_percent": round(gpu.load * 100, 2),
                            "memory_used_mb": round(gpu.memoryUsed, 2),
                            "memory_total_mb": round(gpu.memoryTotal, 2),
                            "memory_percent": round(gpu.memoryUtil * 100, 2),
                            "temperature": gpu.temperature
                        })
            except Exception as e:
                logger.error(f"收集 GPU 指标失败: {e}")
        
        return metrics
    
    def _collect_mongodb_metrics_sync(self) -> Dict[str, Any]:
        """
        收集 MongoDB 性能指标（同步版本，用于监控线程）
        
        注意：使用同步的 pymongo 客户端，避免事件循环冲突
        """
        metrics = {}
        
        try:
            from pymongo import MongoClient
            from pkg.constants.constants import MONGODB_URL, MONGODB_DATABASE
            
            # 创建临时的同步客户端（仅用于收集统计数据）
            sync_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            
            try:
                # 服务器状态
                server_status = sync_client.admin.command("serverStatus")
                
                metrics["mongodb"] = {
                    "status": "healthy",  # 添加健康状态
                    "connections": server_status.get("connections", {}).get("current", 0),  # 简化字段名
                    "connections_current": server_status.get("connections", {}).get("current", 0),
                    "connections_available": server_status.get("connections", {}).get("available", 0),
                    "network_bytes_in": server_status.get("network", {}).get("bytesIn", 0),
                    "network_bytes_out": server_status.get("network", {}).get("bytesOut", 0),
                    "opcounters_query": server_status.get("opcounters", {}).get("query", 0),
                    "opcounters_insert": server_status.get("opcounters", {}).get("insert", 0),
                    "opcounters_update": server_status.get("opcounters", {}).get("update", 0),
                    "opcounters_delete": server_status.get("opcounters", {}).get("delete", 0),
                }
                
                # 数据库统计
                db_stats = sync_client[MONGODB_DATABASE].command("dbStats")
                
                metrics["mongodb"]["databases"] = db_stats.get("collections", 0)  # 添加 databases 字段
                metrics["mongodb"]["db_size_mb"] = round(db_stats.get("dataSize", 0) / (1024**2), 2)
                metrics["mongodb"]["db_collections"] = db_stats.get("collections", 0)
                metrics["mongodb"]["db_documents"] = db_stats.get("objects", 0)
                
            finally:
                # 关闭临时客户端
                sync_client.close()
                
        except Exception as e:
            logger.error(f"收集 MongoDB 指标失败: {e}")
        
        return metrics
    
    def _collect_milvus_metrics(self) -> Dict[str, Any]:
        """收集 Milvus 性能指标"""
        metrics = {}
        
        try:
            from internal.db.milvus import milvus_client
            from pkg.constants.constants import MILVUS_COLLECTION_NAME
            from pymilvus import utility
            
            if milvus_client:
                # 动态获取所有集合
                all_collections = utility.list_collections()
                total_collections = len(all_collections)
                
                # 初始化 milvus 统计
                metrics["milvus"] = {
                    "status": "healthy",  # 添加健康状态
                    "collections": total_collections,  # 动态获取集合数量
                    "total_entities": 0,
                }
                
                # 检查主集合是否存在
                if utility.has_collection(MILVUS_COLLECTION_NAME):
                    # 获取集合
                    collection = milvus_client.get_collection(MILVUS_COLLECTION_NAME)
                    
                    if collection:
                        metrics["milvus"]["collection_name"] = MILVUS_COLLECTION_NAME
                        metrics["milvus"]["total_entities"] = collection.num_entities
                        
                        # 尝试获取集合详细信息
                        try:
                            # 获取集合统计信息
                            stats = utility.get_query_segment_info(MILVUS_COLLECTION_NAME)
                            if stats:
                                total_rows = sum(seg.num_rows for seg in stats)
                                metrics["milvus"]["total_rows"] = total_rows
                                metrics["milvus"]["num_segments"] = len(stats)
                        except:
                            pass
                
        except Exception as e:
            logger.error(f"收集 Milvus 指标失败: {e}")
        
        return metrics
    
    def _collect_kafka_metrics(self) -> Dict[str, Any]:
        """收集 Kafka 性能指标（如果启用）"""
        metrics = {}
        
        try:
            # 这里可以添加 Kafka 监控逻辑
            # 需要 kafka-python 库
            pass
        except Exception as e:
            logger.error(f"收集 Kafka 指标失败: {e}")
        
        return metrics
    
    def _collect_app_metrics(self) -> Dict[str, Any]:
        """收集应用层统计（LLM 调用、Embedding 等）"""
        metrics = {
            "app_stats": {
                "llm_total_calls": self.stats["llm_calls"],
                "llm_total_tokens": self.stats["llm_tokens"],
                "llm_total_errors": self.stats["llm_errors"],
                "embedding_total_calls": self.stats["embedding_calls"],
                "milvus_total_searches": self.stats["milvus_searches"],
                "mongodb_total_queries": self.stats["mongodb_queries"],
            }
        }
        return metrics
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有监控指标（同步版本，用于监控线程）"""
        metrics = {}
        
        # 系统资源
        metrics.update(self._collect_system_metrics())
        
        # MongoDB（使用同步客户端）
        mongodb_metrics = self._collect_mongodb_metrics_sync()
        metrics.update(mongodb_metrics)
        
        # Milvus
        milvus_metrics = self._collect_milvus_metrics()
        metrics.update(milvus_metrics)
        
        # Kafka
        kafka_metrics = self._collect_kafka_metrics()
        metrics.update(kafka_metrics)
        
        # 应用统计
        app_metrics = self._collect_app_metrics()
        metrics.update(app_metrics)
        
        return metrics
    
    def _save_metrics(self, metrics: Dict[str, Any]):
        """保存监控数据到文件"""
        try:
            file_path = self._get_file_path()
            
            # 追加写入（NDJSON 格式）
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics, ensure_ascii=False) + '\n')
            
            logger.debug(f"✅ 资源监控数据已保存")
        
        except Exception as e:
            logger.error(f"保存监控数据失败: {e}")
    
    def _monitor_loop(self):
        """监控循环（在后台线程运行）"""
        logger.info(f"🔍 资源监控线程已启动，间隔: {self.interval}秒")
        
        while self.monitoring:
            try:
                # 收集指标（同步操作，无需事件循环）
                metrics = self.collect_all_metrics()
                
                # 保存指标
                self._save_metrics(metrics)
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}", exc_info=True)
            
            # 等待下一次监控
            time.sleep(self.interval)
        
        logger.info("🛑 资源监控线程已停止")
    
    def start_monitoring(self, interval: int = 60):
        """
        启动资源监控
        
        Args:
            interval: 监控间隔（秒），默认 60 秒
        """
        if self.monitoring:
            logger.warning("资源监控已在运行")
            return
        
        self.interval = interval
        self.monitoring = True
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"✅ 资源监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止资源监控"""
        if not self.monitoring:
            logger.warning("资源监控未运行")
            return
        
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("✅ 资源监控已停止")
    
    # ==================== 统计计数器 ====================
    
    def record_llm_call(self, tokens: int = 0, is_error: bool = False):
        """记录 LLM 调用"""
        self.stats["llm_calls"] += 1
        self.stats["llm_tokens"] += tokens
        if is_error:
            self.stats["llm_errors"] += 1
    
    def record_embedding_call(self):
        """记录 Embedding 调用"""
        self.stats["embedding_calls"] += 1
    
    def record_milvus_search(self):
        """记录 Milvus 搜索"""
        self.stats["milvus_searches"] += 1
    
    def record_mongodb_query(self):
        """记录 MongoDB 查询"""
        self.stats["mongodb_queries"] += 1


# 全局单例
resource_monitor = ResourceMonitor()


# ==================== 便捷函数 ====================

def start_resource_monitoring(interval: int = 60):
    """启动资源监控"""
    resource_monitor.start_monitoring(interval)


def stop_resource_monitoring():
    """停止资源监控"""
    resource_monitor.stop_monitoring()


def record_llm_call(tokens: int = 0, is_error: bool = False):
    """记录 LLM 调用"""
    resource_monitor.record_llm_call(tokens, is_error)


def record_embedding_call():
    """记录 Embedding 调用"""
    resource_monitor.record_embedding_call()


def record_milvus_search():
    """记录 Milvus 搜索"""
    resource_monitor.record_milvus_search()


def record_mongodb_query():
    """记录 MongoDB 查询"""
    resource_monitor.record_mongodb_query()

