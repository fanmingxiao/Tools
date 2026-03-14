#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF批量转JPG工具
将选中的PDF文件批量转换为JPG图片，支持质量调节
"""

import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image


def check_poppler_installed() -> tuple[bool, str]:
    """检查poppler是否已安装
    
    Returns:
        tuple: (是否已安装, poppler路径或错误信息)
    """
    # 检查pdftoppm命令是否可用（poppler的核心工具）
    pdftoppm_path = shutil.which('pdftoppm')
    if pdftoppm_path:
        return True, pdftoppm_path
    
    # 在macOS上检查Homebrew安装的poppler
    homebrew_paths = [
        '/opt/homebrew/bin/pdftoppm',  # Apple Silicon Mac
        '/usr/local/bin/pdftoppm',      # Intel Mac
    ]
    for path in homebrew_paths:
        if os.path.exists(path):
            return True, path
    
    return False, "未找到poppler工具"


class PDF2JPGApp:
    """PDF批量转JPG工具主应用类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF批量转JPG工具")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 存储选中的PDF文件路径
        self.pdf_files: list[str] = []
        # 是否正在转换
        self.is_converting = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 顶部按钮区 ===
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_select = ttk.Button(
            top_frame, 
            text="选择PDF文件", 
            command=self._select_files
        )
        self.btn_select.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_clear = ttk.Button(
            top_frame, 
            text="清空列表", 
            command=self._clear_files
        )
        self.btn_clear.pack(side=tk.LEFT)
        
        # === 质量设置区 ===
        quality_frame = ttk.LabelFrame(main_frame, text="JPG质量", padding="5")
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.quality_var = tk.IntVar(value=85)
        
        quality_inner = ttk.Frame(quality_frame)
        quality_inner.pack(fill=tk.X)
        
        self.quality_label = ttk.Label(quality_inner, text="质量: 85")
        self.quality_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quality_scale = ttk.Scale(
            quality_inner,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            command=self._on_quality_change
        )
        self.quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(quality_inner, text="(1-100，数值越大质量越好)").pack(side=tk.RIGHT)
        
        # === 文件列表区 ===
        list_frame = ttk.LabelFrame(main_frame, text="已选择的PDF文件", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建带滚动条的列表
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED,
            font=("", 11)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 绑定Delete和BackSpace键删除选中项
        self.file_listbox.bind('<Delete>', self._delete_selected)
        self.file_listbox.bind('<BackSpace>', self._delete_selected)
        
        # === 进度区 ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # === 底部按钮和状态区 ===
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        self.btn_convert = ttk.Button(
            bottom_frame,
            text="开始转换",
            command=self._start_convert
        )
        self.btn_convert.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            bottom_frame,
            textvariable=self.status_var,
            foreground="gray"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _on_quality_change(self, value):
        """质量滑块变化事件"""
        quality = int(float(value))
        self.quality_label.config(text=f"质量: {quality}")
    
    def _select_files(self):
        """选择PDF文件"""
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.pdf_files:
                    self.pdf_files.append(f)
                    self.file_listbox.insert(tk.END, f)
            self._update_status(f"已选择 {len(self.pdf_files)} 个文件")
    
    def _clear_files(self):
        """清空文件列表"""
        self.pdf_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.progress_var.set(0)
        self._update_status("列表已清空")
    
    def _delete_selected(self, event=None):
        """删除选中的文件（按Delete或BackSpace键触发）"""
        # 获取所有选中项的索引（逆序，从后往前删除避免索引变化问题）
        selected_indices = list(self.file_listbox.curselection())
        if not selected_indices:
            return
        
        # 从后往前删除
        for idx in reversed(selected_indices):
            self.file_listbox.delete(idx)
            del self.pdf_files[idx]
        
        self._update_status(f"已选择 {len(self.pdf_files)} 个文件")
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_var.set(message)
    
    def _start_convert(self):
        """开始转换"""
        if self.is_converting:
            messagebox.showwarning("提示", "正在转换中，请稍候...")
            return
        
        if not self.pdf_files:
            messagebox.showwarning("提示", "请先选择PDF文件！")
            return
        
        # 检查poppler是否已安装
        poppler_ok, poppler_info = check_poppler_installed()
        if not poppler_ok:
            messagebox.showerror(
                "缺少依赖",
                "PDF转换需要安装poppler工具。\n\n"
                "请在终端运行以下命令安装：\n\n"
                "brew install poppler\n\n"
                "安装完成后重新运行本程序。"
            )
            return
        
        # 选择输出目录，默认为第一个PDF文件所在的目录
        default_dir = str(Path(self.pdf_files[0]).parent)
        output_dir = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=default_dir
        )
        if not output_dir:
            return
        
        # 在后台线程中执行转换
        self.is_converting = True
        self._set_ui_state(False)
        
        thread = threading.Thread(
            target=self._convert_files,
            args=(output_dir,),
            daemon=True
        )
        thread.start()
    
    def _set_ui_state(self, enabled: bool):
        """设置UI控件状态"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.btn_select.config(state=state)
        self.btn_clear.config(state=state)
        self.btn_convert.config(state=state)
        self.quality_scale.config(state=state)
    
    def _convert_files(self, output_dir: str):
        """转换文件（在后台线程中执行）"""
        import traceback
        
        quality = self.quality_var.get()
        total_files = len(self.pdf_files)
        converted_count = 0
        error_files = []
        
        for idx, pdf_path in enumerate(self.pdf_files):
            pdf_name = Path(pdf_path).stem
            self.root.after(0, lambda m=f"正在转换 ({idx+1}/{total_files}): {pdf_name}": self._update_status(m))
            
            try:
                # 创建以PDF名称命名的目录
                pdf_output_dir = os.path.join(output_dir, pdf_name)
                os.makedirs(pdf_output_dir, exist_ok=True)
                
                # 获取poppler路径（用于macOS Homebrew安装）
                poppler_path = None
                if os.path.exists('/opt/homebrew/bin'):
                    poppler_path = '/opt/homebrew/bin'
                elif os.path.exists('/usr/local/bin/pdftoppm'):
                    poppler_path = '/usr/local/bin'
                
                # 使用逐页转换避免内存问题
                # 先获取PDF的总页数
                self.root.after(0, lambda m=f"正在解析: {pdf_name}": self._update_status(m))
                
                if poppler_path:
                    images = convert_from_path(
                        pdf_path, 
                        dpi=150,  # 降低DPI以提高速度
                        poppler_path=poppler_path,
                        thread_count=2
                    )
                else:
                    images = convert_from_path(
                        pdf_path, 
                        dpi=150,
                        thread_count=2
                    )
                
                total_pages = len(images)
                
                # 保存每一页
                for page_num, image in enumerate(images, start=1):
                    self.root.after(
                        0, 
                        lambda m=f"正在转换: {pdf_name} (第 {page_num}/{total_pages} 页)": self._update_status(m)
                    )
                    
                    jpg_path = os.path.join(pdf_output_dir, f"page_{page_num:03d}.jpg")
                    # 转换为RGB模式（处理RGBA情况）
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(jpg_path, 'JPEG', quality=quality)
                
                converted_count += 1
                
            except Exception as e:
                error_msg = f"{pdf_name}: {str(e)}"
                error_files.append(error_msg)
                # 打印详细错误以便调试
                print(f"转换失败: {pdf_path}")
                traceback.print_exc()
            
            # 更新进度
            progress = ((idx + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
        
        # 处理完成
        if error_files:
            if converted_count > 0:
                msg = f"部分完成: {converted_count}/{total_files} 个文件转换成功\n\n失败的文件:\n" + "\n".join(error_files)
                self.root.after(0, lambda: self._on_convert_complete(True, msg, partial=True))
            else:
                msg = "所有文件转换失败:\n" + "\n".join(error_files)
                self.root.after(0, lambda: self._on_convert_complete(False, msg))
        else:
            self.root.after(0, lambda: self._on_convert_complete(True, output_dir))
    
    def _on_convert_complete(self, success: bool, message: str, partial: bool = False):
        """转换完成回调
        
        Args:
            success: 是否成功
            message: 成功时为输出目录路径，失败时为错误信息
            partial: 是否为部分成功
        """
        self.is_converting = False
        self._set_ui_state(True)
        
        if success:
            if partial:
                self._update_status("部分转换完成")
                messagebox.showwarning("部分完成", message)
            else:
                self._update_status("转换完成！")
                messagebox.showinfo("完成", f"所有文件已转换完成！\n输出目录: {message}")
        else:
            self._update_status("转换失败")
            messagebox.showerror("错误", f"转换过程中发生错误:\n{message}")


def main():
    """主函数"""
    root = tk.Tk()
    app = PDF2JPGApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
