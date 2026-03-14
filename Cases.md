# 小工具目录汇总归档

这里收集了日常开发和办公中使用的各种自动化小工具，每个工具都有自己独立的目录及详细的 `Readme.md` 说明。

| 序号 | 目录 | 工具名称 | 功能要点 | 使用条件 & 技术栈 |
|---|---|---|---|---|
| 01 | `01_PDF邮件工具` | PDF邮件发送助手 | 自动收集目录下的 PDF 文件，调用 Outlook 生成带附件的邮件，完成后按日期归档。 | Windows系统，需安装 Microsoft Outlook。 (Bat + VBS) |
| 02 | `02_arxml` | AUTOSAR XML 阅读器 | 读取 ARXML 文件，支持导出为 Excel 或 CANoe DBC 格式。 | Python (CustomTkinter, lxml, openpyxl) |
| 03 | `03_pdf2jpg` | PDF批量转JPG工具 | 支持图形界面批量操作，自定义导出图片质量。 | Python (Tkinter, pdf2image) + 需安装 **poppler** |
| 04 | `04_发票识别工具` | 发票 OCR 识别工具 | 批量扫描图片，自动识别发票要素（代码、号码、金额、税额等）并导出为 Excel。 | Python (Tkinter, PaddleOCR, openpyxl) |
| 05 | `05_合并excel` | Excel 批量合并工具 | 批量合并多个 Excel 文件的表单，保留原格式，并自动生成带超链接的目录页。 | Python (Tkinter, openpyxl, xlrd) |
| 06 | `06_文件夹监控工具` | 文件夹实时监控工具 | 实时监控本地或网络共享文件夹的新文件变动，并提供弹窗提醒和日志记录。 | Windows系统。 (PowerShell) |
| 07 | `07_文件整理工具` | 智能文件整理工具 | 按文件类型（图片、文档、音视频等）和关键字自动对杂乱的文件夹进行分类与整理，生成报告。 | Python (Tkinter) |
| 08 | `08_答题打怪游戏` | 答题打怪小游戏 | 导入 CSV 题库的网页文字刷题小游戏。答对题目击败怪物闯关。 | 纯前端 (HTML + CSS + JS) |

## 使用说明
要了解某个具体工具的详细使用步骤和环境搭建，请进入对应的文件夹并查看其中的 `Readme.md`。
