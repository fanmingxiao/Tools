# -*- coding: utf-8 -*-
"""
文件扫描模块
扫描指定目录中的发票图片、PDF和HEIC文件
"""

import os
import tempfile
from pathlib import Path
from typing import List, Generator, Tuple
from PIL import Image
import fitz  # PyMuPDF

# 注册HEIC格式支持
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    print("警告: pillow-heif未安装，HEIC文件将无法处理")


# 支持的图片格式
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
# 支持的HEIC格式（苹果设备照片）
SUPPORTED_HEIC_EXTENSIONS = {'.heic', '.heif'}
# 支持的PDF格式
SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
# 所有支持的格式
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS | SUPPORTED_HEIC_EXTENSIONS


def scan_files(directory: str, recursive: bool = False) -> List[Tuple[str, str]]:
    """
    扫描目录中的发票文件（图片和PDF）
    
    Args:
        directory: 要扫描的目录路径
        recursive: 是否递归扫描子目录
        
    Returns:
        文件信息列表，每个元素为(文件路径, 文件类型)
        文件类型: 'image' 或 'pdf'
    """
    files = []
    path = Path(directory)
    
    if not path.exists():
        raise ValueError(f"目录不存在: {directory}")
    
    if not path.is_dir():
        raise ValueError(f"路径不是目录: {directory}")
    
    if recursive:
        # 递归扫描
        for file_path in path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in SUPPORTED_IMAGE_EXTENSIONS:
                    files.append((str(file_path), 'image'))
                elif ext in SUPPORTED_HEIC_EXTENSIONS:
                    files.append((str(file_path), 'heic'))
                elif ext in SUPPORTED_PDF_EXTENSIONS:
                    files.append((str(file_path), 'pdf'))
    else:
        # 仅扫描当前目录
        for file_path in path.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in SUPPORTED_IMAGE_EXTENSIONS:
                    files.append((str(file_path), 'image'))
                elif ext in SUPPORTED_HEIC_EXTENSIONS:
                    files.append((str(file_path), 'heic'))
                elif ext in SUPPORTED_PDF_EXTENSIONS:
                    files.append((str(file_path), 'pdf'))
    
    # 按文件名排序
    files.sort(key=lambda x: x[0])
    
    return files


def scan_images(directory: str, recursive: bool = False) -> List[str]:
    """
    扫描目录中的图片和PDF文件（兼容旧接口）
    
    Args:
        directory: 要扫描的目录路径
        recursive: 是否递归扫描子目录
        
    Returns:
        文件路径列表
    """
    files = scan_files(directory, recursive)
    return [f[0] for f in files]


def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[str]:
    """
    将PDF文件转换为图片文件列表
    
    Args:
        pdf_path: PDF文件路径
        dpi: 输出图片的DPI（默认200）
        
    Returns:
        生成的临时图片文件路径列表
    """
    image_paths = []
    
    try:
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        
        # 创建临时目录存放图片
        temp_dir = tempfile.mkdtemp(prefix='invoice_pdf_')
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 设置缩放比例，基于DPI
            zoom = dpi / 72  # 72是PDF默认DPI
            mat = fitz.Matrix(zoom, zoom)
            
            # 渲染页面为图片
            pix = page.get_pixmap(matrix=mat)
            
            # 保存为临时图片文件
            image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)
        
        doc.close()
        
    except Exception as e:
        print(f"PDF转换错误: {e}")
    
    return image_paths


def extract_pdf_text(pdf_path: str) -> Tuple[List[str], bool]:
    """
    从PDF文件中直接提取文字内容，按位置智能组合
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        (每页文字内容列表, 是否成功提取到有效发票文字)
        如果是扫描件PDF，文字内容可能为空或无效
    """
    texts = []
    has_valid_text = False
    
    # 发票关键词列表，用于验证提取的文字是否为有效发票内容
    invoice_keywords = ['发票', '税额', '金额', '合计', '代码', '号码', '纳税', '销售方', '购买方']
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 使用get_text("words")获取每个词的位置信息
            # 返回格式: (x0, y0, x1, y1, word, block_no, line_no, word_no)
            words = page.get_text("words")
            
            if words:
                # 按y坐标分组，再按x坐标排序，将同一行的词组合
                # 使用y容差将相近的y值视为同一行
                y_tolerance = 5  # 5像素的容差
                
                # 按y坐标排序，然后按x坐标排序
                sorted_words = sorted(words, key=lambda w: (round(w[1] / y_tolerance), w[0]))
                
                # 将同一行的词组合成行
                lines = []
                current_line = []
                current_y = None
                
                for word_info in sorted_words:
                    word_y = round(word_info[1] / y_tolerance) * y_tolerance
                    word_text = word_info[4]
                    word_x = word_info[0]
                    
                    if current_y is None:
                        current_y = word_y
                    
                    if abs(word_y - current_y) <= y_tolerance:
                        # 同一行，添加到当前行
                        current_line.append((word_x, word_text))
                    else:
                        # 新行，保存当前行并开始新行
                        if current_line:
                            # 按x坐标排序当前行的词
                            current_line.sort(key=lambda x: x[0])
                            line_text = ' '.join([w[1] for w in current_line])
                            lines.append(line_text)
                        current_line = [(word_x, word_text)]
                        current_y = word_y
                
                # 处理最后一行
                if current_line:
                    current_line.sort(key=lambda x: x[0])
                    line_text = ' '.join([w[1] for w in current_line])
                    lines.append(line_text)
                
                # 组合所有行
                text = '\n'.join(lines)
                
                # 调试输出
                print(f"[PDF提取] 按位置排序后行数: {len(lines)}")
                if lines:
                    print(f"[PDF提取] 前10行: {lines[:10]}")
            else:
                # 如果get_text("words")失败，回退到普通文字提取
                text = page.get_text("text").strip()
            
            texts.append(text)
            
            # 更严格的检测：文字长度超过100且包含发票关键词
            if len(text) > 100:
                keyword_count = sum(1 for kw in invoice_keywords if kw in text)
                # 至少匹配2个发票关键词才认为是有效的文字版发票
                if keyword_count >= 2:
                    has_valid_text = True
        
        doc.close()
        
    except Exception as e:
        print(f"PDF文字提取错误: {e}")
        import traceback
        traceback.print_exc()
    
    return texts, has_valid_text


def heic_to_image(heic_path: str, max_size: int = 2000) -> str:
    """
    将HEIC文件转换为临时图片文件
    
    Args:
        heic_path: HEIC文件路径
        max_size: 图片最大边长（默认2000像素，用于加速OCR）
        
    Returns:
        生成的临时图片文件路径
    """
    try:
        # 使用Pillow打开HEIC文件（需要pillow-heif已注册）
        img = Image.open(heic_path)
        
        # 压缩大图片以加速OCR处理
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"[调试] HEIC图片压缩: {heic_path} -> {new_size}")
        
        # 创建临时文件
        temp_dir = tempfile.mkdtemp(prefix='invoice_heic_')
        output_path = os.path.join(temp_dir, Path(heic_path).stem + '.jpg')
        
        # 转换为RGB并保存为JPEG
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # 处理带透明通道的图片
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, 'JPEG', quality=90)
        img.close()
        
        return output_path
        
    except Exception as e:
        print(f"HEIC转换错误: {e}")
        import traceback
        traceback.print_exc()
        return ""


def get_file_type(file_path: str) -> str:
    """
    获取文件类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        'image', 'heic', 'pdf' 或 'unknown'
    """
    ext = Path(file_path).suffix.lower()
    
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in SUPPORTED_HEIC_EXTENSIONS:
        return 'heic'
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        return 'pdf'
    else:
        return 'unknown'


def is_pdf(file_path: str) -> bool:
    """检查是否为PDF文件"""
    return Path(file_path).suffix.lower() in SUPPORTED_PDF_EXTENSIONS


def get_image_info(image_path: str) -> dict:
    """
    获取图片基本信息
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        包含文件信息的字典
    """
    path = Path(image_path)
    
    if not path.exists():
        return {'error': '文件不存在'}
    
    stat = path.stat()
    
    return {
        'name': path.name,
        'stem': path.stem,       # 不含扩展名的文件名
        'extension': path.suffix.lower(),
        'size': stat.st_size,    # 文件大小（字节）
        'size_mb': round(stat.st_size / (1024 * 1024), 2),  # 文件大小（MB）
        'path': str(path),
        'parent': str(path.parent),
        'type': get_file_type(str(path))
    }


def is_supported_file(file_path: str) -> bool:
    """
    检查文件是否为支持的格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为支持的格式
    """
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def cleanup_temp_images(image_paths: List[str]):
    """
    清理临时生成的图片文件
    
    Args:
        image_paths: 临时图片文件路径列表
    """
    for path in image_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
            # 尝试删除父目录（如果为空）
            parent = os.path.dirname(path)
            if parent and os.path.exists(parent) and not os.listdir(parent):
                os.rmdir(parent)
        except Exception:
            pass
