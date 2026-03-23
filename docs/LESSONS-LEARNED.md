# 📚 经验教训总结 - 论文推送系统 v2.0

**最后更新**: 2026-03-18  
**版本**: v2.0 修正版

---

## 🎯 核心问题与解决方案

### 问题 1：Cron 脚本调用错误 ❌

**问题描述**:
- `daily-papers-cron.sh` 调用的是不存在的 `arxiv-retriever.py`
- 实际应该调用 `papers-orchestrator.py`

**解决方案**:
```bash
# 修复后的 cron 脚本
python3 "$SCRIPTS_DIR/papers-orchestrator.py" \
    --date "$PAPER_DATE" \
    --push-date "$PUSH_DATE" \
    --from-date "$PAPER_DATE" \
    --to-date "$PAPER_DATE" \
    --language Chinese \
    --stage A
```

**经验**: Cron 脚本修改后必须实际测试验证，不能假设逻辑正确。

---

### 问题 2：日期格式错误 ❌

**问题描述**:
- 查询计划使用 `submittedDate:[2026-03-17 TO 2026-03-17]`
- arXiv API 返回 500 错误，正确格式应为 `submittedDate:[202603170000 TO 202603172359]`

**解决方案**:
- 在 `papers-orchestrator.py` 的 `generate_query_plan` 函数中修复日期格式
- 使用 `YYYYMMDDHHMM` 格式

**经验**: arXiv API 日期格式与 ISO 格式不同，需要特别注意。

---

### 问题 3：关键词配置未生效 ❌

**问题描述**:
- 配置了 40 个关键词，实际只用了 4 个
- 目标范围设置错误（10-20 而非 15-30）

**原因**:
- `init_collection_run.py` 读取的关键词被覆盖
- `task_meta.json` 中只保存了部分关键词

**解决方案**:
- 确保 `papers-orchestrator.py` 中关键词列表完整
- 检查 `init_collection_run.py` 的参数传递

**经验**: 关键配置参数需要在多个脚本间正确传递和验证。

---

### 问题 4：AI 解读格式不统一 ❌

**问题描述**:
- 部分论文生成 10 节格式（标准）
- 部分论文生成摘要格式（不标准）
- 网页生成脚本只支持 10 节格式

**原因**:
- 不同 batch 的 subagent 使用了不同的 prompt
- 没有强制要求统一的输出格式

**解决方案**:
1. **统一 prompt 模板**：明确要求 10 节格式
2. **网页生成兼容**：支持多种键名（中英文）
3. **质量检查**：生成后验证格式

**经验**: 多 subagent 并行时必须确保 prompt 一致，输出格式统一。

---

### 问题 5：Gateway 超时导致内容污染 ❌

**问题描述**:
- 并行 subagent（5 篇/批）导致 gateway 超时
- summary.md 被错误信息污染：`Gateway agent failed; falling back to embedded`

**原因**:
- 多个 subagent 同时调用 `openclaw agent --message`
- Gateway 并发请求过多，session 文件锁竞争

**解决方案**:
- **降低并发**: 从 5 篇/批 改为 4 篇/批
- **串行处理**: 对于关键任务使用串行模式
- **错误检测**: 生成后检查文件内容，自动重试

**经验**: 
- 并行虽快但要考虑 gateway 承载能力
- 重要任务优先保证稳定性，其次才是速度
- 建议配置：3 个 subagent 并行 × 4 篇/批 = 12 篇/轮

---

### 问题 6：网页显示英文摘要而非中文解读 ❌

**问题描述**:
- 网页卡片简要内容显示英文摘要
- 展开后深度解读内容为空

**原因**:
1. summary.md 使用英文章节名（`2. Research Background`）
2. 网页生成脚本只查找中文章节名（`2. 研究目标`）
3. 回退逻辑错误触发，用英文摘要覆盖了中文内容

**解决方案**:
```python
# 网页生成脚本支持中英文键名
research_goal = (summary.get('2. 研究目标', '') or 
                summary.get('2. Research Background', '') or
                summary.get('Research Background', ''))
```

**经验**: 
- 数据格式变更时，消费端必须同步更新
- 回退逻辑要谨慎，避免覆盖正确内容

---

### 问题 7：AI 生成标记影响观感 ❌

**问题描述**:
- summary.md 末尾包含 `--- _解读完成 | 字数：约 1,800 字_`
- 网页显示这些标记，影响阅读体验

**原因**:
- subagent prompt 没有明确禁止这些标记
- 模型习惯性地添加生成说明

**解决方案**:
1. **网页生成时过滤**：
```python
text = re.sub(r'\n---.*$', '', text, flags=re.MULTILINE)
text = re.sub(r'\n_.*字.*$', '', text, flags=re.MULTILINE)
```

2. **Prompt 明确要求**：
```
注意：不要添加任何生成说明、字数统计、分隔线等额外内容。
```

**经验**: 
- 网页端过滤是临时方案
- 应该从源头（prompt）禁止生成这些内容

---

## 📋 标准操作流程（SOP）

### Stage A: 智能检索

```bash
python3 papers-orchestrator.py \
  --date 2026-03-17 \
  --push-date 2026-03-18 \
  --from-date "2026-03-17" \
  --to-date "2026-03-17" \
  --language Chinese \
  --stage A
```

**检查点**:
- [ ] 确认日期范围正确（`YYYY-MM-DD` 格式）
- [ ] 确认关键词数量（40 个）
- [ ] 确认目标范围（15-30 篇）
- [ ] 检查 `papers_index.json` 生成
- [ ] 验证论文数量（≥15 篇）

---

### Stage B: AI 解读

```bash
python3 papers-orchestrator.py \
  --date 2026-03-17 \
  --push-date 2026-03-18 \
  --from-date "2026-03-17" \
  --to-date "2026-03-17" \
  --language Chinese \
  --stage B
```

**检查点**:
- [ ] 确认所有论文都有 `summary.md`
- [ ] 验证格式为 10 节（检查 `## 1.` 开头）
- [ ] 检查文件大小（>1000 字符）
- [ ] 确认无 gateway 错误污染
- [ ] 确认无末尾标记（`--- _解读完成`）

**推荐配置**:
- 并发：3 个 subagent 并行
- 每批：4 篇论文
- 超时：每篇 5 分钟
- 批次间隔：2 秒

---

### Stage C: 网页生成

```bash
python3 orchestrator-to-web.py \
  --run-dir /path/to/run_dir \
  --push-date 2026-03-18 \
  --output-html /etc/nginx/html/papers/2026-03-18.html
```

**检查点**:
- [ ] HTML 文件生成（>50KB）
- [ ] `reports.json` 同步到 nginx 目录
- [ ] 网页无空内容（检查展开解读）
- [ ] 网页无 AI 生成标记
- [ ] 访问测试（浏览器打开）

---

## 🔧 脚本修复清单

### 已修复

1. ✅ `daily-papers-cron.sh` - 改为调用 `papers-orchestrator.py`
2. ✅ `papers-orchestrator.py` - 修复日期格式、关键词配置
3. ✅ `orchestrator-to-web.py` - 支持中英文键名、过滤 AI 标记
4. ✅ 统一 Stage B prompt - 强制 10 节格式

### 待修复

- [ ] `papers-orchestrator.py` - 添加格式验证步骤
- [ ] `papers-orchestrator.py` - 添加错误检测和自动重试
- [ ] `papers-orchestrator.py` - Prompt 明确禁止生成标记
- [ ] 添加质量检查脚本（验证 summary.md 格式）

---

## 📊 性能对比

| 模式 | 速度 | 稳定性 | 推荐场景 |
|------|------|--------|----------|
| **并行 5 篇/批** | 快 (~8-10 分钟) | ❌ 不稳定 | 不推荐 |
| **并行 4 篇/批** | 中 (~12-15 分钟) | ⚠️ 偶尔超时 | 一般场景 |
| **并行 3 篇/批** | 中 (~15-18 分钟) | ✅ 稳定 | **推荐** |
| **串行 1 篇/篇** | 慢 (~20-30 分钟) | ✅ 最稳定 | 关键任务 |

**推荐配置**: 3 个 subagent 并行 × 4 篇/批 = 12 篇/轮

---

## 🚨 常见错误与排查

### 错误 1：检索到 0 篇论文

**可能原因**:
- 日期范围错误（未来日期）
- 关键词太窄
- arXiv API 临时故障

**排查步骤**:
```bash
# 检查 query_plan.json
cat run_dir/query_plan.json | python3 -m json.tool

# 手动测试 arXiv API
curl "https://export.arxiv.org/api/query?search_query=all:LLM&submittedDate=[202603170000+TO+202603172359]"
```

---

### 错误 2：summary.md 被 gateway 错误污染

**识别方法**:
```bash
grep "Gateway agent failed" run_dir/*/summary.md
```

**解决方案**:
- 降低并发数量
- 增加批次间隔
- 重新生成被污染的文件

---

### 错误 3：网页显示英文摘要

**识别方法**:
- 卡片简要内容是英文
- 展开后深度解读为空

**排查步骤**:
```bash
# 检查 summary.md 格式
head -20 run_dir/2603.xxxxx/summary.md

# 检查章节名
grep "^## " run_dir/2603.xxxxx/summary.md
```

**解决方案**:
- 更新 `orchestrator-to-web.py` 支持中英文键名
- 重新生成网页

---

## 📝 下次运行前检查清单

### 运行前
- [ ] 确认 Cron 脚本已修复
- [ ] 确认日期范围正确（昨天）
- [ ] 清理旧的临时文件
- [ ] 检查 gateway 状态

### 运行中
- [ ] Stage A 完成后检查论文数量（≥15 篇）
- [ ] Stage B 中监控 subagent 状态
- [ ] Stage B 完成后验证格式（10 节）

### 运行后
- [ ] Stage C 生成网页
- [ ] 检查网页内容（无空内容、无标记）
- [ ] 访问测试
- [ ] 清理临时文件

---

## 🎯 关键改进建议

### 短期（下次运行前）

1. **Prompt 优化**: 明确禁止生成标记和字数统计
2. **格式验证**: 添加 summary.md 格式检查脚本
3. **错误检测**: 自动检测并重试 gateway 错误

### 中期（1-2 周内）

1. **监控告警**: 论文数量<15 篇时告警
2. **自动重试**: gateway 错误自动重新生成
3. **日志完善**: 详细的执行日志和错误追踪

### 长期（1 个月内）

1. **配置管理**: 关键词、日期范围等集中配置
2. **测试框架**: 自动化测试每个阶段
3. **性能优化**: 探索更高效的并行策略

---

_经验教训文档 - 2026-03-18 创建_
