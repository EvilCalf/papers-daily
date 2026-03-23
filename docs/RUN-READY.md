# 🚀 重新运行准备清单

**创建时间**: 2026-03-18  
**状态**: ✅ 已就绪

---

## ✅ 已完成的修复和更新

### 1. 脚本修复

| 脚本 | 修复内容 | 状态 |
|------|----------|------|
| `daily-papers-cron.sh` | 改为调用 `papers-orchestrator.py` | ✅ |
| `papers-orchestrator.py` | 修复日期格式、关键词配置 | ✅ |
| `papers-orchestrator.py` | Prompt 明确禁止生成标记 | ✅ |
| `orchestrator-to-web.py` | 支持中英文键名 | ✅ |
| `orchestrator-to-web.py` | 过滤 AI 生成标记 | ✅ |

### 2. 新增脚本

| 脚本 | 功能 | 状态 |
|------|------|------|
| `check-summary-quality.py` | 质量检查（验证格式、检测错误） | ✅ |
| `run-full-pipeline.sh` | 一键运行完整流程 | ✅ |

### 3. 文档更新

| 文档 | 内容 | 状态 |
|------|------|------|
| `LESSONS-LEARNED.md` | 经验教训总结（7 个核心问题） | ✅ |
| `README.md` | 添加故障排查章节 | ✅ |
| `INDEX.md` | 添加新文档索引 | ✅ |
| `RUN-READY.md` | 本文档（运行准备清单） | ✅ |

---

## 📋 下次运行前检查

### 环境检查

```bash
# 1. 检查 gateway 状态
openclaw status

# 2. 检查 cron 配置
crontab -l | grep papers

# 3. 清理旧临时文件（>24 小时）
find /root/.openclaw/workspace/tmp -name "*.json" -mtime +1 -delete
```

### 脚本验证

```bash
# 1. 验证 papers-orchestrator.py
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py --help

# 2. 验证 orchestrator-to-web.py
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py --help

# 3. 验证 check-summary-quality.py
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/check-summary-quality.py --help
```

### 配置验证

```bash
# 1. 检查关键词配置（40 个）
grep -A5 "keywords" /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py | head -10

# 2. 检查目标范围（15-30）
grep "target-range" /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py

# 3. 检查 cron 时间（23:00）
crontab -l | grep papers
```

---

## 🎯 推荐运行方式

### 方式 1：一键运行（推荐）

```bash
# 使用新脚本运行完整流程
bash /root/.openclaw/workspace/projects/papers-daily/scripts/run-full-pipeline.sh 2026-03-17
```

**优点**:
- 自动执行所有步骤
- 包含质量检查
- 自动访问测试

### 方式 2：分步运行

```bash
# Stage A: 检索
python3 papers-orchestrator.py --date 2026-03-17 --stage A

# 检查检索结果
cat run_dir/papers_index.json | python3 -m json.tool

# Stage B: AI 解读
python3 papers-orchestrator.py --date 2026-03-17 --stage B

# 质量检查
python3 check-summary-quality.py --run-dir run_dir

# Stage C: 网页生成
python3 orchestrator-to-web.py --run-dir run_dir --push-date 2026-03-18
```

**优点**:
- 每步可单独验证
- 便于调试
- 灵活控制

---

## 📊 预期结果

### Stage A（检索）

- ✅ 论文数量：15-30 篇
- ✅ 生成 `papers_index.json`
- ✅ 生成 `query_plan.json`（5 个查询）
- ✅ 每个论文目录有 `metadata.md`

### Stage B（AI 解读）

- ✅ 所有论文有 `summary.md`
- ✅ 每篇 >1000 字符
- ✅ 10 节标准格式
- ✅ 无 gateway 错误污染
- ✅ 无 AI 生成标记

### Stage C（网页生成）

- ✅ HTML 文件 >50KB
- ✅ `reports.json` 同步到 nginx
- ✅ 网页无空内容
- ✅ 网页无 AI 标记
- ✅ 访问测试通过（HTTP 200）

---

## 🚨 故障排查

### 问题 1：检索到 0 篇论文

```bash
# 检查 query_plan.json
cat run_dir/query_plan.json | python3 -m json.tool

# 手动测试 arXiv API
curl "https://export.arxiv.org/api/query?search_query=all:LLM"
```

### 问题 2：summary.md 被污染

```bash
# 检测被污染的文件
grep -l "Gateway agent failed" run_dir/*/summary.md

# 重新生成单篇论文
python3 papers-orchestrator.py --date 2026-03-17 --stage B
```

### 问题 3：网页显示英文

```bash
# 检查 summary.md 格式
head -20 run_dir/2603.xxxxx/summary.md

# 检查章节名
grep "^## " run_dir/2603.xxxxx/summary.md
```

---

## 📝 运行后清理

```bash
# 1. 清理临时文件（保留最近 7 天）
find /root/.openclaw/workspace/tmp/papers-orchestrator -mtime +7 -exec rm -rf {} \;

# 2. 清理旧 reports.json 备份
find /etc/nginx/html/papers -name "reports.json.*" -delete

# 3. 清理日志（保留最近 30 天）
find /root/.openclaw/workspace/projects/papers-daily/logs -mtime +30 -delete
```

---

## 🎯 关键配置（不要修改）

| 配置项 | 值 | 位置 |
|--------|-----|------|
| 关键词数量 | 40 个 | `papers-orchestrator.py` |
| 目标范围 | 15-30 篇 | `papers-orchestrator.py` |
| 并发配置 | 3 subagent × 4 篇 | `papers-orchestrator.py` |
| Cron 时间 | 23:00 | `crontab` |
| 检索日期 | 昨天 | `daily-papers-cron.sh` |

---

## 📞 支持文档

- **经验教训**: [LESSONS-LEARNED.md](LESSONS-LEARNED.md)
- **完整架构**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **快速开始**: [../README.md](../README.md)

---

_准备就绪 - 2026-03-18_
