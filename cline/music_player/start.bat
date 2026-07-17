@echo off
echo ================================
echo  在线音乐管理系统 - 启动脚本
echo ================================
echo.

echo 1. 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查网络连接
    pause
    exit /b %errorlevel%
)

echo.
echo 2. 初始化数据库并启动服务器...
echo 访问地址: http://127.0.0.1:5001
echo.
echo 管理员账号: admin / admin123
echo 演示账号: demo / demo123
echo.
echo 按 Ctrl+C 停止服务器
echo ================================
echo.

python app.py
pause