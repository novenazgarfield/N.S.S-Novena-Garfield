# BovineInsight: 多摄像头牛只身份识别与体况评分系统

## 🐄 项目概述

**BovineInsight** 是一个集成的计算机视觉系统，通过分析来自不同位置的多个摄像头数据，自动完成两项核心任务：
1. **身份识别**: 结合耳标与花色特征识别牛的身份
2. **体况评分**: 评估牛的体况评分(BCS - Body Condition Score)

## 🎯 核心目标

- 实现多摄像头协同工作的牛只监控系统
- 建立双重保障的身份识别机制（耳标 + 花色）
- 自动化体况评分，提高养殖效率
- 构建完整的牛只数据档案管理系统

## 🛠️ 技术栈

- **Python**: 主要开发语言
- **OpenCV**: 图像处理和计算机视觉
- **PyTorch**: 深度学习框架
- **YOLOv8**: 目标检测
- **OCR Engine**: 耳标文字识别
- **Siamese Networks/Triplet Loss**: 花色重识别
- **Scikit-learn**: 机器学习算法
- **SQLite/PostgreSQL**: 数据库存储

## 📁 项目结构

```
bovine-insight/
├── src/
│   ├── data_processing/          # 多源数据处理模块
│   ├── detection/                # 牛只检测模块
│   ├── identification/           # 融合身份识别模块
│   ├── body_condition/           # 体况评分模块
│   ├── database/                 # 数据库管理
│   ├── utils/                    # 工具函数
│   └── main.py                   # 主程序入口
├── models/                       # 训练好的模型文件
├── data/                         # 数据集
├── config/                       # 配置文件
├── tests/                        # 测试文件
├── docs/                         # 文档
└── requirements.txt              # 依赖包
```

## 🚀 开发步骤

### 第一步：多源数据处理模块 ✅
- [x] 多视频流同时处理框架
- [x] 摄像头管理和配置
- [x] 图像预处理管道

### 第二步：牛只检测模块 ✅
- [x] YOLOv8牛只检测
- [x] 边界框提取和优化
- [x] 检测结果后处理

### 第三步：融合身份识别模块 🔄
- [x] 耳标识别流水线
- [x] 花色重识别模型
- [x] 双重识别融合逻辑 (框架完成，算法待完善)

### 第四步：体况评分模块 🔄
- [x] 关键点检测模型
- [x] 特征工程
- [x] BCS评分回归模型 (框架完成，模型待训练)

### 第五步：系统集成 🔄
- [x] 牛只数据档案数据库 (基础框架)
- [ ] 智能决策逻辑
- [ ] 结果可视化界面
- [ ] 数据记录和日志系统

## 🔧 安装和使用

### 环境要求
- Python 3.8+
- CUDA 11.0+ (GPU加速)
- 4GB+ RAM
- 多个USB/IP摄像头

### 安装步骤
```bash
# 克隆项目
git clone <repository-url>
cd bovine-insight

# 安装依赖
pip install -r requirements.txt

# 下载预训练模型
python scripts/download_models.py

# 配置摄像头
python scripts/setup_cameras.py

# 运行系统
python src/main.py
```

## 📊 功能特性

### 身份识别
- **耳标识别**: OCR技术读取耳标ID
- **花色识别**: 深度学习模型识别牛只花纹
- **双重验证**: 耳标失效时自动切换花色识别

### 体况评分
- **关键点检测**: 识别髋骨、尾根等解剖标志
- **几何特征**: 基于关键点计算体型指标
- **BCS评分**: 1-5分标准体况评分

### 系统管理
- **多摄像头管理**: 支持多个视频源同时处理
- **数据档案**: 完整的牛只信息数据库
- **实时监控**: 实时显示识别结果和评分
- **历史记录**: 长期数据跟踪和分析

## 🎥 摄像头配置

### 推荐摄像头布局
1. **耳标识别摄像头**: 侧面45度角，聚焦耳部区域
2. **体况评分摄像头**: 侧后方或正后方，全身视角
3. **辅助摄像头**: 正面或其他角度（可选）

### 摄像头要求
- 分辨率: 1080p或更高
- 帧率: 30fps
- 自动对焦功能
- 良好的低光性能

## 📈 性能指标

### 处理速度
- 实时处理: 30fps
- 延迟: <100ms
- 多摄像头: 支持4路同时处理

## 🔬 技术细节

### 深度学习模型
- **YOLOv8**: 牛只和耳标检测
- **ResNet**: 花色特征提取
- **HRNet**: 关键点检测
- **Siamese Network**: 花色相似度计算

### 数据处理
- **多线程**: 并行处理多个视频流
- **缓存机制**: 优化内存使用
- **异常处理**: 摄像头断线自动恢复

## 📝 使用示例

```python
from src.main import BovineInsightSystem

# 初始化系统
system = BovineInsightSystem()

# 配置摄像头
system.add_camera("ear_tag_cam", camera_id=0)
system.add_camera("body_condition_cam", camera_id=1)

# 启动系统
system.start()

# 获取识别结果
results = system.get_latest_results()
for result in results:
    print(f"牛只ID: {result.cattle_id}")
    print(f"BCS评分: {result.bcs_score}")
    print(f"识别方式: {result.identification_method}")
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📞 联系方式

- 项目维护者: NovenaGarfield
- 邮箱: novenagarfield@gmail.com
- 项目链接: https://github.com/novenazgarfield/N.S.S-Novena-Garfield/tree/main/systems/bovine-insight
---

🐄 **BovineInsight** - 让智能技术服务现代畜牧业！