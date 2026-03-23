# 🔍 论文检索配置说明

**最后更新**: 2026-03-18  
**检索策略**: 40 个关键词 × 4 类方向 × 自动去重

---

## 📊 检索配置总览

### 每天执行 ✅

- **时间**: 每天 23:00（Cron）
- **范围**: 昨天（-1 天）的论文
- **周末**: 不跳过，每天都检索
- **无论文时**: 生成"今天没论文"空页面

---

## 🔑 搜索词配置（40 个，分 4 类）

### LLM 相关（10 个）

```
LLM
large language model
language model
foundation model
pre-trained model
generative AI
chatbot
instruction tuning
RLHF
model alignment
```

### AI Agent 相关（10 个）

```
AI Agent
autonomous agent
intelligent agent
software agent
multi-agent
agent system
agentic workflow
tool use
function calling
agent planning
```

### Transformer 相关（10 个）

```
Transformer
transformer model
transformer architecture
attention model
self-attention
multi-head attention
encoder-decoder
BERT
GPT
vision transformer
```

### Attention 相关（10 个）

```
attention mechanism
attention network
cross-attention
attention layer
attention weight
attention pattern
sparse attention
linear attention
attention rollout
attention visualization
```

---

## 📁 分类过滤

```
cs.AI    - 人工智能
cs.CL    - 计算语言学与自然语言处理
cs.LG    - 机器学习
cs.CV    - 计算机视觉
cs.NE    - 神经网络与进化计算
```

---

## 🎯 目标论文数量

```
--target-range "15-30"
```

- **最少**: 15 篇
- **最多**: 30 篇
- **去重**: 跨查询自动去重 + 模型过滤

---

## 🔧 检索流程

### Stage A: 智能检索（arxiv-search-collector）

```python
# 1. 初始化任务
init_collection_run.py
  ├── --topic "LLM, AI Agent, Transformer, Attention applications"
  ├── --keywords "LLM,large language model,...,attention visualization" (40 个)
  ├── --categories "cs.AI,cs.CL,cs.LG,cs.CV,cs.NE"
  ├── --target-range "15-30"
  └── --language Chinese

# 2. 生成查询计划（AI 自动生成 3-4 个查询）
generate_query_plan.py
  ├── 读取 40 个关键词
  ├── 组合成 3-4 个精准查询（OR/AND 逻辑）
  └── 输出 query_plan.json

# 3. 执行检索（每个查询独立执行）
fetch_queries_batch.py
  ├── 串行执行每个查询（避免 API 限流）
  ├── 每个查询返回 20-30 篇论文
  └── 输出 query_results/<label>.json

# 4. 模型过滤（ relevance filtering）
  ├── 模型阅读每篇论文的标题/摘要
  ├── 标记相关性（keep/drop）
  └── 输出 query_selection/selected_by_query.json

# 5. 合并去重
merge_selected_papers.py
  ├── 跨查询去重（arXiv ID）
  ├── 生成 papers_index.json
  └── 输出 15-30 篇最终论文
```

---

## 📊 查询组合示例

AI 会自动将 40 个关键词组合成 3-4 个查询：

### 查询 1: LLM 核心
```
(LLM OR "large language model" OR "language model" OR "foundation model") 
AND 
(generative AI OR chatbot OR "instruction tuning" OR RLHF)
```

### 查询 2: Agent 应用
```
("AI Agent" OR "autonomous agent" OR "multi-agent" OR "agent system") 
AND 
("tool use" OR "function calling" OR "agentic workflow")
```

### 查询 3: Transformer 架构
```
(Transformer OR "transformer model" OR "transformer architecture" OR BERT OR GPT) 
AND 
("self-attention" OR "multi-head attention" OR "attention model")
```

### 查询 4: Attention 机制
```
("attention mechanism" OR "attention network" OR "cross-attention" OR "sparse attention") 
AND 
("attention weight" OR "attention pattern" OR "linear attention")
```

---

## 🛡️ API 限流保护

```python
# arXiv API 限制
- 每 3 秒 1 次请求
- 重试机制：最多 4 次
- 退避策略：5s → 10s → 20s → 40s（+ 随机抖动）

# 脚本配置
--min-interval-sec 5.0    # 请求间隔
--retry-max 4             # 最大重试次数
--retry-base-sec 5.0      # 退避基数
--retry-max-sec 120.0     # 最大等待时间
--retry-jitter-sec 1.0    # 随机抖动
```

---

## 📄 无论文处理

### 触发条件

1. arXiv API 返回 0 篇论文
2. 所有 PDF 下载失败
3. 模型过滤后无相关论文

### 处理流程

```bash
# Cron 创建标记
papers-no-new-{push_date}.json
  ├── status: "no_new_papers"
  ├── reason: "arXiv 没有新的 LLM/Agent/Transformer/Attention 相关论文"
  └── message: "今天没有新论文"

# Heartbeat 检查到标记
papers-heartbeat-check.py
  ├── 生成推送消息
  ├── 生成空页面（有 UI 无内容）
  ├── 更新 reports.json（count: 0）
  └── 清理标记
```

### 空页面效果

```html
😅 今天没有新论文

arXiv 今天没有新的 LLM / AI Agent / Transformer / Attention 相关论文发布。
明天再来看看吧～

← 返回主页
```

---

## 📝 配置修改位置

### 修改搜索词

文件：`/root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py`

```python
"--keywords", ",".join([
    # LLM 相关（10 个）
    "LLM", "large language model", ...,
    # AI Agent 相关（10 个）
    "AI Agent", "autonomous agent", ...,
    # Transformer 相关（10 个）
    "Transformer", "transformer model", ...,
    # Attention 相关（10 个）
    "attention mechanism", "attention network", ...
]),
```

### 修改分类

```python
"--categories", "cs.AI,cs.CL,cs.LG,cs.CV,cs.NE",
```

### 修改目标数量

```python
"--target-range", "15-30",
```

### 修改检索时间

文件：`/root/.openclaw/workspace/projects/papers-daily/scripts/daily-papers-cron.sh`

```bash
PAPER_DATE=$(date -d "yesterday" +%Y-%m-%d)  # 改为前天：date -d "2 days ago"
```

---

## 🔍 调试命令

### 查看当前配置

```bash
grep -A5 "keywords" /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py
```

### 手动触发检索

```bash
python3 /root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py \
  --date 2026-03-17 \
  --from-date "2026-03-17" \
  --to-date "2026-03-17" \
  --language Chinese
```

### 查看检索结果

```bash
cat /root/.openclaw/workspace/tmp/papers-orchestrator/llm-and-ai-agent-*/papers_index.json | python3 -m json.tool
```

### 查看查询计划

```bash
cat /root/.openclaw/workspace/tmp/papers-orchestrator/llm-and-ai-agent-*/query_plan.json | python3 -m json.tool
```

---

_检索配置文档 - 2026-03-18 更新_
