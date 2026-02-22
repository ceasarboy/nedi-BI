@echo off
chcp 65001 >nul
echo ========================================
echo PB-BI 数据分析平台 - 生产模式启动
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo [3/3] 启动服务...
echo.

set PROJECT_DIR=%~dp0..

echo 启动后端服务 (端口: 8000)...
start "PB-BI Backend" cmd /k "cd /d %PROJECT_DIR% && venv\Scripts\activate && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo 启动前端服务 (端口: 3000)...
start "PB-BI Frontend" cmd /k "cd /d %PROJECT_DIR%\frontend && npm run preview"

echo.
echo ========================================
echo 服务启动完成！
echo.
echo 后端API: http://localhost:8000
echo 前端界面: http://localhost:3000
echo.
echo 局域网访问: http://YOUR_IP:3000
echo ========================================
echo.
pause
