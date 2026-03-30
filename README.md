# 📚 每日论文推送系统 v2.1（数据/展示分离版）

**自动检索 arXiv 论文 + AI 深度解读 + JSON 数据生成 + 动态网页展示**

_最后更新：2026-03-31 | 系统状态：✅ 生产环境_

---

## 🎯 核心功能

1. **智能检索**: 40 个关键词（LLM/Agent/Transformer/Attention 各 10 个）+ 跨查询去重 + 模型过滤
2. **深度解读**: 基于全文（TeX 源码）的 10 节学术格式解读（2000-3000 字/篇）
3. **网页生成**: 深色渐变风格 + 粒子动画 + 可展开详情
4. **动态主页**: JS 动态读取 `reports.json` 展示最新推送和历史记录
5. **自动推送**: 每天 10:00 检索论文（周一检索上周五的论文，周二到周五检索前一天的论文，周末跳过），heartbeat 备份检查（cron + heartbeat 双保险）
6. **无论文处理**: 搜不到时生成"今天没论文"空页面（有 UI 有样式）

---

## 🌐 访问地址

- **主页（动态数据）**: http://evilcalf.online/papers/
- **今日论文**: http://evilcalf.online/papers/detail.html?date=2026-03-27
- **历史论文**: http://evilcalf.online/papers/detail.html?date=YYYY-MM-DD

---

## 🔄 完整链路

```
Cron 触发 (10:00) → 检索 arXiv → AI 解读 (10 节) → 生成网页 → 同步 reports.json → 用户访问主页
```

**详细说明**: 见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🚀 快速开始

### 手动触发完整流程

```bash
# 步骤 1: 检索 + AI 解读（编排器）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-27 \
  --from-date "2026-03-26" \
  --to-date "2026-03-26" \
  --language Chinese

# 步骤 2: 生成 JSON 数据 + 同步索引
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh 2026-03-27
```

### 自动触发（生产环境）

```bash
# Cron 完整流程（每天 10:00）
# 执行：Stage A 检索 → Stage B 解读 → Stage C 网页生成
0 10 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh

# Heartbeat 备份检查（定期）
# 只在 cron 失败或错过时间窗口时执行
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py
```

**注意**：Cron 和 Heartbeat 使用相同的完整流程（Stage A+B+C），确保一致性。

---

## 🔧 故障排查

### 检查论文解读质量

```bash
# 运行质量检查脚本
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/check-summary-quality.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-xxx
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索到 0 篇论文 | 日期范围错误 | 检查 `--from-date` 和 `--to-date` |
| summary.md 被污染 | gateway 超时 | 降低并发，重新生成 |
| 网页显示英文摘要 | 格式不匹配 | 更新 `orchestrator-to-web.py` |
| 展开后内容为空 | 章节名不匹配 | 检查 summary.md 格式 |

**详细经验教训**: 见 [docs/LESSONS-LEARNED.md](docs/LESSONS-LEARNED.md)

---

## 📁 目录结构

```
papers-daily/
├── README.md                        # 本文档
├── docs/
│   ├── INDEX.md                     # 文档索引
│   ├── INTEGRATION.md               # 集成指南
│   └── ARCHITECTURE.md              # 完整架构（必读）⭐
├── scripts/
│   ├── papers-orchestrator.py       # 总编排器（Stage A/B/C）
│   ├── orchestrator-to-web.py       # 网页生成器 ⭐
│   ├── papers-heartbeat-check.py    # Heartbeat 检查
│   ├── daily-papers-cron.sh         # Cron 入口
│   └── arxiv-aggregator.py          # 报告聚合器
└── logs/
    └── papers-cron.log              # Cron 日志
```

**临时文件**（统一存放）:
```
/root/.openclaw/workspace/tmp/
├── papers-orchestrator/             # 编排器输出
│   └── llm-and-ai-agent-{date}/
│       ├── papers_index.json        # 论文索引
│       └── <arxiv_id>/              # 论文目录（直接在 RUN_DIR 下）
│           ├── metadata.md          # 元数据
│           └── summary.md           # AI 解读 ⭐
└── papers-done/
    └── {date}.json                 # 完成标记
```

**网页部署**（v2.1 数据/展示分离）:
```
/etc/nginx/html/papers/
├── index.html                       # 主页（静态，JS 动态读取数据）
├── detail.html                      # 详情页模板（静态，通用所有日期）
├── reports.json                     # 推送索引（自动同步）⭐
└── data/
    └── {date}.json                  # 每日论文数据（JSON 格式）
```

---

## 📊 AI 解读格式

每篇论文包含 **10 节深度解读**（约 2000-3000 字）：

| 章节 | 内容 |
|------|------|
| 1. Paper Snapshot | 元数据（arXiv ID、标题、类别、日期） |
| 2. 研究目标 | 解决什么问题 |
| 3. 方法概述 | 核心技术方案 |
| 4. 数据和评估 | 实验设置、数据集、评估指标 |
| 5. 关键结果 | 具体数字和发现 |
| 6. 优势 | 相比之前方法的优势 |
| 7. 局限性和风险 | 诚实评估不足之处 |
| 8. 可重复性说明 | 代码/数据可用性 |
| 9. 实践启示 | 对从业者的价值 |
| 10. 简要结论 | 3-4 句精华总结 |

**示例**:
```markdown
# Efficient Reasoning on the Edge - AI 论文解读

## 1. Paper Snapshot（元数据）
- **arXiv ID:** 2603.16867
- **标题:** Efficient Reasoning on the Edge（边缘端高效推理）
- **类别:** cs.LG（机器学习）
- **发布日期:** 2026-03-17

## 2. 研究目标
解决大型语言模型在边缘设备（如手机）上部署的核心挑战...

## 10. 简要结论
这篇论文提出了...（3-4 句精华）
```

---

## 🔧 依赖技能

| 技能 | 功能 |
|------|------|
| `arxiv-summarizer-orchestrator` | 总编排器（Stage A/B/C） |
| `arxiv-search-collector` | Stage A: 智能检索（40 关键词×4 类） |
| `arxiv-paper-processor` | Stage B: 并行解读 |
| `arxiv-batch-reporter` | Stage C: 报告生成 |

**检索词配置**: 见 [docs/SEARCH-CONFIG.md](docs/SEARCH-CONFIG.md) 📋

---

## ⏰ 定时任务

### Crontab 配置

```bash
# 查看当前配置
crontab -l

# 添加每日论文检索（10:00）
0 10 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh >> /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log 2>&1
```

### HEARTBEAT.md 配置

编辑 `/root/.openclaw/workspace/HEARTBEAT.md`:

```markdown
## 📚 检查论文推送任务（每天 10:00-10:30，错过时间窗口则立即执行）

**任务**: 检查并执行每日论文推送

**执行脚本**:
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py

**频率**: 每天检查 1 次（10:00-10:30 之间），错过时间窗口则发现任务立即执行
```

---

## 🛠️ 故障排查

### 查看 Cron 日志

```bash
tail -f /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log
```

### 检查临时文件

```bash
# 查看编排器输出
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/

# 查看论文解读
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/llm-and-ai-agent-*/papers/*/summary.md
```

### 检查网页部署

```bash
# 查看 nginx 目录
ls -la /etc/nginx/html/papers/

# 查看 reports.json
cat /etc/nginx/html/papers/reports.json
```

### 手动触发推送

```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py
```

---

## 📝 关键修正记录（2026-03-18）

| 问题 | 现象 | 修复 |
|------|------|------|
| 路径错误 | 找不到 summary.md | 优先使用 `paper_dir` 字段 |
| 字段名不匹配 | 分类/时间为空 | 添加中英文字段映射 |
| 中文标题缺失 | 只有英文标题 | 从 summary.md 读取中文标题 |
| 时间范围显示 | 空框 | 移除该统计项 |
| 主页数据静态 | 不更新 | 自动同步 reports.json 到 nginx |

**详细修复**: 见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 📋

---

## 📋 配置说明

### 时间范围规则

| 星期 | 检索范围 | 说明 |
|------|----------|------|
| 周一 | 3天（周五、周六、周日） | 周末不推送，三天论文合并到周一 |
| 周二-周五 | 1天（前一天） | 工作日每天检索前一天的论文 |
| 周六-周日 | 跳过 | arXiv 周末不更新论文 |

### 手动指定时间范围

```bash
# 检索 1 天
--from-date "2026-03-26" --to-date "2026-03-26"

# 检索 3 天
--from-date "2026-03-24" --to-date "2026-03-26" --lookback "3d"

# 检索 1 周
--lookback "7d"
```

### 语言

```bash
--language Chinese  # 中文解读（默认）
--language English  # 英文解读
```

---

## 🔗 相关文档

- **完整架构**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ⭐
- **集成指南**: [docs/INTEGRATION.md](docs/INTEGRATION.md)
- **文档索引**: [docs/INDEX.md](docs/INDEX.md)

---

_系统已修正完成，生产环境可用 - 2026-03-18 😈_
