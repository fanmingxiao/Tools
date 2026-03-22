import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from core_decryptor import decrypt_batch

class KindleDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kindle AZW3 批量脱壳工作站 - V1.0")
        self.root.geometry("640x550")
        self.root.minsize(640, 550)
        
        # 风格初始化
        style = ttk.Style()
        style.theme_use("clam")
        style.configure('TButton', font=('Microsoft YaHei', 10), padding=5)
        style.configure('TLabel', font=('Microsoft YaHei', 10))
        style.configure('Header.TLabel', font=('Microsoft YaHei', 16, 'bold'))
        
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.serial_number = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 头部说明
        ttk.Label(main_frame, text="Kindle 私有读币脱锁系统", style='Header.TLabel', foreground="#2c3e50").pack(pady=(0, 5))
        ttk.Label(main_frame, text="无需依靠服务端，在本地原生转换锁定的 .azw3 格式文件以适配任何电子书", foreground="#7f8c8d").pack(pady=(0, 20))
        
        # 输入设定域
        settings_frame = ttk.LabelFrame(main_frame, text="工作区配置", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Kindle Serial
        key_frame = ttk.Frame(settings_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="Kindle 序列号 (Serial):").pack(side=tk.LEFT)
        ttk.Entry(key_frame, textvariable=self.serial_number, font=('Consolas', 11)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 输入源文件夹
        source_frame = ttk.Frame(settings_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="目标扫描目录:").pack(side=tk.LEFT, padx=(0, 24))
        ttk.Entry(source_frame, textvariable=self.input_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="浏览...", command=self.select_input, width=8).pack(side=tk.LEFT, padx=(10, 0))
        
        # 输出目标文件夹
        dest_frame = ttk.Frame(settings_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dest_frame, text="净化后保存至:").pack(side=tk.LEFT, padx=(0, 24))
        ttk.Entry(dest_frame, textvariable=self.output_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dest_frame, text="浏览...", command=self.select_output, width=8).pack(side=tk.LEFT, padx=(10, 0))
        
        # 控制流面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(control_frame, text="🚀 启动批量净化脱壳 ", command=self.start_decryption)
        self.btn_start.pack(fill=tk.X, ipady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=10)
        
        # 终端输出日志
        log_frame = ttk.LabelFrame(main_frame, text="运行时日志输出", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled", font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def select_input(self):
        path = filedialog.askdirectory(title="选择包含电子书的文件夹")
        if path:
            self.input_dir.set(path)
            if not self.output_dir.get():
                self.output_dir.set(os.path.join(path, "decrypted_books"))

    def select_output(self):
        path = filedialog.askdirectory(title="选择保存净化电子书的路径")
        if path:
            self.output_dir.set(path)
            
    def append_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def update_progress(self, current, total):
        pct = (current / total) * 100
        self.progress_var.set(pct)
        # 用 root.update_idletasks() 或在回调里被包装好的更新都可以，变量绑定自生反应
        
    def worker_thread(self):
        in_path = self.input_dir.get()
        out_path = self.output_dir.get()
        serial = self.serial_number.get()
        
        self.btn_start.config(state="disabled")
        self.progress_var.set(0)
        
        def safe_log(msg):
            self.root.after(0, self.append_log, msg)
            
        def safe_prog(c, t):
            self.root.after(0, self.update_progress, c, t)
            
        try:
            decrypt_batch(in_path, out_path, serial, safe_prog, safe_log)
        except Exception as e:
            safe_log(f"执行任务群列发生重灾错误: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_start.config(state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("批量解密闭环", "所选工作队列均已执行完毕，请参阅日志流定损！"))

    def start_decryption(self):
        # 预校验
        serial = self.serial_number.get().strip()
        if not serial or len(serial) < 15:
            messagebox.showwarning("Key遗失", "请输入购买时捆绑这批图书的正确 16位 Kindle 序列号。")
            return
            
        if not self.input_dir.get() or not os.path.exists(self.input_dir.get()):
             messagebox.showwarning("目标盲区", "您还未分配书籍搜索来源路径。")
             return
             
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
        
        # 守护非阻断副线程操作
        threading.Thread(target=self.worker_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = KindleDecoderApp(root)
    root.mainloop()
