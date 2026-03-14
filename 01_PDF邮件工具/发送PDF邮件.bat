@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
:: PDF邮件发送工具
:: 功能：收集当前目录下的PDF文件，创建Outlook邮件
::       并将PDF移动到以日期命名的文件夹
:: ============================================

:: 获取当前目录
set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

:: 获取今日日期（格式：YYYYMMDD）
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TODAY=%datetime:~0,8%"

echo ============================================
echo PDF邮件发送工具
echo ============================================
echo.

:: 检查是否有PDF文件
set "PDF_COUNT=0"
set "PDF_LIST="
set "EMAIL_BODY=请帮忙委托K1签署如下文件：" & echo.

:: 收集PDF文件
for %%F in (*.pdf) do (
    set /a PDF_COUNT+=1
    set "PDF_LIST=!PDF_LIST!;%CURRENT_DIR%%%F"
    echo 发现PDF文件: %%F
)

:: 如果没有PDF文件，退出
if %PDF_COUNT%==0 (
    echo.
    echo 错误：当前目录下没有找到PDF文件！
    echo 请将此脚本放在包含PDF文件的目录中。
    pause
    exit /b 1
)

echo.
echo 共发现 %PDF_COUNT% 个PDF文件
echo.

:: 移除PDF_LIST开头的分号
set "PDF_LIST=%PDF_LIST:~1%"

:: 创建日期文件夹
if not exist "%TODAY%" (
    mkdir "%TODAY%"
    echo 已创建文件夹: %TODAY%
) else (
    echo 文件夹已存在: %TODAY%
)

:: 创建VBScript来操作Outlook
set "VBS_FILE=%TEMP%\send_pdf_email.vbs"

:: 生成邮件正文（带编号的文件列表）
set "BODY_CONTENT=请帮忙委托K1签署如下文件：" & echo. & echo.
set "FILE_INDEX=0"
for %%F in (*.pdf) do (
    set /a FILE_INDEX+=1
    set "BODY_CONTENT=!BODY_CONTENT!!FILE_INDEX!. %%F\n"
)

:: 写入VBScript文件
(
echo Dim olApp, olMail, olInspector
echo Dim attachments, bodyText, fileList
echo.
echo ' 创建Outlook应用程序对象
echo On Error Resume Next
echo Set olApp = GetObject^(, "Outlook.Application"^)
echo If olApp Is Nothing Then
echo     Set olApp = CreateObject^("Outlook.Application"^)
echo End If
echo On Error GoTo 0
echo.
echo If olApp Is Nothing Then
echo     WScript.Echo "错误：无法启动Outlook，请确保已安装Microsoft Outlook。"
echo     WScript.Quit 1
echo End If
echo.
echo ' 创建新邮件
echo Set olMail = olApp.CreateItem^(0^)
echo.
echo ' 设置邮件正文
echo bodyText = "请帮忙委托K1签署如下文件：" ^& vbCrLf ^& vbCrLf
echo.
echo ' 添加附件并构建文件列表
echo attachments = "%PDF_LIST%"
echo fileArray = Split^(attachments, ";"^)
echo fileIndex = 0
echo.
echo For Each filePath In fileArray
echo     If Len^(Trim^(filePath^)^) ^> 0 Then
echo         fileIndex = fileIndex + 1
echo         ' 获取文件名
echo         fileName = Mid^(filePath, InStrRev^(filePath, "\"^) + 1^)
echo         ' 添加到正文
echo         bodyText = bodyText ^& fileIndex ^& ". " ^& fileName ^& vbCrLf
echo         ' 添加附件
echo         olMail.Attachments.Add filePath
echo     End If
echo Next
echo.
echo ' 设置邮件属性
echo olMail.Subject = "文件签署请求 - " ^& "%TODAY%"
echo olMail.Body = bodyText
echo.
echo ' 显示邮件（不发送，等待用户编辑）
echo olMail.Display
echo.
echo ' 清理对象
echo Set olMail = Nothing
echo Set olApp = Nothing
echo.
echo WScript.Echo "邮件已创建，请在Outlook中完成编辑后发送。"
) > "%VBS_FILE%"

echo.
echo 正在创建Outlook邮件...

:: 运行VBScript
cscript //nologo "%VBS_FILE%"

:: 检查VBScript执行结果
if errorlevel 1 (
    echo.
    echo 创建邮件时出现错误！
    del "%VBS_FILE%" 2>nul
    pause
    exit /b 1
)

:: 移动PDF文件到日期文件夹
echo.
echo 正在移动PDF文件到 %TODAY% 文件夹...
for %%F in (*.pdf) do (
    move "%%F" "%TODAY%\" >nul
    echo 已移动: %%F
)

:: 清理临时文件
del "%VBS_FILE%" 2>nul

echo.
echo ============================================
echo 操作完成！
echo - PDF文件已移动到: %TODAY%
echo - Outlook邮件已创建，请填写收件人后发送
echo ============================================
echo.
pause
