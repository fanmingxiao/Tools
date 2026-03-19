@echo off
chcp 65001 >nul
echo ============================================
echo    SVW Copilot Word 插件安装脚本
echo ============================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 请以管理员身份运行此脚本！
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

:: 设置WEF目录
set "WEF_DIR=%USERPROFILE%\AppData\Local\Microsoft\Office\16.0\Wef"
set "MANIFEST_SOURCE=%~dp0manifest.xml"

:: 检查源文件
if not exist "%MANIFEST_SOURCE%" (
    echo [错误] 找不到 manifest.xml 文件！
    echo 请确保此脚本位于插件目录中。
    pause
    exit /b 1
)

:: 创建WEF目录（如果不存在）
if not exist "%WEF_DIR%" (
    echo [信息] 创建 WEF 目录...
    mkdir "%WEF_DIR%" 2>nul
    if errorlevel 1 (
        echo [错误] 无法创建目录: %WEF_DIR%
        pause
        exit /b 1
    )
)

:: 复制 manifest 文件
echo [信息] 安装插件...
copy /Y "%MANIFEST_SOURCE%" "%WEF_DIR%\SVW-Copilot.xml" >nul

if errorlevel 1 (
    echo [错误] 复制文件失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo [成功] 插件安装完成！
echo ============================================
echo.
echo 请按以下步骤操作：
echo 1. 完全关闭所有 Word 窗口
echo 2. 重新打开 Word
echo 3. 在 Ribbon 中查找 "AI助手" 选项卡
echo.
echo 如果未显示，请手动添加受信任目录：
echo   文件 -^> 选项 -^> 信任中心 -^> 信任中心设置
echo   -^> 受信任的加载项目录 -^> 添加新目录
echo   输入: %WEF_DIR%
echo.
pause
