# 📁 数据目录结构

**最后更新**: 2026-03-18

---

## 🎯 核心原则

**项目数据** vs **临时文件**:
- ✅ **项目数据** - 永久保存（AI 解读、元数据、报告）
- ❌ **临时文件** - 可定期清理（中间产物、缓存）

---

## 📂 完整目录结构

```
/root/.openclaw/workspace/projects/papers-daily/    # 项目根目录
├── README.md                                        # 快速入门
├── docs/                                            # 文档
│   ├── COMPLETE-GUIDE.md                           # 完整指南
│   ├── DATA-STRUCTURE.md                           # 本文档
│   ├── DAILY-WORKFLOW.md                           # 每日工作流
│   └── ...
├── scripts/                                         # 脚本
│   ├── papers-orchestrator.py                      # 总编排器
│   ├── interpret-papers-parallel.py                # 并行解读
│   └── ...
├── data/                                            # 项目数据 ⭐ 永久保存
│   └── summaries/                                   # AI 解读数据
│       ├── 2026-03-18/                             # 按日期组织
│       │   ├── 2603.16871/
│       │   │   ├── metadata.md                     # 论文元数据
│       │   │   └── summary.md                      # AI 深度解读 ⭐
│       │   ├── 2603.16870/
│       │   │   ├── metadata.md
│       │   │   └── summary.md
│       │   └── ...
│       ├── 2026-03-17/
│       └── ...
└── templates/                                       # 网页模板
    └── detail-with-toc.html

/root/.openclaw/workspace/tmp/                       # 临时文件 ⭐ 可清理
└── papers-orchestrator/
    └── llm-ai-agent-xxx-YYYY-MM-DD_to_YYYY-MM-DD/
        ├── papers_index.json                       # 论文索引（中间产物）
        └── 2603.xxxxx/                             # 论文源码/缓存
            ├── source/                             # TeX 源码（可重新下载）
            └── pdf_text.txt                        # PDF 提取文本

/etc/nginx/html/papers/                              # nginx 部署
├── index.html                                       # 主页
├── detail.html                                      # 详情页
├── reports.json                                     # 推送索引
└── data/
    └── YYYY-MM-DD.json                             # 每日网页数据
```

---

## 📊 数据分类

### 1. 项目数据（永久保存）⭐

**位置**: `/root/.openclaw/workspace/projects/papers-daily/data/summaries/{date}/`

**内容**:
- `metadata.md` - 论文元数据（标题、作者、摘要等）
- `summary.md` - AI 深度解读（10 节，2000-3000 字）

**特点**:
- ✅ 按日期组织，易于查找
- ✅ 每篇论文独立目录
- ✅ 永久保存，不清理
- ✅ 可重复使用（重新生成网页时直接读取）

**示例**:
```
data/summaries/2026-03-18/
├── 2603.16871/
│   ├── metadata.md
│   └── summary.md          # AI 解读：WorldCam 论文
├── 2603.16870/
│   ├── metadata.md
│   └── summary.md          # AI 解读：Video Reasoning 论文
└── ...
```

---

### 2. 临时文件（可清理）

**位置**: `/root/.openclaw/workspace/tmp/papers-orchestrator/`

**内容**:
- `papers_index.json` - 检索结果索引（中间产物）
- `2603.xxxxx/source/` - 论文源码（可重新下载）
- `2603.xxxxx/pdf_text.txt` - PDF 提取文本（可重新提取）

**特点**:
- ⚠️ 仅用于中间处理
- ⚠️ 可定期清理（保留最新 1-2 个）
- ⚠️ 重新运行时会自动生成

**清理策略**:
```bash
# 保留最新的 1 个，删除旧的
ls -td /root/.openclaw/workspace/tmp/papers-orchestrator/*/ | tail -n +2 | xargs rm -rf
```

---

### 3. 网页数据（部署用）

**位置**: `/etc/nginx/html/papers/`

**内容**:
- `index.html` - 主页（静态）
- `detail.html` - 详情页模板（静态）
- `reports.json` - 推送索引（每日更新）
- `data/YYYY-MM-DD.json` - 每日论文数据（每日生成）

**特点**:
- ✅ 静态文件不需要每天生成
- ✅ 数据文件每日更新
- ✅ 直接由 nginx 提供服务

---

## 🔄 数据流

```
Stage A: 检索
  arXiv API → papers_index.json (tmp/)
  
Stage B: AI 解读
  papers_index.json + 论文源码 → summary.md (data/summaries/{date}/) ⭐
  
Stage C: 网页生成
  data/summaries/{date}/ → data/YYYY-MM-DD.json (nginx) → 用户访问
```

---

## 📋 每日执行后的数据结构

**执行**: `bash generate-daily.sh 2026-03-18`

**生成**:

```
# 项目数据（新增，永久保存）⭐
data/summaries/2026-03-18/
├── 2603.16871/
│   ├── metadata.md
│   └── summary.md
├── 2603.16870/
│   ├── metadata.md
│   └── summary.md
└── ... (40 篇论文)

# nginx 部署（新增/更新）
/etc/nginx/html/papers/
├── data/2026-03-18.json          # 新增
└── reports.json                  # 更新（添加新记录）

# 临时文件（可清理）
tmp/papers-orchestrator/
└── llm-ai-agent-xxx-2026-03-18/  # 可保留，下次清理时删除
```

---

## 🧹 清理策略

### 项目数据（data/summaries/）
- ❌ **不清理** - 永久保存
- ✅ 可按日期归档（如超过 30 天打包压缩）

### 临时文件（tmp/papers-orchestrator/）
- ✅ **定期清理** - 保留最新 1-2 个
- ✅ 使用清理脚本：
```bash
bash /root/.openclaw/workspace/scripts/cleanup-papers-tmp.sh
```

### nginx 数据（/etc/nginx/html/papers/data/）
- ✅ **保留最近 30 天** - 节省空间
- ✅ 旧数据可归档或删除

---

## 📊 空间占用估算

| 目录 | 单日大小 | 30 天累计 | 清理策略 |
|------|---------|----------|----------|
| `data/summaries/` | ~2MB (40 篇 × 50KB) | ~60MB | 永久保存 |
| `tmp/papers-orchestrator/` | ~50MB (含源码) | ~1.5GB | 保留最新 1 个 |
| `nginx/data/` | ~400KB | ~12MB | 保留 30 天 |

---

## 🔍 查找数据

### 查找某篇论文的解读
```bash
find /root/.openclaw/workspace/projects/papers-daily/data/summaries -name "summary.md" | grep 2603.16871
```

### 查看某日所有解读
```bash
ls -la /root/.openclaw/workspace/projects/papers-daily/data/summaries/2026-03-18/
```

### 统计解读字数
```bash
wc -w /root/.openclaw/workspace/projects/papers-daily/data/summaries/2026-03-18/*/summary.md
```

---

_数据目录规范 - 2026-03-18 😈_
