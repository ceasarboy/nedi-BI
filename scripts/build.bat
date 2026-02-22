@echo off
chcp 65001 >nul
echo ========================================
echo PB-BI 数据分析平台 - 构建生产版本
echo ========================================
echo.

echo [1/2] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

set PROJECT_DIR=%~dp0..

echo [2/2] 构建前端...
cd /d %PROJECT_DIR%\frontend

echo 安装依赖...
call npm install

echo 构建生产版本...
call npm run build

echo.
echo ========================================
echo 构建完成！
echo.
echo 输出目录: %PROJECT_DIR%\frontend\dist
echo.
echo 使用 start.bat 启动生产服务
echo 使用 start-dev.bat 启动开发服务
echo ========================================
echo.
pause
