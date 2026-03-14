@echo off
chcp 65001 >nul
:: ============================================
:: 添加文件夹监控到开机启动
:: 说明：运行此脚本将监控工具添加到Windows启动项
:: ============================================

echo ============================================
echo 添加文件夹监控到开机启动
echo ============================================
echo.

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"
set "STARTUP_BAT=%SCRIPT_DIR%启动监控.bat"

:: 检查启动脚本是否存在
if not exist "%STARTUP_BAT%" (
    echo 错误：找不到 启动监控.bat
    pause
    exit /b 1
)

:: 创建快捷方式到启动文件夹
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\文件夹监控工具.lnk"

:: 使用PowerShell创建快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%STARTUP_BAT%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = '文件夹监控工具'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo 成功！文件夹监控已添加到开机启动。
    echo.
    echo 快捷方式位置：
    echo %SHORTCUT_PATH%
    echo.
    echo 如需取消开机启动，请运行 移除开机启动.bat
) else (
    echo 添加失败，请检查权限。
)

echo.
pause
