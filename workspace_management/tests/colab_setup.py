# Google Colab 运行脚本
# 在 Colab 中运行此代码块

# 安装依赖
!pip install streamlit pyngrok

# 下载便携版本
!wget https://raw.githubusercontent.com/novenazgarfield/research-workstation/main/rag_portable.py

# 设置 ngrok (需要注册账号获取token)
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