"""
Milvus 索引配置
针对不同数据规模的优化方案
"""

# 索引配置字典
INDEX_CONFIGS = {
    # 小规模：< 10万 条数据
    "small": {
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "index_params": {
            "nlist": 1024  # 聚类中心数量
        },
        "search_params": {
            "nprobe": 10  # 搜索的聚类数量
        },
        "description": "适合小数据量，精确度高，内存占用少",
        "memory_estimate": "全量加载，约 4KB/向量"
    },
    
    # 中规模：10万 - 100万 条数据
    "medium": {
        "index_type": "IVF_SQ8",  # 使用标量量化，减少内存
        "metric_type": "COSINE",
        "index_params": {
            "nlist": 2048
        },
        "search_params": {
            "nprobe": 16
        },
        "description": "使用标量量化，内存减少 75%",
        "memory_estimate": "约 1KB/向量（压缩后）"
    },
    
    # 大规模：100万 - 1000万 条数据
    "large": {
        "index_type": "HNSW",  # 图索引，性能最好
        "metric_type": "COSINE",
        "index_params": {
            "M": 16,           # 每个节点的邻居数
            "efConstruction": 256  # 构建时的候选数
        },
        "search_params": {
            "ef": 64          # 搜索时的候选数
        },
        "description": "图索引，速度快，适合大规模",
        "memory_estimate": "约 5KB/向量，但搜索极快"
    },
    
    # 超大规模：> 1000万 条数据
    "xlarge": {
        "index_type": "IVF_PQ",  # 乘积量化，内存最小
        "metric_type": "COSINE",
        "index_params": {
            "nlist": 4096,
            "m": 8,            # 子向量数量
            "nbits": 8         # 每个子向量的位数
        },
        "search_params": {
            "nprobe": 32
        },
        "description": "极限压缩，内存减少 97%，精度略降",
        "memory_estimate": "约 128 bytes/向量（极限压缩）"
    },
}


def get_index_config(data_size: int) -> dict:
    """
    根据数据量自动选择索引配置
    
    Args:
        data_size: 预计数据量（条数）
        
    Returns:
        dict: 索引配置
    """
    if data_size < 100_000:
        return INDEX_CONFIGS["small"]
    elif data_size < 1_000_000:
        return INDEX_CONFIGS["medium"]
    elif data_size < 10_000_000:
        return INDEX_CONFIGS["large"]
    else:
        return INDEX_CONFIGS["xlarge"]


def estimate_memory(data_size: int, dimension: int = 1024) -> str:
    """
    估算内存占用
    
    Args:
        data_size: 数据量
        dimension: 向量维度
        
    Returns:
        str: 内存估算
    """
    config = get_index_config(data_size)
    index_type = config["index_type"]
    
    # 不同索引的内存系数（bytes per dimension）
    memory_factors = {
        "IVF_FLAT": 4,      # float32: 4 bytes/dim
        "IVF_SQ8": 1,       # int8: 1 byte/dim
        "HNSW": 5,          # float32 + graph: ~5 bytes/dim
        "IVF_PQ": 0.125,    # m=8, nbits=8: dimension/8 bytes
    }
    
    factor = memory_factors.get(index_type, 4)
    memory_mb = (data_size * dimension * factor) / (1024 * 1024)
    
    if memory_mb < 1024:
        return f"{memory_mb:.2f} MB"
    else:
        return f"{memory_mb / 1024:.2f} GB"


# 分区策略配置
PARTITION_STRATEGIES = {
    "by_time": {
        "description": "按时间分区（如按月）",
        "example": ["2024_01", "2024_02", "2024_03"],
        "benefit": "查询时只搜索相关时间段，减少搜索范围"
    },
    "by_category": {
        "description": "按类别分区（如按文档类型）",
        "example": ["通知", "政策", "新闻"],
        "benefit": "可以只在特定类别中搜索"
    },
    "by_source": {
        "description": "按来源分区",
        "example": ["学院A", "学院B", "学院C"],
        "benefit": "权限控制和分类检索"
    }
}


def print_recommendations(data_size: int):
    """打印推荐配置"""
    config = get_index_config(data_size)
    memory = estimate_memory(data_size)
    
    print(f"\n{'='*60}")
    print(f"数据量: {data_size:,} 条")
    print(f"推荐索引: {config['index_type']}")
    print(f"预估内存: {memory}")
    print(f"说明: {config['description']}")
    print(f"{'='*60}\n")
    
    # 超过 100 万建议使用分区
    if data_size > 1_000_000:
        print("⚠️  建议使用分区（Partition）策略：")
        print("   - 将数据按时间/类别分区")
        print("   - 查询时只搜索相关分区")
        print("   - 可以大幅减少内存占用和提升速度")


if __name__ == "__main__":
    # 测试不同数据量的配置
    test_sizes = [10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]
    
    for size in test_sizes:
        print_recommendations(size)

