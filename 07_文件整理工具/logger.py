# -*- coding: utf-8 -*-
"""
日志报告生成模块 - 生成整理日志和报告
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from config import get_category_emoji


class ReportGenerator:
    """整理报告生成器"""
    
    def __init__(self):
        self.logs: List[str] = []
        self.moved_files: List[Tuple[str, str, str]] = []  # (原路径, 新路径, 分类)
        self.skipped_files: List[Tuple[str, str]] = []  # (路径, 原因)
        self.stats: Dict[str, int] = {}
        self.start_time: datetime = None
        self.end_time: datetime = None
    
    def start(self):
        """开始记录"""
        self.start_time = datetime.now()
        self.logs = []
        self.moved_files = []
        self.skipped_files = []
        self.stats = {}
        self.log("开始整理文件...")
    
    def end(self):
        """结束记录"""
        self.end_time = datetime.now()
        self.log("整理完成！")
    
    def log(self, message: str):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
    
    def record_move(self, source: str, dest: str, category: str):
        """记录文件移动"""
        self.moved_files.append((source, dest, category))
        self.stats[category] = self.stats.get(category, 0) + 1
        self.log(f"移动: {Path(source).name} → {category}/")
    
    def record_skip(self, path: str, reason: str):
        """记录跳过的文件"""
        self.skipped_files.append((path, reason))
        self.log(f"跳过: {Path(path).name} ({reason})")
    
    def get_logs(self) -> List[str]:
        """获取所有日志"""
        return self.logs.copy()
    
    def get_summary(self) -> str:
        """获取简要统计"""
        total = sum(self.stats.values())
        categories = len(self.stats)
        skipped = len(self.skipped_files)
        return f"共处理 {total} 个文件，分入 {categories} 个分类，跳过 {skipped} 个文件"
    
    def generate_report(self, output_dir: str = None) -> str:
        """
        生成Markdown格式的整理报告
        
        Args:
            output_dir: 报告输出目录，默认为当前目录
        
        Returns:
            报告文件路径
        """
        if output_dir is None:
            output_dir = os.getcwd()
        
        report_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"整理报告_{report_time}.md"
        report_path = Path(output_dir) / report_name
        
        # 生成报告内容
        content = self._build_report_content()
        
        # 写入文件
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(report_path)
    
    def _build_report_content(self) -> str:
        """构建报告内容"""
        lines = []
        
        # 标题
        lines.append("# 📁 文件整理报告")
        lines.append("")
        
        # 基本信息
        lines.append("## 📋 基本信息")
        lines.append("")
        if self.start_time:
            lines.append(f"- **开始时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.end_time:
            lines.append(f"- **结束时间**: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if self.start_time:
                duration = (self.end_time - self.start_time).total_seconds()
                lines.append(f"- **耗时**: {duration:.2f} 秒")
        lines.append(f"- **总文件数**: {sum(self.stats.values())}")
        lines.append(f"- **跳过文件数**: {len(self.skipped_files)}")
        lines.append("")
        
        # 分类统计
        lines.append("## 📊 分类统计")
        lines.append("")
        lines.append("| 分类 | 文件数量 |")
        lines.append("|------|----------|")
        for category, count in sorted(self.stats.items(), key=lambda x: -x[1]):
            emoji = get_category_emoji(category)
            lines.append(f"| {emoji} {category} | {count} |")
        lines.append("")
        
        # 移动详情
        if self.moved_files:
            lines.append("## 📝 移动详情")
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>点击展开全部移动记录</summary>")
            lines.append("")
            lines.append("| 原文件名 | 目标分类 |")
            lines.append("|----------|----------|")
            for source, dest, category in self.moved_files:
                filename = Path(source).name
                emoji = get_category_emoji(category)
                lines.append(f"| {filename} | {emoji} {category} |")
            lines.append("")
            lines.append("</details>")
            lines.append("")
        
        # 跳过的文件
        if self.skipped_files:
            lines.append("## ⚠️ 跳过的文件")
            lines.append("")
            lines.append("| 文件名 | 原因 |")
            lines.append("|--------|------|")
            for path, reason in self.skipped_files:
                filename = Path(path).name
                lines.append(f"| {filename} | {reason} |")
            lines.append("")
        
        # 日志
        lines.append("## 📜 执行日志")
        lines.append("")
        lines.append("```")
        for log in self.logs[-50:]:  # 只显示最后50条日志
            lines.append(log)
        if len(self.logs) > 50:
            lines.append(f"... (共 {len(self.logs)} 条日志)")
        lines.append("```")
        lines.append("")
        
        return "\n".join(lines)
