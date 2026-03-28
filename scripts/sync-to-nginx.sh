#!/bin/bash
# 同步论文数据到主站

set -e

echo "🔄 开始同步论文数据到主站..."

# 同步网页
echo "📄 同步网页文件..."
cp /root/.openclaw/workspace/tmp/papers-daily-*.html /etc/nginx/html/papers/ 2>/dev/null || echo "  无 HTML 文件可同步"

# 仅当 reports.json 存在且更新时间小于 1 小时时才同步，避免覆盖新数据
REPORTS_JSON="/root/.openclaw/workspace/tmp/reports.json"
if [ -f "$REPORTS_JSON" ]; then
    # 检查文件修改时间是否在 1 小时内
    if [ $(find "$REPORTS_JSON" -mmin -60 | wc -l) -gt 0 ]; then
        cp "$REPORTS_JSON" /etc/nginx/html/papers/
        echo "  ✅ reports.json 已同步"
    else
        echo "  ⚠️  reports.json 文件已超过 1 小时，跳过同步以避免覆盖新数据"
        echo "  💡 如果确认要同步，请手动执行: cp $REPORTS_JSON /etc/nginx/html/papers/"
    fi
else
    echo "  无 reports.json 可同步"
fi

# 同步 AI 评分到数据库
echo "📊 同步 AI 评分到数据库..."
if [ -f "/root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py" ]; then
    python3 /root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py \
       --db /etc/nginx/html/data/papers.db
else
    echo "  ⚠️  sync-ratings-to-db.py 不存在，跳过评分同步"
fi

echo "✅ 同步完成！"
