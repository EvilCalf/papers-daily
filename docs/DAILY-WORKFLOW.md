# 📚 每日论文推送工作流

**目标**：每天只需运行一个命令，自动生成论文推送网页。

---

## 🚀 快速开始

### 方式 1：一键生成（推荐）

```bash
# 使用最新日期（今天）
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh

# 或指定日期
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh 2026-03-18
```

**自动完成**：
1. 查找最新的编排器运行目录
2. 生成 JSON 数据文件
3. 更新 reports.json 索引
4. 生成 detail.html 详情页（带侧边栏目录）

**访问地址**：
- 主页：http://evilcalf.online/papers/
- 详情：http://evilcalf.online/papers/detail.html?date=2026-03-18

---

## 📋 完整流程

### Step 1: 运行编排器（检索 + AI 解读）

```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-18 \
  --lookback 1d \
  --language Chinese
```

**输出**：
- `/root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-xxx/papers_index.json`
- `/root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-xxx/2603.*/summary.md`（每篇论文的 AI 解读）

### Step 2: 生成网页和数据

```bash
bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh 2026-03-18
```

**输出**：
- `/etc/nginx/html/papers/data/2026-03-18.json`（论文详细数据）
- `/etc/nginx/html/papers/reports.json`（推送索引）
- `/etc/nginx/html/papers/detail.html`（详情页模板，通用）

---

## 📁 目录结构

```
/etc/nginx/html/papers/           # nginx 部署目录
├── index.html                    # 主页（静态，不需要每天生成）
├── detail.html                   # 详情页模板（静态，不需要每天生成）
├── reports.json                  # 推送索引（每天更新）⭐
└── data/
    └── 2026-03-18.json          # 每日论文数据（每天生成）⭐

/root/.openclaw/workspace/tmp/papers-orchestrator/  # 编排器输出
└── llm-ai-agent-xxx/
    ├── papers_index.json
    └── 2603.*/
        ├── metadata.md
        └── summary.md
```

---

## ✅ 每日任务清单

**只需要做**：
1. 运行编排器（Step 1）
2. 运行生成脚本（Step 2）

**不需要做**：
- ❌ 修改 detail.html 模板（已通用化）
- ❌ 修改 index.html 主页（已通用化）
- ❌ 手动复制文件（脚本自动完成）
- ❌ 手动更新 reports.json（脚本自动完成）

---

## 🔧 故障排查

### 问题 1：找不到运行目录

```
❌ 未找到包含日期 2026-03-18 的编排器运行目录
```

**解决**：先运行编排器生成数据
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-18 --lookback 1d --language Chinese
```

### 问题 2：数据文件为空

**检查**：
```bash
# 查看编排器输出
ls -la /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-*/

# 查看 summary.md 数量
find /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-*/ -name "summary.md" | wc -l
```

### 问题 3：网页不显示内容

**检查浏览器控制台**：
- 按 F12 打开开发者工具
- 查看 Console 是否有错误
- 检查 Network 标签页中 data/xxx.json 是否成功加载

---

## 📊 自动化建议

### Cron 自动运行（可选）

```bash
# 每天 23:00 运行编排器
0 23 * * * python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py --date $(date -d tomorrow +%Y-%m-%d) --lookback 1d --language Chinese

# 每天 23:30 生成网页
30 23 * * * bash /root/.openclaw/workspace/projects/papers-daily/scripts/generate-daily.sh $(date -d tomorrow +%Y-%m-%d)
```

### Heartbeat 检查（可选）

编辑 `/root/.openclaw/workspace/HEARTBEAT.md`：

```markdown
## 📚 检查论文推送任务

**任务**: 检查并执行每日论文推送

**执行脚本**:
```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py
```

**频率**: 每天检查 1 次（23:30-24:00 之间）
```

---

_最后更新：2026-03-18 😈_
