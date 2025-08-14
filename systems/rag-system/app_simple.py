"""
RAG系统简化版前端 - 用于演示核心功能
"""
import sys
from pathlib import Path
import os

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量避免一些警告
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

def main():
    """主函数"""
    print("🚀 启动RAG系统简化版...")
    
    try:
        from config import init_config, StorageConfig, ModelConfig
        from database.chat_db import ChatDatabase
        from memory.memory_manager import MemoryManager
        
        # 初始化配置
        init_config()
        print("✅ 配置初始化完成")
        
        # 初始化组件
        db = ChatDatabase()
        memory = MemoryManager()
        
        print("✅ 核心组件初始化完成")
        print(f"📁 数据目录: {StorageConfig.DATA_DIR}")
        print(f"🤖 嵌入模型: {ModelConfig.EMBEDDING_MODEL_PATH}")
        print(f"🧠 LLM模型: {ModelConfig.LLM_MODEL_PATH or '未配置'}")
        
        # 简单的命令行交互
        print("\n" + "="*50)
        print("🎯 RAG系统简化版演示")
        print("输入 'quit' 退出，'help' 查看帮助")
        print("="*50)
        
        while True:
            try:
                user_input = input("\n🤔 请输入问题: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if user_input.lower() == 'help':
                    print("""
📖 可用命令:
- help: 显示帮助信息
- stats: 显示系统统计
- memory: 显示记忆统计
- clear: 清除当前任务数据
- quit/exit/q: 退出系统
                    """)
                    continue
                
                if user_input.lower() == 'stats':
                    print("\n📊 系统统计:")
                    print(f"  - 数据目录: {StorageConfig.DATA_DIR}")
                    print(f"  - 数据库路径: {StorageConfig.CHAT_DB_PATH}")
                    print(f"  - 记忆目录: {StorageConfig.MEMORY_DIR}")
                    continue
                
                if user_input.lower() == 'memory':
                    stats = memory.get_memory_stats()
                    print(f"\n🧠 记忆统计: {stats}")
                    continue
                
                if user_input.lower() == 'clear':
                    memory.clear_temporary_memory("demo")
                    print("✅ 当前任务数据已清除")
                    continue
                
                if not user_input:
                    continue
                
                # 模拟处理问题
                print(f"🔍 正在处理问题: {user_input}")
                
                # 保存到记忆
                memory.save_temporary_memory(f"用户问题: {user_input}", "demo")
                
                # 模拟回答（因为没有LLM模型）
                answer = f"""
🤖 模拟回答:

您的问题是: "{user_input}"

由于当前系统配置为演示模式（未配置LLM模型），这是一个模拟回答。

在完整配置的系统中，会执行以下步骤:
1. 📄 文档检索: 从向量数据库中搜索相关文档
2. 🧠 记忆加载: 加载相关的历史对话和记忆
3. 🤖 智能生成: 使用LLM模型生成基于上下文的回答

当前系统状态:
- ✅ 数据库功能正常
- ✅ 记忆系统正常  
- ⚠️  向量检索需要配置嵌入模型
- ⚠️  智能回答需要配置LLM模型

要启用完整功能，请:
1. 配置嵌入模型路径 (如 multilingual-e5-large)
2. 配置LLM模型路径 (如 deepseek-llm-7b-chat.gguf)
3. 上传文档到文献库
                """
                
                print(answer)
                
                # 保存回答到记忆
                memory.save_temporary_memory(f"系统回答: {answer[:100]}...", "demo")
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 处理错误: {e}")
        
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)