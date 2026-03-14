<#
.SYNOPSIS
    文件夹监控工具 - 实时监控指定目录的新文件并弹窗提醒
.DESCRIPTION
    功能：
    1. 实时监控指定文件夹（支持共享目录）
    2. 新文件添加时弹窗提醒
    3. 系统托盘图标运行
    4. 监控日志记录
.NOTES
    使用方法：右键点击此文件 -> 使用 PowerShell 运行
    或者运行 启动监控.bat
#>

# ============================================
# 配置区域 - 请根据需要修改以下设置
# ============================================

# 要监控的文件夹路径（支持本地路径和网络共享路径）
# 示例：
# $MonitorPath = "C:\共享文件夹"
# $MonitorPath = "\\192.168.1.100\共享目录"
# $MonitorPath = "\\服务器名\共享文件夹"
$MonitorPath = "C:\监控测试"  # 请修改为您要监控的路径

# 是否监控子文件夹
$IncludeSubfolders = $true

# 日志文件路径（留空则不记录日志）
$LogFile = "$PSScriptRoot\监控日志.txt"

# 监控的文件类型筛选（"*.*" 表示所有文件）
$FileFilter = "*.*"

# ============================================
# 加载必要的程序集
# ============================================
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ============================================
# 日志函数
# ============================================
function Write-Log {
    param([string]$Message)
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    
    # 输出到控制台
    Write-Host $logMessage
    
    # 写入日志文件
    if ($LogFile) {
        Add-Content -Path $LogFile -Value $logMessage -Encoding UTF8
    }
}

# ============================================
# 验证监控路径
# ============================================
if (-not (Test-Path $MonitorPath)) {
    $result = [System.Windows.Forms.MessageBox]::Show(
        "监控路径不存在：`n$MonitorPath`n`n是否创建此文件夹？",
        "文件夹监控工具",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Question
    )
    
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        New-Item -Path $MonitorPath -ItemType Directory -Force | Out-Null
        Write-Log "已创建监控文件夹: $MonitorPath"
    } else {
        Write-Log "监控路径不存在，程序退出"
        exit
    }
}

# ============================================
# 创建系统托盘图标
# ============================================
$script:notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$script:notifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$script:notifyIcon.Text = "文件夹监控工具`n正在监控: $MonitorPath"
$script:notifyIcon.Visible = $true

# 创建右键菜单
$contextMenu = New-Object System.Windows.Forms.ContextMenuStrip

# 菜单项：显示状态
$menuStatus = New-Object System.Windows.Forms.ToolStripMenuItem
$menuStatus.Text = "📁 监控中: $MonitorPath"
$menuStatus.Enabled = $false
$contextMenu.Items.Add($menuStatus) | Out-Null

# 分隔线
$contextMenu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator)) | Out-Null

# 菜单项：打开监控文件夹
$menuOpenFolder = New-Object System.Windows.Forms.ToolStripMenuItem
$menuOpenFolder.Text = "📂 打开监控文件夹"
$menuOpenFolder.Add_Click({
    Start-Process explorer.exe -ArgumentList $MonitorPath
})
$contextMenu.Items.Add($menuOpenFolder) | Out-Null

# 菜单项：打开日志文件
$menuOpenLog = New-Object System.Windows.Forms.ToolStripMenuItem
$menuOpenLog.Text = "📋 查看日志文件"
$menuOpenLog.Add_Click({
    if (Test-Path $LogFile) {
        Start-Process notepad.exe -ArgumentList $LogFile
    } else {
        [System.Windows.Forms.MessageBox]::Show("日志文件尚未创建", "提示", "OK", "Information")
    }
})
$contextMenu.Items.Add($menuOpenLog) | Out-Null

# 分隔线
$contextMenu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator)) | Out-Null

# 菜单项：退出
$menuExit = New-Object System.Windows.Forms.ToolStripMenuItem
$menuExit.Text = "❌ 退出监控"
$menuExit.Add_Click({
    Write-Log "用户退出监控程序"
    $script:notifyIcon.Visible = $false
    $script:notifyIcon.Dispose()
    [System.Windows.Forms.Application]::Exit()
})
$contextMenu.Items.Add($menuExit) | Out-Null

$script:notifyIcon.ContextMenuStrip = $contextMenu

# 双击托盘图标打开文件夹
$script:notifyIcon.Add_DoubleClick({
    Start-Process explorer.exe -ArgumentList $MonitorPath
})

# ============================================
# 创建文件系统监视器
# ============================================
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $MonitorPath
$watcher.Filter = $FileFilter
$watcher.IncludeSubdirectories = $IncludeSubfolders
$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::LastWrite

# ============================================
# 定义事件处理器
# ============================================

# 新文件创建事件
$onCreated = {
    $fileName = $Event.SourceEventArgs.Name
    $fullPath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    
    # 记录日志
    Write-Log "新文件: $fileName"
    
    # 显示托盘气泡通知
    $script:notifyIcon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
    $script:notifyIcon.BalloonTipTitle = "发现新文件"
    $script:notifyIcon.BalloonTipText = $fileName
    $script:notifyIcon.ShowBalloonTip(5000)
    
    # 弹窗提醒
    $result = [System.Windows.Forms.MessageBox]::Show(
        "发现新文件：`n`n$fileName`n`n是否打开文件所在位置？",
        "文件夹监控提醒",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Information
    )
    
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        # 打开文件所在文件夹并选中文件
        Start-Process explorer.exe -ArgumentList "/select,`"$fullPath`""
    }
}

# 文件重命名事件（可选）
$onRenamed = {
    $oldName = $Event.SourceEventArgs.OldName
    $newName = $Event.SourceEventArgs.Name
    Write-Log "文件重命名: $oldName -> $newName"
}

# 文件删除事件（可选）
$onDeleted = {
    $fileName = $Event.SourceEventArgs.Name
    Write-Log "文件删除: $fileName"
}

# ============================================
# 注册事件
# ============================================
$handlers = @()
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Created -Action $onCreated
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $onRenamed
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $onDeleted

# 启用监视器
$watcher.EnableRaisingEvents = $true

# ============================================
# 启动通知
# ============================================
Write-Log "=========================================="
Write-Log "文件夹监控工具已启动"
Write-Log "监控路径: $MonitorPath"
Write-Log "包含子文件夹: $IncludeSubfolders"
Write-Log "文件筛选: $FileFilter"
Write-Log "=========================================="

# 显示启动通知
$script:notifyIcon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$script:notifyIcon.BalloonTipTitle = "文件夹监控已启动"
$script:notifyIcon.BalloonTipText = "正在监控: $MonitorPath"
$script:notifyIcon.ShowBalloonTip(3000)

# ============================================
# 运行消息循环（保持程序运行）
# ============================================
try {
    [System.Windows.Forms.Application]::Run()
}
finally {
    # 清理资源
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    foreach ($handler in $handlers) {
        Unregister-Event -SubscriptionId $handler.Id
    }
    $script:notifyIcon.Dispose()
    Write-Log "监控程序已停止"
}
