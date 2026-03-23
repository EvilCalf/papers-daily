# 📚 每日论文推送系统 - 文档索引

**最后更新**: 2026-03-18  
**系统版本**: v2.0 (arxiv-summarizer-orchestrator)

---

## 📋 核心文档

- **[INTEGRATION.md](INTEGRATION.md)** - 集成指南（必读）
  - 新技能对比和优势
  - 集成策略和迁移步骤

- **[LESSONS-LEARNED.md](LESSONS-LEARNED.md)** - 经验教训总结 ⭐
  - 核心问题与解决方案
  - 标准操作流程（SOP）
  - 常见错误与排查
  - 性能对比和推荐配置

- **[FLOW-UNIFIED.md](FLOW-UNIFIED.md)** - 统一流程说明 ⭐
  - Cron vs 手动运行对比
  - 脚本调用关系
  - 备份机制说明

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完整架构文档
  - 系统概述和链路
  - 目录结构
  - 脚本说明

---

## 🔧 脚本说明

### 新系统脚本

| 脚本 | 功能 |
|------|------|
| `papers-orchestrator.py` | 总编排器（Stage A/B/C） |
| `orchestrator-to-web.py` | 生成网页（深度解读格式） |
| `papers-heartbeat-check.py` | Heartbeat 检查（推送触发） |

### 依赖技能

- `arxiv-summarizer-orchestrator` - 总编排
- `arxiv-search-collector` - 智能检索
- `arxiv-paper-processor` - 下载 + 解读
- `arxiv-batch-reporter` - 报告生成

---

## 🌐 访问地址

- **主页**: http://evilcalf.online/papers/
- **今日论文**: http://evilcalf.online/papers/2026-03-18.html

---

## 📅 推送时间

- **检索**: 每天 23:00
- **推送**: 每天 23:30

---

_系统已升级到 arxiv-summarizer-orchestrator，旧文档已归档_
