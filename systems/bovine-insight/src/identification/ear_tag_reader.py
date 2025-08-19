"""
耳标识别器
Ear Tag Reader

使用OCR技术读取牛只耳标上的ID信息
"""

import cv2
import numpy as np
import logging
import re
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .identification_utils import IdentificationResult, IdentificationMethod, validate_ear_tag_format, normalize_ear_tag_id
from ..detection.detection_utils import BoundingBox

# OCR引擎导入
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available, using mock OCR")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("easyocr not available")

@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    bbox: BoundingBox
    method: str

class MockOCR:
    """模拟OCR引擎"""
    
    def __init__(self):
        self.mock_tags = ['A001', 'B002', 'C003', 'D004', 'E005']
        self.call_count = 0
    
    def image_to_string(self, image, config=None):
        """模拟文字识别"""
        self.call_count += 1
        # 根据图像内容生成模拟结果
        if np.random.random() > 0.3:  # 70%成功率
            return self.mock_tags[self.call_count % len(self.mock_tags)]
        else:
            return ""
    
    def image_to_data(self, image, config=None, output_type=None):
        """模拟详细识别结果"""
        text = self.image_to_string(image, config)
        if text:
            h, w = image.shape[:2]
            return {
                'text': [text],
                'conf': [85.0],
                'left': [w//4],
                'top': [h//4],
                'width': [w//2],
                'height': [h//2]
            }
        else:
            return {
                'text': [''],
                'conf': [0.0],
                'left': [0],
                'top': [0],
                'width': [0],
                'height': [0]
            }

class EarTagPreprocessor:
    """耳标图像预处理器"""
    
    def __init__(self):
        self.kernel_size = 3
        self.blur_kernel = (3, 3)
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """为OCR预处理图像"""
        if image is None or image.size == 0:
            return image
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 调整图像大小（如果太小）
        h, w = gray.shape
        if h < 50 or w < 50:
            scale_factor = max(50 / h, 50 / w)
            new_h, new_w = int(h * scale_factor), int(w * scale_factor)
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)
        
        # 自适应阈值二值化
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 形态学操作去除噪声
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 反转图像（如果背景是深色的）
        if np.mean(cleaned) < 127:
            cleaned = cv2.bitwise_not(cleaned)
        
        return cleaned
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """增强对比度"""
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        if len(image.shape) == 3:
            # 彩色图像
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # 灰度图像
            enhanced = clahe.apply(image)
        
        return enhanced
    
    def detect_text_regions(self, image: np.ndarray) -> List[BoundingBox]:
        """检测文本区域"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 使用MSER检测文本区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        text_regions = []
        h, w = gray.shape
        
        for region in regions:
            # 计算边界框
            x_coords = region[:, 0]
            y_coords = region[:, 1]
            
            x1, y1 = np.min(x_coords), np.min(y_coords)
            x2, y2 = np.max(x_coords), np.max(y_coords)
            
            # 过滤太小或太大的区域
            region_w, region_h = x2 - x1, y2 - y1
            if (region_w > 10 and region_h > 10 and 
                region_w < w * 0.8 and region_h < h * 0.8):
                
                bbox = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
                text_regions.append(bbox)
        
        return text_regions

class TesseractOCR:
    """Tesseract OCR引擎封装"""
    
    def __init__(self):
        self.config = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
        
    def recognize_text(self, image: np.ndarray) -> List[OCRResult]:
        """识别文本"""
        if not TESSERACT_AVAILABLE:
            mock_ocr = MockOCR()
            text = mock_ocr.image_to_string(image)
            h, w = image.shape[:2]
            return [OCRResult(
                text=text,
                confidence=0.8 if text else 0.0,
                bbox=BoundingBox(0, 0, w, h),
                method='mock_tesseract'
            )]
        
        try:
            # 获取详细结果
            data = pytesseract.image_to_data(image, config=self.config, output_type=pytesseract.Output.DICT)
            
            results = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                
                if text and conf > 0:
                    bbox = BoundingBox(
                        x1=data['left'][i],
                        y1=data['top'][i],
                        x2=data['left'][i] + data['width'][i],
                        y2=data['top'][i] + data['height'][i]
                    )
                    
                    results.append(OCRResult(
                        text=text,
                        confidence=conf / 100.0,  # 转换为0-1范围
                        bbox=bbox,
                        method='tesseract'
                    ))
            
            return results
            
        except Exception as e:
            logging.error(f"Tesseract OCR失败: {e}")
            return []

class EasyOCREngine:
    """EasyOCR引擎封装"""
    
    def __init__(self):
        if EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader(['en'], gpu=False)
        else:
            self.reader = None
    
    def recognize_text(self, image: np.ndarray) -> List[OCRResult]:
        """识别文本"""
        if not EASYOCR_AVAILABLE or self.reader is None:
            return []
        
        try:
            results = self.reader.readtext(image)
            
            ocr_results = []
            for (bbox_coords, text, confidence) in results:
                # 转换边界框格式
                x_coords = [point[0] for point in bbox_coords]
                y_coords = [point[1] for point in bbox_coords]
                
                bbox = BoundingBox(
                    x1=min(x_coords),
                    y1=min(y_coords),
                    x2=max(x_coords),
                    y2=max(y_coords)
                )
                
                ocr_results.append(OCRResult(
                    text=text.strip(),
                    confidence=confidence,
                    bbox=bbox,
                    method='easyocr'
                ))
            
            return ocr_results
            
        except Exception as e:
            logging.error(f"EasyOCR失败: {e}")
            return []

class EarTagReader:
    """耳标识别器主类"""
    
    def __init__(self, 
                 use_tesseract: bool = True,
                 use_easyocr: bool = True,
                 min_confidence: float = 0.5):
        """
        初始化耳标识别器
        
        Args:
            use_tesseract: 是否使用Tesseract
            use_easyocr: 是否使用EasyOCR
            min_confidence: 最小置信度阈值
        """
        self.min_confidence = min_confidence
        self.preprocessor = EarTagPreprocessor()
        
        # 初始化OCR引擎
        self.ocr_engines = []
        
        if use_tesseract:
            self.ocr_engines.append(TesseractOCR())
        
        if use_easyocr:
            easy_ocr = EasyOCREngine()
            if easy_ocr.reader is not None:
                self.ocr_engines.append(easy_ocr)
        
        if not self.ocr_engines:
            logging.warning("没有可用的OCR引擎，使用模拟OCR")
            self.ocr_engines.append(MockOCR())
        
        # 统计信息
        self.stats = {
            'total_attempts': 0,
            'successful_reads': 0,
            'average_confidence': 0.0
        }
        
        logging.info(f"耳标识别器初始化完成，OCR引擎数量: {len(self.ocr_engines)}")
    
    def read_ear_tag(self, image: np.ndarray) -> IdentificationResult:
        """
        读取耳标ID
        
        Args:
            image: 耳标区域图像
        
        Returns:
            识别结果
        """
        self.stats['total_attempts'] += 1
        
        if image is None or image.size == 0:
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.EAR_TAG,
                confidence=0.0,
                metadata={'error': 'Invalid image'}
            )
        
        # 预处理图像
        processed_image = self.preprocessor.preprocess_for_ocr(image)
        
        # 使用多个OCR引擎识别
        all_results = []
        for engine in self.ocr_engines:
            try:
                if hasattr(engine, 'recognize_text'):
                    results = engine.recognize_text(processed_image)
                else:
                    # 兼容MockOCR
                    text = engine.image_to_string(processed_image)
                    if text:
                        h, w = processed_image.shape[:2]
                        results = [OCRResult(
                            text=text,
                            confidence=0.8,
                            bbox=BoundingBox(0, 0, w, h),
                            method='mock'
                        )]
                    else:
                        results = []
                
                all_results.extend(results)
                
            except Exception as e:
                logging.error(f"OCR引擎识别失败: {e}")
                continue
        
        # 选择最佳结果
        best_result = self._select_best_result(all_results)
        
        if best_result:
            self.stats['successful_reads'] += 1
            self._update_confidence_stats(best_result.confidence)
            
            return IdentificationResult(
                cattle_id=best_result.text,
                method=IdentificationMethod.EAR_TAG,
                confidence=best_result.confidence,
                ear_tag_id=best_result.text,
                metadata={
                    'ocr_method': best_result.method,
                    'bbox': best_result.bbox.to_dict() if hasattr(best_result.bbox, 'to_dict') else None,
                    'all_candidates': [r.text for r in all_results if r.confidence > 0.1]
                }
            )
        else:
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.EAR_TAG,
                confidence=0.0,
                metadata={'error': 'No valid text detected'}
            )
    
    def _select_best_result(self, results: List[OCRResult]) -> Optional[OCRResult]:
        """选择最佳OCR结果"""
        if not results:
            return None
        
        # 过滤低置信度结果
        valid_results = [r for r in results if r.confidence >= self.min_confidence]
        
        if not valid_results:
            return None
        
        # 验证和清理文本
        cleaned_results = []
        for result in valid_results:
            cleaned_text = self._clean_ear_tag_text(result.text)
            if validate_ear_tag_format(cleaned_text):
                result.text = normalize_ear_tag_id(cleaned_text)
                cleaned_results.append(result)
        
        if not cleaned_results:
            return None
        
        # 选择置信度最高的结果
        best_result = max(cleaned_results, key=lambda r: r.confidence)
        
        return best_result
    
    def _clean_ear_tag_text(self, text: str) -> str:
        """清理OCR识别的文本"""
        if not text:
            return ""
        
        # 移除空白字符
        cleaned = text.strip()
        
        # 移除常见的OCR错误字符
        cleaned = cleaned.replace('|', '1')
        cleaned = cleaned.replace('O', '0')
        cleaned = cleaned.replace('o', '0')
        cleaned = cleaned.replace('l', '1')
        cleaned = cleaned.replace('I', '1')
        
        # 只保留字母数字和连字符
        cleaned = re.sub(r'[^A-Za-z0-9\-]', '', cleaned)
        
        return cleaned
    
    def _update_confidence_stats(self, confidence: float):
        """更新置信度统计"""
        current_avg = self.stats['average_confidence']
        successful_reads = self.stats['successful_reads']
        
        if successful_reads == 1:
            self.stats['average_confidence'] = confidence
        else:
            self.stats['average_confidence'] = (
                (current_avg * (successful_reads - 1) + confidence) / successful_reads
            )
    
    def read_multiple_regions(self, image: np.ndarray, regions: List[BoundingBox]) -> List[IdentificationResult]:
        """读取多个耳标区域"""
        results = []
        
        for i, region in enumerate(regions):
            # 裁剪区域
            x1, y1, x2, y2 = map(int, region.to_xyxy())
            cropped = image[y1:y2, x1:x2]
            
            if cropped.size > 0:
                result = self.read_ear_tag(cropped)
                result.metadata['region_index'] = i
                result.metadata['region_bbox'] = region.to_dict() if hasattr(region, 'to_dict') else None
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取识别统计信息"""
        stats = self.stats.copy()
        if stats['total_attempts'] > 0:
            stats['success_rate'] = stats['successful_reads'] / stats['total_attempts']
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_attempts': 0,
            'successful_reads': 0,
            'average_confidence': 0.0
        }