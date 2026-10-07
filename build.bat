@echo off
chcp 65001 >nul
cd /d "%~dp0"
title TabFlow - 打包独立 EXE

echo ========================================================
echo               正在打包 TabFlow 为单文件 EXE
echo ========================================================
echo.

REM 检查 Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python 环境，请确认已安装 Python。
    pause
    exit /b 1
)

REM 若正在运行已打包的 TabFlow.exe，先安全关闭以避免文件被占用锁定
taskkill /F /IM TabFlow.exe >nul 2>nul

REM 生成图标 (如果不存在)
if not exist "app.ico" (
    echo [1/3] 生成高清应用图标...
    python -c "from PIL import Image, ImageDraw; img = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); draw = ImageDraw.Draw(img); draw.rounded_rectangle([8, 8, 248, 248], radius=56, fill=(30, 41, 59, 255)); draw.rounded_rectangle([44, 60, 124, 196], radius=24, fill=(99, 102, 241, 255)); draw.rounded_rectangle([124, 76, 204, 196], radius=24, fill=(14, 165, 233, 255)); draw.ellipse([176, 176, 232, 232], fill=(16, 185, 129, 255), outline=(255, 255, 255, 220), width=8); img.save('app.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])"
)

echo [2/3] 执行 PyInstaller 静态编译打包...
python -m PyInstaller --name "TabFlow" --onefile --windowed --icon "app.ico" --hidden-import "pystray._win32" --collect-all "pystray" --collect-all "PIL" --add-data "app.ico;." --clean main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo [成功] 打包完成！
    echo [产物目录] dist\TabFlow.exe
    echo 该 EXE 可拷贝到任何 Windows 电脑直接运行，无需安装 Python！
    echo ========================================================
) else (
    echo.
    echo [错误] 打包失败，请检查上方输出信息。
)

pause
