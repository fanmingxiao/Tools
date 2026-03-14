# -*- coding: utf-8 -*-
"""
GUI界面模块
发票识别工具的图形用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Optional
import queue

from scanner import scan_files, get_image_info, pdf_to_images, extract_pdf_text, heic_to_image, cleanup_temp_images, is_pdf
from ocr_engine import get_ocr_engine
from invoice_parser import parse_invoice, InvoiceInfo
from excel_exporter import export_to_excel, generate_output_filename


class InvoiceScannerApp:
    """发票识别工具主应用"""
    
    def __init__(self, root: tk.Tk):
        """初始化应用"""
        self.root = root
        self.root.title("发票识别工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 数据存储
        self.files_to_process: List[tuple] = []  # (文件路径, 文件类型)
        self.invoices: List[InvoiceInfo] = []
        self.selected_directory: str = ""
        self.is_processing: bool = False
        self.message_queue = queue.Queue()
        
        # 创建界面
        self._create_ui()
        
        # 定期检查消息队列
        self._check_queue()
    
    def _create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制区
        self._create_control_panel(main_frame)
        
        # 中间结果显示区
        self._create_result_panel(main_frame)
        
        # 底部状态栏
        self._create_status_bar(main_frame)
    
    def _create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="操作区", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：文件夹选择
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="发票目录:").pack(side=tk.LEFT)
        
        self.dir_entry = ttk.Entry(row1, width=60)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(row1, text="浏览...", command=self._browse_directory)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        
        # 第二行：选项和按钮
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=5)
        
        self.recursive_var = tk.BooleanVar(value=False)
        self.recursive_check = ttk.Checkbutton(
            row2, 
            text="包含子目录",
            variable=self.recursive_var
        )
        self.recursive_check.pack(side=tk.LEFT)
        
        # 按钮组
        btn_frame = ttk.Frame(row2)
        btn_frame.pack(side=tk.RIGHT)
        
        self.scan_btn = ttk.Button(
            btn_frame, 
            text="开始识别", 
            command=self._start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(
            btn_frame, 
            text="导出Excel", 
            command=self._export_excel,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="清空结果", 
            command=self._clear_results
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_result_panel(self, parent):
        """创建结果显示面板"""
        result_frame = ttk.LabelFrame(parent, text="识别结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview表格
        columns = ('序号', '文件名', '发票代码', '发票号码', '金额', '税率', '税额', '价税合计', '日期', '销售方')
        
        # 创建滚动条
        scroll_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL)
        
        self.result_tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.config(command=self.result_tree.yview)
        scroll_x.config(command=self.result_tree.xview)
        
        # 设置列标题和宽度
        column_widths = {
            '序号': 50,
            '文件名': 150,
            '发票代码': 100,
            '发票号码': 130,
            '金额': 80,
            '税率': 60,
            '税额': 80,
            '价税合计': 100,
            '日期': 90,
            '销售方': 200
        }
        
        for col in columns:
            self.result_tree.heading(col, text=col, anchor=tk.CENTER)
            self.result_tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
        
        # 布局
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # 进度条
        self.progress = ttk.Progressbar(
            status_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(side=tk.LEFT, padx=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 统计信息
        self.stats_label = ttk.Label(status_frame, text="")
        self.stats_label.pack(side=tk.RIGHT)
    
    def _browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(
            title="选择发票图片目录",
            initialdir=os.path.expanduser("~")
        )
        
        if directory:
            self.selected_directory = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def _start_scan(self):
        """开始扫描识别"""
        directory = self.dir_entry.get().strip()
        
        if not directory:
            messagebox.showwarning("警告", "请先选择发票目录！")
            return
        
        if not os.path.isdir(directory):
            messagebox.showerror("错误", "指定的目录不存在！")
            return
        
        # 扫描发票文件（图片和PDF）
        try:
            recursive = self.recursive_var.get()
            
            # 清空之前的结果（在扫描前清空）
            self._clear_results()
            
            # 调试：显示扫描的目录
            print(f"[调试] 扫描目录: {directory}")
            print(f"[调试] 递归扫描: {recursive}")
            
            # 列出目录中的所有文件（调试用）
            print(f"[调试] 目录内容:")
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    print(f"  - [文件] {item} (扩展名: {ext})")
                else:
                    print(f"  - [目录] {item}/")
            
            self.files_to_process = scan_files(directory, recursive)
            
            print(f"[调试] scan_files返回 {len(self.files_to_process)} 个文件")
            
            if not self.files_to_process:
                messagebox.showinfo("提示", "未找到发票文件（图片或PDF）！")
                return
            
            # 禁用按钮
            self._set_processing_state(True)
            
            # 在后台线程中执行OCR
            thread = threading.Thread(target=self._process_files)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描目录失败: {e}")
    
    def _process_files(self):
        """处理文件（在后台线程中执行）"""
        import traceback
        temp_images = []  # 存储PDF转换的临时图片，用于清理
        
        try:
            ocr = get_ocr_engine()
            total = len(self.files_to_process)
            result_idx = 0
            
            # 调试输出：显示扫描到的文件
            print(f"[调试] 共扫描到 {total} 个文件:")
            for fp, ft in self.files_to_process:
                print(f"  - [{ft}] {fp}")
            
            for idx, (file_path, file_type) in enumerate(self.files_to_process, start=1):
                if not self.is_processing:
                    break
                
                file_name = Path(file_path).name
                print(f"[调试] 正在处理 ({idx}/{total}): {file_name} [{file_type}]")
                self.message_queue.put(('status', f"正在识别: {file_name} ({idx}/{total})"))
                self.message_queue.put(('progress', int(idx / total * 100)))
                
                try:
                    if file_type == 'pdf':
                        # PDF文件：先尝试提取文字，失败再用OCR
                        self.message_queue.put(('status', f"正在处理PDF: {file_name}"))
                        
                        # 尝试直接提取文字
                        pdf_texts, has_text = extract_pdf_text(file_path)
                        print(f"[调试] PDF文字提取: has_text={has_text}, 页数={len(pdf_texts)}")
                        if pdf_texts:
                            print(f"[调试] 首页文字长度: {len(pdf_texts[0]) if pdf_texts[0] else 0}")
                        
                        if has_text and pdf_texts:
                            # 文字版PDF：直接使用提取的文字
                            processed_any = False
                            for page_idx, text in enumerate(pdf_texts):
                                if not self.is_processing:
                                    break
                                
                                # 只要有内容就处理
                                if text.strip():
                                    processed_any = True
                                    result_idx += 1
                                    page_name = f"{file_name} (第{page_idx+1}页)" if len(pdf_texts) > 1 else file_name
                                    
                                    # 合并相邻行来处理发票代码:和数值在不同行的情况
                                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                                    merged_lines = []
                                    i = 0
                                    import re
                                    # 匹配纯数字、日期或金额的模式
                                    number_pattern = re.compile(r'^[\d\-\/年月日\.,:：]+$')
                                    
                                    while i < len(lines):
                                        current = lines[i]
                                        # 如果当前行以冒号结尾，检查下一行是否是数字/日期
                                        if i + 1 < len(lines) and (current.endswith(':') or current.endswith('：')):
                                            next_line = lines[i + 1]
                                            # 只有下一行主要是数字或日期时才合并
                                            if number_pattern.match(next_line) or (len(next_line) <= 20 and any(c.isdigit() for c in next_line)):
                                                merged_lines.append(current + next_line)
                                                i += 2
                                                continue
                                        merged_lines.append(current)
                                        i += 1
                                    
                                    # 转换为OCR结果格式
                                    ocr_result = [{'text': line, 'confidence': 1.0, 'box': []} 
                                                  for line in merged_lines]
                                    
                                    # 调试：显示合并后的文字片段
                                    print(f"[调试] {page_name} 合并后行数: {len(ocr_result)}")
                                    if ocr_result:
                                        print(f"[调试] 前5行: {[r['text'][:40] for r in ocr_result[:5]]}")
                                    
                                    # 解析发票信息
                                    invoice_info = parse_invoice(ocr_result, page_name)
                                    print(f"[调试] 解析结果: 代码={invoice_info.invoice_code}, 号码={invoice_info.invoice_number}")
                                    
                                    # 添加到结果
                                    self.message_queue.put(('result', (result_idx, invoice_info)))
                            
                            # 如果文字版PDF没有处理任何页面，尝试OCR
                            if not processed_any:
                                has_text = False
                        
                        if not has_text:
                            # 扫描件PDF：转换为图片后OCR识别
                            print(f"[调试] {file_name} 使用OCR识别（扫描件或无有效文字）")
                            self.message_queue.put(('status', f"正在OCR识别: {file_name}"))
                            pdf_images = pdf_to_images(file_path)
                            temp_images.extend(pdf_images)
                            print(f"[调试] PDF转图片: {len(pdf_images)} 页")
                            
                            for page_idx, img_path in enumerate(pdf_images):
                                if not self.is_processing:
                                    break
                                
                                result_idx += 1
                                page_name = f"{file_name} (第{page_idx+1}页)" if len(pdf_images) > 1 else file_name
                                
                                # OCR识别
                                ocr_result = ocr.recognize(img_path)
                                print(f"[调试] OCR识别 {page_name}: {len(ocr_result)} 个结果")
                                if ocr_result:
                                    print(f"[调试] OCR前3行: {[r['text'][:30] for r in ocr_result[:3]]}")
                                
                                # 解析发票信息
                                invoice_info = parse_invoice(ocr_result, page_name)
                                print(f"[调试] 解析结果: 代码={invoice_info.invoice_code}, 号码={invoice_info.invoice_number}")
                                
                                # 添加到结果
                                self.message_queue.put(('result', (result_idx, invoice_info)))
                    
                    elif file_type == 'heic':
                        # HEIC文件：先转换为标准图片再识别
                        self.message_queue.put(('status', f"正在转换HEIC: {file_name}"))
                        converted_path = heic_to_image(file_path)
                        print(f"[调试] HEIC转换结果: {converted_path}")
                        
                        if converted_path:
                            temp_images.append(converted_path)
                            result_idx += 1
                            
                            # OCR识别
                            ocr_result = ocr.recognize(converted_path)
                            print(f"[调试] HEIC OCR识别: {len(ocr_result)} 个结果")
                            if ocr_result:
                                print(f"[调试] HEIC前3行: {[r['text'][:30] if len(r['text']) > 30 else r['text'] for r in ocr_result[:3]]}")
                            
                            # 解析发票信息
                            invoice_info = parse_invoice(ocr_result, file_name)
                            print(f"[调试] HEIC解析: 代码={invoice_info.invoice_code}, 号码={invoice_info.invoice_number}")
                            
                            # 添加到结果
                            self.message_queue.put(('result', (result_idx, invoice_info)))
                        else:
                            raise Exception("HEIC转换失败")
                    
                    else:
                        # 图片文件：直接识别
                        result_idx += 1
                        
                        # OCR识别
                        ocr_result = ocr.recognize(file_path)
                        
                        # 解析发票信息
                        invoice_info = parse_invoice(ocr_result, file_name)
                        
                        # 添加到结果
                        self.message_queue.put(('result', (result_idx, invoice_info)))
                        
                except Exception as file_error:
                    # 单个文件错误不影响其他文件继续处理
                    print(f"处理文件 {file_name} 出错: {file_error}")
                    traceback.print_exc()
                    result_idx += 1
                    # 创建一个包含错误信息的空发票记录
                    error_info = InvoiceInfo()
                    error_info.file_name = file_name
                    error_info.remarks = f"识别失败: {str(file_error)[:50]}"
                    self.message_queue.put(('result', (result_idx, error_info)))
            
            self.message_queue.put(('complete', result_idx))
            
        except Exception as e:
            print(f"处理过程出错: {e}")
            traceback.print_exc()
            self.message_queue.put(('error', str(e)))
        
        finally:
            # 清理临时文件
            if temp_images:
                cleanup_temp_images(temp_images)
    
    def _check_queue(self):
        """检查消息队列"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_label.config(text=data)
                    
                elif msg_type == 'progress':
                    self.progress['value'] = data
                    
                elif msg_type == 'result':
                    idx, invoice = data
                    self._add_result_row(idx, invoice)
                    self.invoices.append(invoice)
                    
                elif msg_type == 'complete':
                    self._set_processing_state(False)
                    self._update_stats()
                    self.status_label.config(text=f"识别完成，共处理 {data} 个文件")
                    messagebox.showinfo("完成", f"识别完成！\n共处理 {data} 个发票图片")
                    
                elif msg_type == 'error':
                    self._set_processing_state(False)
                    messagebox.showerror("错误", f"识别过程出错: {data}")
                    
        except queue.Empty:
            pass
        
        # 持续检查
        self.root.after(100, self._check_queue)
    
    def _add_result_row(self, idx: int, invoice: InvoiceInfo):
        """添加结果行"""
        values = (
            idx,
            invoice.file_name,
            invoice.invoice_code,
            invoice.invoice_number,
            f"{invoice.amount:.2f}" if invoice.amount else "",
            invoice.tax_rate if invoice.tax_rate else "",
            f"{invoice.tax_amount:.2f}" if invoice.tax_amount else "",
            f"{invoice.total_amount:.2f}" if invoice.total_amount else "",
            invoice.invoice_date,
            invoice.seller_name
        )
        self.result_tree.insert('', tk.END, values=values)
    
    def _set_processing_state(self, processing: bool):
        """设置处理状态"""
        self.is_processing = processing
        
        if processing:
            self.scan_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.DISABLED)
            self.browse_btn.config(state=tk.DISABLED)
        else:
            self.scan_btn.config(state=tk.NORMAL)
            self.browse_btn.config(state=tk.NORMAL)
            if self.invoices:
                self.export_btn.config(state=tk.NORMAL)
    
    def _update_stats(self):
        """更新统计信息"""
        if not self.invoices:
            self.stats_label.config(text="")
            return
        
        total_amount = sum(inv.total_amount for inv in self.invoices)
        total_tax = sum(inv.tax_amount for inv in self.invoices)
        
        self.stats_label.config(
            text=f"共 {len(self.invoices)} 张发票 | "
                 f"金额合计: ¥{total_amount:,.2f} | "
                 f"税额合计: ¥{total_tax:,.2f}"
        )
    
    def _export_excel(self):
        """导出到Excel"""
        if not self.invoices:
            messagebox.showwarning("警告", "没有可导出的数据！")
            return
        
        # 选择保存位置
        default_name = generate_output_filename()
        file_path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            initialfile=default_name,
            initialdir=self.selected_directory or os.path.expanduser("~")
        )
        
        if not file_path:
            return
        
        # 导出
        try:
            success = export_to_excel(self.invoices, file_path)
            if success:
                messagebox.showinfo("成功", f"Excel文件已保存至:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出Excel失败！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def _clear_results(self):
        """清空结果"""
        self.invoices.clear()
        self.files_to_process.clear()
        
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.progress['value'] = 0
        self.status_label.config(text="就绪")
        self.stats_label.config(text="")
        self.export_btn.config(state=tk.DISABLED)


def create_app() -> tk.Tk:
    """创建应用实例"""
    root = tk.Tk()
    app = InvoiceScannerApp(root)
    return root
