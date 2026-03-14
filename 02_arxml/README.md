# AUTOSAR XML阅读器

一个用于读取AUTOSAR XML（ARXML）文件并将其内容导出为Excel或CANoe DBC格式的桌面应用程序。

## 功能特性

- 📂 支持加载单个或多个ARXML文件
- 📁 支持从文件夹批量加载
- 🔍 预览XML结构和内容
- 🔎 关键字搜索功能
- 📊 导出为格式化的Excel文件
- 🚗 **导出为CANoe DBC文件**（CAN数据库格式）
- 🎨 现代化深色/浅色主题界面

## 安装依赖

```bash
uv sync
```

## 运行程序

```bash
uv run python -m src.main
```

## 打包为可执行程序

### macOS
```bash
uv run python build.py
```
打包后的应用将生成在 `dist/ARXML阅读器.app`

### Windows
在Windows系统上运行：
```bash
pip install customtkinter lxml openpyxl pyinstaller
python build.py
```
打包后的exe文件将生成在 `dist/ARXML阅读器.exe`

## 导出功能说明

### Excel导出
将解析后的ARXML数据导出为结构化的Excel文件，包含：
- 概览工作表（统计信息）
- 按元素类型分类的详细工作表
- 包结构工作表

### DBC导出
将ARXML数据转换为CANoe兼容的DBC文件格式：
- 软件组件 → CAN节点 (BU_)
- 发送接收接口 → CAN消息 (BO_) 和信号 (SG_)
- 客户端服务端接口 → CAN消息和信号
- 描述信息 → 注释 (CM_)

## 技术栈

- Python 3.10+
- CustomTkinter (GUI)
- lxml (XML解析)
- openpyxl (Excel导出)
- PyInstaller (打包)

## 项目结构

```
arxml/
├── src/
│   ├── main.py           # 程序入口
│   ├── gui.py            # 图形界面
│   ├── arxml_parser.py   # ARXML解析器
│   ├── excel_exporter.py # Excel导出模块
│   └── dbc_exporter.py   # DBC导出模块
├── examples/
│   └── sample.arxml      # 示例文件
├── build.py              # 打包脚本
├── icon.ico              # 应用图标
└── README.md
```
