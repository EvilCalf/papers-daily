#!/bin/bash
# 同步论文数据到 Git 仓库
# 用法：./sync-data-to-git.sh [日期] [提交信息]

set -e

PUSH_DATE=${1:-$(date +%Y-%m-%d)}
COMMIT_MSG=${2:-"📚 添加每日论文数据：$PUSH_DATE"}

# 项目根目录
PROJECT_DIR="/root/.openclaw/workspace/projects/papers-daily"
NGINX_DIR="/etc/nginx/html/papers"

# 要同步的文件
FILES_TO_SYNC=(
    "$PROJECT_DIR/data/${PUSH_DATE}.json"
    "$PROJECT_DIR/data/reports.json"
    "$NGINX_DIR/data/${PUSH_DATE}.json"
    "$NGINX_DIR/reports.json"
)

echo "🔄 同步论文数据到 Git 仓库..."
echo "推送日期：$PUSH_DATE"
echo "提交信息：$COMMIT_MSG"
echo ""

# 检查文件是否存在
for file in "${FILES_TO_SYNC[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️  文件不存在：$file，跳过"
    fi
done

echo ""
echo "📦 提交到 Git 仓库..."

# 切换到项目目录
cd "$PROJECT_DIR"

# 添加文件
git add data/

# 检查是否有改动
if git status --porcelain | grep -q .; then
    git commit -m "$COMMIT_MSG"
    git push origin main
    echo "✅ 数据已同步到 Git 仓库"
else
    echo "ℹ️  没有需要提交的改动"
fi

echo ""
echo "✅ 同步完成！"
