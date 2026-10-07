@echo off
chcp 65001 >nul
cd /d "%~dp0"
title TabFlow 启动器

REM 优先使用 pythonw 无控制台黑框启动
where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw main.py
    exit
)

REM 如果没有 pythonw，则使用常规 python 启动
where python >nul 2>nul
if %errorlevel% equ 0 (
    start "" python main.py
    exit
)

echo 未检测到 Python 环境，请确认已安装 Python 并在系统环境变量 PATH 中。
pause
