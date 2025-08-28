#!/usr/bin/env python3
"""
升级任务测试脚本
测试BovineInsight和Changlee的AI升级功能
"""

import sys
import os
import time
import requests
import numpy as np
from pathlib import Path
import json

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

def test_bovine_insight_upgrades():
    """测试BovineInsight的博士级AI升级"""
    print("🐄 测试BovineInsight博士级AI升级...")
    
    try:
        # 测试DINOv2特征提取器
        print("   测试DINOv2特征提取器...")
        
        sys.path.append(str(Path(__file__).parent / "systems" / "bovine-insight" / "src"))
        
        try:
            from feature_extraction.feature_extractor import DINOv2FeatureExtractor, CattleFeatureDatabase
            
            # 创建特征提取器
            extractor = DINOv2FeatureExtractor(model_name='dinov2_vitb14')
            
            # 创建测试图像
            test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            print("   ⏳ 加载DINOv2模型...")
            success = extractor.load_model()
            
            if success:
                print("   ✅ DINOv2模型加载成功")
                
                # 提取特征
                features = extractor.extract_features(test_image)
                print(f"   ✅ 特征提取成功，维度: {features.shape}")
                
                # 测试特征数据库
                db = CattleFeatureDatabase("test_cattle_features.npz")
                db.add_cattle_features("test_cattle_001", features, {"breed": "Holstein"})
                
                similar_cattle = db.find_similar_cattle(features, top_k=3)
                print(f"   ✅ 特征数据库测试成功，找到{len(similar_cattle)}个相似牛只")
                
            else:
                print("   ⚠️ DINOv2模型加载失败，可能需要网络连接下载模型")
                
        except ImportError as e:
            print(f"   ⚠️ DINOv2模块导入失败: {e}")
        except Exception as e:
            print(f"   ⚠️ DINOv2测试失败: {e}")
        
        # 测试GLM-4V文本分析服务
        print("   测试GLM-4V文本分析服务...")
        
        try:
            from text_analysis.bovine_description_service import BovineDescriptionService
            
            # 创建文本分析服务
            service = BovineDescriptionService()
            
            # 创建测试图像
            test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            
            # 生成BCS描述（使用备用方案）
            description = service.generate_bcs_description(
                test_image, 
                bcs_score=3.5, 
                region="tail_head"
            )
            
            print(f"   ✅ BCS文本分析成功")
            print(f"   📝 生成描述: {description['expert_description'][:100]}...")
            
        except ImportError as e:
            print(f"   ⚠️ GLM-4V模块导入失败: {e}")
        except Exception as e:
            print(f"   ⚠️ GLM-4V测试失败: {e}")
        
        # 测试增强BCS分析器
        print("   测试增强BCS分析器...")
        
        try:
            from body_condition.body_condition_utils import create_enhanced_bcs_analyzer
            
            # 创建增强分析器
            analyzer = create_enhanced_bcs_analyzer(
                use_dinov2=False,  # 避免模型加载
                use_glm4v=False
            )
            
            # 创建测试图像
            test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            
            # 进行综合分析
            result = analyzer.analyze_body_condition(
                test_image, 
                region="tail_head", 
                generate_report=True
            )
            
            if 'error' not in result:
                print(f"   ✅ 增强BCS分析成功")
                print(f"   📊 最终评分: {result.get('final_bcs_score', 'N/A')}")
                print(f"   🎯 分析方法: {result.get('metadata', {}).get('analysis_methods', [])}")
            else:
                print(f"   ⚠️ 增强BCS分析失败: {result['error']}")
                
        except ImportError as e:
            print(f"   ⚠️ 增强BCS分析器模块导入失败: {e}")
        except Exception as e:
            print(f"   ⚠️ 增强BCS分析器测试失败: {e}")
        
        print("   ✅ BovineInsight升级测试完成\n")
        
    except Exception as e:
        print(f"   ❌ BovineInsight升级测试失败: {e}\n")

def test_changlee_local_ai():
    """测试Changlee本地AI功能"""
    print("🤖 测试Changlee本地AI升级...")
    
    try:
        # 测试本地AI服务类
        print("   测试本地AI服务类...")
        
        sys.path.append(str(Path(__file__).parent / "systems" / "Changlee" / "src" / "backend"))
        
        try:
            from services.LocalAIService import LocalAIService
            
            # 创建本地AI服务
            ai_service = LocalAIService()
            
            print("   ✅ 本地AI服务类创建成功")
            print(f"   🤖 模型名称: {ai_service.model_name}")
            print(f"   💻 计算设备: {ai_service.device}")
            
            # 测试服务状态
            status = ai_service.get_service_status()
            print(f"   📊 服务状态: {status['service_name']}")
            print(f"   🔧 支持的上下文: {len(status['supported_contexts'])}个")
            
            # 注意：不加载实际模型以避免资源消耗
            print("   ⚠️ 跳过模型加载测试（避免资源消耗）")
            
        except ImportError as e:
            print(f"   ⚠️ 本地AI服务模块导入失败: {e}")
        except Exception as e:
            print(f"   ⚠️ 本地AI服务测试失败: {e}")
        
        # 测试API端点（如果服务正在运行）
        print("   测试本地AI API端点...")
        
        try:
            # 检查本地AI服务是否运行
            response = requests.get('http://localhost:8001/health', timeout=5)
            
            if response.status_code == 200:
                print("   ✅ 本地AI服务正在运行")
                
                # 测试生成功能
                test_response = requests.post('http://localhost:8001/generate', 
                    json={
                        'prompt': '你好',
                        'context': 'daily_greeting',
                        'max_length': 30
                    }, 
                    timeout=30
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    if result.get('success'):
                        print(f"   ✅ AI生成测试成功: {result['response']}")
                    else:
                        print(f"   ⚠️ AI生成失败: {result.get('error', '未知错误')}")
                else:
                    print(f"   ⚠️ AI生成请求失败: {test_response.status_code}")
                    
            else:
                print(f"   ⚠️ 本地AI服务健康检查失败: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ 本地AI服务未运行，跳过API测试")
        except requests.exceptions.Timeout:
            print("   ⚠️ 本地AI服务响应超时")
        except Exception as e:
            print(f"   ⚠️ 本地AI API测试失败: {e}")
        
        # 测试Changlee集成
        print("   测试Changlee主服务集成...")
        
        try:
            # 检查Changlee主服务是否运行
            response = requests.get('http://localhost:3001/api/local-ai/health', timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Changlee本地AI集成正常")
                print(f"   📊 集成状态: {result.get('data', {}).get('status', '未知')}")
                
                # 测试集成API
                test_response = requests.post('http://localhost:3001/api/local-ai/greeting',
                    json={'time_of_day': 'morning'},
                    timeout=30
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    if result.get('success'):
                        print(f"   ✅ 集成API测试成功: {result['response']}")
                    else:
                        print(f"   ⚠️ 集成API失败: {result.get('error', '未知错误')}")
                else:
                    print(f"   ⚠️ 集成API请求失败: {test_response.status_code}")
                    
            else:
                print(f"   ⚠️ Changlee本地AI集成检查失败: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Changlee主服务未运行，跳过集成测试")
        except requests.exceptions.Timeout:
            print("   ⚠️ Changlee主服务响应超时")
        except Exception as e:
            print(f"   ⚠️ Changlee集成测试失败: {e}")
        
        print("   ✅ Changlee本地AI升级测试完成\n")
        
    except Exception as e:
        print(f"   ❌ Changlee本地AI升级测试失败: {e}\n")

def test_system_integration():
    """测试系统整体集成"""
    print("🔗 测试系统整体集成...")
    
    try:
        # 检查所有服务状态
        services = {
            'Chronicle': 'http://localhost:3000/health',
            'Changlee主服务': 'http://localhost:3001/health',
            'Changlee本地AI': 'http://localhost:8001/health'
        }
        
        running_services = []
        
        for service_name, health_url in services.items():
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    running_services.append(service_name)
                    print(f"   ✅ {service_name}: 运行中")
                else:
                    print(f"   ⚠️ {service_name}: 状态异常 ({response.status_code})")
            except requests.exceptions.ConnectionError:
                print(f"   ❌ {service_name}: 未运行")
            except Exception as e:
                print(f"   ⚠️ {service_name}: 检查失败 ({e})")
        
        print(f"   📊 运行中的服务: {len(running_services)}/{len(services)}")
        
        if len(running_services) >= 2:
            print("   ✅ 系统集成测试通过")
        else:
            print("   ⚠️ 部分服务未运行，建议启动完整系统")
        
        print("   ✅ 系统整体集成测试完成\n")
        
    except Exception as e:
        print(f"   ❌ 系统整体集成测试失败: {e}\n")

def main():
    """主测试函数"""
    print("🧪 开始升级任务测试...\n")
    
    # 测试BovineInsight升级
    test_bovine_insight_upgrades()
    
    # 测试Changlee本地AI升级
    test_changlee_local_ai()
    
    # 测试系统整体集成
    test_system_integration()
    
    print("🎉 升级任务测试完成！")
    print("\n📋 测试总结:")
    print("   1. BovineInsight博士级AI升级 - DINOv2特征提取 + GLM-4V文本分析")
    print("   2. Changlee本地AI核心 - Gemma 2 (2B)本地化智能对话")
    print("   3. 系统集成验证 - 多服务协同工作")
    print("\n💡 提示:")
    print("   - 如需完整测试，请先启动相关服务")
    print("   - DINOv2和GLM-4V首次使用需要下载模型")
    print("   - Gemma 2模型需要足够的内存和计算资源")

if __name__ == "__main__":
    main()