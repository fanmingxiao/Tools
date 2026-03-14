# PDF批量转JPG工具

## 功能简介
这是一个基于 Python 和 `tkinter` 的桌面图形界面小工具，用于将选中的 PDF 文件批量转换为 JPG 格式的图片。支持在界面中调节导出的图片质量。

## 使用条件
- 需要安装 Python 环境。
- 操作系统中必须安装 `poppler` 工具（核心依赖）。
  - **macOS (Homebrew)**: `brew install poppler`
  - **Windows/Linux**: 需根据对应系统安装 `poppler` 并配置到环境变量。

## 安装依赖
使用 `uv` 进行依赖安装与管理：
```bash
uv sync
```
*或者使用 pip：*
```bash
pip install pdf2image Pillow
```

## 使用方法
```bash
uv run python pdf2jpg.py
```
运行后会弹出图形界面：
1. 点击“选择PDF文件”可多选需要解析的 PDF。
2. 通过滑块调节导出的 JPG 质量（1-100）。
3. 点击“开始转换”并选择输出目录。
4. 工具将在后台逐步转换并实时显示进度，PDF 第一页会变成 `page_001.jpg` 等等，均会存入与原文件同名的新文件夹中。
