"""
AUTOSAR XML阅读器 - 打包脚本

使用PyInstaller将程序打包为Windows可执行文件。
"""

import subprocess
import sys
from pathlib import Path


def build():
    """打包程序"""
    # 获取项目根目录
    root_dir = Path(__file__).parent
    main_script = root_dir / "src" / "main.py"
    icon_file = root_dir / "icon.ico"
    
    # PyInstaller 配置
    pyinstaller_args = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=ARXML阅读器",
        "--onefile",  # 打包为单个文件
        "--windowed",  # Windows GUI模式，不显示控制台
        "--clean",  # 清理临时文件
        f"--distpath={root_dir / 'dist'}",
        f"--workpath={root_dir / 'build'}",
        f"--specpath={root_dir}",
        # 添加图标
        f"--icon={icon_file}",
        # 添加必要的隐藏导入
        "--hidden-import=customtkinter",
        "--hidden-import=lxml",
        "--hidden-import=lxml.etree",
        "--hidden-import=openpyxl",
        # 收集customtkinter的数据文件
        "--collect-data=customtkinter",
        str(main_script),
    ]
    
    print("=" * 60)
    print("开始打包 AUTOSAR XML阅读器...")
    print("=" * 60)
    
    # 运行PyInstaller
    result = subprocess.run(pyinstaller_args, cwd=root_dir)
    
    if result.returncode == 0:
        print("=" * 60)
        print("✅ 打包成功！")
        print(f"📁 输出文件: {root_dir / 'dist' / 'ARXML阅读器.exe'}")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ 打包失败！")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build()
