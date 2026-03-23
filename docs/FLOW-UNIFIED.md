# 🔄 统一流程说明 - Cron vs 手动

**最后更新**: 2026-03-18  
**状态**: ✅ 已统一

---

## 📋 核心原则

**Cron 和手动运行使用完全相同的流程！**

---

## 🎯 两种运行方式

### 方式 1：Cron 自动运行（生产环境）

**触发时间**: 每天 23:00（北京时间）

**入口脚本**: `daily-papers-cron.sh`

**执行流程**:
```
23:00 Cron 触发
    ↓
Stage A: 检索 arXiv 论文（40 关键词，15-30 篇目标）
    ↓
Stage B: AI 深度解读（10 节格式，1500-2500 字/篇）
    ↓
Stage C: 生成网页 + 同步 reports.json
    ↓
完成！网页部署到 nginx
```

**Cron 配置**:
```bash
0 23 * * * /bin/bash /root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh >> /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log 2>&1
```

---

### 方式 2：手动运行（测试/调试）

**触发时间**: 随时

**入口脚本**: `run-full-pipeline.sh`

**执行流程**:
```
手动触发
    ↓
Stage A: 检索 arXiv 论文（40 关键词，15-30 篇目标）
    ↓
质量检查：验证检索结果
    ↓
Stage B: AI 深度解读（10 节格式，1500-2500 字/篇）
    ↓
质量检查：验证 summary.md 格式
    ↓
Stage C: 生成网页 + 同步 reports.json
    ↓
完成！网页部署到 nginx
```

**手动运行命令**:
```bash
# 使用昨天日期
bash scripts/run-full-pipeline.sh 2026-03-17

# 或指定日期
bash scripts/run-full-pipeline.sh 2026-03-16
```

---

## 📊 流程对比

| 步骤 | Cron 自动 | 手动运行 | 说明 |
|------|----------|----------|------|
| Stage A | ✅ | ✅ | 完全相同 |
| 质量检查 A | ❌ | ✅ | 手动多一步检查 |
| Stage B | ✅ | ✅ | 完全相同 |
| 质量检查 B | ❌ | ✅ | 手动多一步检查 |
| Stage C | ✅ | ✅ | 完全相同 |
| 访问测试 | ❌ | ✅ | 手动多一步测试 |
| 日志输出 | 文件 | 控制台 + 文件 | 输出位置不同 |

**核心逻辑完全一致**：都调用 `papers-orchestrator.py` 和 `orchestrator-to-web.py`

---

## 🔧 脚本调用关系

```
┌─────────────────────────────────────────────────────────────┐
│                    每日论文推送系统                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  daily-papers-cron.sh│         │ run-full-pipeline.sh │
│  (Cron 自动，23:00)   │         │   (手动，随时)        │
└───────────┬──────────┘         └───────────┬──────────┘
            │                                │
            └──────────────┬─────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  papers-orchestrator.py │
              │    (总编排器)            │
              │  Stage A / B / C        │
              └───────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Stage A       │ │ Stage B       │ │ Stage C       │
│ 智能检索      │ │ AI 解读        │ │ 网页生成      │
│ arxiv-search- │ │ arxiv-paper-  │ │ orchestrator- │
│ collector     │ │ processor     │ │ to-web.py     │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 📁 关键脚本说明

### 1. daily-papers-cron.sh（Cron 入口）

**用途**: 生产环境自动运行

**特点**:
- 自动计算日期（昨天）
- 静默执行（日志输出到文件）
- 包含错误处理和退出码
- 无质量检查（依赖编排器内部验证）

**执行内容**:
```bash
# Stage A
python3 papers-orchestrator.py --stage A

# Stage B
python3 papers-orchestrator.py --stage B

# Stage C
python3 orchestrator-to-web.py
```

---

### 2. run-full-pipeline.sh（手动入口）

**用途**: 手动测试、调试、补运行

**特点**:
- 支持指定日期参数
- 日志输出到控制台 + 文件
- 包含质量检查步骤
- 包含访问测试

**执行内容**:
```bash
# Stage A
python3 papers-orchestrator.py --stage A

# 质量检查
python3 check-summary-quality.py

# Stage B
python3 papers-orchestrator.py --stage B

# 质量检查
python3 check-summary-quality.py --fix

# Stage C
python3 orchestrator-to-web.py

# 访问测试
curl http://localhost/papers/xxx.html
```

---

### 3. papers-orchestrator.py（总编排器）

**用途**: 执行 Stage A/B/C

**被调用**:
- `daily-papers-cron.sh`
- `run-full-pipeline.sh`
- `papers-heartbeat-check.py`（备份）

**Stage A**: 智能检索
- 40 个关键词
- 5 个查询计划
- 目标 15-30 篇
- 跨查询去重

**Stage B**: AI 解读
- 10 节标准格式
- 1500-2500 字/篇
- 支持并行（3 subagent × 4 篇）
- 自动跳过已解读

**Stage C**: 报告生成
- 由 `orchestrator-to-web.py` 执行
- 生成 HTML 网页
- 同步 reports.json

---

### 4. orchestrator-to-web.py（网页生成器）

**用途**: 生成 HTML 网页

**功能**:
- 读取 summary.md（10 节格式）
- 支持中英文键名
- 过滤 AI 生成标记
- 生成深色渐变风格网页
- 同步 reports.json 到 nginx

---

### 5. papers-heartbeat-check.py（备份检查）

**用途**: Cron 失败时的备份机制

**触发条件**:
- Cron 执行失败
- Cron 错过时间窗口
- 有待处理任务遗留

**执行内容**: 与 Cron 相同的完整流程

---

## 🚨 备份机制

```
┌────────────────────────────────────────────┐
│          每日论文推送 - 执行保障            │
└────────────────────────────────────────────┘

主流程：Cron (23:00) ────▶ 成功完成
                        │
                        └───▶ 失败 ────▶ Heartbeat 检查 ────▶ 执行完整流程
                                            (备份)
```

**Heartbeat 检查频率**: 建议每 30-60 分钟

**Heartbeat 触发条件**:
1. 发现 `papers-task-pending.json`（Cron 遗留）
2. 网页已生成但未推送
3. 无新论文标记

---

## 📝 日志位置

| 运行方式 | 日志文件 | 查看命令 |
|----------|----------|----------|
| Cron | `logs/papers-cron.log` | `tail -f logs/papers-cron.log` |
| 手动 | `logs/papers-run.log` | `tail -f logs/papers-run.log` |
| Heartbeat | `logs/papers-heartbeat.log` | `tail -f logs/papers-heartbeat.log` |

---

## ✅ 一致性保证

| 方面 | Cron | 手动 | 说明 |
|------|------|------|------|
| 检索关键词 | 40 个 | 40 个 | ✅ 相同 |
| 目标论文数 | 15-30 | 15-30 | ✅ 相同 |
| AI 解读格式 | 10 节 | 10 节 | ✅ 相同 |
| 网页生成 | 同脚本 | 同脚本 | ✅ 相同 |
| 输出目录 | 同位置 | 同位置 | ✅ 相同 |
| 错误处理 | 有 | 有 | ✅ 相同 |

**唯一区别**: 手动运行多了质量检查步骤（推荐）

---

## 🎯 推荐使用方式

### 生产环境
- **Cron 自动运行**（每天 23:00）
- Heartbeat 作为备份

### 测试/调试
- **手动运行**（带质量检查）
- 可以指定日期重跑

### 补运行
- **手动运行**（指定遗漏的日期）
- 或等待 Heartbeat 自动执行

---

## 📞 故障排查

### Cron 执行失败

```bash
# 1. 查看 Cron 日志
tail -100 logs/papers-cron.log

# 2. 手动运行测试
bash scripts/run-full-pipeline.sh 2026-03-17

# 3. 检查 Cron 配置
crontab -l | grep papers
```

### Heartbeat 未触发

```bash
# 1. 检查是否有待处理任务
ls -la tmp/papers-task-pending.json

# 2. 手动触发 Heartbeat
python3 scripts/papers-heartbeat-check.py

# 3. 检查 Heartbeat 配置
# （通常在 HEARTBEAT.md 或 crontab 中配置）
```

---

_统一流程文档 - 2026-03-18 创建_
