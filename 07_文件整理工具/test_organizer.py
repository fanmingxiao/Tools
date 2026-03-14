# -*- coding: utf-8 -*-
"""
测试脚本 - 验证核心整理功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from organizer_core import FileOrganizer
from config import get_extension_category

def test_core_functions():
    """测试核心功能"""
    print("=" * 50)
    print("智能文件整理工具 - 核心功能测试")
    print("=" * 50)
    
    # 测试文件类型识别
    print("\n[测试1] 文件类型识别:")
    test_extensions = [".jpg", ".pdf", ".mp4", ".py", ".zip", ".xyz"]
    for ext in test_extensions:
        category = get_extension_category(ext)
        print(f"  {ext} → {category}")
    
    # 测试整理器预览功能
    print("\n[测试2] 文件整理预览:")
    test_folder = os.path.join(os.path.dirname(__file__), "测试文件夹")
    
    if os.path.exists(test_folder):
        organizer = FileOrganizer(test_folder)
        organizer.set_keywords({
            "财务": ["财务", "invoice", "report"],
            "会议": ["会议", "meeting", "纪要"]
        })
        
        result = organizer.preview()
        
        print(f"  扫描目录: {test_folder}")
        print(f"  发现分类:")
        for category, files in result.items():
            print(f"    {category}: {len(files)} 个文件")
            for f in files[:3]:
                print(f"      - {f.name}")
        
        print("\n[测试3] 日志摘要:")
        print(f"  {organizer.get_summary()}")
        
        print("\n✅ 所有测试通过!")
    else:
        print(f"  ⚠️ 测试文件夹不存在: {test_folder}")
        print("  请先创建测试文件夹和测试文件")

if __name__ == "__main__":
    test_core_functions()
