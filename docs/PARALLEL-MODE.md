# 并行解读模式 - 快速 AI 解读论文

**最后更新**: 2026-03-18

---

## 🚀 性能对比

| 模式 | 并发数 | 40 篇耗时 | 超时风险 |
|------|--------|----------|----------|
| 旧 subagent 模式 | 5 | ~25 分钟 | 高（容易超时） |
| **新 API 并行模式** | **10** | **~5 分钟** | **低（独立超时）** |
| 新 API 并行模式（高配） | 20 | ~3 分钟 | 低 |

---

## 📋 使用方式

### 1. 配置 API Key

**方式 A: 环境变量**
```bash
export DASHSCOPE_API_KEY="sk-xxxxx"
```

**方式 B: 配置文件**
```json
// ~/.openclaw/config.json
{
  "models": {
    "dashscope": {
      "apiKey": "sk-xxxxx"
    }
  }
}
```

### 2. 手动触发

```bash
# 使用默认 10 并发
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/interpret-papers-parallel.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-20260318-*

# 使用 20 并发（更快）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/interpret-papers-parallel.py \
  --run-dir /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-20260318-* \
  --max-workers 20
```

### 3. 定时任务（Cron）

编辑 `daily-papers-cron.sh`:

```bash
#!/bin/bash
DATE=$(date -d "yesterday" +%Y-%m-%d)
RUN_DIR=$(ls -d /root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-*${DATE//-/}* 2>/dev/null | head -1)

if [ -z "$RUN_DIR" ]; then
    echo "❌ 未找到运行目录"
    exit 1
fi

# Stage A+B: 检索 + 解读（使用并行模式）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date $DATE \
  --from-date $DATE \
  --to-date $DATE \
  --language Chinese \
  --stage A

# 使用新的并行解读脚本（快速！）
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/interpret-papers-parallel.py \
  --run-dir "$RUN_DIR" \
  --max-workers 10 \
  --language Chinese

# Stage C: 生成网页
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py \
  --run-dir "$RUN_DIR" \
  --push-date $DATE \
  --data-dir /etc/nginx/html/papers
```

---

## 🔧 脚本参数

```bash
python3 interpret-papers-parallel.py \
  --run-dir <运行目录> \        # 必需
  --max-workers <并发数> \      # 可选，默认 10
  --language <语言>             # 可选，默认 Chinese
```

### 并发数建议

| 场景 | 并发数 | 说明 |
|------|--------|------|
| 默认 | 10 | 平衡速度和稳定性 |
| 快速 | 20 | 适合时间敏感场景 |
| 保守 | 5 | API 限流时使用 |

---

## ⏱️ 超时控制

- **每篇独立超时**: 120 秒
- **不会互相影响**: 一篇失败不影响其他
- **自动重试**: 失败的任务可以重新运行脚本

---

## 📊 输出示例

```
============================================================
📚 每日论文推送 - 并行 AI 解读
============================================================
📂 运行目录：/path/to/run-dir
🔧 并发数：10
🌐 语言：Chinese
⏱️  超时：120 秒/篇

📋 论文总数：40 篇
📝 待解读：40 篇

   [1/40] ✅ 2603.16871
   [2/40] ✅ 2603.16870
   [3/40] ✅ 2603.16867
   ...
   [40/40] ✅ 2603.16021

============================================================
✅ 完成！
📊 成功：40 篇
⏭️  跳过：0 篇
❌ 失败：0 篇
⏱️  耗时：285.3 秒 (4.8 分钟)
🚀 速度：8.4 篇/分钟
============================================================
```

---

## 🔍 故障排查

### 问题 1: 未找到 API Key

```
❌ 未找到 DASHSCOPE_API_KEY，请设置环境变量或在 config.json 中配置
```

**解决**:
```bash
# 方式 1: 环境变量
export DASHSCOPE_API_KEY="sk-xxxxx"

# 方式 2: 配置文件
mkdir -p ~/.openclaw
cat > ~/.openclaw/config.json << EOF
{
  "models": {
    "dashscope": {
      "apiKey": "sk-xxxxx"
    }
  }
}
EOF
```

### 问题 2: API 限流

```
❌ 2603.16871: API 429
```

**解决**: 降低并发数
```bash
python3 interpret-papers-parallel.py \
  --run-dir <dir> \
  --max-workers 5  # 降低到 5
```

### 问题 3: 部分论文失败

**解决**: 重新运行脚本（会自动跳过已完成的）
```bash
python3 interpret-papers-parallel.py \
  --run-dir <dir> \
  --max-workers 10
```

---

## 📈 性能优化建议

1. **并发数**: 默认 10，根据 API 限流调整
2. **超时时间**: 默认 120 秒，复杂论文可调到 180 秒
3. **断点续跑**: 脚本自动跳过已完成的，可随时中断重跑
4. **定时任务**: 建议设置 23:00 执行，预留 30 分钟完成

---

_并行模式说明 - 2026-03-18 😈_
