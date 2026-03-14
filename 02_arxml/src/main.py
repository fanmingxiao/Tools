"""
AUTOSAR XML阅读器 - 程序入口

启动图形用户界面应用程序。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.gui import run_app


def main():
    """主函数"""
    run_app()


if __name__ == "__main__":
    main()

