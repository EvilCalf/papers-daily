# 📚 每日论文推送系统 - 文档索引

**最后更新**: 2026-03-24  
**系统版本**: v2.0 (生产环境)

---

## 📋 核心文档

| 文档 | 说明 | 必读 |
|------|------|------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 系统架构、目录结构、脚本说明 | ⭐ |
| **[LESSONS-LEARNED.md](LESSONS-LEARNED.md)** | 经验教训、常见问题、SOP | ⭐ |
| **[SEARCH-CONFIG.md](SEARCH-CONFIG.md)** | 40 个检索关键词配置 | 可选 |

---

## 🌐 访问地址

- **主页**: http://evilcalf.online/papers/
- **今日论文**: http://evilcalf.online/papers/detail.html?date=2026-03-24

---

## ⏰ 定时任务

- **Cron**: 每天 10:00 执行
- **检索规则**：
  - 周一：检索前3天的论文（周五、周六、周日）
  - 周二到周五：检索前1天的论文
  - 周六周日：跳过（arXiv 周末不更新）
- **Heartbeat**: 备份检查（10:00-10:30）

---

## 🔧 快速命令

```bash
# 手动触发今日论文推送
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-heartbeat-check.py

# 查看 Cron 日志
tail -f /root/.openclaw/workspace/projects/papers-daily/logs/papers-cron.log

# 检查 Git 状态
cd /root/.openclaw/workspace/projects/papers-daily && git status
```

---

_精简版文档 - 2026-03-24_
