# 每日论文推送系统 v2.1 - 完整实现方案

**最后更新**: 2026-03-18  
**系统状态**: ✅ 生产环境可用

---

## 📋 目录

1. [系统架构](#系统架构)
2. [目录结构](#目录结构)
3. [核心脚本](#核心脚本)
4. [数据格式](#数据格式)
5. [使用指南](#使用指南)
6. [定时任务配置](#定时任务配置)

---

## 系统架构

### 完整链路

```
Cron 触发 (23:00) → 检索 arXiv → AI 解读 (10 节) → 生成 JSON 数据 → 更新索引 → 动态网页展示
```

### 新架构特点（v2.1）

| 特性 | 旧架构 (v2.0) | 新架构 (v2.1) |
|------|--------------|--------------|
| 数据格式 | 静态 HTML | JSON 数据 |
| 详情页 | 每天生成一个 HTML | 通用模板 + 动态数据 |
| 文件大小 | ~200KB/天 | ~350KB/天（JSON） |
| 样式修改 | 需修改多个文件 | 只需改 detail.html |
| 数据展示 | 分离 | 完全分离 |

### 数据流

```
arXiv API
    ↓
papers-orchestrator.py (Stage A: 检索)
    ↓
papers_index.json (40 篇论文元数据)
    ↓
papers-orchestrator.py (Stage B: AI 解读)
    ↓
papers/<arxiv_id>/summary.md (10 节深度解读)
    ↓
orchestrator-to-web.py (Stage C: 生成 JSON)
    ↓
/etc/nginx/html/papers/data/{date}.json
/etc/nginx/html/papers/reports.json
    ↓
前端网页动态读取展示
```

---

## 目录结构

### 项目目录

```
/root/.openclaw/workspace/projects/papers-daily/
├── README.md                        # 项目说明
├── docs/
│   ├── INDEX.md                     # 文档索引
│   ├── ARCHITECTURE.md              # 完整架构
│   ├── IMPLEMENTATION.md            # 实现方案（本文档）
│   └── SEARCH-CONFIG.md             # 检索配置
├── scripts/
│   ├── papers-orchestrator.py       # 总编排器（Stage A/B）⭐
│   ├── orchestrator-to-web.py       # 网页生成器（Stage C）⭐
│   ├── papers-heartbeat-check.py    # Heartbeat 检查脚本
│   ├── daily-papers-cron.sh         # Cron 入口脚本
│   ├── run-full-pipeline.sh         # 完整流程脚本
│   └── check-summary-quality.py     # 质量检查脚本
└── logs/
    └── papers-cron.log              # Cron 日志
```

### 临时文件

```
/root/.openclaw/workspace/tmp/papers-orchestrator/
└── llm-ai-agent-{date}/
    ├── task_meta.json               # 任务元数据
    ├── task_meta.md                 # 任务元数据（可读）
    ├── papers_index.json            # 论文索引（40 篇）
    └── papers/<arxiv_id>/
        ├── metadata.md              # 论文元数据
        ├── source/                  # 论文源码/PDF
        └── summary.md               # AI 深度解读（10 节）⭐
```

### 网页部署

```
/etc/nginx/html/papers/
├── index.html                       # 主页（动态读取 reports.json）
├── detail.html                      # 通用详情页模板 ⭐
├── reports.json                     # 推送索引 ⭐
└── data/
    ├── 2026-03-18.json              # 每日论文数据 ⭐
    └── ...
```

---

## 核心脚本

### 0. interpret-papers-parallel.py（并行解读）⭐

**新增**: v2.1 新增，直接调用 API 并行解读，**速度提升 5 倍**！

**功能**: 并行 AI 解读论文（不依赖 subagent）

**参数**:
```bash
python3 interpret-papers-parallel.py \
  --run-dir /path/to/run-dir \
  --max-workers 10 \      # 并发数，默认 10
  --language Chinese
```

**性能对比**:
| 模式 | 并发数 | 40 篇耗时 | 超时风险 |
|------|--------|----------|----------|
| 旧 subagent 模式 | 5 | ~25 分钟 | 高 |
| **新 API 并行模式** | **10** | **~5 分钟** | **低** |

**特点**:
- ✅ 直接调用 DashScope API，不依赖 subagent
- ✅ ThreadPoolExecutor 并行处理，支持 10-20 并发
- ✅ 每篇独立超时（120 秒），不会互相影响
- ✅ 自动跳过已解读的论文
- ✅ 支持断点续跑
- ✅ 适合定时任务和手动触发

**API Key 配置**:
```bash
# 方式 1: 环境变量
export DASHSCOPE_API_KEY="sk-xxxxx"

# 方式 2: 配置文件 ~/.openclaw/config.json
{
  "models": {
    "dashscope": {
      "apiKey": "sk-xxxxx"
    }
  }
}
```

---

### 1. papers-orchestrator.py（总编排器）

**功能**: Stage A 检索 + Stage B AI 解读

**参数**:
```bash
python3 papers-orchestrator.py \
  --date 2026-03-18 \
  --from-date "2026-03-18" \
  --to-date "2026-03-18" \
  --language Chinese \
  --stage all  # A:检索 B:解读 C:报告 all:全部
```

**核心流程**:

```python
# Stage A: 检索
init_run() → 初始化任务
generate_query_plan() → 生成 40 个关键词查询
fetch_queries() → 执行查询
merge_papers() → 合并去重 → papers_index.json

# Stage B: AI 解读
download_papers() → 下载源码/PDF
interpret_papers() → 为每篇论文 spawn subagent
  → 读取 metadata.md + source
  → 撰写 10 节深度解读
  → 写入 summary.md
```

**10 节解读格式**:
```markdown
## 1. Paper Snapshot
- arXiv ID, 标题，作者，分类，日期

## 2. 研究目标
解决什么问题

## 3. 方法概述
核心技术方案

## 4. 数据和评估
实验设置、数据集、指标

## 5. 关键结果
具体数字和发现

## 6. 优势
相比之前方法的优势

## 7. 局限性和风险
诚实评估不足之处

## 8. 可重复性说明
代码/数据可用性

## 9. 实践启示
对从业者的价值

## 10. 简要结论
3-4 句精华总结
```

---

### 2. orchestrator-to-web.py（网页生成器）

**功能**: Stage C - 生成 JSON 数据 + 更新索引

**参数**:
```bash
python3 orchestrator-to-web.py \
  --run-dir /path/to/run-dir \
  --push-date 2026-03-18 \
  --data-dir /etc/nginx/html/papers
```

**核心流程**:

```python
# 1. 读取所有 summary.md
for paper in papers_index:
    summary = read_summary_md(paper_dir)
    metadata = read_metadata_md(paper_dir)

# 2. 构建 JSON 数据结构
data = {
    'push_date': '2026-03-18',
    'total_count': 40,
    'category_count': 5,
    'categories': [
        {
            'name': 'cs.AI',
            'papers': [
                {
                    'arxiv_id': '2603.16871',
                    'title': 'WorldCam...',
                    'brief': '<p>...</p>',  # HTML 格式
                    'details': {
                        'research_goal': '<p>...</p>',
                        'method': '<p>...</p>',
                        'results': '<p>...</p>',
                        'conclusion': '<p>...</p>'
                    }
                }
            ]
        }
    ]
}

# 3. 写入 JSON 文件
write_json(f"{data_dir}/data/{push_date}.json")

# 4. 更新 reports.json 索引
reports = [
    {
        'date': '2026-03-18',
        'count': 40,
        'llm_count': 8,
        'agent_count': 19,
        'data_file': 'data/2026-03-18.json',
        'detail_url': 'detail.html?date=2026-03-18'
    }
]
write_json(f"{data_dir}/reports.json")
```

**markdown_to_html 函数**:
- ✅ 支持标题（`#`, `##`, `###`）
- ✅ 支持列表（`- `, `* `）
- ✅ 支持粗体/斜体（`**text**`, `*text*`）
- ✅ 支持行内代码（`` `code` ``）
- ✅ 支持链接（`[text](url)`）
- ✅ 支持表格（`| col1 | col2 |`）
- ✅ 自动清理 AI 生成标记

---

### 3. papers-heartbeat-check.py（Heartbeat 检查）

**功能**: 检查并执行遗漏的论文推送

**触发条件**:
- 每天 23:30-24:00 之间检查
- 错过时间窗口则发现任务立即执行

**检查逻辑**:
```python
# 场景 A: 有待处理任务
if exists('papers-task-pending.json'):
    执行完整流程：AI 解读 → 生成网页 → 同步 reports.json → 发送推送

# 场景 B: 网页已生成但未推送
elif exists('{date}.html') and not exists('papers-done/{date}.json'):
    直接发送推送

# 场景 C: 无新论文标记
elif exists('papers-no-new-{date}.json'):
    生成"无新论文"推送
```

---

### 4. daily-papers-cron.sh（Cron 入口）

**功能**: Cron 定时任务入口脚本

**内容**:
```bash
#!/bin/bash
# 每日论文检索（23:00 执行）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date $(date -d "yesterday" +%Y-%m-%d) \
  --from-date $(date -d "yesterday" +%Y-%m-%d) \
  --to-date $(date -d "yesterday" +%Y-%m-%d) \
  --language Chinese \
  --stage all

# 生成网页
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-$(date -d "yesterday" +%Y%m%d)-* \
  --push-date $(date -d "yesterday" +%Y-%m-%d) \
  --data-dir /etc/nginx/html/papers
```

---

## 数据格式

### papers_index.json

```json
[
  {
    "arxiv_id": "2603.16871",
    "title": "WorldCam: Interactive Autoregressive 3D Gaming Worlds...",
    "primary_category": "cs.CV",
    "published": "2026-03-17T17:59:56Z",
    "paper_dir": "/path/to/run-dir/2603.16871",
    "metadata_md": "/path/to/run-dir/2603.16871/metadata.md"
  }
]
```

### {date}.json（每日论文数据）

```json
{
  "push_date": "2026-03-18",
  "total_count": 40,
  "category_count": 5,
  "categories": [
    {
      "name": "cs.AI",
      "papers": [
        {
          "arxiv_id": "2603.16871",
          "title": "WorldCam...",
          "published": "2026-03-17",
          "category": "cs.CV",
          "brief": "<p>WorldCam 是...</p>",
          "link": "https://arxiv.org/abs/2603.16871",
          "details": {
            "research_goal": "<p>...</p>",
            "method": "<p>...</p>",
            "results": "<p>...</p>",
            "conclusion": "<p>...</p>"
          }
        }
      ]
    }
  ]
}
```

### reports.json（推送索引）

```json
[
  {
    "date": "2026-03-18",
    "paper_date": "2026-03-18",
    "count": 40,
    "llm_count": 8,
    "agent_count": 19,
    "data_file": "data/2026-03-18.json",
    "detail_url": "detail.html?date=2026-03-18"
  }
]
```

---

## 使用指南

### 手动触发完整流程

```bash
# 1. 检索 + AI 解读
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-18 \
  --from-date "2026-03-18" \
  --to-date "2026-03-18" \
  --language Chinese

# 2. 生成 JSON 数据
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-20260318-* \
  --push-date 2026-03-18 \
  --data-dir /etc/nginx/html/papers

# 3. 验证
ls -la /etc/nginx/html/papers/data/2026-03-18.json
cat /etc/nginx/html/papers/reports.json
```

### 访问地址

- **主页**: http://evilcalf.online/papers/
- **详情页**: http://evilcalf.online/papers/detail.html?date=2026-03-18

---

## 定时任务配置

### Crontab 配置

```bash
# 编辑 crontab
crontab -e

# 添加每日论文检索（23:00）
0 23 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh >> /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log 2>&1
```

### HEARTBEAT.md 配置

编辑 `/root/.openclaw/workspace/HEARTBEAT.md`:

```markdown
## 📚 检查论文推送任务（每天 23:30-24:00，错过时间窗口则立即执行）

**任务**: 检查并执行每日论文推送

**执行脚本**:
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py

**频率**: 每天检查 1 次（23:30-24:00 之间），错过时间窗口则发现任务立即执行
```

---

## 故障排查

### 检查论文解读质量

```bash
# 运行质量检查脚本
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/check-summary-quality.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-*
```

### 查看 Cron 日志

```bash
tail -f /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log
```

### 检查临时文件

```bash
# 查看编排器输出
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/

# 查看论文解读
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/*/papers/*/summary.md
```

### 检查网页部署

```bash
# 查看 nginx 目录
ls -la /etc/nginx/html/papers/

# 查看 reports.json
cat /etc/nginx/html/papers/reports.json

# 查看数据文件
cat /etc/nginx/html/papers/data/2026-03-18.json | python3 -m json.tool | head -50
```

---

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索到 0 篇论文 | 日期范围错误 | 检查 `--from-date` 和 `--to-date` |
| summary.md 为空 | subagent 超时 | 增加超时时间，减少并发数 |
| 网页显示英文摘要 | 格式不匹配 | 检查 summary.md 格式 |
| JSON 解析失败 | 文件未生成完成 | 等待生成完成再访问 |
| 主页不更新 | reports.json 未同步 | 检查 orchestrator-to-web.py 是否执行成功 |

---

_系统已完善，生产环境可用 - 2026-03-18 😈_
