"""
AUTOSAR XML阅读器 - 图形用户界面模块

使用CustomTkinter构建现代化的桌面应用界面。
支持：文件加载、预览、关键字搜索、Excel导出
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
import re

from .arxml_parser import ARXMLParser
from .excel_exporter import ExcelExporter
from .dbc_exporter import DBCExporter


class ARXMLReaderApp(ctk.CTk):
    """ARXML阅读器主应用程序"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title("AUTOSAR XML阅读器")
        self.geometry("1100x850")
        self.minsize(900, 750)
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 数据存储
        self.loaded_files: List[str] = []
        self.parsed_data: Dict[str, Any] = {}
        self.parser: Optional[ARXMLParser] = None
        self.raw_xml_content: str = ""  # 存储原始XML内容
        
        # 创建界面
        self._create_widgets()
        self._create_layout()
        
    def _create_widgets(self):
        """创建界面组件"""
        # ===== 顶部工具栏 =====
        self.toolbar_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        
        # Logo/标题
        self.title_label = ctk.CTkLabel(
            self.toolbar_frame,
            text="📄 AUTOSAR XML阅读器",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        
        # 主题切换按钮
        self.theme_var = ctk.StringVar(value="dark")
        self.theme_switch = ctk.CTkSwitch(
            self.toolbar_frame,
            text="深色模式",
            variable=self.theme_var,
            onvalue="dark",
            offvalue="light",
            command=self._toggle_theme
        )
        
        # ===== 左侧控制面板 =====
        self.control_frame = ctk.CTkFrame(self, width=280)
        
        # 文件选择区
        self.file_section_label = ctk.CTkLabel(
            self.control_frame,
            text="📁 文件选择",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        self.select_file_btn = ctk.CTkButton(
            self.control_frame,
            text="选择ARXML文件",
            command=self._select_file,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        
        self.select_folder_btn = ctk.CTkButton(
            self.control_frame,
            text="选择文件夹",
            command=self._select_folder,
            height=40,
            fg_color="transparent",
            border_width=2,
            font=ctk.CTkFont(size=13)
        )
        
        # 已加载文件列表
        self.files_label = ctk.CTkLabel(
            self.control_frame,
            text="已加载文件:",
            font=ctk.CTkFont(size=12)
        )
        
        self.files_listbox = ctk.CTkTextbox(
            self.control_frame,
            height=80,
            font=ctk.CTkFont(size=11)
        )
        self.files_listbox.configure(state="disabled")
        
        self.clear_files_btn = ctk.CTkButton(
            self.control_frame,
            text="清除文件",
            command=self._clear_files,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=ctk.CTkFont(size=12)
        )
        
        # ===== 搜索区 =====
        self.search_section_label = ctk.CTkLabel(
            self.control_frame,
            text="🔍 关键字搜索",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        self.search_entry = ctk.CTkEntry(
            self.control_frame,
            placeholder_text="输入搜索关键字...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.bind("<Return>", lambda e: self._search_keyword())
        
        self.search_btn = ctk.CTkButton(
            self.control_frame,
            text="搜索",
            command=self._search_keyword,
            height=35,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            font=ctk.CTkFont(size=12)
        )
        
        # 操作区
        self.action_section_label = ctk.CTkLabel(
            self.control_frame,
            text="⚡ 操作",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        self.parse_btn = ctk.CTkButton(
            self.control_frame,
            text="解析文件",
            command=self._parse_files,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#27AE60",
            hover_color="#219A52"
        )
        
        self.export_btn = ctk.CTkButton(
            self.control_frame,
            text="导出为Excel",
            command=self._export_to_excel,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3498DB",
            hover_color="#2980B9"
        )
        
        # DBC导出按钮
        self.export_dbc_btn = ctk.CTkButton(
            self.control_frame,
            text="导出为DBC",
            command=self._export_to_dbc,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        
        # 进度条
        self.progress_label = ctk.CTkLabel(
            self.control_frame,
            text="就绪",
            font=ctk.CTkFont(size=11)
        )
        
        self.progress_bar = ctk.CTkProgressBar(self.control_frame)
        self.progress_bar.set(0)
        
        # ===== 右侧预览区 =====
        self.preview_frame = ctk.CTkFrame(self)
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="📊 解析结果预览",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        # 选项卡视图
        self.tabview = ctk.CTkTabview(self.preview_frame)
        self.tabview.add("结构树")
        self.tabview.add("统计信息")
        self.tabview.add("元素列表")
        self.tabview.add("原始XML")
        self.tabview.add("搜索结果")
        
        # 结构树文本框
        self.tree_textbox = ctk.CTkTextbox(
            self.tabview.tab("结构树"),
            font=ctk.CTkFont(family="Courier New", size=12)
        )
        
        # 统计信息文本框
        self.stats_textbox = ctk.CTkTextbox(
            self.tabview.tab("统计信息"),
            font=ctk.CTkFont(size=12)
        )
        
        # 元素列表文本框
        self.elements_textbox = ctk.CTkTextbox(
            self.tabview.tab("元素列表"),
            font=ctk.CTkFont(family="Courier New", size=11)
        )
        
        # 原始XML文本框
        self.raw_xml_textbox = ctk.CTkTextbox(
            self.tabview.tab("原始XML"),
            font=ctk.CTkFont(family="Courier New", size=11)
        )
        
        # 搜索结果文本框
        self.search_textbox = ctk.CTkTextbox(
            self.tabview.tab("搜索结果"),
            font=ctk.CTkFont(family="Courier New", size=11)
        )
        
    def _create_layout(self):
        """布局界面组件"""
        # 顶部工具栏
        self.toolbar_frame.pack(fill="x", padx=0, pady=0)
        self.title_label.pack(side="left", padx=20, pady=15)
        self.theme_switch.pack(side="right", padx=20, pady=15)
        
        # 左侧控制面板
        self.control_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        
        # 文件选择区
        self.file_section_label.pack(anchor="w", padx=15, pady=(15, 10))
        self.select_file_btn.pack(fill="x", padx=15, pady=5)
        self.select_folder_btn.pack(fill="x", padx=15, pady=5)
        self.files_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.files_listbox.pack(fill="x", padx=15, pady=5)
        self.clear_files_btn.pack(fill="x", padx=15, pady=5)
        
        # 搜索区
        self.search_section_label.pack(anchor="w", padx=15, pady=(15, 10))
        self.search_entry.pack(fill="x", padx=15, pady=5)
        self.search_btn.pack(fill="x", padx=15, pady=5)
        
        # 操作区
        self.action_section_label.pack(anchor="w", padx=15, pady=(15, 10))
        self.parse_btn.pack(fill="x", padx=15, pady=5)
        self.export_btn.pack(fill="x", padx=15, pady=5)
        self.export_dbc_btn.pack(fill="x", padx=15, pady=5)
        
        # 进度条
        self.progress_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        
        # 右侧预览区
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.preview_label.pack(anchor="w", padx=15, pady=(15, 10))
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 选项卡内容
        self.tree_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.stats_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.elements_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.raw_xml_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.search_textbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _toggle_theme(self):
        """切换主题"""
        mode = self.theme_var.get()
        ctk.set_appearance_mode(mode)
        self.theme_switch.configure(text="深色模式" if mode == "dark" else "浅色模式")
    
    def _select_file(self):
        """选择ARXML文件"""
        files = filedialog.askopenfilenames(
            title="选择ARXML文件",
            filetypes=[
                ("ARXML文件", "*.arxml"),
                ("XML文件", "*.xml"),
                ("所有文件", "*.*")
            ]
        )
        
        if files:
            for file in files:
                if file not in self.loaded_files:
                    self.loaded_files.append(file)
            self._update_files_list()
    
    def _select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含ARXML文件的文件夹")
        
        if folder:
            folder_path = Path(folder)
            arxml_files = list(folder_path.glob("*.arxml")) + list(folder_path.glob("*.xml"))
            
            for file in arxml_files:
                file_str = str(file)
                if file_str not in self.loaded_files:
                    self.loaded_files.append(file_str)
            
            self._update_files_list()
    
    def _update_files_list(self):
        """更新文件列表显示"""
        self.files_listbox.configure(state="normal")
        self.files_listbox.delete("0.0", "end")
        
        for file in self.loaded_files:
            filename = Path(file).name
            self.files_listbox.insert("end", f"• {filename}\n")
        
        self.files_listbox.configure(state="disabled")
    
    def _clear_files(self):
        """清除所有文件"""
        self.loaded_files.clear()
        self.parsed_data = {}
        self.parser = None
        self.raw_xml_content = ""
        
        self.files_listbox.configure(state="normal")
        self.files_listbox.delete("0.0", "end")
        self.files_listbox.configure(state="disabled")
        
        self.tree_textbox.delete("0.0", "end")
        self.stats_textbox.delete("0.0", "end")
        self.elements_textbox.delete("0.0", "end")
        self.raw_xml_textbox.delete("0.0", "end")
        self.search_textbox.delete("0.0", "end")
        
        self.progress_bar.set(0)
        self._update_status("已清除")
    
    def _parse_files(self):
        """解析文件"""
        if not self.loaded_files:
            messagebox.showwarning("警告", "请先选择ARXML文件！")
            return
        
        # 在后台线程中解析
        self._update_status("正在解析...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._parse_files_thread, daemon=True).start()
    
    def _parse_files_thread(self):
        """后台解析线程"""
        try:
            total_files = len(self.loaded_files)
            all_packages = []
            all_raw_content = []
            
            for i, file_path in enumerate(self.loaded_files):
                self.parser = ARXMLParser()
                
                # 读取原始XML内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        all_raw_content.append(f"{'='*60}\n文件: {Path(file_path).name}\n{'='*60}\n{content}\n\n")
                except Exception as e:
                    all_raw_content.append(f"读取文件失败: {file_path}\n错误: {e}\n\n")
                
                if self.parser.load_file(file_path):
                    data = self.parser.parse()
                    packages = data.get('packages', [])
                    all_packages.extend(packages)
                
                # 更新进度
                progress = (i + 1) / total_files
                self.after(0, lambda p=progress: self.progress_bar.set(p))
            
            self.parsed_data = {
                'file_info': {'schema_version': '', 'admin_data': {}},
                'packages': all_packages
            }
            self.raw_xml_content = "".join(all_raw_content)
            
            # 更新UI
            self.after(0, self._update_preview)
            self.after(0, lambda: self._update_status(f"解析完成 - {total_files}个文件"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("错误", f"解析失败: {str(e)}"))
            self.after(0, lambda: self._update_status("解析失败"))
    
    def _update_preview(self):
        """更新预览显示"""
        if not self.parsed_data:
            return
        
        # 更新结构树
        self._update_tree_view()
        
        # 更新统计信息
        self._update_stats_view()
        
        # 更新元素列表
        self._update_elements_view()
        
        # 更新原始XML
        self._update_raw_xml_view()
    
    def _update_tree_view(self):
        """更新结构树视图"""
        self.tree_textbox.delete("0.0", "end")
        
        def format_package(pkg: Dict[str, Any], level: int = 0) -> str:
            indent = "  " * level
            lines = []
            
            # 包信息
            pkg_icon = "📦" if level == 0 else "📁"
            lines.append(f"{indent}{pkg_icon} {pkg['short_name']}")
            
            if pkg.get('long_name'):
                lines.append(f"{indent}   └─ 长名称: {pkg['long_name']}")
            
            # 元素
            for elem in pkg.get('elements', []):
                elem_type = elem.get('type', 'Unknown')
                elem_name = elem.get('short_name', '')
                
                # 根据类型选择图标
                icon = self._get_element_icon(elem_type)
                lines.append(f"{indent}   ├─ {icon} [{elem_type}] {elem_name}")
            
            # 子包
            for sub_pkg in pkg.get('sub_packages', []):
                lines.append(format_package(sub_pkg, level + 1))
            
            return "\n".join(lines)
        
        tree_text = []
        for pkg in self.parsed_data.get('packages', []):
            tree_text.append(format_package(pkg))
        
        self.tree_textbox.insert("0.0", "\n\n".join(tree_text))
    
    def _get_element_icon(self, elem_type: str) -> str:
        """根据元素类型获取图标"""
        icons = {
            'APPLICATION-SW-COMPONENT-TYPE': '🔧',
            'SENDER-RECEIVER-INTERFACE': '📡',
            'CLIENT-SERVER-INTERFACE': '🔌',
            'IMPLEMENTATION-DATA-TYPE': '📊',
            'APPLICATION-PRIMITIVE-DATA-TYPE': '🔢',
            'COMPU-METHOD': '📐',
            'UNIT': '📏',
            'SW-BASE-TYPE': '🔤',
        }
        return icons.get(elem_type, '📄')
    
    def _update_stats_view(self):
        """更新统计信息视图"""
        self.stats_textbox.delete("0.0", "end")
        
        stats = {
            '总包数': 0,
            '总元素数': 0,
        }
        element_types = {}
        
        def count_package(pkg: Dict[str, Any]):
            stats['总包数'] += 1
            
            for elem in pkg.get('elements', []):
                stats['总元素数'] += 1
                elem_type = elem.get('type', 'Unknown')
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            for sub_pkg in pkg.get('sub_packages', []):
                count_package(sub_pkg)
        
        for pkg in self.parsed_data.get('packages', []):
            count_package(pkg)
        
        # 格式化输出
        lines = [
            "═══════════════════════════════════════",
            "           📊 统计摘要",
            "═══════════════════════════════════════",
            "",
            f"   📁 总包数:      {stats['总包数']}",
            f"   📄 总元素数:    {stats['总元素数']}",
            "",
            "───────────────────────────────────────",
            "           元素类型分布",
            "───────────────────────────────────────",
            ""
        ]
        
        for elem_type, count in sorted(element_types.items(), key=lambda x: -x[1]):
            icon = self._get_element_icon(elem_type)
            lines.append(f"   {icon} {elem_type}: {count}")
        
        self.stats_textbox.insert("0.0", "\n".join(lines))
    
    def _update_elements_view(self):
        """更新元素列表视图"""
        self.elements_textbox.delete("0.0", "end")
        
        lines = [
            "类型                                | 短名称                    | 包路径",
            "─" * 100
        ]
        
        def list_elements(pkg: Dict[str, Any], path: str = ''):
            current_path = f"{path}/{pkg['short_name']}" if path else pkg['short_name']
            
            for elem in pkg.get('elements', []):
                elem_type = elem.get('type', 'Unknown')[:35].ljust(35)
                elem_name = elem.get('short_name', '')[:25].ljust(25)
                lines.append(f"{elem_type} | {elem_name} | {current_path}")
            
            for sub_pkg in pkg.get('sub_packages', []):
                list_elements(sub_pkg, current_path)
        
        for pkg in self.parsed_data.get('packages', []):
            list_elements(pkg)
        
        self.elements_textbox.insert("0.0", "\n".join(lines))
    
    def _update_raw_xml_view(self):
        """更新原始XML视图"""
        self.raw_xml_textbox.delete("0.0", "end")
        self.raw_xml_textbox.insert("0.0", self.raw_xml_content)
    
    def _search_keyword(self):
        """搜索关键字"""
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("警告", "请输入搜索关键字！")
            return
        
        if not self.raw_xml_content and not self.parsed_data:
            messagebox.showwarning("警告", "请先解析ARXML文件！")
            return
        
        self._update_status(f"正在搜索: {keyword}")
        
        # 在后台线程中搜索
        threading.Thread(
            target=self._search_keyword_thread,
            args=(keyword,),
            daemon=True
        ).start()
    
    def _search_keyword_thread(self, keyword: str):
        """后台搜索线程"""
        try:
            results = []
            
            # 1. 在解析后的元素中搜索
            results.append("═══════════════════════════════════════")
            results.append(f"  🔍 搜索关键字: \"{keyword}\"")
            results.append("═══════════════════════════════════════\n")
            
            # 在元素中搜索
            element_results = []
            def search_in_package(pkg: Dict[str, Any], path: str = ''):
                current_path = f"{path}/{pkg['short_name']}" if path else pkg['short_name']
                
                # 检查包名
                if keyword.lower() in pkg.get('short_name', '').lower():
                    element_results.append(f"📦 包: {current_path}")
                
                for elem in pkg.get('elements', []):
                    # 检查元素名
                    short_name = elem.get('short_name', '')
                    long_name = elem.get('long_name', '')
                    description = elem.get('description', '')
                    elem_type = elem.get('type', '')
                    
                    matches = []
                    if keyword.lower() in short_name.lower():
                        matches.append(f"短名称: {short_name}")
                    if keyword.lower() in long_name.lower():
                        matches.append(f"长名称: {long_name}")
                    if keyword.lower() in description.lower():
                        matches.append(f"描述: {description[:50]}...")
                    
                    if matches:
                        icon = self._get_element_icon(elem_type)
                        element_results.append(f"{icon} [{elem_type}] {short_name}")
                        element_results.append(f"   路径: {current_path}")
                        for m in matches:
                            element_results.append(f"   匹配: {m}")
                        element_results.append("")
                
                for sub_pkg in pkg.get('sub_packages', []):
                    search_in_package(sub_pkg, current_path)
            
            for pkg in self.parsed_data.get('packages', []):
                search_in_package(pkg)
            
            if element_results:
                results.append("【元素匹配结果】")
                results.append("─" * 40)
                results.extend(element_results)
            else:
                results.append("【元素匹配结果】")
                results.append("未找到匹配的元素")
            
            results.append("\n")
            
            # 2. 在原始XML中搜索（显示行号）
            results.append("【原始XML匹配结果】")
            results.append("─" * 40)
            
            if self.raw_xml_content:
                lines_with_keyword = []
                for i, line in enumerate(self.raw_xml_content.split('\n'), 1):
                    if keyword.lower() in line.lower():
                        # 高亮关键字
                        highlighted_line = line.strip()
                        lines_with_keyword.append(f"行 {i}: {highlighted_line}")
                
                if lines_with_keyword:
                    results.append(f"找到 {len(lines_with_keyword)} 个匹配行:\n")
                    results.extend(lines_with_keyword[:100])  # 限制显示100行
                    if len(lines_with_keyword) > 100:
                        results.append(f"\n... 还有 {len(lines_with_keyword) - 100} 个匹配项")
                else:
                    results.append("未在原始XML中找到匹配")
            
            # 更新UI
            self.after(0, lambda: self._display_search_results("\n".join(results)))
            self.after(0, lambda: self._update_status(f"搜索完成"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("错误", f"搜索失败: {str(e)}"))
    
    def _display_search_results(self, results: str):
        """显示搜索结果"""
        self.search_textbox.delete("0.0", "end")
        self.search_textbox.insert("0.0", results)
        # 切换到搜索结果选项卡
        self.tabview.set("搜索结果")
    
    def _export_to_excel(self):
        """导出到Excel"""
        if not self.parsed_data:
            messagebox.showwarning("警告", "请先解析ARXML文件！")
            return
        
        # 选择保存路径
        output_path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")]
        )
        
        if not output_path:
            return
        
        self._update_status("正在导出...")
        self.progress_bar.set(0.5)
        
        threading.Thread(
            target=self._export_thread,
            args=(output_path,),
            daemon=True
        ).start()
    
    def _export_thread(self, output_path: str):
        """后台导出线程"""
        try:
            exporter = ExcelExporter()
            success = exporter.export(self.parsed_data, output_path)
            
            self.after(0, lambda: self.progress_bar.set(1.0))
            
            if success:
                self.after(0, lambda: self._update_status("导出完成"))
                self.after(0, lambda: messagebox.showinfo(
                    "成功",
                    f"Excel文件已保存到:\n{output_path}"
                ))
            else:
                self.after(0, lambda: self._update_status("导出失败"))
                self.after(0, lambda: messagebox.showerror("错误", "导出失败"))
                
        except Exception as e:
            self.after(0, lambda: self._update_status("导出失败"))
            self.after(0, lambda: messagebox.showerror("错误", f"导出失败: {str(e)}"))
    
    def _export_to_dbc(self):
        """导出到DBC文件"""
        if not self.parsed_data:
            messagebox.showwarning("警告", "请先解析ARXML文件！")
            return
        
        # 选择保存路径
        output_path = filedialog.asksaveasfilename(
            title="保存DBC文件",
            defaultextension=".dbc",
            filetypes=[("DBC文件", "*.dbc"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
        
        self._update_status("正在导出DBC...")
        self.progress_bar.set(0.5)
        
        threading.Thread(
            target=self._export_dbc_thread,
            args=(output_path,),
            daemon=True
        ).start()
    
    def _export_dbc_thread(self, output_path: str):
        """后台DBC导出线程"""
        try:
            exporter = DBCExporter()
            success = exporter.export(self.parsed_data, output_path)
            
            self.after(0, lambda: self.progress_bar.set(1.0))
            
            if success:
                self.after(0, lambda: self._update_status("DBC导出完成"))
                self.after(0, lambda: messagebox.showinfo(
                    "成功",
                    f"DBC文件已保存到:\n{output_path}"
                ))
            else:
                self.after(0, lambda: self._update_status("DBC导出失败"))
                self.after(0, lambda: messagebox.showerror("错误", "DBC导出失败"))
                
        except Exception as e:
            self.after(0, lambda: self._update_status("DBC导出失败"))
            self.after(0, lambda: messagebox.showerror("错误", f"DBC导出失败: {str(e)}"))
    
    def _update_status(self, text: str):
        """更新状态文本"""
        self.progress_label.configure(text=text)


def run_app():
    """启动应用程序"""
    app = ARXMLReaderApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
