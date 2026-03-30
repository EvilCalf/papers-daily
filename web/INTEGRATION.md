# 论文模块集成文档

## 完成时间
2026-03-24

## 完成的工作

### 1. 数据库创建 ✅
- **文件**: `/etc/nginx/html/data/papers.db`
- **表结构**:
  - `papers` - 论文信息表
  - `paper_ratings` - 评分表（管理员专用）
  - `paper_votes` - 投票表（游客 + 用户）
- **索引**: 已创建优化查询性能的索引

### 2. API 接口 ✅

#### GET /api/papers/ratings.php/{arxiv_id}
获取论文评分和投票统计

**响应示例**:
```json
{
  "arxiv_id": "2403.12345",
  "rating": {
    "id": "rating_xxx",
    "overall": 8,
    "innovation": 9,
    "practicality": 7,
    "quality": 8,
    "impact": 9,
    "reason": "提出了有效的优化方法...",
    "tags": ["llm", "optimization"],
    "is_admin_rating": true
  },
  "votes": {
    "up": 15,
    "down": 3
  }
}
```

#### POST /api/papers/ratings.php/{arxiv_id}
创建/更新论文评分（仅管理员）

**请求体**:
```json
{
  "arxiv_id": "2403.12345",
  "overall": 8,
  "innovation": 9,
  "practicality": 7,
  "quality": 8,
  "impact": 9,
  "reason": "评分理由",
  "tags": ["tag1", "tag2"]
}
```

**权限**: 需要管理员登录

#### POST /api/papers/votes.php
投票（游客和用户）

**请求体**:
```json
{
  "arxiv_id": "2403.12345",
  "vote_type": "up"  // 或 "down"
}
```

**防刷机制**:
- 游客：基于 IP+UserAgent+ 日期哈希，每天每篇论文限投一次
- 用户：每篇论文限投一次，可修改投票

### 3. 同步脚本 ✅

#### sync-to-nginx.sh
**位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/sync-to-nginx.sh`

**功能**:
- 同步 HTML 网页到 `/etc/nginx/html/papers/`
- 同步 reports.json 到 `/etc/nginx/html/papers/`
- 调用 sync-ratings-to-db.py 同步 AI 评分到数据库

**使用**:
```bash
/root/.openclaw/workspace/projects/papers-daily/scripts/sync-to-nginx.sh
```

#### sync-ratings-to-db.py
**位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py`

**功能**:
- 读取 rating.json 中的 AI 评分
- 同步到 papers.db 数据库
- 自动创建或更新评分记录

**使用**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py \
  --db /etc/nginx/html/data/papers.db
```

### 4. 前端集成 ✅

#### papers/index.html
**新增功能**:
- ✅ 登录状态检查（右上角显示用户名或登录按钮）
- ✅ 管理员功能（评分编辑按钮，仅管理员可见）
- ✅ 评分显示组件（星级 + 详细分数 + 评价理由）
- ✅ 投票功能（点赞/点踩按钮，游客可用）

**JavaScript 函数**:
- `checkLoginStatus()` - 检查登录状态
- `logout()` - 退出登录
- `vote(voteType)` - 投票
- `editRating()` - 编辑评分（管理员）
- `submitRating(arxivId, reason)` - 提交评分
- `loadRatingAndVotes(arxivId)` - 加载评分和投票数据

**使用示例**:
```javascript
// 在论文详情页加载评分
const arxivId = '2403.12345';
loadRatingAndVotes(arxivId);

// 投票
vote('up');  // 点赞
vote('down'); // 点踩
```

### 5. Nginx 配置 ✅

**文件**: `/etc/nginx/conf.d/evilcalf.conf`

**新增路由**:
```nginx
# 论文 API 路由 - 支持 PATH_INFO (ratings.php/arxiv_id 格式)
location ~ ^/api/papers/(.+)\.php(/.*)?$ {
    root /etc/nginx/html;
    
    fastcgi_pass unix:/run/php-fpm/www.sock;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME /etc/nginx/html/api/papers/$1.php;
    fastcgi_param PATH_INFO $2;
    include fastcgi_params;
}
```

### 6. 数据库权限 ✅

**已设置权限**:
```bash
chmod 666 /etc/nginx/html/data/papers.db
chmod 777 /etc/nginx/html/data/
```

## 测试验证

### 测试脚本
**位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/test-papers-api.sh`

### 手动测试

1. **测试 GET 评分**:
```bash
curl http://localhost/api/papers/ratings.php/2403.12345
```

2. **测试投票**:
```bash
curl -X POST http://localhost/api/papers/votes.php \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2403.12345", "vote_type": "up"}'
```

3. **测试管理员评分** (需要登录):
```bash
curl -X POST http://localhost/api/papers/ratings.php/2403.12345 \
  -H "Content-Type: application/json" \
  -H "Cookie: auth_token=YOUR_TOKEN" \
  -d '{"arxiv_id": "2403.12345", "overall": 8, "reason": "测试评分"}'
```

4. **前端测试**:
访问 http://evilcalf.online/papers/ 查看论文列表页面

## 数据库表结构

### papers 表
```sql
CREATE TABLE papers (
    arxiv_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    categories TEXT,  -- JSON 数组
    paper_date TEXT,
    push_date TEXT,
    pdf_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### paper_ratings 表
```sql
CREATE TABLE paper_ratings (
    id TEXT PRIMARY KEY,
    arxiv_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    overall INTEGER CHECK(overall BETWEEN 1 AND 10),
    innovation INTEGER CHECK(innovation BETWEEN 1 AND 10),
    practicality INTEGER CHECK(practicality BETWEEN 1 AND 10),
    quality INTEGER CHECK(quality BETWEEN 1 AND 10),
    impact INTEGER CHECK(impact BETWEEN 1 AND 10),
    reason TEXT,
    tags TEXT,  -- JSON 数组
    is_ai_generated BOOLEAN DEFAULT TRUE,
    is_admin_rating BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY(arxiv_id) REFERENCES papers(arxiv_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### paper_votes 表
```sql
CREATE TABLE paper_votes (
    id TEXT PRIMARY KEY,
    arxiv_id TEXT NOT NULL,
    user_id TEXT,  -- NULL 表示游客
    vote_type TEXT CHECK(vote_type IN ('up', 'down')),
    session_hash TEXT,  -- 游客防刷
    ip_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(arxiv_id) REFERENCES papers(arxiv_id)
);
```

## 文件清单

### 数据库
- `/etc/nginx/html/data/papers.db`

### API 文件
- `/etc/nginx/html/api/papers/ratings.php`
- `/etc/nginx/html/api/papers/votes.php`

### 同步脚本
- `/root/.openclaw/workspace/projects/papers-daily/scripts/sync-to-nginx.sh`
- `/root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py`

### 前端
- `/etc/nginx/html/papers/index.html` (已更新)

### 配置
- `/etc/nginx/conf.d/evilcalf.conf` (已更新)

### 库文件
- `/etc/nginx/html/lib/DB.php` (已更新支持多数据库)

## 后续工作

1. **前端完善**:
   - 在论文详情页集成评分和投票组件
   - 添加评分编辑弹窗
   - 优化移动端显示

2. **功能增强**:
   - 添加评分历史记录
   - 添加投票统计图表
   - 添加热门论文排行

3. **安全加固**:
   - 添加 API 速率限制
   - 完善游客防刷机制
   - 添加异常监控

## 注意事项

1. **数据库权限**: 确保 PHP-FPM 进程有权限写入 papers.db
2. **外键约束**: paper_ratings 表的 user_id 需要存在于 users 表中
3. **PATH_INFO**: API 使用 PATH_INFO 传递 arxiv_id，确保 Nginx 配置正确
4. **CORS**: API 已启用 CORS，允许跨域访问

---
_集成完成 by EvilBot 😈_
