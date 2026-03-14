@echo off
chcp 65001 >nul
:: ============================================
:: 从开机启动中移除文件夹监控
:: ============================================

echo ============================================
echo 移除文件夹监控开机启动
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\文件夹监控工具.lnk"

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo 已成功移除开机启动。
) else (
    echo 未找到开机启动项，可能已被移除。
)

echo.
pause
