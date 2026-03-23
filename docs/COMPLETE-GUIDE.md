# 📚 每日论文推送系统 - 完整指南 v2.2

**最后更新**: 2026-03-18  
**系统版本**: v2.2 (TeX 源码深度解读 + 数据/展示分离)

---

## 🎯 系统概述

自动检索 arXiv 论文 → 下载 TeX 源码 → AI 深度解读（10 节，8000-12000 字）→ 生成网页 → 动态展示

**核心特性**:
- 🔍 **智能检索**: 40 个关键词（LLM/Agent/Transformer/Attention 各 10 个）
- 📥 **源码下载**: 自动下载 TeX 源码，支持批量并发
- 📝 **深度解读**: 每篇论文 10 节、8000-12000 字中文解读（从 TeX 源码提取）
- 🎨 **现代 UI**: 深色渐变风格 + 粒子动画 + 侧边栏目录导航
- 📱 **响应式**: 支持桌面端和移动端
- 🔄 **自动化**: 一键生成每日推送

---

## 📁 完整目录结构

```
/root/.openclaw/workspace/projects/papers-daily/    # 项目根目录
├── README.md                                        # 快速入门指南
├── docs/                                            # 文档目录 ⭐
│   ├── COMPLETE-GUIDE.md                           # 本文档（完整指南）
│   ├── DATA-STRUCTURE.md                           # 数据结构说明
│   ├── DAILY-WORKFLOW.md                           # 每日工作流
│   └── ARCHITECTURE.md                             # 系统架构
├── scripts/                                         # 脚本目录 ⭐
│   ├── papers-orchestrator.py                      # 总编排器（Stage A/B/C）
│   ├── interpret-papers-parallel.py                # 并行 AI 解读 ⭐
│   ├── orchestrator-to-web.py                      # 网页生成器 ⭐
│   ├── simple-arxiv-search.py                      # arXiv 检索 + 源码下载
│   ├── papers-heartbeat-check.py                   # Heartbeat 检查脚本
│   ├── daily-papers-cron.sh                        # Cron 入口脚本
│   └── generate-daily.sh                           # 一键生成脚本 ⭐
├── data/                                            # 项目数据目录 ⭐ 永久保存
│   └── summaries/                                   # AI 解读数据
│       ├── 2026-03-18/                             # 按日期组织
│       │   ├── 2603.16871v1/
│       │   │   ├── metadata.md                     # 论文元数据
│       │   │   └── summary.md                      # AI 深度解读 ⭐ (10000 字)
│       │   └── ...
└── templates/                                       # 网页模板
    └── detail-with-toc.html                        # 详情页模板（带侧边栏）

/root/.openclaw/workspace/tmp/                       # 临时文件目录 ⭐ 可清理
└── papers-orchestrator/
    └── llm-ai-agent-YYYY-MM-DD/
        ├── papers_index.json                       # 论文索引（中间产物）
        └── 2603.xxxxx/                             # 每篇论文目录
            ├── metadata.md                         # 论文元数据
            └── source/                             # TeX 源码（可重新下载）
                └── source_extract/
                    ├── main.tex                    # 主 TeX 文件
                    └── ...

/etc/nginx/html/papers/                              # nginx 部署目录 ⭐
├── index.html                                       # 主页（静态）
├── detail.html                                      # 详情页模板（静态）
├── reports.json                                     # 推送索引（每日更新）⭐
└── data/                                            # 每日数据
    └── YYYY-MM-DD.json                             # 每日论文数据 ⭐
```

---

## 🔧 核心脚本说明

### 1. `simple-arxiv-search.py` - arXiv 检索 + 源码下载

**功能**: 检索 arXiv 论文 → 下载 TeX 源码

**执行**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/simple-arxiv-search.py \
  --date 2026-03-18 \
  --from-date 2026-03-17 \
  --to-date 2026-03-17 \
  --output-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18 \
  --max-results 5
```

**输出**:
- `papers_index.json` - 论文索引（29 篇）
- `2603.xxxxx/source/source_extract/*.tex` - TeX 源码

**特点**:
- ✅ 40 个关键词检索（LLM/Agent/Transformer/Attention 各 10 个）
- ✅ 自动调用 `arxiv-paper-processor` 下载 TeX 源码
- ✅ 2-3 并发下载，自动重试和限流

---

### 2. `interpret-papers-parallel.py` - 并行 AI 解读 ⭐

**功能**: 从 TeX 源码深度解读每篇论文

**执行**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/interpret-papers-parallel.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18 \
  --summaries-dir /root/.openclaw/workspace/projects/papers-daily/data/summaries/2026-03-18 \
  --max-workers 10 \
  --language Chinese
```

**输出**:
- `data/summaries/YYYY-MM-DD/2603.xxxxx/summary.md` - AI 深度解读（8000-12000 字）

**配置**:
```python
MAX_WORKERS = 10          # 最大并发数
TIMEOUT = 900             # 超时时间（15 分钟，因为解读很长）
MODEL = "qwen3.5-plus"    # 使用支持长上下文的模型
```

**解读格式**（10 节）:
1. **Paper Snapshot（元数据）** - 标题、作者、机构、arXiv ID、日期、分类、项目链接
2. **研究目标（详细）** - 核心痛点、研究问题、具体目标、应用场景
3. **方法概述（技术细节）** - 核心思想、架构设计、关键创新（含数学公式）
4. **数据和评估（完整信息）** - 数据集、评估设置、实现细节
5. **关键结果（包含具体数字）** - 对比表格、关键发现、消融实验
6. **优势（量化对比）** - 性能、效率、通用性、理论优势
7. **局限性和风险（诚实评估）** - 技术局限、实验局限、应用风险
8. **可重复性说明** - 代码、数据、预训练模型可用性
9. **实践启示** - 对研究者、工程师、行业的价值
10. **简要结论（精华总结）** - 3-4 句包含具体贡献和结果

**特点**:
- ✅ 从 TeX 源码提取真实数据（非推测）
- ✅ 包含数学公式、对比表格、具体数字
- ✅ 10 并发，每篇约 1.5-2 分钟
- ✅ 自动跳过已解读的论文

---

### 3. `orchestrator-to-web.py` - 网页生成器 ⭐

**功能**: 读取 AI 解读 → 生成 JSON 数据 + 更新索引

**执行**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18 \
  --push-date 2026-03-18 \
  --data-dir /etc/nginx/html/papers
```

**输出**:
- `/etc/nginx/html/papers/data/YYYY-MM-DD.json` - 论文详细数据（每篇 10000 字解读）
- `/etc/nginx/html/papers/reports.json` - 推送索引（自动更新）

**数据格式**:
```json
{
  "push_date": "2026-03-18",
  "total_count": 29,
  "category_count": 8,
  "categories": [
    {
      "name": "cs.CV",
      "papers": [
        {
          "arxiv_id": "2603.16871v1",
          "title": "英文标题",
          "chinese_title": "中文标题",
          "published": "2026-03-17",
          "category": "cs.CV",
          "brief": "<p>AI 生成的中文摘要（从结论提取）</p>",
          "link": "https://arxiv.org/abs/2603.16871v1",
          "details": {
            "research_goal": "<p>研究目标（HTML 格式）</p>",
            "method": "<p>方法概述（HTML 格式）</p>",
            "results": "<p>关键结果（含表格）</p>",
            "conclusion": "<p>结论（HTML 格式）</p>"
          }
        }
      ]
    }
  ]
}
```

**特点**:
- ✅ 自动从项目数据目录读取 summary.md
- ✅ 模糊匹配 section keys（支持括号内的详细说明）
- ✅ Markdown 转 HTML（支持表格、列表、加粗、斜体）
- ✅ 表格内 markdown 渲染（**加粗** → `<strong>`）

---

### 4. `generate-daily.sh` - 一键生成脚本 ⭐

**功能**: 自动查找编排器输出 → 调用网页生成器 → 完成部署

**执行**:
```bash
# 使用最新日期
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh

# 或指定日期
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh 2026-03-18
```

**自动完成**:
1. ✅ 查找最新的编排器运行目录
2. ✅ 生成 `data/YYYY-MM-DD.json`
3. ✅ 更新 `reports.json`
4. ✅ 显示访问地址

---

### 5. `papers-heartbeat-check.py` - Heartbeat 检查

**功能**: 检查 cron 是否执行，错过时间窗口则立即执行

**触发条件**:
- 每天 23:30-24:00 之间检查
- 如果 cron 失败或错过时间窗口，立即执行完整流程

**配置**: 在 `/root/.openclaw/workspace/HEARTBEAT.md` 中添加：
```markdown
## 📚 检查论文推送任务（每天 23:30-24:00，错过时间窗口则立即执行）

**任务**: 检查并执行每日论文推送

**执行脚本**:
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py

**频率**: 每天检查 1 次（23:30-24:00 之间）
```

---

## 🌐 网页架构

### 主页 (`index.html`)

**功能**: 展示最新推送和历史记录

**特性**:
- 动态读取 `reports.json`
- 显示最新推送日期和论文总数
- 历史记录列表（按日期倒序）

**访问**: http://evilcalf.online/papers/

---

### 详情页 (`detail.html`) - 带侧边栏目录 ⭐

**功能**: 显示单篇论文的详细解读

**特性**:
- 📑 **左侧固定侧边栏** - 按分类显示所有论文目录
- 🎯 **点击导航** - 点击论文标题查看完整详情
- 📝 **Markdown 渲染** - 使用 marked.js 动态渲染论文解读
- 🧭 **章节导航** - 论文详情内支持切换不同章节
- 📱 **响应式设计** - 移动端自动隐藏侧边栏
- 🎨 **深色渐变风格** - 与主页一致的视觉效果
- 🔍 **深度解读** - 每篇 8000-12000 字，包含真实数据、公式、表格

**访问**: http://evilcalf.online/papers/detail.html?date=YYYY-MM-DD

**模板位置**: `/root/.openclaw/workspace/projects/papers-daily/templates/detail-with-toc.html`

---

### 数据文件 (`data/YYYY-MM-DD.json`)

**内容**:
- 29 篇论文的完整数据
- 每篇包含：标题、分类、发布日期、简要摘要、详细解读（4 节）
- HTML 格式，可直接用 `innerHTML` 渲染

**大小**: 约 350-400KB

---

### 推送索引 (`reports.json`)

**内容**:
```json
[
  {
    "date": "2026-03-18",
    "paper_date": "2026-03-17",
    "count": 29,
    "llm_count": 3,
    "agent_count": 4,
    "data_file": "data/2026-03-18.json",
    "detail_url": "detail.html?date=2026-03-18"
  }
]
```

**用途**:
- 主页动态读取，展示历史记录
- 自动同步到 nginx 目录

---

## 🚀 每日工作流程

### 方式 1：手动执行（推荐）

```bash
# Step 1: 检索 arXiv + 下载 TeX 源码
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/simple-arxiv-search.py \
  --date 2026-03-18 --from-date 2026-03-17 --to-date 2026-03-17 \
  --output-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18

# Step 2: AI 深度解读（10 并发，约 8 分钟）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/interpret-papers-parallel.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18 \
  --summaries-dir /root/.openclaw/workspace/projects/papers-daily/data/summaries/2026-03-18 \
  --max-workers 10 --language Chinese

# Step 3: 生成网页和数据
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18 \
  --push-date 2026-03-18 --data-dir /etc/nginx/html/papers

# 或使用一键生成脚本
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh 2026-03-18
```

**访问**:
- 主页：http://evilcalf.online/papers/
- 详情：http://evilcalf.online/papers/detail.html?date=2026-03-18

---

### 方式 2：Cron 自动执行

```bash
# 编辑 crontab
crontab -e

# 添加每日论文检索（23:00）
0 23 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh >> /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log 2>&1
```

**Heartbeat 备份**（定期执行，发现未执行则立即运行）:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py
```

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 检索论文数 | 25-35 篇/天 |
| 源码下载成功率 | ~100% |
| AI 解读成功率 | ~100% |
| 平均每篇解读字数 | 8000-12000 字 |
| 解读耗时（10 并发） | ~8 分钟（29 篇） |
| 总耗时（含检索 + 下载） | ~15 分钟 |

---

## 🛠️ 故障排查

### 问题 1：找不到运行目录

```
❌ 未找到编排器输出目录
```

**解决**: 先运行检索脚本
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/simple-arxiv-search.py \
  --date 2026-03-18 --from-date 2026-03-17 --to-date 2026-03-17 \
  --output-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-18
```

---

### 问题 2：AI 解读超时

```
❌ HTTPSConnectionPool: Read timed out. (read timeout=900)
```

**解决**: 
- 增加超时时间（`TIMEOUT = 900` 秒）
- 减少并发数（`--max-workers 5`）
- 检查 API key 是否有效

---

### 问题 3：网页不显示内容

**检查浏览器控制台**:
1. 按 F12 打开开发者工具
2. 查看 Console 是否有错误
3. 检查 Network 标签页中 `data/xxx.json` 是否成功加载

**常见错误**:
- `404 Not Found`: 数据文件不存在 → 运行 `generate-daily.sh`
- `CORS error`: nginx 配置问题 → 检查 nginx 配置
- `JSON parse error`: 数据文件损坏 → 重新生成

---

### 问题 4：深度解读为空

**原因**: section key 匹配失败

**解决**: 检查 `orchestrator-to-web.py` 中的模糊匹配逻辑
```python
def find_section(sections, prefix, keywords):
    for key in sections.keys():
        if key.startswith(prefix) and any(kw in key for kw in keywords):
            return sections[key]
    return ''
```

---

## 📈 监控和维护

### 查看 Cron 日志

```bash
tail -f /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log
```

### 检查完成标记

```bash
cat /root/.openclaw/workspace/tmp/papers-done/YYYY-MM-DD.json
```

### 清理临时文件

```bash
# 清理超过 7 天的编排器输出
find /root/.openclaw/workspace/tmp/papers-orchestrator -type d -mtime +7 -exec rm -rf {} \;

# 清理临时 HTML 文件
rm -f /root/.openclaw/workspace/tmp/papers-daily-*.html

# 或使用清理脚本
bash /root/.openclaw/workspace/scripts/cleanup-papers-tmp.sh
```

---

## 🎯 快速参考

### 每日必做

```bash
# 一键生成（推荐）
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh
```

### 访问地址

- **主页**: http://evilcalf.online/papers/
- **详情**: http://evilcalf.online/papers/detail.html?date=YYYY-MM-DD

### 关键文件

| 文件 | 位置 | 用途 |
|------|------|------|
| AI 解读数据 | `projects/papers-daily/data/summaries/YYYY-MM-DD/` | 永久保存 ⭐ |
| JSON 数据 | `/etc/nginx/html/papers/data/` | 网页数据源 |
| 推送索引 | `/etc/nginx/html/papers/reports.json` | 历史记录 |
| 详情页模板 | `/etc/nginx/html/papers/detail.html` | 通用模板 |

### 关键脚本

| 脚本 | 用途 |
|------|------|
| `simple-arxiv-search.py` | 检索 + 下载 TeX 源码 |
| `interpret-papers-parallel.py` | 并行 AI 解读（10 并发）⭐ |
| `orchestrator-to-web.py` | 生成网页数据 |
| `generate-daily.sh` | 一键生成 ⭐ |

---

## 📝 版本历史

### v2.2 (2026-03-18)
- ✅ 支持从 TeX 源码深度解读（8000-12000 字）
- ✅ 自动下载 TeX 源码
- ✅ 模糊匹配 section keys（支持括号内的详细说明）
- ✅ 表格内 markdown 渲染（加粗、斜体）
- ✅ 摘要优先使用 AI 解读的结论

### v2.1 (2026-03-18)
- ✅ 数据/展示分离架构
- ✅ 项目数据永久保存
- ✅ 临时文件可清理

### v2.0 (2026-03-17)
- ✅ 侧边栏目录导航
- ✅ Markdown 渲染
- ✅ 响应式设计

---

_系统已就绪，生产环境可用 - 2026-03-18 😈_
