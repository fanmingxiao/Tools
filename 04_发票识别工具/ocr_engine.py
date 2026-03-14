# -*- coding: utf-8 -*-
"""
OCR识别引擎模块
封装PaddleOCR进行文字识别
"""

import os
import logging

# 禁用PaddleOCR的日志输出
os.environ["PADDLEOCR_QUIET"] = "1"
os.environ["FLAGS_use_mkldnn"] = "0"  # 禁用MKL-DNN可能加速
logging.getLogger("ppocr").setLevel(logging.WARNING)

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np


class OCREngine:
    """OCR识别引擎类"""
    
    def __init__(self):
        """初始化OCR引擎"""
        # 初始化PaddleOCR，使用中文模型
        # 使用mobile版本模型以提高处理速度
        print("[OCR] 正在初始化OCR引擎（使用轻量模型）...")
        self.ocr = PaddleOCR(
            lang='ch',
            ocr_version='PP-OCRv4',  # 使用v4版本，更快
            use_doc_orientation_classify=False,  # 禁用文档方向检测
            use_doc_unwarping=False,  # 禁用文档矫正
            use_textline_orientation=False,  # 禁用文字方向检测
        )
        print("[OCR] OCR引擎初始化完成！")
    
    def recognize(self, image_path: str) -> list:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别结果列表，每个元素包含：
            - text: 识别的文字
            - confidence: 置信度
            - box: 文字框坐标
        """
        try:
            # 执行OCR识别
            result = self.ocr.ocr(image_path)
            
            if not result:
                print("[OCR] 结果为空")
                return []
            
            recognized_items = []
            
            # 处理返回结果
            ocr_result = result[0]  # 取第一个结果
            
            # OCRResult对象是类字典对象，使用get方法访问
            try:
                # 使用字典方式获取数据
                texts = ocr_result.get('rec_texts') if hasattr(ocr_result, 'get') else None
                scores = ocr_result.get('rec_scores') if hasattr(ocr_result, 'get') else None
                boxes = ocr_result.get('dt_polys') if hasattr(ocr_result, 'get') else None
                
                print(f"[OCR] texts: {texts}")
                print(f"[OCR] scores: {scores}")
                
                if texts is not None and len(texts) > 0:
                    print(f"[OCR] 识别到 {len(texts)} 个文字区域")
                    print(f"[OCR] 前3个文字: {list(texts[:3])}")
                    
                    for i, text in enumerate(texts):
                        if text and str(text).strip():
                            confidence = float(scores[i]) if scores is not None and i < len(scores) else 1.0
                            box = boxes[i].tolist() if boxes is not None and i < len(boxes) and hasattr(boxes[i], 'tolist') else []
                            recognized_items.append({
                                'text': str(text),
                                'confidence': confidence,
                                'box': box
                            })
                    
                    return recognized_items
                else:
                    print(f"[OCR] texts为空: {texts}")
                    # 尝试打印所有可用的键
                    if hasattr(ocr_result, 'keys'):
                        print(f"[OCR] 可用键: {list(ocr_result.keys())}")
                        for key in ocr_result.keys():
                            val = ocr_result.get(key)
                            if val is not None:
                                print(f"[OCR] {key}: {type(val)} = {str(val)[:100] if val else 'None'}")
            except Exception as e:
                print(f"[OCR] 新格式解析失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 如果上面失败，尝试旧格式（列表）
            if isinstance(ocr_result, list):
                for line in ocr_result:
                    try:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            box = line[0] if isinstance(line[0], list) else []
                            text_info = line[1]
                            
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                text = str(text_info[0])
                                confidence = float(text_info[1])
                            elif isinstance(text_info, str):
                                text = text_info
                                confidence = 1.0
                            else:
                                text = str(text_info)
                                confidence = 1.0
                            
                            if text.strip():
                                recognized_items.append({
                                    'text': text,
                                    'confidence': confidence,
                                    'box': box
                                })
                    except Exception as e:
                        print(f"[OCR] 跳过解析异常行: {e}")
                        continue
            
            return recognized_items
            
        except Exception as e:
            print(f"OCR识别错误: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_text(self, image_path: str) -> str:
        """
        获取图片中的所有文字（合并成一个字符串）
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            合并后的文字字符串
        """
        items = self.recognize(image_path)
        texts = [item['text'] for item in items]
        return '\n'.join(texts)


# 单例模式，避免重复加载模型
_ocr_instance = None

def get_ocr_engine() -> OCREngine:
    """获取OCR引擎单例"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCREngine()
    return _ocr_instance
