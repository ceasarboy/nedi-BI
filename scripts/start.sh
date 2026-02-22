#!/bin/bash

echo "========================================"
echo "PB-BI 数据分析平台 - 生产模式启动"
echo "========================================"
echo ""

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

echo "[2/3] 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

echo "[3/3] 启动服务..."
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "启动后端服务 (端口: 8000)..."
cd "$PROJECT_DIR"
source venv/bin/activate
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "启动前端服务 (端口: 3000)..."
cd "$PROJECT_DIR/frontend"
npm run preview &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "服务启动完成！"
echo ""
echo "后端API: http://localhost:8000"
echo "前端界面: http://localhost:3000"
echo ""
echo "局域网访问: http://YOUR_IP:3000"
echo ""
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo "========================================"
echo ""

# 等待用户按Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
