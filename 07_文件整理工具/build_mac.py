# -*- coding: utf-8 -*-
"""
Mac应用打包脚本
使用PyInstaller将文件整理工具打包为Mac应用
"""

import os
import subprocess
import sys

def build_mac_app():
    """打包Mac应用"""
    print("=" * 50)
    print("📦 开始打包Mac应用...")
    print("=" * 50)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 应用信息
    app_name = "智能文件整理工具"
    main_script = "file_organizer.py"
    
    # PyInstaller参数
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--windowed",  # 不显示控制台窗口
        "--onefile",   # 打包成单个文件
        "--clean",     # 清理临时文件
        "--noconfirm", # 不确认覆盖
        # 添加数据文件
        "--add-data", f"config.py:.",
        "--add-data", f"organizer_core.py:.",
        "--add-data", f"logger.py:.",
        # 隐藏导入
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.scrolledtext",
        # 输出目录
        "--distpath", os.path.join(current_dir, "dist"),
        "--workpath", os.path.join(current_dir, "build"),
        "--specpath", current_dir,
        # 主脚本
        os.path.join(current_dir, main_script)
    ]
    
    print(f"\n正在执行: {' '.join(pyinstaller_args[3:])}\n")
    
    try:
        result = subprocess.run(pyinstaller_args, cwd=current_dir)
        
        if result.returncode == 0:
            dist_path = os.path.join(current_dir, "dist", app_name)
            print("\n" + "=" * 50)
            print("✅ 打包成功!")
            print(f"📍 应用位置: {dist_path}")
            print("=" * 50)
        else:
            print("\n❌ 打包失败，请检查错误信息")
            
    except FileNotFoundError:
        print("\n❌ 找不到PyInstaller，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("请重新运行此脚本")

if __name__ == "__main__":
    build_mac_app()
