@echo off
chcp 65001 >nul
title 五大行高股息监控系统 v2.0

echo ========================================
echo   五大行高股息监控系统 v2.0
echo   一键启动 (Windows)
echo ========================================
echo.

:: 安装依赖
echo [1/3] 安装Python依赖...
pip install -r requirements.txt -q 2>nul

:: 启动后端
echo [2/3] 启动Flask后端 (端口5001)...
start /min "" python app.py

:: 等待后端启动
echo 等待后端启动...
ping -n 4 127.0.0.1 >nul

:: 打开浏览器
echo [3/3] 打开Chrome浏览器...
start chrome "file:///%~dp0index.html" 2>nul
if %errorlevel% neq 0 (
    :: Chrome没找到，用默认浏览器
    start "" "%~dp0index.html"
)

echo.
echo ========================================
echo   ✅ 启动完成！
echo   后端: http://127.0.0.1:5001
echo   前端: %~dp0index.html
echo ========================================
echo.
echo 关闭后端请按 Ctrl+C 关闭此窗口
echo.
pause