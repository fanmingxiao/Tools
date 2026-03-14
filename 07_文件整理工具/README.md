# 智能文件整理工具

一个类似 Claude Cowork 的智能文件整理分类工具，能够按文件类型和关键字自动分类整理指定文件夹内的文件。

## 功能特性

- 📁 **按文件类型分类**：自动识别图片、文档、视频、音频、压缩包、代码等文件类型
- 🔑 **按关键字分类**：支持自定义关键字规则，优先级高于类型分类
- 👁️ **预览模式**：整理前可预览分类结果
- 📊 **整理报告**：生成详细的 Markdown 格式整理日志
- 🖥️ **图形界面**：简洁易用的 GUI 界面

## 快速开始

### 安装依赖

```bash
cd /Users/fanmingxiao/个人文档/Antigravity/文件整理工具
uv pip install -r requirements.txt
```

### 运行程序

```bash
uv run python file_organizer.py
```

## 使用说明

1. **选择源文件夹**：点击「浏览」选择要整理的文件夹
2. **设置输出目录**：默认在源文件夹下创建「已整理」目录
3. **配置关键字规则**（可选）：添加自定义关键字分类规则
4. **预览分类**：点击「预览分类」查看分类结果
5. **开始整理**：确认无误后点击「开始整理」执行文件移动
6. **导出报告**：整理完成后可导出 Markdown 格式报告

## 文件类型分类

| 分类 | 支持的扩展名 |
|------|-------------|
| 📷 图片 | jpg, jpeg, png, gif, bmp, webp, svg, ico, tiff, heic |
| 📄 文档 | doc, docx, pdf, txt, rtf, xls, xlsx, ppt, pptx, md |
| 🎬 视频 | mp4, avi, mkv, mov, wmv, flv, webm, m4v |
| 🎵 音频 | mp3, wav, flac, aac, ogg, wma, m4a |
| 📦 压缩包 | zip, rar, 7z, tar, gz, bz2, dmg, iso |
| 💻 代码 | py, js, ts, html, css, java, c, cpp, go, rs |
| 📊 数据 | json, xml, csv, yaml, yml, sql, db |
| 🔧 可执行 | exe, msi, app, deb, rpm, pkg, apk |
| ❓ 未分类 | 未识别的其他文件 |

## 项目结构

```
文件整理工具/
├── file_organizer.py    # 主程序和 GUI 界面
├── organizer_core.py    # 核心整理逻辑
├── config.py            # 配置和分类规则
├── logger.py            # 日志报告生成
├── requirements.txt     # 依赖列表
└── README.md            # 本文档
```
