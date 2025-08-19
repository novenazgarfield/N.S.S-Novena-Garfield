#!/usr/bin/env python3
"""
配置管理工具
用于设置API密钥、模型路径等配置
"""
import os
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config_advanced import APIConfig, ModelConfig, save_config_to_file, load_config_from_file

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🔧 RAG系统配置管理工具")
    print("=" * 60)

def show_current_config():
    """显示当前配置"""
    print("\n📋 当前配置:")
    print(f"当前API类型: {ModelConfig.CURRENT_API}")
    
    for api_type, api_name in APIConfig.API_TYPES.items():
        config = APIConfig.get_config(api_type)
        print(f"\n{api_name} ({api_type}):")
        
        if api_type == "local":
            print(f"  模型路径: {config.get('model_path', '未配置')}")
            print(f"  设备: {config.get('device', 'cuda:0')}")
            print(f"  GPU层数: {config.get('n_gpu_layers', 30)}")
        else:
            print(f"  API密钥: {'已配置' if config.get('api_key') else '未配置'}")
            print(f"  基础URL: {config.get('base_url', '未配置')}")
            print(f"  模型: {config.get('model', '未配置')}")

def configure_local_model():
    """配置本地模型"""
    print("\n🤖 配置本地模型")
    
    current_config = APIConfig.get_config("local")
    
    # 模型路径
    current_path = current_config.get("model_path", "")
    print(f"当前模型路径: {current_path}")
    
    new_path = input("请输入新的模型路径 (回车保持不变): ").strip()
    if new_path:
        if Path(new_path).exists():
            current_config["model_path"] = new_path
            print("✅ 模型路径已更新")
        else:
            print("❌ 文件不存在，请检查路径")
            return
    
    # 设备配置
    current_device = current_config.get("device", "cuda:0")
    print(f"当前设备: {current_device}")
    
    new_device = input("请输入设备 (cuda:0/cuda:1/cpu, 回车保持不变): ").strip()
    if new_device:
        current_config["device"] = new_device
        print("✅ 设备配置已更新")
    
    # GPU层数
    current_layers = current_config.get("n_gpu_layers", 30)
    print(f"当前GPU层数: {current_layers}")
    
    new_layers = input("请输入GPU层数 (回车保持不变): ").strip()
    if new_layers:
        try:
            current_config["n_gpu_layers"] = int(new_layers)
            print("✅ GPU层数已更新")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    APIConfig.set_config("local", current_config)

def configure_api(api_type: str):
    """配置API"""
    api_name = APIConfig.API_TYPES.get(api_type, api_type)
    print(f"\n🌐 配置 {api_name}")
    
    current_config = APIConfig.get_config(api_type)
    
    # API密钥
    current_key = current_config.get("api_key", "")
    masked_key = f"{current_key[:8]}..." if current_key else "未配置"
    print(f"当前API密钥: {masked_key}")
    
    new_key = input("请输入API密钥 (回车保持不变): ").strip()
    if new_key:
        current_config["api_key"] = new_key
        print("✅ API密钥已更新")
    
    # 基础URL
    current_url = current_config.get("base_url", "")
    print(f"当前基础URL: {current_url}")
    
    new_url = input("请输入基础URL (回车保持不变): ").strip()
    if new_url:
        current_config["base_url"] = new_url
        print("✅ 基础URL已更新")
    
    # 模型名称
    current_model = current_config.get("model", "")
    print(f"当前模型: {current_model}")
    
    new_model = input("请输入模型名称 (回车保持不变): ").strip()
    if new_model:
        current_config["model"] = new_model
        print("✅ 模型名称已更新")
    
    APIConfig.set_config(api_type, current_config)

def set_environment_variables():
    """设置环境变量"""
    print("\n🔐 设置环境变量")
    print("您可以设置以下环境变量来配置API密钥:")
    
    env_vars = {
        "MODELSCOPE_API_KEY": "魔搭API密钥",
        "OPENAI_API_KEY": "OpenAI API密钥", 
        "ZHIPU_API_KEY": "智谱API密钥",
        "RAG_API_TYPE": "默认API类型"
    }
    
    for var, desc in env_vars.items():
        current_value = os.getenv(var, "")
        masked_value = f"{current_value[:8]}..." if current_value else "未设置"
        print(f"{desc} ({var}): {masked_value}")
        
        new_value = input(f"请输入新值 (回车保持不变): ").strip()
        if new_value:
            os.environ[var] = new_value
            print(f"✅ {var} 已设置")

def switch_default_api():
    """切换默认API"""
    print("\n🔄 切换默认API")
    
    print("可用的API类型:")
    api_list = list(APIConfig.API_TYPES.items())
    for i, (api_type, api_name) in enumerate(api_list, 1):
        current_mark = " (当前)" if api_type == ModelConfig.CURRENT_API else ""
        print(f"{i}. {api_name} ({api_type}){current_mark}")
    
    try:
        choice = int(input("请选择API类型 (输入数字): ")) - 1
        if 0 <= choice < len(api_list):
            new_api = api_list[choice][0]
            ModelConfig.switch_api(new_api)
            print(f"✅ 默认API已切换到: {APIConfig.API_TYPES[new_api]}")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入有效数字")

def quick_setup():
    """快速设置"""
    print("\n⚡ 快速设置向导")
    print("这将帮助您快速配置最常用的选项")
    
    # 1. 选择主要使用的API类型
    print("\n1. 您主要想使用哪种API?")
    print("1. 本地模型 (需要下载模型文件)")
    print("2. 魔搭API (需要API密钥)")
    print("3. OpenAI API (需要API密钥)")
    
    try:
        choice = int(input("请选择 (1-3): "))
        
        if choice == 1:
            # 配置本地模型
            model_path = input("请输入DeepSeek 7B Q5模型文件路径: ").strip()
            if model_path and Path(model_path).exists():
                config = APIConfig.get_config("local")
                config["model_path"] = model_path
                config["device"] = "cuda:0"  # 3090
                config["n_gpu_layers"] = 35
                APIConfig.set_config("local", config)
                ModelConfig.switch_api("local")
                print("✅ 本地模型配置完成")
            else:
                print("❌ 模型文件不存在")
        
        elif choice == 2:
            # 配置魔搭API
            api_key = input("请输入魔搭API密钥: ").strip()
            if api_key:
                config = APIConfig.get_config("modelscope")
                config["api_key"] = api_key
                APIConfig.set_config("modelscope", config)
                ModelConfig.switch_api("modelscope")
                print("✅ 魔搭API配置完成")
            else:
                print("❌ API密钥不能为空")
        
        elif choice == 3:
            # 配置OpenAI API
            api_key = input("请输入OpenAI API密钥: ").strip()
            if api_key:
                config = APIConfig.get_config("openai")
                config["api_key"] = api_key
                APIConfig.set_config("openai", config)
                ModelConfig.switch_api("openai")
                print("✅ OpenAI API配置完成")
            else:
                print("❌ API密钥不能为空")
        
        else:
            print("❌ 无效选择")
            return
        
        # 2. 保存配置
        save_config_to_file()
        print("✅ 配置已保存")
        
    except ValueError:
        print("❌ 请输入有效数字")

def main():
    """主函数"""
    print_banner()
    
    # 加载现有配置
    load_config_from_file()
    
    while True:
        print("\n📋 请选择操作:")
        print("1. 显示当前配置")
        print("2. 快速设置向导")
        print("3. 配置本地模型")
        print("4. 配置魔搭API")
        print("5. 配置OpenAI API")
        print("6. 配置智谱API")
        print("7. 切换默认API")
        print("8. 设置环境变量")
        print("9. 保存配置")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-9): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                show_current_config()
            elif choice == "2":
                quick_setup()
            elif choice == "3":
                configure_local_model()
            elif choice == "4":
                configure_api("modelscope")
            elif choice == "5":
                configure_api("openai")
            elif choice == "6":
                configure_api("zhipu")
            elif choice == "7":
                switch_default_api()
            elif choice == "8":
                set_environment_variables()
            elif choice == "9":
                save_config_to_file()
                print("✅ 配置已保存")
            else:
                print("❌ 无效选择，请重新输入")
        
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()