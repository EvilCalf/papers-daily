#!/bin/bash
# daily-papers-cron.sh - 每日论文推送系统（完整版）
# 执行时间：每天 10:00 (北京时间)
# 用法：bash scripts/daily-papers-cron.sh

set -e

# 项目根目录
PROJECT_DIR="/root/.openclaw/workspace/projects/papers-daily"
WORKSPACE="/root/.openclaw/workspace"

# 脚本和日志使用项目目录
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"

# 临时文件和输出使用 workspace（共享）
TMP_DIR="$WORKSPACE/tmp"
NGINX_PAPERS="/etc/nginx/html/papers"

# 确保目录存在
mkdir -p "$LOG_DIR" "$TMP_DIR" "$NGINX_PAPERS/data"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/papers-cron.log"
}

log "=== 每日论文推送任务开始 ==="

# 计算日期
PUSH_DATE=$(date +%Y-%m-%d)          # 推送日期（今天）
TO_DATE=$(date -d "yesterday" +%Y-%m-%d)     # 检索结束日期（昨天）
DAY_OF_WEEK=$(date +%u)              # 星期几（1=周一，7=周日）

# 周一检索上周五的论文（arXiv 周末不更新），周二到周五检索 1 天（昨天）
if [ "$DAY_OF_WEEK" -eq 1 ]; then
    # 周一：检索上周五的论文（arXiv 周末不更新，周五是最近的发布日）
    FROM_DATE=$(date -d "3 days ago" +%Y-%m-%d)
    TO_DATE=$FROM_DATE  # 只检索周五当天
    LOOKBACK="1d"
    log "📅 周一：检索上周五的论文（$FROM_DATE）"
elif [ "$DAY_OF_WEEK" -eq 6 ] || [ "$DAY_OF_WEEK" -eq 7 ]; then
    # 周末：跳过
    log "🎉 周末时间，跳过推送（arXiv 周末不更新论文）"
    log "💤 下周一再见～"
    exit 0
else
    # 周二到周五：检索 1 天（昨天）
    FROM_DATE="$TO_DATE"
    LOOKBACK="1d"
    log "📅 工作日：检索 1 天（$FROM_DATE）"
fi

log "推送日期：$PUSH_DATE"
log "检索范围：$FROM_DATE 到 $TO_DATE"
log "星期：$DAY_OF_WEEK"

# 步骤 1: 运行编排器（检索 + AI 解读）
log "📥 步骤 1: 运行编排器（检索 + AI 解读）..."
log "⏱️ 预计耗时：10-20 分钟（取决于论文数量）"

# 根据星期几动态设置检索范围
if python3 "$SCRIPTS_DIR/papers-orchestrator.py" \
    --date "$PUSH_DATE" \
    --from-date "$FROM_DATE" \
    --to-date "$TO_DATE" \
    --lookback "$LOOKBACK" \
    --language Chinese; then
    log "✅ 编排器成功完成"
else
    log "⚠️  编排器返回非零状态，检查是否有部分成功"
fi

# 查找最新生成的目录
RUN_DIR=$(ls -td "$TMP_DIR/papers-orchestrator"/llm-ai-agent-* 2>/dev/null | head -1)
if [ -z "$RUN_DIR" ]; then
    log "❌ 未找到编排器输出目录"
    exit 1
fi

log "✅ 编排器目录：$RUN_DIR"

# 检查论文数量（优先使用过滤后的索引）
if [ -f "$RUN_DIR/papers_index_filtered.json" ]; then
    PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('$RUN_DIR/papers_index_filtered.json'))))" 2>/dev/null || echo "0")
    log "✅ 过滤后论文数：$PAPER_COUNT 篇"
else
    PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('$RUN_DIR/papers_index.json'))))" 2>/dev/null || echo "0")
    log "✅ 检索到 $PAPER_COUNT 篇论文"
fi

# 检查是否无论文
if [ "$PAPER_COUNT" -eq 0 ]; then
    log "⚠️  无新论文，生成空页面..."
    # 创建无论文标记
    cat > "$TMP_DIR/papers-no-new-${PUSH_DATE}.json" << EOF
{
    "date": "$PUSH_DATE",
    "paper_date": "$FROM_DATE",
    "status": "no_new_papers",
    "reason": "arXiv 没有相关论文发布"
}
EOF
    log "✅ 无论文标记已创建"
    log "=== 完整流程完成（无论文）==="
    exit 0
fi

# 步骤 2: 生成网页和数据
log "📄 步骤 2: 生成网页和数据..."

bash "$SCRIPTS_DIR/generate-daily.sh" "$PUSH_DATE" "$RUN_DIR"

log "✅ 网页和数据已生成"

# 步骤 3: 创建完成标记
log "📝 步骤 3: 创建完成标记..."

mkdir -p "$TMP_DIR/papers-done"
cat > "$TMP_DIR/papers-done/${PUSH_DATE}.json" << EOF
{
    "date": "$PUSH_DATE",
    "status": "success",
    "completed_at": "$(date -Iseconds)",
    "paper_count": $PAPER_COUNT,
    "run_dir": "$RUN_DIR",
    "note": "Cron 自动执行完成"
}
EOF

log "✅ 完成标记已创建"

# 完成
log "=========================================="
log "✅ 完整流程完成！"
log "=========================================="
log "📄 访问地址：http://evilcalf.online/papers/"
log "📊 论文数量：$PAPER_COUNT 篇"
log "=========================================="
