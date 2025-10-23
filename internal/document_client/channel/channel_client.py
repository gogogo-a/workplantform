"""
Channel 模式客户端 - 使用 Python Queue 实现单机内存队列
"""
import queue
import threading
import time
from typing import Callable, Dict, Any, Optional
from log import logger


class ChannelClient:
    """Channel 客户端（单例模式）"""
    
    _instance: Optional['ChannelClient'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_size: int = 1000, timeout: int = 5):
        if self._initialized:
            return
        
        self.max_size = max_size
        self.timeout = timeout
        self.queue = queue.Queue(maxsize=max_size)
        self.running = False
        self.consumers = []
        
        self._initialized = True
        logger.info(f"Channel 客户端已初始化，队列大小: {max_size}")
    
    def send_message(self, message: Dict[str, Any], block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        发送消息到队列
        
        Args:
            message: 消息字典
            block: 是否阻塞等待
            timeout: 超时时间（秒）
        
        Returns:
            bool: 是否成功入队
        """
        try:
            if timeout is None:
                timeout = self.timeout
            
            self.queue.put(message, block=block, timeout=timeout)
            logger.debug(f"消息已入队，当前队列大小: {self.queue.qsize()}")
            return True
            
        except queue.Full:
            logger.warning(f"队列已满（{self.max_size}），消息入队失败")
            return False
        except Exception as e:
            logger.error(f"消息入队失败: {e}", exc_info=True)
            return False
    
    def start_consumer(self, handler: Callable[[Dict[str, Any]], None], num_consumers: int = 1):
        """
        启动消费者线程
        
        Args:
            handler: 消息处理函数
            num_consumers: 消费者数量
        """
        if self.running:
            logger.warning("消费者已在运行中")
            return
        
        self.running = True
        
        for i in range(num_consumers):
            consumer_thread = threading.Thread(
                target=self._consume_loop,
                args=(handler, i),
                daemon=True,
                name=f"ChannelConsumer-{i}"
            )
            consumer_thread.start()
            self.consumers.append(consumer_thread)
        
        logger.info(f"已启动 {num_consumers} 个消费者线程")
    
    def _consume_loop(self, handler: Callable[[Dict[str, Any]], None], consumer_id: int):
        """
        消费者循环
        
        Args:
            handler: 消息处理函数
            consumer_id: 消费者ID
        """
        logger.info(f"消费者 {consumer_id} 已启动")
        
        while self.running:
            try:
                # 从队列获取消息（阻塞，带超时）
                message = self.queue.get(timeout=1)
                
                try:
                    # 处理消息
                    handler(message)
                    logger.debug(f"消费者 {consumer_id} 处理消息成功")
                except Exception as e:
                    logger.error(f"消费者 {consumer_id} 处理消息失败: {e}", exc_info=True)
                finally:
                    # 标记任务完成
                    self.queue.task_done()
                    
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                logger.error(f"消费者 {consumer_id} 异常: {e}", exc_info=True)
                time.sleep(1)
        
        logger.info(f"消费者 {consumer_id} 已停止")
    
    def stop(self):
        """停止消费者"""
        logger.info("正在停止 Channel 客户端...")
        self.running = False
        
        # 等待所有消费者线程结束
        for consumer in self.consumers:
            consumer.join(timeout=5)
        
        # 等待队列中的任务处理完成
        self.queue.join()
        
        logger.info("Channel 客户端已停止")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        return {
            "mode": "channel",
            "queue_size": self.queue.qsize(),
            "max_size": self.max_size,
            "num_consumers": len(self.consumers),
            "running": self.running
        }


# 创建全局实例
channel_client = ChannelClient()

