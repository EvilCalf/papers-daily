# 🔄 论文推送系统集成指南

**创建时间**: 2026-03-18  
**集成技能**: arxiv-summarizer-orchestrator (v0.1.1)

---

## 📦 已安装技能

| 技能 | 版本 | 功能 |
|------|------|------|
| `arxiv-summarizer-orchestrator` | 0.1.1 | 总编排器 |
| `arxiv-search-collector` | 0.1.1 | Stage A: 智能检索 |
| `arxiv-paper-processor` | 0.1.1 | Stage B: 并行解读 |
| `arxiv-batch-reporter` | 0.1.1 | Stage C: 报告生成 |

---

## 🎯 集成策略

**保留现有架构** (cron + heartbeat + 网页推送)，**替换核心处理模块**：

```
现有脚本                          新技能
─────────────────────────────────────────────
arxiv-retriever.py       →   arxiv-search-collector
                           (多查询迭代 + 模型过滤)

batch-interpret.py       →   arxiv-paper-processor
                           (源码优先 + 5 篇并行)

arxiv-aggregator.py      →   保留 (已升级 UI 风格)
                           (深色渐变 + 粒子动画)

papers-heartbeat-check.py → 保留 (调度逻辑不变)
```

---

## 📊 对比优势

### Stage A: 检索

| 维度 | 旧系统 | 新技能 | 提升 |
|------|--------|--------|------|
| 检索策略 | 固定 2 关键词 | AI 生成 3-4 查询 | ✅ 覆盖率 ↑ |
| 查询优化 | 无 | 同义词 OR + 跨组 AND | ✅ 相关性 ↑ |
| 去重逻辑 | 简单标题去重 | 跨查询去重 + 模型过滤 | ✅ 质量 ↑ |
| API 限流 | 无 | 自动重试/退避 | ✅ 稳定性 ↑ |

### Stage B: 解读

| 维度 | 旧系统 | 新技能 | 提升 |
|------|--------|--------|------|
| 输入源 | PDF 前 10 页 | 完整源码 (TeX) 或 PDF | ✅ 信息量 ↑ |
| 解读深度 | 800-1000 字 5 段式 | 10 节标准格式 | ✅ 结构化 ↑ |
| 并行策略 | 串行 (3 秒间隔) | 最多 5 篇并行 | ⚡ 速度 ↑ 5x |
| 缓存复用 | ❌ 每次都重做 | ✅ 跳过已完成 | ✅ 效率 ↑ |

### Stage C: 报告

| 维度 | 旧系统 | 新技能 |
|------|--------|--------|
| 网页风格 | 浅色紫渐变 | 深色渐变 + 粒子动画 ✨ |
| 结论来源 | AI 解读字段 | summary.md 第 10 节 |
| 输出格式 | HTML+JSON | Markdown → HTML |

---

## 🚀 使用方法

### 方案 A: 使用新编排器 (推荐测试)

```bash
# 完整流程
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-17 \
  --push-date 2026-03-18 \
  --language Chinese

# 分阶段执行
python3 papers-orchestrator.py --date 2026-03-17 --stage A  # 只检索
python3 papers-orchestrator.py --date 2026-03-17 --stage B  # 只解读
python3 papers-orchestrator.py --date 2026-03-17 --stage C  # 只报告
```

### 方案 B: 保留现有系统 (生产环境)

```bash
# Cron 检索 (每天 23:00)
bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh

# Heartbeat 检查 (定期)
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py
```

---

## 📁 输出目录结构

### 新技能输出

```
/root/.openclaw/workspace/tmp/papers-orchestrator/
└── llm-agent-{date}-{push-date}/
    ├── task_meta.json
    ├── task_meta.md
    ├── query_plan.json
    ├── query_results/
    │   ├── llm-core.json
    │   ├── llm-core.md
    │   ├── agent-apps.json
    │   └── agent-apps.md
    ├── query_selection/
    │   └── selected_by_query.json
    ├── papers_index.json
    ├── papers_index.md
    ├── <arxiv_id>/
    │   ├── metadata.md
    │   ├── source/
    │   │   ├── source_bundle.bin
    │   │   ├── source_extract/  (TeX 源码)
    │   │   └── paper.pdf
    │   └── summary.md  (AI 解读)
    ├── summaries_bundle.md
    ├── collection_report_template.md
    └── collection_report.md
```

### 现有系统输出

```
/root/.openclaw/workspace/tmp/
├── papers-list-{date}.json
├── papers-pdf-{date}/
│   └── <paper_id>.pdf
├── papers-task-pending.json
├── papers-summaries-{date}/
│   └── paper-<arxiv_id>.json
└── papers-done/{date}.json
```

---

## 🎨 网页风格升级

### 新风格特点

- **深色渐变背景**: `#0f0c29 → #302b63 → #24243e → #1a1a2e`
- **粒子动画**: 10 个浮动粒子，不同颜色和延迟
- **毛玻璃卡片**: `backdrop-filter: blur(10px)`
- **渐变色文字**: `#fff → var(--glow) → var(--accent)`
- **统一配色**:
  - `--primary: #a855f7` (紫色)
  - `--secondary: #6366f1` (靛蓝)
  - `--accent: #ec4899` (粉色)
  - `--glow: #c084fc` (亮紫)

### 与主页一致性

✅ 背景渐变动画  
✅ 粒子浮动效果  
✅ 毛玻璃卡片边框  
✅ 渐变色标题  
✅ 悬停动画效果  

---

## 🔧 迁移步骤

### 阶段 1: 并行测试 (推荐)

1. **保持现有系统运行** (cron + heartbeat)
2. **手动测试新编排器** 1-2 次
3. **对比检索质量** (论文数量、相关性)
4. **对比解读质量** (深度、结构化程度)
5. **对比处理时间** (串行 vs 并行)

### 阶段 2: 逐步替换

1. **替换检索模块**: 用 `arxiv-search-collector` 替换 `arxiv-retriever.py`
2. **替换解读模块**: 用 `arxiv-paper-processor` 替换 `batch-interpret.py`
3. **保留调度逻辑**: `papers-heartbeat-check.py` 不变
4. **保留网页生成**: `arxiv-aggregator.py` (已升级 UI)

### 阶段 3: 完全切换

1. **更新 cron 脚本**: 调用新编排器
2. **更新 heartbeat**: 适配新输出格式
3. **清理旧脚本**: 备份后删除

---

## ⚠️ 注意事项

### API 限流

- arXiv API 限制：每 3 秒 1 次请求
- 新技能已内置重试/退避机制
- 首次运行建议观察 API 调用频率

### 磁盘空间

- 新技能会下载 TeX 源码 (每篇 ~100KB-1MB)
- PDF 文件 (每篇 ~500KB-5MB)
- 建议定期清理 `tmp/papers-orchestrator/`

### 模型调用

- Stage B 解读需要调用 `openclaw agent --agent main`
- 每篇论文约 180 秒超时
- 并行模式 (5 篇) 需注意并发限制

---

## 📝 待办事项

### P0（必须）

- [ ] 测试新编排器完整流程
- [ ] 对比检索质量 (新旧系统)
- [ ] 验证网页风格一致性

### P1（重要）

- [ ] 适配 heartbeat 检查脚本到新格式
- [ ] 添加错误重试机制
- [ ] 添加日志记录

### P2（可选）

- [ ] 实现增量检索 (跳过已处理论文)
- [ ] 添加推送历史统计
- [ ] 优化并行策略 (根据论文数量动态调整)

---

## 🔗 相关文档

- **编排器脚本**: `/root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py`
- **网页生成器**: `/root/.openclaw/workspace/projects/papers-daily/scripts/arxiv-aggregator.py`
- **技能目录**: `/root/.openclaw/workspace/skills/arxiv-summarizer-orchestrator/`
- **现有系统**: `/root/.openclaw/workspace/projects/papers-daily/README.md`

---

_集成完成！准备测试新系统～ 😈_
