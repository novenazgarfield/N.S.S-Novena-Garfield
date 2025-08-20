"""
自动化BCS文本报告生成器 - 基于GLM-4V
生成专家级的牛只体况评分文字描述
"""

import torch
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import numpy as np
import logging
from typing import Union, Dict, List, Optional
import cv2
import base64
import io
import json
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BovineDescriptionService:
    """
    基于GLM-4V的牛只体况描述生成服务
    生成专家级的BCS评分文字报告
    """
    
    def __init__(self, 
                 model_name: str = "THUDM/glm-4v-9b",
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        初始化BCS描述生成服务
        
        Args:
            model_name: GLM-4V模型名称
            device: 计算设备
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir
        
        self.tokenizer = None
        self.model = None
        
        # BCS评分标准
        self.bcs_standards = {
            1: {
                "condition": "极瘦",
                "description": "严重营养不良，骨骼突出明显",
                "keywords": ["骨骼突出", "肌肉萎缩", "脂肪覆盖极少"]
            },
            2: {
                "condition": "瘦",
                "description": "营养不良，骨骼可见",
                "keywords": ["骨骼可见", "肌肉发育不良", "脂肪覆盖少"]
            },
            3: {
                "condition": "中等偏瘦",
                "description": "营养状况一般，骨骼轮廓可辨",
                "keywords": ["骨骼轮廓可辨", "肌肉发育一般", "脂肪覆盖中等"]
            },
            4: {
                "condition": "良好",
                "description": "营养状况良好，体型匀称",
                "keywords": ["体型匀称", "肌肉发育良好", "脂肪覆盖适中"]
            },
            5: {
                "condition": "肥胖",
                "description": "营养过剩，脂肪覆盖厚",
                "keywords": ["脂肪覆盖厚", "体型圆润", "骨骼不易触及"]
            }
        }
        
        logger.info(f"初始化BCS描述生成服务: {model_name}, 设备: {self.device}")
    
    def load_model(self):
        """加载GLM-4V模型"""
        try:
            logger.info(f"加载GLM-4V模型: {self.model_name}")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir
            )
            
            # 加载模型
            self.model = AutoModel.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                cache_dir=self.cache_dir
            ).to(self.device)
            
            self.model.eval()
            
            logger.info("GLM-4V模型加载成功")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            # 如果GLM-4V不可用，使用备用方案
            logger.warning("使用备用文本生成方案")
            self.model = None
            self.tokenizer = None
    
    def preprocess_image(self, image: Union[str, np.ndarray, Image.Image]) -> Image.Image:
        """
        预处理图像
        
        Args:
            image: 输入图像
            
        Returns:
            PIL图像
        """
        try:
            if isinstance(image, str):
                pil_image = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                if image.shape[-1] == 3:  # BGR to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)
            elif isinstance(image, Image.Image):
                pil_image = image.convert('RGB')
            else:
                raise ValueError(f"不支持的图像类型: {type(image)}")
            
            # 调整图像大小 (GLM-4V推荐尺寸)
            max_size = 1024
            if max(pil_image.size) > max_size:
                ratio = max_size / max(pil_image.size)
                new_size = tuple(int(dim * ratio) for dim in pil_image.size)
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            
            return pil_image
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def generate_bcs_description(self, 
                                image: Union[str, np.ndarray, Image.Image],
                                bcs_score: Optional[float] = None,
                                region: str = "tail_head") -> Dict[str, str]:
        """
        生成BCS评分的专家级文字描述
        
        Args:
            image: 牛只图像
            bcs_score: BCS评分 (1-5)
            region: 评估区域 ("tail_head", "ribs", "spine", "hooks", "pins")
            
        Returns:
            包含描述信息的字典
        """
        if self.model is None:
            return self._generate_fallback_description(bcs_score, region)
        
        try:
            # 预处理图像
            pil_image = self.preprocess_image(image)
            
            # 构建专家级提示词
            prompt = self._build_expert_prompt(bcs_score, region)
            
            # 生成描述
            with torch.no_grad():
                inputs = self.tokenizer.apply_chat_template(
                    [{"role": "user", "image": pil_image, "content": prompt}],
                    add_generation_prompt=True,
                    tokenize=True,
                    return_tensors="pt",
                    return_dict=True
                ).to(self.device)
                
                gen_kwargs = {
                    "max_length": 2048,
                    "do_sample": True,
                    "top_k": 1,
                    "temperature": 0.7,
                    "repetition_penalty": 1.1
                }
                
                outputs = self.model.generate(**inputs, **gen_kwargs)
                outputs = outputs[:, inputs['input_ids'].shape[1]:]
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 解析和结构化响应
            structured_response = self._parse_response(response, bcs_score, region)
            
            logger.info(f"成功生成BCS描述，区域: {region}")
            return structured_response
            
        except Exception as e:
            logger.error(f"BCS描述生成失败: {str(e)}")
            return self._generate_fallback_description(bcs_score, region)
    
    def _build_expert_prompt(self, bcs_score: Optional[float], region: str) -> str:
        """构建专家级提示词"""
        
        region_descriptions = {
            "tail_head": "尾根部位的脂肪覆盖程度和坐骨、髋骨的显露情况",
            "ribs": "肋骨区域的脂肪覆盖和肌肉发育状况",
            "spine": "脊椎骨的突出程度和周围肌肉脂肪分布",
            "hooks": "髋骨钩状突起的显露程度和脂肪覆盖",
            "pins": "坐骨结节的突出程度和周围组织状况"
        }
        
        base_prompt = f"""
请以一位资深畜牧专家的专业口吻，基于这张牛只的{region_descriptions.get(region, '身体部位')}图片，
进行详细的体况评分(BCS)分析。请从以下几个方面进行描述：

1. **解剖结构观察**: 详细描述可见的骨骼结构、肌肉发育状况
2. **脂肪覆盖评估**: 分析脂肪层的厚度和分布情况
3. **体况判断**: 基于观察结果判断营养状况和健康水平
4. **专业建议**: 提供饲养管理方面的专业建议

请使用专业术语，但保持描述的准确性和可读性。
"""
        
        if bcs_score:
            score_int = int(round(bcs_score))
            if 1 <= score_int <= 5:
                standard = self.bcs_standards[score_int]
                base_prompt += f"\n参考BCS评分: {bcs_score:.1f}分 ({standard['condition']})"
        
        return base_prompt
    
    def _parse_response(self, response: str, bcs_score: Optional[float], region: str) -> Dict[str, str]:
        """解析和结构化模型响应"""
        
        # 基本信息
        result = {
            "region": region,
            "bcs_score": bcs_score,
            "expert_description": response.strip(),
            "timestamp": str(np.datetime64('now')),
            "model_version": self.model_name
        }
        
        # 尝试提取结构化信息
        try:
            # 查找关键段落
            sections = {
                "anatomical_observation": "",
                "fat_coverage_assessment": "",
                "condition_judgment": "",
                "professional_advice": ""
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 识别段落标题
                if "解剖结构" in line or "骨骼结构" in line:
                    current_section = "anatomical_observation"
                elif "脂肪覆盖" in line or "脂肪层" in line:
                    current_section = "fat_coverage_assessment"
                elif "体况判断" in line or "营养状况" in line:
                    current_section = "condition_judgment"
                elif "专业建议" in line or "饲养管理" in line:
                    current_section = "professional_advice"
                elif current_section and line:
                    sections[current_section] += line + " "
            
            # 添加结构化信息
            for key, value in sections.items():
                if value.strip():
                    result[key] = value.strip()
                    
        except Exception as e:
            logger.warning(f"响应解析失败: {str(e)}")
        
        return result
    
    def _generate_fallback_description(self, bcs_score: Optional[float], region: str) -> Dict[str, str]:
        """生成备用描述 (当GLM-4V不可用时)"""
        
        region_templates = {
            "tail_head": {
                "focus": "尾根部位和髋骨区域",
                "indicators": ["尾根脂肪覆盖", "坐骨显露程度", "髋骨轮廓"]
            },
            "ribs": {
                "focus": "肋骨区域",
                "indicators": ["肋骨可触性", "肋间脂肪", "胸壁肌肉发育"]
            },
            "spine": {
                "focus": "脊椎区域",
                "indicators": ["脊椎突起", "背部脂肪层", "腰部肌肉"]
            }
        }
        
        template = region_templates.get(region, region_templates["tail_head"])
        
        if bcs_score:
            score_int = int(round(bcs_score))
            if 1 <= score_int <= 5:
                standard = self.bcs_standards[score_int]
                
                description = f"""
**专业体况评估报告**

**评估区域**: {template['focus']}
**BCS评分**: {bcs_score:.1f}分 ({standard['condition']})

**解剖结构观察**: 
基于{template['focus']}的视觉检查，{standard['description']}。
主要观察指标包括{', '.join(template['indicators'])}。

**脂肪覆盖评估**: 
{standard['keywords'][2]}，符合BCS {score_int}分的典型特征。

**体况判断**: 
该牛只当前营养状况为{standard['condition']}，{standard['description']}。

**专业建议**: 
建议根据当前体况调整饲养方案，确保营养均衡和健康发育。
"""
            else:
                description = f"BCS评分 {bcs_score:.1f}分，需要专业评估。"
        else:
            description = f"对{template['focus']}进行专业体况评估，建议结合多个部位综合判断。"
        
        return {
            "region": region,
            "bcs_score": bcs_score,
            "expert_description": description.strip(),
            "timestamp": str(np.datetime64('now')),
            "model_version": "fallback_template",
            "anatomical_observation": f"基于{template['focus']}的专业观察",
            "fat_coverage_assessment": "脂肪覆盖程度评估",
            "condition_judgment": "体况状况判断",
            "professional_advice": "专业饲养建议"
        }
    
    def generate_comprehensive_report(self, 
                                    images: Dict[str, Union[str, np.ndarray, Image.Image]],
                                    bcs_scores: Dict[str, float]) -> Dict[str, any]:
        """
        生成综合BCS报告
        
        Args:
            images: 不同部位的图像字典 {"region": image}
            bcs_scores: 不同部位的BCS评分 {"region": score}
            
        Returns:
            综合报告字典
        """
        try:
            regional_reports = {}
            
            # 为每个区域生成描述
            for region, image in images.items():
                bcs_score = bcs_scores.get(region)
                report = self.generate_bcs_description(image, bcs_score, region)
                regional_reports[region] = report
            
            # 计算综合评分
            overall_score = np.mean(list(bcs_scores.values())) if bcs_scores else None
            
            # 生成综合评估
            comprehensive_report = {
                "overall_bcs_score": overall_score,
                "assessment_date": str(np.datetime64('now')),
                "regional_reports": regional_reports,
                "summary": self._generate_summary(regional_reports, overall_score),
                "recommendations": self._generate_recommendations(overall_score)
            }
            
            logger.info(f"生成综合BCS报告，整体评分: {overall_score:.2f}")
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"综合报告生成失败: {str(e)}")
            raise
    
    def _generate_summary(self, regional_reports: Dict, overall_score: Optional[float]) -> str:
        """生成报告摘要"""
        if not overall_score:
            return "无法生成摘要，缺少评分数据。"
        
        score_int = int(round(overall_score))
        if 1 <= score_int <= 5:
            condition = self.bcs_standards[score_int]["condition"]
            
            summary = f"""
**综合体况评估摘要**

该牛只整体BCS评分为 {overall_score:.2f}分，体况状况为{condition}。
通过对多个关键部位的专业评估，包括{', '.join(regional_reports.keys())}，
综合判断该牛只的营养状况和健康水平。

各部位评估结果显示一致的体况特征，符合当前评分标准。
建议继续监测体况变化，适时调整饲养管理策略。
"""
            return summary.strip()
        
        return f"整体BCS评分: {overall_score:.2f}分，需要专业评估。"
    
    def _generate_recommendations(self, overall_score: Optional[float]) -> List[str]:
        """生成专业建议"""
        if not overall_score:
            return ["建议进行完整的体况评估"]
        
        recommendations = []
        
        if overall_score < 2.5:
            recommendations.extend([
                "增加营养密度高的饲料供应",
                "检查是否存在健康问题",
                "增加饲喂频次",
                "提供优质粗饲料和精饲料",
                "定期监测体重变化"
            ])
        elif overall_score < 3.5:
            recommendations.extend([
                "适当增加精饲料比例",
                "保持当前饲养管理水平",
                "定期体况评估",
                "注意饲料质量"
            ])
        elif overall_score < 4.5:
            recommendations.extend([
                "维持当前营养水平",
                "定期体况监测",
                "适当运动促进健康",
                "保持饲料品质稳定"
            ])
        else:
            recommendations.extend([
                "适当控制精饲料供应",
                "增加运动量",
                "调整饲料配方",
                "预防代谢性疾病",
                "定期健康检查"
            ])
        
        return recommendations
    
    def save_report(self, report: Dict, filepath: str):
        """保存报告到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"报告已保存到: {filepath}")
        except Exception as e:
            logger.error(f"报告保存失败: {str(e)}")
            raise
    
    def get_service_info(self) -> Dict[str, any]:
        """获取服务信息"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.model is not None,
            "supported_regions": ["tail_head", "ribs", "spine", "hooks", "pins"],
            "bcs_range": "1-5",
            "output_language": "Chinese"
        }


# 使用示例和测试函数
def test_description_service():
    """测试BCS描述生成服务"""
    try:
        # 初始化服务
        service = BovineDescriptionService()
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        # 生成单个区域描述
        description = service.generate_bcs_description(
            test_image, 
            bcs_score=3.5, 
            region="tail_head"
        )
        
        print("单个区域描述:")
        print(f"区域: {description['region']}")
        print(f"评分: {description['bcs_score']}")
        print(f"描述: {description['expert_description'][:200]}...")
        
        # 测试综合报告
        images = {
            "tail_head": test_image,
            "ribs": test_image
        }
        scores = {
            "tail_head": 3.5,
            "ribs": 3.2
        }
        
        comprehensive_report = service.generate_comprehensive_report(images, scores)
        print(f"\n综合报告:")
        print(f"整体评分: {comprehensive_report['overall_bcs_score']:.2f}")
        print(f"建议数量: {len(comprehensive_report['recommendations'])}")
        
        print("✅ BCS描述生成服务测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_description_service()