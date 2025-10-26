"""
日志数据读取服务

读取 json_log 目录下的错误日志
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from log import logger


class LogService:
    """日志读取服务（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 日志目录
        project_root = Path(__file__).parent.parent.parent.parent
        self.log_dir = project_root / "json_log"
        
        self._initialized = True
        logger.info(f"日志服务已初始化，日志目录: {self.log_dir}")
    
    def _get_log_dir(self, date: Optional[str] = None) -> Path:
        """
        获取指定日期的日志目录
        
        Args:
            date: 日期字符串，格式 YYYY-MM-DD（可选，默认今天）
        
        Returns:
            Path: 日志目录路径，格式：json_log/YY_MM_DD_log/
        """
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
                dir_name = dt.strftime("%y_%m_%d_log")
            except ValueError:
                logger.error(f"日期格式错误: {date}，应为 YYYY-MM-DD")
                return None
        else:
            # 默认今天
            dir_name = datetime.now().strftime("%y_%m_%d_log")
        
        return self.log_dir / dir_name
    
    def get_error_logs(
        self, 
        date: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取错误日志
        
        Args:
            date: 日期字符串，格式 YYYY-MM-DD（可选，默认今天）
            limit: 返回的最大日志条数（可选，默认100）
            offset: 偏移量，用于分页（默认0）
        
        Returns:
            Dict: {
                "date": "2025-10-26",
                "total": 150,
                "count": 100,
                "offset": 0,
                "logs": [...]
            }
        """
        try:
            log_dir = self._get_log_dir(date)
            
            if not log_dir or not log_dir.exists():
                return {
                    "date": date or datetime.now().strftime("%Y-%m-%d"),
                    "total": 0,
                    "count": 0,
                    "offset": 0,
                    "logs": [],
                    "message": f"日志目录不存在: {log_dir}"
                }
            
            error_file = log_dir / "error.json"
            
            if not error_file.exists():
                return {
                    "date": date or datetime.now().strftime("%Y-%m-%d"),
                    "total": 0,
                    "count": 0,
                    "offset": 0,
                    "logs": [],
                    "message": f"错误日志文件不存在"
                }
            
            # 读取 NDJSON 文件
            logs = []
            with open(error_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError as e:
                            logger.warning(f"解析日志行失败: {e}")
            
            total = len(logs)
            
            # 反转列表，最新的在前面
            logs.reverse()
            
            # 分页
            if limit:
                paginated_logs = logs[offset:offset + limit]
            else:
                paginated_logs = logs[offset:]
            
            return {
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "total": total,
                "count": len(paginated_logs),
                "offset": offset,
                "logs": paginated_logs
            }
        
        except Exception as e:
            logger.error(f"读取错误日志失败: {e}", exc_info=True)
            return {
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "total": 0,
                "count": 0,
                "offset": 0,
                "logs": [],
                "error": str(e)
            }
    
    def get_available_dates(self) -> List[str]:
        """
        获取所有可用的日志日期
        
        Returns:
            List[str]: 日期列表，格式 YYYY-MM-DD
        """
        try:
            if not self.log_dir.exists():
                return []
            
            dates = []
            for dir_path in self.log_dir.iterdir():
                if dir_path.is_dir() and dir_path.name.endswith("_log"):
                    # 解析目录名：YY_MM_DD_log -> YYYY-MM-DD
                    try:
                        date_str = dir_path.name.replace("_log", "")
                        dt = datetime.strptime(date_str, "%y_%m_%d")
                        dates.append(dt.strftime("%Y-%m-%d"))
                    except ValueError:
                        continue
            
            # 按日期倒序排列
            dates.sort(reverse=True)
            return dates
        
        except Exception as e:
            logger.error(f"获取可用日期失败: {e}")
            return []
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        获取错误日志统计信息
        
        Returns:
            Dict: {
                "total_errors": 总错误数（所有历史错误）,
                "today_errors": 今日错误数,
                "error_rate": 错误率（今日错误数占总错误数的百分比）,
                "recent_errors": 最近错误列表（今日最新的10条）,
                "today_date": "2025-10-26",
                "available_dates": 可用日期列表
            }
        """
        try:
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            # 获取所有可用日期
            available_dates = self.get_available_dates()
            
            # 统计总错误数（所有历史日期）
            total_errors = 0
            for date in available_dates:
                log_dir = self._get_log_dir(date)
                if log_dir and log_dir.exists():
                    error_file = log_dir / "error.json"
                    if error_file.exists():
                        with open(error_file, 'r', encoding='utf-8') as f:
                            total_errors += sum(1 for line in f if line.strip())
            
            # 获取今日错误数和最近错误
            today_result = self.get_error_logs(date=None, limit=10, offset=0)
            today_errors = today_result.get("total", 0)
            recent_errors = today_result.get("logs", [])
            
            # 计算错误率（今日错误占总错误的百分比）
            error_rate = 0.0
            if total_errors > 0:
                error_rate = round((today_errors / total_errors) * 100, 2)
            
            # 统计今日错误的级别分布
            error_level_stats = {}
            for error in recent_errors:
                level_obj = error.get("record", {}).get("level", {})
                # level 可能是字典 {"name": "ERROR", ...} 或字符串
                if isinstance(level_obj, dict):
                    level = level_obj.get("name", "UNKNOWN")
                else:
                    level = str(level_obj) if level_obj else "UNKNOWN"
                error_level_stats[level] = error_level_stats.get(level, 0) + 1
            
            # 统计今日错误的时间分布（按小时）
            error_hour_stats = {}
            for error in recent_errors:
                # 从 record.time.repr 提取时间
                time_obj = error.get("record", {}).get("time", {})
                if isinstance(time_obj, dict):
                    timestamp = time_obj.get("repr", "")
                else:
                    timestamp = ""
                
                try:
                    # 处理时间字符串，例如 "2025-10-26 10:39:39.561511+08:00"
                    if timestamp:
                        dt = datetime.fromisoformat(str(timestamp))
                        hour = dt.strftime("%H:00")
                        error_hour_stats[hour] = error_hour_stats.get(hour, 0) + 1
                except Exception:
                    continue
            
            return {
                "total_errors": total_errors,
                "today_errors": today_errors,
                "error_rate": error_rate,
                "recent_errors": recent_errors,
                "today_date": today_date,
                "available_dates": available_dates,
                "error_level_stats": error_level_stats,
                "error_hour_stats": dict(sorted(error_hour_stats.items()))
            }
        
        except Exception as e:
            logger.error(f"获取错误统计信息失败: {e}", exc_info=True)
            return {
                "total_errors": 0,
                "today_errors": 0,
                "error_rate": 0.0,
                "recent_errors": [],
                "today_date": datetime.now().strftime("%Y-%m-%d"),
                "available_dates": [],
                "error_level_stats": {},
                "error_hour_stats": {},
                "error": str(e)
            }


# 全局单例
log_service = LogService()

