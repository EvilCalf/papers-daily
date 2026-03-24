#!/bin/bash
# 每日论文推送生成脚本
# 用法：./generate-daily.sh [日期] [编排器运行目录]
# 示例：./generate-daily.sh 2026-03-18 /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-xxx

set -e

# 默认值
PUSH_DATE=${1:-$(date +%Y-%m-%d)}
RUN_DIR=${2:-""}

# 路径配置
WORKSPACE="/root/.openclaw/workspace"
ORCHESTRATOR_DIR="$WORKSPACE/tmp/papers-orchestrator"
NGINX_DIR="/etc/nginx/html/papers"
SCRIPTS_DIR="$WORKSPACE/projects/papers-daily/scripts"

echo "📚 每日论文推送生成脚本"
echo "========================"
echo "推送日期：$PUSH_DATE"
echo ""

# 如果没有指定运行目录，自动查找最新的
if [ -z "$RUN_DIR" ]; then
    echo "🔍 自动查找最新的编排器运行目录..."
    RUN_DIR=$(ls -td "$ORCHESTRATOR_DIR"/*/ 2>/dev/null | grep "$PUSH_DATE" | head -1)
    
    if [ -z "$RUN_DIR" ]; then
        echo "❌ 未找到包含日期 $PUSH_DATE 的编排器运行目录"
        echo "请先运行编排器生成论文数据："
        echo "  python3 $SCRIPTS_DIR/papers-orchestrator.py --date $PUSH_DATE --lookback 1d --language Chinese"
        exit 1
    fi
    
    # 移除末尾的斜杠
    RUN_DIR="${RUN_DIR%/}"
fi

echo "运行目录：$RUN_DIR"
echo ""

# 检查运行目录是否存在
if [ ! -d "$RUN_DIR" ]; then
    echo "❌ 运行目录不存在：$RUN_DIR"
    exit 1
fi

# 检查 papers_index.json 是否存在
if [ ! -f "$RUN_DIR/papers_index.json" ]; then
    echo "❌ 未找到 papers_index.json，请先运行编排器"
    exit 1
fi

# 统计论文数量
PAPER_COUNT=$(ls -d "$RUN_DIR"/2603.*/ 2>/dev/null | wc -l)
SUMMARY_COUNT=$(find "$RUN_DIR" -name "summary.md" | wc -l)

echo "📊 论文统计："
echo "  - 论文目录数：$PAPER_COUNT"
echo "  - 已完成解读：$SUMMARY_COUNT"
echo ""

# 生成网页和数据
echo "🔨 生成网页和数据..."

# 生成 JSON 数据文件（包含所有论文和 AI 解读）
python3 "$SCRIPTS_DIR/orchestrator-to-web.py" \
    --run-dir "$RUN_DIR" \
    --push-date "$PUSH_DATE" \
    --data-dir "$NGINX_DIR"

# 验证生成结果
if [ -f "$NGINX_DIR/${PUSH_DATE}.json" ]; then
    echo ""
    echo "✅ 数据文件已生成：$NGINX_DIR/${PUSH_DATE}.json"
    echo "   文件大小：$(ls -lh "$NGINX_DIR/${PUSH_DATE}.json" | awk '{print $5}')"
else
    echo "❌ 数据文件生成失败"
    exit 1
fi

if [ -f "$NGINX_DIR/reports.json" ]; then
    echo "✅ 索引文件已更新：$NGINX_DIR/reports.json"
fi

echo ""
echo "🎉 生成完成！"
echo ""
echo "📄 访问地址："
echo "  主页：http://evilcalf.online/papers/"
echo "  详情：http://evilcalf.online/papers/detail.html?date=$PUSH_DATE"
echo ""

# 自动同步到 Git 仓库
echo "🔄 自动同步到 Git 仓库..."
"$SCRIPTS_DIR/sync-data-to-git.sh" "$PUSH_DATE" "📚 添加每日论文数据：$PUSH_DATE"
