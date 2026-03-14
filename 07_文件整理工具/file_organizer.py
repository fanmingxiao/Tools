# -*- coding: utf-8 -*-
"""
智能文件整理工具 - 主程序和GUI界面
支持按文件类型和关键字自动分类整理文件
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FILE_TYPES, get_category_emoji, load_config, save_config
from organizer_core import FileOrganizer


class FileOrganizerApp:
    """文件整理工具GUI应用"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📁 智能文件整理工具")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # 设置主题样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 变量
        self.source_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=False)
        self.preview_mode = tk.BooleanVar(value=True)
        
        # 关键字规则
        self.keyword_rules = {}
        
        # 加载配置
        self._load_user_config()
        
        # 创建界面
        self._create_ui()
        
        # 整理器实例
        self.organizer = None
        self.is_running = False
    
    def _load_user_config(self):
        """加载用户配置"""
        config = load_config()
        self.keyword_rules = config.get("keywords", {})
        self.include_subfolders.set(config.get("include_subfolders", False))
        self.preview_mode.set(config.get("preview_mode", True))
    
    def _save_user_config(self):
        """保存用户配置"""
        config = {
            "keywords": self.keyword_rules,
            "include_subfolders": self.include_subfolders.get(),
            "preview_mode": self.preview_mode.get(),
        }
        save_config(config)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="📁 智能文件整理工具", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # === 文件夹选择区域 ===
        folder_frame = ttk.LabelFrame(main_frame, text="📂 文件夹设置", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 源文件夹
        source_row = ttk.Frame(folder_frame)
        source_row.pack(fill=tk.X, pady=2)
        ttk.Label(source_row, text="源文件夹:", width=10).pack(side=tk.LEFT)
        ttk.Entry(source_row, textvariable=self.source_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(source_row, text="浏览...", command=self._browse_source).pack(side=tk.RIGHT)
        
        # 输出目录
        output_row = ttk.Frame(folder_frame)
        output_row.pack(fill=tk.X, pady=2)
        ttk.Label(output_row, text="输出目录:", width=10).pack(side=tk.LEFT)
        ttk.Entry(output_row, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_row, text="浏览...", command=self._browse_output).pack(side=tk.RIGHT)
        
        # 选项
        options_row = ttk.Frame(folder_frame)
        options_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Checkbutton(
            options_row, 
            text="包含子文件夹", 
            variable=self.include_subfolders
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(
            options_row, 
            text="预览模式（先预览再执行）", 
            variable=self.preview_mode
        ).pack(side=tk.LEFT)
        
        # === 关键字规则区域 ===
        keyword_frame = ttk.LabelFrame(main_frame, text="🔑 关键字分类规则", padding="10")
        keyword_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 规则列表
        self.keyword_list = ttk.Treeview(
            keyword_frame, 
            columns=("category", "keywords"), 
            show="headings",
            height=5
        )
        self.keyword_list.heading("category", text="分类名称")
        self.keyword_list.heading("keywords", text="关键字（逗号分隔）")
        self.keyword_list.column("category", width=150)
        self.keyword_list.column("keywords", width=400)
        self.keyword_list.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 加载现有规则
        self._refresh_keyword_list()
        
        # 规则编辑按钮
        btn_row = ttk.Frame(keyword_frame)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="➕ 添加规则", command=self._add_keyword_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="✏️ 编辑规则", command=self._edit_keyword_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🗑️ 删除规则", command=self._delete_keyword_rule).pack(side=tk.LEFT, padx=2)
        
        # === 操作按钮区域 ===
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.preview_btn = ttk.Button(
            action_frame, 
            text="🔍 预览分类", 
            command=self._preview_organize,
            width=15
        )
        self.preview_btn.pack(side=tk.LEFT, padx=5)
        
        self.organize_btn = ttk.Button(
            action_frame, 
            text="▶ 开始整理", 
            command=self._start_organize,
            width=15
        )
        self.organize_btn.pack(side=tk.LEFT, padx=5)
        
        self.report_btn = ttk.Button(
            action_frame, 
            text="📄 导出报告", 
            command=self._export_report,
            width=15,
            state=tk.DISABLED
        )
        self.report_btn.pack(side=tk.RIGHT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(main_frame, text="就绪")
        self.progress_label.pack()
        
        # === 日志区域 ===
        log_frame = ttk.LabelFrame(main_frame, text="📊 整理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=10, 
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def _refresh_keyword_list(self):
        """刷新关键字规则列表"""
        for item in self.keyword_list.get_children():
            self.keyword_list.delete(item)
        
        for category, keywords in self.keyword_rules.items():
            keywords_str = ", ".join(keywords)
            self.keyword_list.insert("", tk.END, values=(category, keywords_str))
    
    def _browse_source(self):
        """选择源文件夹"""
        folder = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder:
            self.source_dir.set(folder)
            # 自动设置输出目录
            if not self.output_dir.get():
                self.output_dir.set(os.path.join(folder, "已整理"))
    
    def _browse_output(self):
        """选择输出目录"""
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir.set(folder)
    
    def _add_keyword_rule(self):
        """添加关键字规则"""
        dialog = KeywordRuleDialog(self.root, "添加关键字规则")
        if dialog.result:
            category, keywords = dialog.result
            self.keyword_rules[category] = keywords
            self._refresh_keyword_list()
            self._save_user_config()
    
    def _edit_keyword_rule(self):
        """编辑关键字规则"""
        selection = self.keyword_list.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条规则")
            return
        
        item = self.keyword_list.item(selection[0])
        old_category = item["values"][0]
        old_keywords = self.keyword_rules.get(old_category, [])
        
        dialog = KeywordRuleDialog(
            self.root, 
            "编辑关键字规则",
            initial_category=old_category,
            initial_keywords=old_keywords
        )
        if dialog.result:
            category, keywords = dialog.result
            # 删除旧规则
            if old_category in self.keyword_rules:
                del self.keyword_rules[old_category]
            # 添加新规则
            self.keyword_rules[category] = keywords
            self._refresh_keyword_list()
            self._save_user_config()
    
    def _delete_keyword_rule(self):
        """删除关键字规则"""
        selection = self.keyword_list.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条规则")
            return
        
        item = self.keyword_list.item(selection[0])
        category = item["values"][0]
        
        if messagebox.askyesno("确认", f"确定要删除规则「{category}」吗？"):
            if category in self.keyword_rules:
                del self.keyword_rules[category]
            self._refresh_keyword_list()
            self._save_user_config()
    
    def _log(self, message: str):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_progress(self, current: int, total: int, filename: str):
        """更新进度"""
        progress = (current / total) * 100 if total > 0 else 0
        self.progress["value"] = progress
        self.progress_label.config(text=f"处理中: {filename} ({current}/{total})")
        self.root.update_idletasks()
    
    def _validate_inputs(self) -> bool:
        """验证输入"""
        if not self.source_dir.get():
            messagebox.showerror("错误", "请选择源文件夹")
            return False
        
        if not os.path.isdir(self.source_dir.get()):
            messagebox.showerror("错误", "源文件夹不存在")
            return False
        
        return True
    
    def _preview_organize(self):
        """预览分类"""
        if not self._validate_inputs():
            return
        
        self._clear_log()
        self._log("🔍 开始预览分类...")
        
        # 创建整理器
        self.organizer = FileOrganizer(
            self.source_dir.get(),
            self.output_dir.get() or None
        )
        self.organizer.set_keywords(self.keyword_rules)
        self.organizer.include_subfolders = self.include_subfolders.get()
        self.organizer.set_progress_callback(self._update_progress)
        
        # 在线程中执行预览
        def preview_task():
            self.is_running = True
            self._set_buttons_state(False)
            
            try:
                result = self.organizer.preview()
                
                # 显示预览结果
                self._log("\n📊 预览结果:")
                self._log("-" * 40)
                
                total_files = 0
                for category, files in sorted(result.items()):
                    emoji = get_category_emoji(category)
                    self._log(f"{emoji} {category}: {len(files)} 个文件")
                    total_files += len(files)
                
                self._log("-" * 40)
                self._log(f"总计: {total_files} 个文件")
                self._log("\n✅ 预览完成！点击「开始整理」执行移动操作")
                
                self.progress_label.config(text=f"预览完成: {total_files} 个文件")
                self.report_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                self._log(f"❌ 预览失败: {str(e)}")
                messagebox.showerror("错误", f"预览失败: {str(e)}")
            finally:
                self.is_running = False
                self._set_buttons_state(True)
        
        threading.Thread(target=preview_task, daemon=True).start()
    
    def _start_organize(self):
        """开始整理"""
        if not self._validate_inputs():
            return
        
        # 确认
        if not messagebox.askyesno("确认", "确定要开始整理文件吗？\n文件将被移动到分类目录中。"):
            return
        
        self._clear_log()
        self._log("▶ 开始整理文件...")
        
        # 创建整理器
        self.organizer = FileOrganizer(
            self.source_dir.get(),
            self.output_dir.get() or None
        )
        self.organizer.set_keywords(self.keyword_rules)
        self.organizer.include_subfolders = self.include_subfolders.get()
        self.organizer.set_progress_callback(self._update_progress)
        
        # 在线程中执行整理
        def organize_task():
            self.is_running = True
            self._set_buttons_state(False)
            
            try:
                success, fail = self.organizer.organize()
                
                # 显示结果
                self._log("\n" + "=" * 40)
                self._log("✅ 整理完成!")
                self._log(f"   成功: {success} 个文件")
                self._log(f"   失败: {fail} 个文件")
                self._log("=" * 40)
                
                # 显示详细日志
                for log in self.organizer.get_logs():
                    self._log(log)
                
                self.progress_label.config(text=f"整理完成: 成功 {success}, 失败 {fail}")
                self.report_btn.config(state=tk.NORMAL)
                
                messagebox.showinfo("完成", f"文件整理完成！\n成功: {success} 个\n失败: {fail} 个")
                
            except Exception as e:
                self._log(f"❌ 整理失败: {str(e)}")
                messagebox.showerror("错误", f"整理失败: {str(e)}")
            finally:
                self.is_running = False
                self._set_buttons_state(True)
        
        threading.Thread(target=organize_task, daemon=True).start()
    
    def _export_report(self):
        """导出报告"""
        if not self.organizer:
            messagebox.showwarning("提示", "请先执行预览或整理操作")
            return
        
        try:
            # 选择保存位置
            report_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")],
                initialfile="整理报告.md"
            )
            
            if report_path:
                # 生成报告到临时位置再移动
                temp_report = self.organizer.generate_report(os.path.dirname(report_path))
                if temp_report != report_path:
                    import shutil
                    shutil.move(temp_report, report_path)
                
                self._log(f"📄 报告已保存: {report_path}")
                messagebox.showinfo("完成", f"报告已导出至:\n{report_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出报告失败: {str(e)}")
    
    def _set_buttons_state(self, enabled: bool):
        """设置按钮状态"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.preview_btn.config(state=state)
        self.organize_btn.config(state=state)


class KeywordRuleDialog:
    """关键字规则编辑对话框"""
    
    def __init__(self, parent, title, initial_category="", initial_keywords=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 分类名称
        ttk.Label(self.dialog, text="分类名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.category_entry = ttk.Entry(self.dialog, width=40)
        self.category_entry.grid(row=0, column=1, padx=10, pady=10)
        self.category_entry.insert(0, initial_category)
        
        # 关键字
        ttk.Label(self.dialog, text="关键字:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.keywords_entry = ttk.Entry(self.dialog, width=40)
        self.keywords_entry.grid(row=1, column=1, padx=10, pady=5)
        if initial_keywords:
            self.keywords_entry.insert(0, ", ".join(initial_keywords))
        
        ttk.Label(self.dialog, text="（多个关键字用逗号分隔）", font=("Arial", 9)).grid(
            row=2, column=1, padx=10, sticky=tk.W
        )
        
        # 按钮
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="确定", command=self._on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.wait_window()
    
    def _on_ok(self):
        category = self.category_entry.get().strip()
        keywords_str = self.keywords_entry.get().strip()
        
        if not category:
            messagebox.showwarning("提示", "请输入分类名称")
            return
        
        if not keywords_str:
            messagebox.showwarning("提示", "请输入至少一个关键字")
            return
        
        # 解析关键字
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        
        self.result = (category, keywords)
        self.dialog.destroy()
    
    def _on_cancel(self):
        self.dialog.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置高DPI支持
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = FileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
