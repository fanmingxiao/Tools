@echo off
:: ============================================
:: 文件夹监控工具启动器
:: 说明：双击此文件启动文件夹监控
:: ============================================

:: 使用隐藏窗口模式运行PowerShell脚本
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0文件夹监控.ps1"
