"""
全局常量配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Token 限制配置
MAX_TOKEN = int(os.getenv("MAX_TOKEN_LIMIT_FOR_SUMMARY", "6400"))

# MongoDB 配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:rootpassword@localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "rag_platform")

# Milvus 向量数据库配置
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_USER = os.getenv("MILVUS_USER", "root")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "rootpassword")
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "rag_platform")
