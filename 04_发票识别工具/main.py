# -*- coding: utf-8 -*-
"""
发票识别工具 - 主程序入口
扫描发票图片，识别关键信息并导出到Excel
"""

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """主函数"""
    print("正在启动发票识别工具...")
    print("首次运行需要下载OCR模型，请耐心等待...")
    
    # 导入GUI模块
    from gui import create_app
    
    # 创建并运行应用
    root = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
