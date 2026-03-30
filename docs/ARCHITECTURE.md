# 📚 每日论文推送系统 - 完整架构文档

**最后更新**: 2026-03-31  
**系统版本**: v2.1 (时区修复版)  
**文档状态**: ✅ 生产环境

---

## 🎯 系统概述

自动检索 arXiv 论文 → AI 深度解读 → 网页生成 → 动态主页展示

---

## 🔄 完整链路

```
┌─────────────────────────────────────────────────────────────────────┐
│                        每日论文推送系统 v2.0                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Cron 触发  │───▶│  2. 检索论文  │───▶│  3. AI 解读   │───▶│  4. 生成网页  │
│  每天 10:00   │    │  arXiv API  │    │  10 节格式   │    │  HTML+JSON   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
                                                                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  7. 清理临时  │◀───│  6. 用户访问  │◀───│  5. 同步数据  │◀───│  4. 部署网页  │
│  >24 小时文件 │    │  主页/详情页 │    │  reports.json │    │  nginx 目录  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 📁 目录结构

```
/root/.openclaw/workspace/
├── projects/papers-daily/           # 项目根目录
│   ├── README.md                    # 快速开始指南
│   ├── docs/
│   │   ├── INDEX.md                 # 文档索引
│   │   ├── INTEGRATION.md           # 集成指南
│   │   └── ARCHITECTURE.md          # 本文档（完整架构）
│   ├── scripts/
│   │   ├── papers-orchestrator.py   # 总编排器（Stage A/B/C）
│   │   ├── orchestrator-to-web.py   # 网页生成器 ⭐
│   │   ├── papers-heartbeat-check.py # Heartbeat 检查
│   │   ├── daily-papers-cron.sh     # Cron 入口脚本
│   │   └── arxiv-aggregator.py      # 报告聚合器
│   └── logs/
│       └── papers-cron.log          # Cron 日志
│
├── tmp/                             # 临时文件（统一存放）
│   ├── papers-orchestrator/         # 编排器输出
│   │   └── llm-and-ai-agent-{date}/
│   │       ├── papers_index.json    # 论文索引
│   │       ├── papers/
│   │       │   └── <arxiv_id>/
│   │       │       ├── metadata.md  # 元数据
│   │       │       └── summary.md   # AI 解读 ⭐
│   │       └── summaries_bundle.md  # 解读汇总
│   ├── papers-daily-{date}.html     # 生成的网页
│   ├── reports.json                 # 推送索引 ⭐
│   └── papers-done/                 # 完成标记
│
└── skills/
    ├── arxiv-summarizer-orchestrator/  # 编排技能
    ├── arxiv-search-collector/         # 检索技能
    ├── arxiv-paper-processor/          # 解读技能
    └── arxiv-batch-reporter/           # 报告技能

/etc/nginx/html/papers/              # 网页部署目录
├── index.html                       # 主页（动态读取）
├── reports.json                     # 推送索引 ⭐
└── {date}.html                      # 每日详情页
```

---

## 🔧 核心脚本说明

### 1. daily-papers-cron.sh（Cron 入口）

**执行时间**: 每天 10:00  
**功能**: 检索 arXiv 论文 + 下载 PDF/TeX

**检索规则**：
- 周一：检索上周五的论文（arXiv 周末不更新，周五是最近的发布日）
- 周二到周五：检索 1 天（昨天）
- 周六周日：跳过

```bash
#!/bin/bash
# 调用编排器执行
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date $(date +%Y-%m-%d) \
  --from-date $FROM_DATE \
  --to-date $TO_DATE \
  --lookback $LOOKBACK \
  --language Chinese
```

**输出**:
- `tmp/papers-orchestrator/llm-and-ai-agent-{date}/papers_index.json`
- `tmp/papers-orchestrator/llm-and-ai-agent-{date}/papers/<arxiv_id>/metadata.md`
- `tmp/papers-orchestrator/llm-and-ai-agent-{date}/papers/<arxiv_id>/source/` (PDF/TeX)

---

### 2. papers-orchestrator.py（总编排器）

**三阶段流程**:

#### Stage A: 智能检索
- 使用 `arxiv-search-collector` 技能
- AI 生成 3-4 个查询词（LLM、Agent 等）
- 跨查询去重 + 模型过滤
- 输出 `papers_index.json`

#### Stage B: AI 深度解读
- 使用 `arxiv-paper-processor` 技能
- 优先读取 TeX 源码，回退到 PDF
- 每篇论文生成 10 节中文解读（2000-3000 字）
- 并行处理（最多 5 篇同时）
- 输出 `papers/<arxiv_id>/summary.md`

#### Stage C: 报告生成
- 使用 `arxiv-batch-reporter` 技能
- 聚合所有 `summary.md`
- 生成 `summaries_bundle.md`

---

### 3. orchestrator-to-web.py（网页生成器）⭐

**功能**: 读取 AI 解读 → 生成 HTML 网页 → 同步 reports.json

**关键修正**（2026-03-18）:
1. ✅ 支持 `paper_dir` 字段（正确路径）
2. ✅ 支持中英文字段名映射（metadata.md）
3. ✅ 支持多种 summary.md 键名格式
4. ✅ 从 summary.md 读取中文标题
5. ✅ 自动同步 `reports.json` 到 nginx 目录

**使用方法**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-and-ai-agent-{date} \
  --push-date 2026-03-18 \
  --output-html /root/.openclaw/workspace/tmp/papers-daily-2026-03-18.html
```

**输出**:
- `/root/.openclaw/workspace/tmp/papers-daily-{date}.html`
- `/root/.openclaw/workspace/tmp/reports.json`
- `/etc/nginx/html/papers/reports.json`（自动同步）⭐

---

### 4. papers-heartbeat-check.py（Heartbeat 检查）

**执行时间**: 定期（错过时间窗口则立即执行）  
**功能**: 检查并执行推送流程

**三种场景**:
- **场景 A**: 有待处理任务 → 执行完整流程（解读→网页→推送）
- **场景 B**: 网页已生成但未推送 → 直接发送推送
- **场景 C**: 无新论文标记 → 生成"无新论文"推送

---

## 🌐 网页架构

### 主页（index.html）

**数据源**: `./reports.json`（动态 fetch）

**展示内容**:
- 最新推送卡片（日期、论文数、LLM/Agent 数量）
- 历史记录网格（所有推送日期）

**关键代码**:
```javascript
const response = await fetch('./reports.json');
const reports = await response.json();
// 渲染最新推送和历史记录
```

---

### 详情页（{date}.html）

**数据源**: 生成时嵌入 HTML

**展示内容**:
- 头部统计（论文总数、研究方向数）
- 分类展示（按 arXiv 分类分组）
- 论文卡片（标题、日期、分类、摘要、展开解读）

**分类映射**:
```python
category_map = {
    'cs.AI': ('AI 基础', '人工智能基础研究'),
    'cs.CL': ('NLP 与对话', '自然语言处理'),
    'cs.LG': ('机器学习', '机器学习方法'),
    'cs.SE': ('软件工程', '软件与代码'),
    'cs.HC': ('人机交互', '人机交互'),
    'cs.CR': ('安全', '安全与隐私'),
}
```

---

## 📊 AI 解读格式（10 节）

每篇论文的 `summary.md` 包含：

```markdown
# {论文标题} - AI 论文解读

## 1. Paper Snapshot（元数据）
- arXiv ID、标题、类别、发布日期、核心问题

## 2. 研究目标
解决什么问题

## 3. 方法概述
核心技术方案

## 4. 数据和评估
实验设置、数据集、评估指标

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

**字数要求**: 2000-3000 字/篇

---

## ⏰ 定时任务配置

### Crontab 配置

```bash
# 每日论文检索（10:00）
0 10 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh >> /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log 2>&1
```

### HEARTBEAT.md 配置

```markdown
## 📚 检查论文推送任务（每天 10:00-10:30，错过时间窗口则立即执行）

**任务**: 检查并执行每日论文推送

**执行脚本**:
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py

**频率**: 每天检查 1 次（10:00-10:30 之间），错过时间窗口则发现任务立即执行
```

### 临时文件清理

```bash
# HEARTBEAT 每次执行时检查
bash /root/.openclaw/workspace/scripts/cleanup-tmp.sh
```

---

## 🔍 数据流详解

### 检索阶段（Stage A）

```
arxiv-search-collector
    ├── 生成查询计划（3-4 个查询词）
    ├── 执行 arXiv API 搜索
    ├── 跨查询去重
    ├── 模型过滤（相关性评分）
    └── 输出 papers_index.json
```

### 解读阶段（Stage B）

```
arxiv-paper-processor (每篇论文)
    ├── 读取 metadata.md
    ├── 下载 TeX 源码（优先）或 PDF
    ├── 模型阅读全文
    ├── 撰写 10 节中文解读
    └── 输出 summary.md
```

### 网页生成阶段

```
orchestrator-to-web.py
    ├── 读取 papers_index.json
    ├── 读取每篇 summary.md
    ├── 解析中文字段（标题、摘要等）
    ├── 生成 HTML（深色渐变风格）
    ├── 更新 reports.json
    └── 同步 reports.json 到 nginx ⭐
```

### 主页访问流程

```
用户访问 http://evilcalf.online/papers/
    ├── nginx 返回 index.html
    ├── JS fetch('./reports.json')
    ├── 解析 JSON 数据
    ├── 渲染最新推送卡片
    └── 渲染历史记录网格
```

---

## 🛠️ 故障排查

### 检查 Cron 日志

```bash
tail -f /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log
```

### 查看临时文件

```bash
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/
ls -la /root/.openclaw/workspace/tmp/papers-*/
```

### 检查 nginx 目录

```bash
ls -la /etc/nginx/html/papers/
cat /etc/nginx/html/papers/reports.json
```

### 手动触发完整流程

```bash
# 1. 检索
python3 scripts/papers-orchestrator.py --date 2026-03-18 --language Chinese

# 2. 生成网页
python3 scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-and-ai-agent-{date} \
  --push-date 2026-03-18 \
  --output-html /root/.openclaw/workspace/tmp/papers-daily-2026-03-18.html

# 3. 检查网页
cat /etc/nginx/html/papers/reports.json
```

---

## 📝 关键修正记录（2026-03-18）

### 问题 1: 网页路径错误
**现象**: 脚本找不到 summary.md  
**原因**: 路径拼接错误（`run_dir/arxiv_id` vs `run_dir/papers/arxiv_id`）  
**修复**: 优先使用 `paper_dir` 字段

### 问题 2: 字段名不匹配
**现象**: 分类标题、发布时间为空  
**原因**: metadata.md 是英文字段，脚本期望中文  
**修复**: 添加字段名映射（Published→发布时间等）

### 问题 3: 中文标题缺失
**现象**: 论文标题只有英文  
**原因**: 脚本从 metadata.md 读取，但中文标题在 summary.md  
**修复**: 从 summary.md 的 Paper Snapshot 读取中文标题

### 问题 4: 时间范围显示
**现象**: 主页显示空的"时间范围"框  
**原因**: date_range 变量为空  
**修复**: 移除时间范围统计项

### 问题 5: 主页数据静态
**现象**: 主页不显示最新推送  
**原因**: reports.json 在 tmp 目录，nginx 访问不到  
**修复**: 脚本自动同步 reports.json 到 nginx 目录

---

## 🚀 访问地址

- **主页（动态数据）**: http://evilcalf.online/papers/
- **今日论文**: http://evilcalf.online/papers/detail.html?date=2026-03-18
- **历史论文**: http://evilcalf.online/papers/{date}.html

---

## 📋 待办事项

### P0（已完成）✅
- [x] 修正网页生成路径问题
- [x] 修正字段名映射
- [x] 添加中文标题读取
- [x] 同步 reports.json 到 nginx
- [x] 移除空时间范围显示

### P1（优化）
- [ ] 添加错误重试机制
- [ ] 添加详细日志记录
- [ ] 优化并行策略

### P2（增强）
- [ ] 实现增量检索
- [ ] 添加推送统计
- [ ] 支持多语言切换

---

_完整架构文档 - 2026-03-18 修正版_
