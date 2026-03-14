# -*- coding: utf-8 -*-
"""
配置模块 - 定义文件类型分类规则和默认关键字配置
"""

import json
import os
from pathlib import Path

# 文件类型分类规则
FILE_TYPES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".heic", ".raw"],
    "文档": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".md", ".pages", ".numbers", ".key"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".ape"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".dmg", ".iso"],
    "代码": [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".swift", ".kt", ".rb", ".php", ".sh", ".bat"],
    "数据": [".json", ".xml", ".csv", ".yaml", ".yml", ".sql", ".db", ".sqlite", ".arxml"],
    "可执行": [".exe", ".msi", ".app", ".deb", ".rpm", ".pkg", ".apk", ".ipa"],
}

# 默认关键字规则示例
DEFAULT_KEYWORDS = {
    "项目文档": ["project", "项目", "工程"],
    "财务": ["invoice", "receipt", "发票", "收据", "报销"],
    "会议": ["meeting", "会议", "纪要", "minutes"],
    "截图": ["screenshot", "截图", "screen"],
}

# 配置文件路径
CONFIG_DIR = Path.home() / ".file_organizer"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_extension_category(extension: str) -> str:
    """
    根据扩展名获取文件类型分类
    
    Args:
        extension: 文件扩展名（包含点号，如 .jpg）
    
    Returns:
        分类名称，如果无法识别则返回 "未分类"
    """
    ext_lower = extension.lower()
    for category, extensions in FILE_TYPES.items():
        if ext_lower in extensions:
            return category
    return "未分类"


def load_config() -> dict:
    """
    加载用户配置文件
    
    Returns:
        配置字典，包含关键字规则等
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # 返回默认配置
    return {
        "keywords": DEFAULT_KEYWORDS.copy(),
        "include_subfolders": False,
        "preview_mode": True,
    }


def save_config(config: dict) -> bool:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
    
    Returns:
        保存是否成功
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_category_emoji(category: str) -> str:
    """
    获取分类对应的emoji图标
    
    Args:
        category: 分类名称
    
    Returns:
        对应的emoji
    """
    emoji_map = {
        "图片": "📷",
        "文档": "📄",
        "视频": "🎬",
        "音频": "🎵",
        "压缩包": "📦",
        "代码": "💻",
        "数据": "📊",
        "可执行": "🔧",
        "未分类": "❓",
    }
    return emoji_map.get(category, "📁")
