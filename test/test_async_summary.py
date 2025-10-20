"""
测试异步历史记录总结功能
"""
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from internal.llm.llm_service import LLMService
from pkg.agent_prompt.agent_tool import knowledge_search


async def test_auto_summary():
    """测试自动总结功能"""
    print("=" * 80)
    print("测试异步历史记录总结")
    print("=" * 80)
    
    # 创建服务，设置较小的阈值便于测试
    llm = LLMService(
        model_name="deepseek-chat",
        model_type="cloud",
        auto_summary=True,
        max_history_count=8,  # 8条消息就触发总结
        max_history_tokens=1000  # 或者1000 token
    )
    
    print("\n⚙️  配置:")
    print(f"  自动总结: 是")
    print(f"  最大历史条数: 8")
    print(f"  最大历史 token: 1000")
    
    # 模拟更多轮对话，内容更丰富
    conversations = [
        ("你好，我叫张三，我想学习 FastAPI", 
         "你好张三！很高兴认识你。FastAPI 是一个现代、快速的 Web 框架，用于构建 API。它基于 Python 3.6+ 的类型提示，性能接近 NodeJS 和 Go。主要特点包括：自动文档生成、数据验证、异步支持等。"),
        
        ("FastAPI 和 Flask 有什么区别？", 
         "FastAPI 和 Flask 的主要区别在于：1) FastAPI 原生支持异步，性能更好；2) FastAPI 基于类型提示，自动生成文档和数据验证；3) Flask 更轻量，社区更成熟；4) FastAPI 更适合构建现代 RESTful API 和微服务。"),
        
        ("我想用 FastAPI 开发一个用户管理系统，应该如何设计数据库？", 
         "开发用户管理系统，建议使用以下数据库设计：1) 用户表 (users)：包含 id、username、email、password_hash、created_at 等字段；2) 角色表 (roles)：id、name、permissions；3) 用户角色关联表；4) 使用 SQLAlchemy 或 Tortoise ORM 作为 ORM 框架；5) 密码使用 bcrypt 加密存储。"),
        
        ("能详细说说 FastAPI 的依赖注入吗？", 
         "FastAPI 的依赖注入非常强大！它通过 Depends() 实现。主要用途：1) 共享数据库连接；2) 用户认证；3) 参数验证；4) 权限检查。例如：def get_db(): return database; @app.get('/users'); async def read_users(db = Depends(get_db)): ...。依赖项可以嵌套，形成依赖树。"),
        
        ("我的项目需要实现 JWT 认证，有什么建议吗？", 
         "实现 JWT 认证的建议：1) 使用 python-jose 库生成和验证 token；2) 创建 /login 端点返回 access_token；3) 使用 Depends(get_current_user) 保护需要认证的路由；4) 设置合理的过期时间（如30分钟）；5) 考虑实现 refresh token 机制；6) 敏感操作需要二次验证。"),
        
        ("在开发过程中，如何调试 FastAPI 应用？", 
         "调试 FastAPI 应用的方法：1) 使用 uvicorn --reload 实现热重载；2) 利用自动生成的 /docs 接口测试 API；3) 使用 logging 或 loguru 记录日志；4) PyCharm/VSCode 配置断点调试；5) 使用 pytest 编写单元测试；6) 利用 FastAPI 的异常处理机制捕获错误。"),
        
        ("项目部署时，生产环境应该注意什么？", 
         "生产环境部署注意事项：1) 使用 gunicorn + uvicorn worker 运行；2) 配置 Nginx 反向代理；3) 启用 HTTPS（Let's Encrypt）；4) 设置环境变量管理配置；5) 使用 Docker 容器化部署；6) 配置日志收集；7) 设置监控告警（如 Prometheus）；8) 定期备份数据库。"),
        
        ("非常感谢你的详细解答，我学到了很多！", 
         "不客气，张三！很高兴能帮到你。FastAPI 是一个非常优秀的框架，建议你：1) 多看官方文档；2) 实践小项目；3) 关注异步编程；4) 学习类型提示。祝你开发顺利！有问题随时问我。")
    ]
    
    print("\n" + "=" * 80)
    print("📝 第一阶段：模拟多轮对话（会触发自动总结）")
    print("=" * 80)
    
    for i, (user_msg, assistant_msg) in enumerate(conversations, 1):
        print(f"\n第 {i} 轮对话:")
        print(f"  👤 用户: {user_msg}")
        print(f"  🤖 助手: {assistant_msg[:60]}...")
        
        # 添加到历史
        llm.add_to_history("user", user_msg)
        llm.add_to_history("assistant", assistant_msg)
        
        # 显示统计
        stats = llm.get_history_stats()
        print(f"  📊 历史记录: {stats['count']} 条, {stats['total_tokens']} tokens")
        
        # 等待一下，让异步总结有机会执行
        await asyncio.sleep(0.5)
        
        # 如果正在总结
        if stats['is_summarizing']:
            print(f"  ⏳ 触发总结！正在后台总结历史记录...")
            await asyncio.sleep(3)  # 等待总结完成
    
    # 确保总结完成
    print("\n⏳ 等待总结完成...")
    await asyncio.sleep(2)
    
    # 显示总结后的状态
    print("\n" + "=" * 80)
    print("📋 总结后的历史记录状态")
    print("=" * 80)
    
    final_stats = llm.get_history_stats()
    print(f"\n历史记录统计:")
    print(f"  条数: {final_stats['count']}/{final_stats['max_count']}")
    print(f"  Token: {final_stats['total_tokens']}/{final_stats['max_tokens']}")
    
    history = llm.get_history()
    print(f"\n当前历史记录内容 (共 {len(history)} 条):")
    print("-" * 80)
    for i, msg in enumerate(history, 1):
        role_icon = "👤" if msg['role'] == 'user' else "🤖" if msg['role'] == 'assistant' else "📝"
        print(f"\n{role_icon} [{msg['role'].upper()}]:")
        print(f"{msg['content']}")
        print("-" * 80)
    
    # 第二阶段：基于总结的历史继续对话
    print("\n" + "=" * 80)
    print("🔄 第二阶段：验证 AI 是否记得总结的内容")
    print("=" * 80)
    
    # 测试问题：验证 AI 是否记得之前对话的内容
    test_questions = [
        "我叫什么名字？",
        "我们之前讨论过数据库设计吗？",
        "你给我推荐了哪些部署方案？"
    ]
    
    for question in test_questions:
        print(f"\n👤 用户追问: {question}")
        
        # 构建消息列表（包含历史记录）
        messages = llm.get_history().copy()
        messages.append({"role": "user", "content": question})
        
        print(f"🤖 助手回答: ", end="", flush=True)
        
        # 流式输出回答
        response_text = ""
        try:
            for chunk in llm.chat(messages, stream=True):
                print(chunk, end="", flush=True)
                response_text += chunk
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            response_text = "抱歉，我无法回答这个问题。"
        
        print()  # 换行
        
        # 添加到历史
        llm.add_to_history("user", question)
        llm.add_to_history("assistant", response_text)
        
        await asyncio.sleep(1)
    
    print("\n✅ 测试完成！")
    print("\n💡 观察要点：")
    print("  1. 总结是否保留了关键信息（用户名、讨论主题等）")
    print("  2. AI 在后续对话中是否能基于总结回答问题")
    print("  3. 历史记录数量是否大幅减少（从多条压缩到少量总结）")


async def test_manual_summary():
    """测试手动触发总结"""
    print("\n" + "=" * 60)
    print("测试手动总结")
    print("=" * 60)
    
    llm = LLMService(
        model_name="deepseek-chat",
        model_type="cloud",
        auto_summary=False  # 关闭自动总结
    )
    
    # 添加一些历史
    llm.add_to_history("user", "什么是机器学习？")
    llm.add_to_history("assistant", "机器学习是人工智能的一个分支...")
    llm.add_to_history("user", "它有哪些应用？")
    llm.add_to_history("assistant", "应用包括：图像识别、语音识别...")
    
    print(f"\n添加历史前: {len(llm.get_history())} 条")
    
    # 手动触发总结
    print("\n手动触发总结...")
    await llm._summarize_history_async()
    
    print(f"总结后: {len(llm.get_history())} 条")
    
    history = llm.get_history()
    if history:
        print(f"\n总结内容:\n{history[0]['content']}")



async def main():
    """主函数"""
    print("\n🚀 开始测试异步历史记录总结功能\n")
    
    # 测试自动总结
    await test_auto_summary()
    
    # 测试手动总结
    # await test_manual_summary()
    
    # 测试 token 限制
    # await test_token_limit()
    
    print("\n✅ 所有测试完成！\n")


if __name__ == "__main__":
    asyncio.run(main())

