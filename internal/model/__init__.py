"""
数据模型包
包含所有 Beanie ODM 模型
"""
from internal.model.document import DocumentModel
from internal.model.message import MessageModel
from internal.model.user_info import UserInfoModel

__all__ = [
    "DocumentModel",
    "MessageModel",
    "UserInfoModel"
]

