#!/bin/bash
# 同步论文数据到主站

set -e

echo "🔄 开始同步论文数据到主站..."

# 同步网页
echo "📄 同步网页文件..."
cp /root/.openclaw/workspace/tmp/papers-daily-*.html /etc/nginx/html/papers/ 2>/dev/null || echo "  无 HTML 文件可同步"
cp /root/.openclaw/workspace/tmp/reports.json /etc/nginx/html/papers/ 2>/dev/null || echo "  无 reports.json 可同步"

# 同步 AI 评分到数据库
echo "📊 同步 AI 评分到数据库..."
if [ -f "/root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py" ]; then
    python3 /root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py \
       --db /etc/nginx/html/data/papers.db
else
    echo "  ⚠️  sync-ratings-to-db.py 不存在，跳过评分同步"
fi

echo "✅ 同步完成！"
