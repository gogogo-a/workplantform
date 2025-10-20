"""
测试简化版 LLM 服务
演示提示词和工具的配对使用
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.llm.llm_service import LLMService
from pkg.agent_prompt.agent_tool import (
    list_all_tools,
    knowledge_search,
    document_analyzer,
    code_executor
)
from pkg.agent_prompt.prompt_templates import (
    DEFAULT_PROMPT,
    RAG_PROMPT,
    CODE_PROMPT,
    DOCUMENT_PROMPT
)


def test_basic_chat():
    """测试基础对话"""
    print("=" * 60)
    print("1️⃣ 测试基础对话（无工具）")
    print("=" * 60)
    
    try:
        # 不使用任何工具
        llm = LLMService(
            model_name="llama3.2",
            model_type="local"
        )
        
        # 显示配置
        info = llm.get_info()
        print(f"\n模型: {info['model_name']} ({info['model_type']})")
        print(f"工具: {info['tools'] if info['tools'] else '无'}")
        print(f"提示词: {info['system_prompt'][:80]}...")
        
        # 对话
        messages = [{"role": "user", "content": "你好，请简单介绍一下自己"}]
        
        print(f"\n用户: {messages[0]['content']}")
        print("助手: ", end="", flush=True)
        
        for chunk in llm.chat(messages, stream=True):
            print(chunk, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_rag_with_tool():
    """测试 RAG 工具"""
    print("\n" + "=" * 60)
    print("2️⃣ 测试 RAG 工具（知识库检索）")
    print("=" * 60)
    
    try:
        # 使用知识库搜索工具（可以直接点击函数名跳转）
        llm = LLMService(
            model_name="llama3.2",
            model_type="local",
            tools=[knowledge_search]  # 直接传入函数引用，IDE 可以点击跳转
        )
        
        info = llm.get_info()
        print(f"\n模型: {info['model_name']}")
        print(f"工具: {info['tools']}")
        print(f"提示词: {info['system_prompt'][:80]}...")
        
        # 模拟知识库上下文
        knowledge_context = """
【知识片段1】
RAG（检索增强生成）结合了信息检索和文本生成技术。

【知识片段2】
RAG 的优势：减少幻觉、提供可追溯来源、无需重训练。
"""
        
        messages = [{"role": "user", "content": "什么是RAG？"}]
        
        print(f"\n用户: {messages[0]['content']}")
        print("助手: ", end="", flush=True)
        
        for chunk in llm.chat(messages, context=knowledge_context, stream=True):
            print(chunk, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_code_tool():
    """测试代码工具"""
    print("\n" + "=" * 60)
    print("3️⃣ 测试代码工具")
    print("=" * 60)
    
    try:
        # 使用代码执行工具（可以 Cmd+点击跳转）
        llm = LLMService(
            model_name="llama3.2",
            model_type="local",
            tools=[code_executor]  # 直接传入函数引用
        )
        
        info = llm.get_info()
        print(f"\n模型: {info['model_name']}")
        print(f"工具: {info['tools']}")
        print(f"提示词模板: code")
        
        messages = [{"role": "user", "content": "如何优化Python代码性能？"}]
        
        print(f"\n用户: {messages[0]['content']}")
        print("助手: ", end="", flush=True)
        
        for chunk in llm.chat(messages, stream=True):
            print(chunk, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_custom_prompt():
    """测试自定义提示词"""
    print("\n" + "=" * 60)
    print("4️⃣ 测试自定义提示词")
    print("=" * 60)
    
    try:
        # 直接使用提示词常量（可以 Cmd+点击跳转）
        llm = LLMService(
            model_name="llama3.2",
            model_type="local",
            system_prompt=DEFAULT_PROMPT,  # 点击可跳转到提示词定义
            tools=[knowledge_search, document_analyzer]  # 可以传入多个工具
        )
        
        info = llm.get_info()
        print(f"\n模型: {info['model_name']}")
        print(f"工具: {info['tools']}")
        print(f"自定义提示词: 是")
        
        messages = [{"role": "user", "content": "无人机如何实现自主导航？"}]
        
        print(f"\n用户: {messages[0]['content']}")
        print("助手: ", end="", flush=True)
        
        for chunk in llm.chat(messages, stream=True):
            print(chunk, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_list_tools():
    """列出所有可用工具"""
    print("\n" + "=" * 60)
    print("5️⃣ 查看所有可用工具")
    print("=" * 60)
    
    tools = list_all_tools()
    print(f"\n共有 {len(tools)} 个可用工具:\n")
    
    for tool in tools:
        print(f"工具名: {tool['name']}")
        print(f"  描述: {tool['description']}")
        print(f"  提示词: {tool['prompt_template']}")
        print()


def main():
    """主函数"""
    print("\n🚀 开始测试简化版 LLM 服务\n")
    
    # 测试基础对话
    test_basic_chat()
    
    # 测试 RAG 工具
    test_rag_with_tool()
    
    # 测试代码工具
    test_code_tool()
    
    # 测试自定义提示词
    test_custom_prompt()
    
    # 列出所有工具
    test_list_tools()
    
    print("\n✅ 所有测试完成！\n")


if __name__ == "__main__":
    main()

