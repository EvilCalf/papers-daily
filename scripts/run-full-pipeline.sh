#!/bin/bash
# 每日论文推送 - 完整流程运行脚本
# 用法：bash scripts/run-full-pipeline.sh [论文日期]

set -e

# 项目根目录
PROJECT_DIR="/root/.openclaw/workspace/projects/papers-daily"
WORKSPACE="/root/.openclaw/workspace"

# 脚本和日志
SCRIPTS_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"

# 临时文件
TMP_DIR="$WORKSPACE/tmp"
NGINX_PAPERS="/etc/nginx/html/papers"

# 确保目录存在
mkdir -p "$LOG_DIR" "$TMP_DIR" "$NGINX_PAPERS"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/papers-run.log"
}

# 参数处理
PAPER_DATE=${1:-$(date -d "yesterday" +%Y-%m-%d)}
PUSH_DATE=$(date +%Y-%m-%d)

log "=========================================="
log "📚 每日论文推送 - 完整流程"
log "=========================================="
log "论文日期：$PAPER_DATE"
log "推送日期：$PUSH_DATE"
log "=========================================="

# 步骤 1: 检索论文（Stage A）
log "📥 步骤 1: 检索 arXiv 论文（Stage A）..."

python3 "$SCRIPTS_DIR/papers-orchestrator.py" \
    --date "$PAPER_DATE" \
    --push-date "$PUSH_DATE" \
    --from-date "$PAPER_DATE" \
    --to-date "$PAPER_DATE" \
    --language Chinese \
    --stage A

if [ $? -ne 0 ]; then
    log "❌ 检索失败"
    exit 1
fi

# 查找最新生成的目录
RUN_DIR=$(ls -td "$TMP_DIR/papers-orchestrator"/llm-ai-agent-* 2>/dev/null | head -1)
if [ -z "$RUN_DIR" ]; then
    log "❌ 未找到检索输出目录"
    exit 1
fi

log "✅ 检索完成：$RUN_DIR"

# 检查论文数量
PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('$RUN_DIR/papers_index.json'))))" 2>/dev/null || echo "0")
log "✅ 检索到 $PAPER_COUNT 篇论文"

if [ "$PAPER_COUNT" -lt 15 ]; then
    log "⚠️  论文数量较少（<$15 篇），但仍继续处理"
fi

# 步骤 2: 质量检查（可选）
log "🔍 步骤 2: 质量检查（Stage A 输出）..."

python3 "$SCRIPTS_DIR/check-summary-quality.py" \
    --run-dir "$RUN_DIR"

# 步骤 3: AI 解读（Stage B）
log "🤖 步骤 3: AI 解读论文（Stage B）..."

python3 "$SCRIPTS_DIR/papers-orchestrator.py" \
    --date "$PAPER_DATE" \
    --push-date "$PUSH_DATE" \
    --from-date "$PAPER_DATE" \
    --to-date "$PAPER_DATE" \
    --language Chinese \
    --stage B

# 步骤 4: 质量检查（Stage B 输出）
log "🔍 步骤 4: 质量检查（Stage B 输出）..."

python3 "$SCRIPTS_DIR/check-summary-quality.py" \
    --run-dir "$RUN_DIR" \
    --fix

# 如果有需要重新生成的论文，处理它们
REGEN_FILE="$RUN_DIR/papers-need-regen.json"
if [ -f "$REGEN_FILE" ]; then
    log "⚠️  发现需要重新生成的论文，处理中..."
    # TODO: 实现自动重试逻辑
fi

# 步骤 5: 生成网页（Stage C）
log "📄 步骤 5: 生成网页（Stage C）..."

python3 "$SCRIPTS_DIR/orchestrator-to-web.py" \
    --run-dir "$RUN_DIR" \
    --push-date "$PUSH_DATE" \
    --output-html "$NGINX_PAPERS/$PUSH_DATE.html"

log "✅ 网页已生成：$NGINX_PAPERS/$PUSH_DATE.html"

# 步骤 6: 访问测试
log "🌐 步骤 6: 访问测试..."

if curl -s -o /dev/null -w "%{http_code}" "http://localhost/papers/$PUSH_DATE.html" | grep -q "200"; then
    log "✅ 网页访问正常"
else
    log "⚠️  网页访问测试失败，请手动检查"
fi

# 完成
log "=========================================="
log "✅ 完整流程完成！"
log "=========================================="
log "📄 访问地址：http://evilcalf.online/papers/$PUSH_DATE.html"
log "📊 论文数量：$PAPER_COUNT 篇"
log "=========================================="
