"""
Google Colab 运行脚本
在 Colab 中运行此代码块

注意：此文件包含Jupyter/Colab魔法命令，不能直接用Python运行
"""

import subprocess
import sys

def setup_colab_environment():
    """设置Colab环境"""
    
    # 安装依赖
    subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "pyngrok"])
    
    # 下载便携版本
    subprocess.run(["wget", "https://raw.githubusercontent.com/novenazgarfield/research-workstation/main/rag_portable.py"])
    
    print("Colab环境设置完成")
    print("请在Colab中使用以下魔法命令:")
    print("!pip install streamlit pyngrok")
    print("!wget https://raw.githubusercontent.com/novenazgarfield/research-workstation/main/rag_portable.py")

if __name__ == "__main__":
    setup_colab_environment()
from pyngrok import ngrok
import threading
import subprocess
import time

# 启动 Streamlit
def run_streamlit():
    subprocess.run(["streamlit", "run", "rag_portable.py", "--server.port", "8501"])

# 在后台运行
thread = threading.Thread(target=run_streamlit)
thread.daemon = True
thread.start()

# 等待服务启动
time.sleep(10)

# 创建公共URL
public_url = ngrok.connect(8501)
print(f"🌐 访问地址: {public_url}")