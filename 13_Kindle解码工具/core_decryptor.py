import os
import sys
import subprocess
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_executable_path():
    # 利用当前的运行环境获取解释器（为了兼容 uv）
    return sys.executable

def decrypt_single(infile, outdir, serial):
    """
    单文件使用 DeDRM 的剥壳脚本进行解密
    """
    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
    script_path = os.path.join(lib_dir, 'k4mobidedrm.py')
    
    # 清理非法的序列号间隔或全角空格
    serial = serial.strip().replace(" ", "").upper()
    
    cmd = [
        get_executable_path(), script_path,
        "-s", serial,
        infile, outdir
    ]
    
    try:
        # cwd 指向 lib_dir 规避 DeDRM 内部复杂的同源导包失败
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=lib_dir)
        if result.returncode == 0:
            return True, f"[成功] {os.path.basename(infile)}"
        else:
            return False, f"[错误] {os.path.basename(infile)}\n> {result.stderr.strip()}"
    except Exception as e:
         return False, f"[异常] {os.path.basename(infile)}\n> {str(e)}"

def decrypt_batch(input_dir, out_dir, serial, progress_callback=None, log_callback=None):
    """
    多线程批处理文件调度中心
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    search_patterns = [
        os.path.join(input_dir, "*.azw3"),
        os.path.join(input_dir, "*.mobi"),
        os.path.join(input_dir, "*.prc")
    ]
    
    files_to_decrypt = []
    for pattern in search_patterns:
        files_to_decrypt.extend(glob.glob(pattern))
        
    total_files = len(files_to_decrypt)
    if total_files == 0:
        if log_callback:
            log_callback("错误：未在选定目录发现支持的电子书格式 (*.azw3, *.mobi, *.prc)")
        return
        
    if log_callback:
        log_callback(f"搜索完毕：共计命中 {total_files} 本待脱壳书籍。")
        log_callback("引擎已轰鸣，正在唤醒异步脱壳队列...\n" + "-"*40)
        
    processed = 0
    success = 0
    # 设置合理的最大工作线程以防 I/O 及解压缩高占用 CPU
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(decrypt_single, f, out_dir, serial): f for f in files_to_decrypt}
        for future in as_completed(futures):
            ok, msg = future.result()
            
            if log_callback:
                log_callback(msg)
                
            processed += 1
            if ok:
                success += 1
                
            if progress_callback:
                progress_callback(processed, total_files)
                
    if log_callback:
        log_callback("-" * 40)
        log_callback(f"【批量终了】 总书籍: {total_files} 本 | 成功净化: {success} 本 | 破译失败: {total_files - success} 本")
