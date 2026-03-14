# -*- coding: utf-8 -*-
"""
核心整理模块 - 实现文件扫描、分类和移动功能
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from config import get_extension_category, load_config, get_category_emoji
from logger import ReportGenerator


class FileOrganizer:
    """文件整理器核心类"""
    
    def __init__(self, source_dir: str, output_dir: str = None):
        """
        初始化文件整理器
        
        Args:
            source_dir: 源文件夹路径
            output_dir: 输出目录路径，默认为源文件夹下创建"已整理"文件夹
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else self.source_dir / "已整理"
        self.keywords: Dict[str, List[str]] = {}
        self.include_subfolders = False
        self.reporter = ReportGenerator()
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        
        # 加载配置
        config = load_config()
        self.keywords = config.get("keywords", {})
    
    def set_keywords(self, keywords: Dict[str, List[str]]):
        """
        设置关键字分类规则
        
        Args:
            keywords: 关键字字典，格式如 {"分类名": ["关键字1", "关键字2", ...]}
        """
        self.keywords = keywords
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """
        设置进度回调函数
        
        Args:
            callback: 回调函数，参数为 (当前进度, 总数, 当前文件名)
        """
        self.progress_callback = callback
    
    def scan_folder(self) -> List[Path]:
        """
        扫描源文件夹获取所有文件
        
        Returns:
            文件路径列表
        """
        files = []
        
        if self.include_subfolders:
            # 递归扫描
            for item in self.source_dir.rglob("*"):
                if item.is_file() and not item.name.startswith("."):
                    # 排除输出目录中的文件
                    if not str(item).startswith(str(self.output_dir)):
                        files.append(item)
        else:
            # 只扫描顶层
            for item in self.source_dir.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    files.append(item)
        
        self.reporter.log(f"扫描完成，发现 {len(files)} 个文件")
        return files
    
    def classify_file(self, file_path: Path) -> str:
        """
        根据文件类型和关键字对文件进行分类
        
        Args:
            file_path: 文件路径
        
        Returns:
            分类名称
        """
        filename = file_path.name.lower()
        stem = file_path.stem.lower()  # 不含扩展名的文件名
        
        # 1. 首先尝试关键字匹配（优先级最高）
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in stem or keyword_lower in filename:
                    return category
        
        # 2. 按文件扩展名分类
        extension = file_path.suffix
        if extension:
            category = get_extension_category(extension)
            return category
        
        # 3. 无法识别的文件
        return "未分类"
    
    def _get_unique_path(self, dest_path: Path) -> Path:
        """
        获取唯一的目标路径（处理同名文件冲突）
        
        Args:
            dest_path: 原目标路径
        
        Returns:
            唯一的目标路径
        """
        if not dest_path.exists():
            return dest_path
        
        # 自动重命名：添加序号
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def move_file(self, source: Path, category: str) -> Optional[Path]:
        """
        移动文件到分类目录
        
        Args:
            source: 源文件路径
            category: 目标分类
        
        Returns:
            新文件路径，如果移动失败则返回None
        """
        # 创建分类目录
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # 确定目标路径（处理同名冲突）
        dest_path = self._get_unique_path(category_dir / source.name)
        
        try:
            shutil.move(str(source), str(dest_path))
            self.reporter.record_move(str(source), str(dest_path), category)
            return dest_path
        except Exception as e:
            self.reporter.record_skip(str(source), f"移动失败: {str(e)}")
            return None
    
    def preview(self) -> Dict[str, List[Path]]:
        """
        预览分类结果（不实际移动文件）
        
        Returns:
            分类结果字典，格式如 {"分类名": [文件路径列表]}
        """
        self.reporter.start()
        files = self.scan_folder()
        
        result: Dict[str, List[Path]] = {}
        total = len(files)
        
        for i, file_path in enumerate(files):
            category = self.classify_file(file_path)
            
            if category not in result:
                result[category] = []
            result[category].append(file_path)
            
            # 更新进度
            if self.progress_callback:
                self.progress_callback(i + 1, total, file_path.name)
        
        # 记录统计信息
        for category, file_list in result.items():
            self.reporter.log(f"{get_category_emoji(category)} {category}: {len(file_list)} 个文件")
        
        self.reporter.end()
        return result
    
    def organize(self) -> Tuple[int, int]:
        """
        执行文件整理
        
        Returns:
            (成功移动数量, 失败数量)
        """
        self.reporter.start()
        files = self.scan_folder()
        
        success_count = 0
        fail_count = 0
        total = len(files)
        
        for i, file_path in enumerate(files):
            category = self.classify_file(file_path)
            result = self.move_file(file_path, category)
            
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            # 更新进度
            if self.progress_callback:
                self.progress_callback(i + 1, total, file_path.name)
        
        self.reporter.end()
        self.reporter.log(f"整理完成：成功 {success_count}，失败 {fail_count}")
        
        return success_count, fail_count
    
    def generate_report(self, output_dir: str = None) -> str:
        """
        生成整理报告
        
        Args:
            output_dir: 报告输出目录
        
        Returns:
            报告文件路径
        """
        if output_dir is None:
            output_dir = str(self.output_dir)
        
        return self.reporter.generate_report(output_dir)
    
    def get_logs(self) -> List[str]:
        """获取日志列表"""
        return self.reporter.get_logs()
    
    def get_summary(self) -> str:
        """获取统计摘要"""
        return self.reporter.get_summary()
