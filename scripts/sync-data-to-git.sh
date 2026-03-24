#!/bin/bash
# 同步论文数据到 Git 仓库
# 用法：./sync-data-to-git.sh [日期] [commit 信息]

set -e

# 默认值
PUSH_DATE=${1:-$(date +%Y-%m-%d)}
COMMIT_MSG=${2:-"📚 添加每日论文数据：$PUSH_DATE"}

# 路径配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
NGINX_DATA_DIR="/etc/nginx/html/papers"

echo "🔄 同步论文数据到 Git 仓库"
echo "=========================="
echo "日期：$PUSH_DATE"
echo "项目目录：$PROJECT_DIR"
echo ""

cd "$PROJECT_DIR"

# 检查数据文件是否存在
if [ ! -f "$NGINX_DATA_DIR/${PUSH_DATE}.json" ]; then
    echo "❌ 数据文件不存在：$NGINX_DATA_DIR/${PUSH_DATE}.json"
    echo "请先运行 generate-daily.sh 生成数据"
    exit 1
fi

# 确保 data 目录存在
mkdir -p "$DATA_DIR/summaries"

# 复制数据文件到 Git 仓库
echo "📋 复制数据文件..."
cp "$NGINX_DATA_DIR/${PUSH_DATE}.json" "$DATA_DIR/"
echo "✅ 已复制：${PUSH_DATE}.json"

# 复制 reports.json（论文索引）
if [ -f "$NGINX_DATA_DIR/reports.json" ]; then
    cp "$NGINX_DATA_DIR/reports.json" "$DATA_DIR/"
    echo "✅ 已复制：reports.json"
fi

# 如果有 summaries 目录，也同步过来
ORCHESTRATOR_DIR="/root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-${PUSH_DATE}"
if [ -d "$ORCHESTRATOR_DIR" ]; then
    echo "📋 同步论文解读 summaries..."
    for paper_dir in "$ORCHESTRATOR_DIR"/2603.*/; do
        if [ -d "$paper_dir" ]; then
            arxiv_id=$(basename "$paper_dir")
            target_dir="$DATA_DIR/summaries/$arxiv_id"
            mkdir -p "$target_dir"
            
            # 复制 summary.md 和 metadata.md
            [ -f "$paper_dir/summary.md" ] && cp "$paper_dir/summary.md" "$target_dir/"
            [ -f "$paper_dir/metadata.md" ] && cp "$paper_dir/metadata.md" "$target_dir/"
        fi
    done
    echo "✅ 已同步 summaries"
fi

# Git 操作
echo ""
echo "📤 提交到 Git..."
git add -A
git status --short

# 如果有变化，提交并推送
if ! git diff --staged --quiet; then
    git commit -m "$COMMIT_MSG"
    echo "✅ 已提交"
    
    echo "🚀 推送到远程仓库..."
    git push origin main
    echo "✅ 已推送"
else
    echo "⚠️  没有新变化，跳过提交"
fi

echo ""
echo "🎉 同步完成！"
echo ""
echo "📊 数据统计："
echo "  - data/ 目录大小：$(du -sh "$DATA_DIR" | awk '{print $1}')"
echo "  - Git 仓库大小：$(du -sh "$PROJECT_DIR/.git" | awk '{print $1}')"
echo ""
