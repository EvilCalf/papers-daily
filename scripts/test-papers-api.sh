#!/bin/bash
# 测试论文 API 功能

BASE_URL="http://localhost/api/papers"

echo "🧪 开始测试论文 API..."
echo ""

# 测试 1: GET 评分（无 arxiv_id）
echo "测试 1: GET 评分（缺少 arxiv_id）"
curl -s "$BASE_URL/ratings.php/" | jq .
echo ""

# 测试 2: 插入测试论文数据
echo "测试 2: 插入测试论文数据..."
sqlite3 /etc/nginx/html/data/papers.db "INSERT OR REPLACE INTO papers (arxiv_id, title, abstract, categories, paper_date, push_date, pdf_url) VALUES ('2403.12345', 'Test Paper Title', 'This is a test abstract', '[\"cs.AI\", \"cs.LG\"]', '2024-03-24', '2024-03-24', 'https://arxiv.org/abs/2403.12345');"
echo "✓ 测试论文已插入"
echo ""

# 测试 3: GET 评分（有 arxiv_id，无数据）
echo "测试 3: GET 评分（有 arxiv_id，暂无评分）"
curl -s "$BASE_URL/ratings.php/2403.12345" | jq .
echo ""

# 测试 4: POST 投票（游客）
echo "测试 4: POST 投票（游客点赞）"
curl -s -X POST "$BASE_URL/votes.php" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2403.12345", "vote_type": "up"}' | jq .
echo ""

# 测试 5: GET 评分（有投票数据）
echo "测试 5: GET 评分（查看投票统计）"
curl -s "$BASE_URL/ratings.php/2403.12345" | jq .
echo ""

# 测试 6: POST 评分（需要管理员）
echo "测试 6: POST 评分（需要管理员权限）"
curl -s -X POST "$BASE_URL/ratings.php/2403.12345" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2403.12345", "overall": 8, "reason": "Test rating"}' | jq .
echo ""

echo "✅ API 测试完成！"
echo ""
echo "📝 手动测试说明："
echo "  1. 访问 http://evilcalf.online/papers/ 查看前端页面"
echo "  2. 登录后测试管理员评分功能"
echo "  3. 使用游客身份测试投票功能"
