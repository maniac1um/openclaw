#!/bin/bash

# OpenClaw 自动化新闻发布系统 - 仓库初始化脚本
# 使用方法: ./scripts/init_repo.sh [remote-url]

set -e  # 遇到错误立即退出

echo "=== OpenClaw 新闻发布系统 - 仓库初始化 ==="

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "项目根目录: $PROJECT_ROOT"

# 检查是否已经是 Git 仓库
if [ -d ".git" ]; then
    echo "Git 仓库已存在，检查状态..."
    git status --porcelain
    echo "仓库初始化完成。"
    exit 0
fi

echo "初始化 Git 仓库..."
git init

# 检查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    echo "创建 .gitignore 文件..."
    cat > .gitignore << 'EOF'
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# 环境变量
.env
.env.local

# 本地数据（不提交到 Git）
data/news/*.json

# 日志文件
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.temp
EOF
else
    echo ".gitignore 已存在，跳过创建"
fi

# 创建必要的目录
echo "创建必要目录..."
mkdir -p data/news web

# 添加所有文件到 Git
echo "添加文件到 Git..."
git add .

# 检查是否有文件需要提交
if git diff --cached --quiet; then
    echo "没有文件需要提交"
    exit 0
fi

# 提交初始文件
echo "提交初始文件..."
git commit -m "Initial commit for OpenClaw news publisher

- Flask server for automated news publishing
- Webhook API for receiving news content
- Static site generation with Jinja2 templates
- Git integration for version control"

echo "初始提交完成！"

# 如果提供了远程仓库 URL，设置远程仓库
if [ $# -eq 1 ]; then
    REMOTE_URL="$1"
    echo "设置远程仓库: $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
    echo "远程仓库已设置。您可以运行 'git push -u origin main' 推送代码。"
fi

echo ""
echo "仓库初始化完成！"
echo "接下来可以："
echo "  1. 设置远程仓库（如果还没有）：git remote add origin <url>"
echo "  2. 推送代码：git push -u origin main"
echo "  3. 启动服务器：./scripts/start_server.sh"