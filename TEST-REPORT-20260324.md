# 论文模块集成测试报告

**日期**: 2026-03-24  
**分支**: feat/papers-module-20260324  
**测试人**: EvilBot 😈

---

## 测试结果

### 后端测试

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 数据库权限 | ✅ | `/etc/nginx/html/data/papers.db` 所有者 apache:apache，权限 644 |
| 评分 API (GET) | ✅ | `curl http://localhost/api/papers/ratings.php/2403.12345` 返回正确 JSON |
| 评分 API (POST) | ✅ | 管理员可创建/更新评分（需登录） |
| 投票 API (POST) | ✅ | 游客/登录用户可投票，游客限流生效 |
| 日志检查 | ✅ | 无新报错（旧错误为 09:xx 时段，已修复） |

**API 测试详情：**

```bash
# GET 评分
$ curl -s "http://localhost/api/papers/ratings.php/2403.12345"
{"arxiv_id":"2403.12345","rating":null,"votes":{"up":1,"down":0}}

# POST 投票（游客首次）
$ curl -s -X POST "http://localhost/api/papers/votes.php" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2403.12345", "vote_type": "up"}'
{"success": true, "action": "created"}

# POST 投票（游客重复，触发限流）
$ curl -s -X POST "http://localhost/api/papers/votes.php" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2403.12345", "vote_type": "down"}'
{"error":"每天只能投一次票"}
```

### 前端测试

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 控制台 | ✅ | 无 JavaScript 错误 |
| 网络请求 | ✅ | API 请求返回 200 |
| ID 冲突 | ✅ | 无重复 ID（动态 ID 使用模板字符串） |
| 缓存问题 | ✅ | 强制刷新后功能正常 |

**检查命令：**

```bash
# 检查重复 ID
$ grep -rn 'id="[^"]*"' papers/detail.html | grep -o 'id="[^"]*"' | sort | uniq -d
# 输出：无重复（仅动态模板字符串）
```

### 集成测试

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 评分显示 | ✅ | detail.html 每篇论文显示 AI 评分区域 |
| 投票功能 | ✅ | 点击点赞/点踩成功，计数更新 |
| 管理员编辑 | ✅ | 登录后管理员看到编辑按钮 |
| 权限验证 | ✅ | 未登录用户不能编辑评分（API 返回 401） |

**前端集成详情：**

- **detail.html**: 每篇论文卡片底部添加评分和投票区域
  - 自动加载评分数据（API: `/api/papers/ratings.php/{arxiv_id}`）
  - 显示星级、详细分数、评分理由
  - 点赞/点踩按钮（游客可用）
  - 管理员编辑按钮（仅管理员可见）

- **index.html**: 历史列表页支持单篇论文查看
  - 通过 URL 参数 `?paper={arxiv_id}` 指定论文
  - 显示评分和投票区域

### 同步脚本测试

| 测试项 | 状态 | 说明 |
|--------|------|------|
| sync-ratings-to-db.py | ✅ | 脚本存在，可执行 |
| 功能验证 | ⚠️ | rating.json 暂未生成（等待首次论文推送） |

**脚本位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/sync-ratings-to-db.py`

**使用说明**:
```bash
python3 scripts/sync-ratings-to-db.py --db /etc/nginx/html/data/papers.db
```

---

## Git 提交

### nginx-html 仓库

```bash
cd /etc/nginx/html
git commit -m "feat: 完成论文模块集成（评分 + 投票）"
git push origin feat/papers-module-20260324
```

**提交内容**:
- `.gitignore` - 更新，只忽略生成的 JSON 文件
- `api/papers/ratings.php` - 评分 API
- `api/papers/votes.php` - 投票 API
- `papers/detail.html` - 详情页集成评分投票
- `papers/index.html` - 列表页集成评分投票

**PR 链接**: https://github.com/EvilCalf/nginx-html/pull/new/feat/papers-module-20260324

### papers-daily 仓库

```bash
cd /root/.openclaw/workspace/projects/papers-daily
git push origin feat/papers-module-20260324
```

**同步脚本已在之前提交**: `scripts/sync-ratings-to-db.py`

**PR 链接**: https://github.com/EvilCalf/papers-daily/pull/new/feat/papers-module-20260324

---

## 问题与修复

### 问题 1: .gitignore 配置过严

**现象**: papers/*.html 文件未被 Git 跟踪

**原因**: `.gitignore` 中包含 `papers/`，忽略了整个目录

**修复**: 更新 `.gitignore`，只忽略生成的 JSON 文件：
```gitignore
# Generated papers data (JSON files only)
papers/*.json
papers/data/
```

### 问题 2: 游客投票限流测试

**现象**: 第二次投票返回"每天只能投一次票"

**原因**: 游客防刷机制正常工作（基于 IP+UserAgent 哈希）

**状态**: ✅ 预期行为，非 Bug

---

## 后续工作

1. **合并分支**: 等待主会话审核并合并到 main
2. **首次论文推送**: 运行 orchestrator 生成 rating.json
3. **同步测试**: 运行 sync-ratings-to-db.py 验证数据同步
4. **线上验证**: 访问 http://evilcalf.online/papers/ 测试完整流程

---

_测试完成时间：2026-03-24 17:40 UTC_
