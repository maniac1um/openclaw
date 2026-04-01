#!/bin/bash

# OpenClaw 自动化新闻发布系统 - 一键启动脚本
# 使用方法: ./scripts/start_server.sh

set -e  # 遇到错误立即退出

echo "=== OpenClaw 新闻发布服务器启动脚本 ==="

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "项目根目录: $PROJECT_ROOT"

# 检查 Python 虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 未找到 Python 虚拟环境 (.venv)"
    echo "请先运行: python -m venv .venv && source .venv/bin/activate && pip install -r REQUIRMENTS.txt"
    exit 1
fi

echo "激活 Python 虚拟环境..."
source .venv/bin/activate

# 检查依赖是否安装
echo "检查 Python 依赖..."
python -c "import flask, jinja2" 2>/dev/null || {
    echo "错误: 缺少必要的 Python 包"
    echo "请运行: pip install -r REQUIRMENTS.txt"
    exit 1
}

# 设置环境变量
export PORT="${PORT:-5000}"
export DEBUG="${DEBUG:-True}"
export REPO_PATH="${REPO_PATH:-.}"

echo "服务器配置:"
echo "  - 端口: $PORT"
echo "  - 调试模式: $DEBUG"
echo "  - 仓库路径: $REPO_PATH"

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "警告: 端口 $PORT 已被占用"
    echo "尝试使用其他端口..."
    for alt_port in 5001 5002 5003 8000 8080; do
        if ! lsof -Pi :$alt_port -sTCP:LISTEN -t >/dev/null 2>&1; then
            export PORT=$alt_port
            echo "使用端口: $PORT"
            break
        fi
    done
fi

# 创建必要的目录
echo "创建必要目录..."
mkdir -p data/news web

# 检查 Git 仓库状态
if [ -d ".git" ]; then
    echo "Git 仓库状态正常"
else
    echo "警告: 当前目录不是 Git 仓库"
    echo "如果需要 Git 功能，请先初始化: git init"
fi

echo ""
echo "启动 Flask 服务器..."
echo "访问地址: http://localhost:$PORT"
echo "Webhook 接口: http://localhost:$PORT/api/webhook"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"

# 启动服务器
exec python src/server/app.py