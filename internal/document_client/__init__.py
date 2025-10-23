"""
消息客户端模块
支持 Channel（内存队列）和 Kafka（分布式队列）两种模式
"""
from internal.document_client.config_loader import config
from internal.document_client.message_client import message_client
from internal.document_client.document_processor import document_processor

__all__ = [
    'config',
    'message_client',
    'document_processor'
]

