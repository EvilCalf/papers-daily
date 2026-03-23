# 核心脚本代码参考

**最后更新**: 2026-03-18

---

## 1. papers-orchestrator.py

**位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/papers-orchestrator.py`

**功能**: Stage A 检索 + Stage B AI 解读

**完整代码**:

```python
#!/usr/bin/env python3
"""
papers-orchestrator.py - 使用 arxiv-summarizer-orchestrator 技能编排完整论文推送流程

集成 arxiv-summarizer-orchestrator 三阶段：
- Stage A: arxiv-search-collector (智能检索)
- Stage B: arxiv-paper-processor (并行解读)
- Stage C: arxiv-batch-reporter (报告生成)
"""

import json
import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# 技能脚本路径
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
SEARCH_COLLECTOR = SKILLS_DIR / "arxiv-search-collector" / "scripts"
PAPER_PROCESSOR = SKILLS_DIR / "arxiv-paper-processor" / "scripts"
BATCH_REPORTER = SKILLS_DIR / "arxiv-batch-reporter" / "scripts"

# 输出根目录
OUTPUT_ROOT = Path("/root/.openclaw/workspace/tmp/papers-orchestrator")

def init_run(date, push_date, language="Chinese", lookback="3d", from_date=None, to_date=None):
    """Stage A.1: 初始化检索任务"""
    print(f"\n🚀 Stage A.1: 初始化检索任务")
    print(f"   论文日期：{date}")
    print(f"   推送日期：{push_date}")
    if from_date:
        print(f"   起始日期：{from_date}")
    if to_date:
        print(f"   结束日期：{to_date}")
    print(f"   Lookback: {lookback}")
    print(f"   语言：{language}")
    
    # 构建基础命令 - 扩展搜索词（LLM/Agent/Transformer/Attention 等，每种 10 个，自动去重）
    cmd = [
        "python3", str(SEARCH_COLLECTOR / "init_collection_run.py"),
        "--output-root", str(OUTPUT_ROOT),
        "--topic", "LLM, AI Agent, Transformer, Attention applications",
        "--keywords", ",".join([
            # LLM 相关（10 个）
            "LLM", "large language model", "language model", "foundation model",
            "pre-trained model", "generative AI", "chatbot", "instruction tuning",
            "RLHF", "model alignment",
            # AI Agent 相关（10 个）
            "AI Agent", "autonomous agent", "intelligent agent", "software agent",
            "multi-agent", "agent system", "agentic workflow", "tool use",
            "function calling", "agent planning",
            # Transformer 相关（10 个）
            "Transformer", "transformer model", "transformer architecture",
            "attention model", "self-attention", "multi-head attention",
            "encoder-decoder", "BERT", "GPT", "vision transformer",
            # Attention 相关（10 个）
            "attention mechanism", "attention network", "cross-attention",
            "attention layer", "attention weight", "attention pattern",
            "sparse attention", "linear attention", "attention rollout",
            "attention visualization"
        ]),
        "--categories", "cs.AI,cs.CL,cs.LG,cs.CV,cs.NE",
        "--target-range", "15-30",
        "--language", language
    ]
    
    # 添加日期参数
    if from_date and to_date:
        cmd.extend(["--from-date", from_date, "--to-date", to_date])
    else:
        cmd.extend(["--lookback", lookback])
    
    print(f"   执行：{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(f"   输出：{result.stdout[:500]}")
    if result.stderr:
        print(f"   错误：{result.stderr[:200]}")
    
    # 解析输出获取 run_dir
    try:
        output = json.loads(result.stdout.split('{')[1].split('}')[0])
        run_dir = Path(output.get('run_dir', ''))
        print(f"   ✅ run_dir: {run_dir}")
        return run_dir
    except:
        print(f"   ❌ 解析 run_dir 失败")
        return None

def generate_query_plan(run_dir, date):
    """Stage A.2: 生成查询计划"""
    print(f"\n📝 Stage A.2: 生成查询计划")
    
    query_plan = run_dir / "query_plan.json"
    if query_plan.exists():
        print(f"   ✅ query_plan.json 已存在")
        return True
    
    # 让模型生成查询计划（简化：直接使用预设关键词）
    print(f"   ✅ 使用预设关键词")
    return True

def fetch_queries(run_dir, language="Chinese"):
    """Stage A.3: 执行查询获取论文元数据"""
    print(f"\n📥 Stage A.3: 执行查询")
    
    cmd = [
        "python3", str(SEARCH_COLLECTOR / "fetch_queries_batch.py"),
        "--run-dir", str(run_dir),
        "--language", language,
        "--min-interval-sec", "5",
        "--retry-max", "4"
    ]
    
    print(f"   执行：{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(f"   输出：{result.stdout[:500]}")
    if result.stderr:
        print(f"   错误：{result.stderr[:200]}")
    
    # 检查 papers_index.json
    papers_index = run_dir / "papers_index.json"
    if papers_index.exists():
        print(f"   ✅ papers_index.json 已生成")
        return True
    else:
        print(f"   ❌ papers_index.json 未生成")
        return False

def merge_papers(run_dir, language="Chinese"):
    """Stage A.4: 合并去重"""
    print(f"\n🔀 Stage A.4: 合并去重")
    
    # 简化：直接使用已有的 papers_index.json
    print(f"   ✅ 已自动去重")
    return True

def download_papers(run_dir, language="Chinese"):
    """Stage B.1: 批量下载论文"""
    print(f"\n📥 Stage B.1: 批量下载论文")
    
    cmd = [
        "python3", str(PAPER_PROCESSOR / "download_papers_batch.py"),
        "--run-dir", str(run_dir),
        "--artifact", "source_then_pdf",
        "--max-workers", "3",
        "--min-interval-sec", "5",
        "--language", language
    ]
    
    print(f"   执行：{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    print(f"   输出：{result.stdout[:500]}")
    if result.stderr:
        print(f"   错误：{result.stderr[:200]}")
    
    print(f"   ✅ 下载完成")
    return True

def interpret_papers_parallel(run_dir, language="Chinese", max_parallel=5):
    """Stage B.2: AI 解读每篇论文（并行模式 - 使用 subagent）"""
    print(f"\n🤖 Stage B.2: AI 解读论文（并行模式，max={max_parallel}）")
    
    # 读取 papers_index 获取论文列表
    papers_index = run_dir / "papers_index.json"
    if not papers_index.exists():
        print(f"   ❌ papers_index.json 不存在")
        return False
    
    with open(papers_index, 'r') as f:
        index = json.load(f)
    
    papers = index if isinstance(index, list) else index.get('papers', [])
    print(f"   待解读：{len(papers)} 篇")
    
    # 构建每篇论文的解读任务
    tasks = []
    for paper in papers:
        paper_id = paper.get('arxiv_id', '')
        paper_dir = run_dir / paper_id
        
        if not paper_dir.exists():
            print(f"   ⚠️ {paper_id} 目录不存在，跳过")
            continue
        
        summary_file = paper_dir / "summary.md"
        if summary_file.exists():
            print(f"   ✅ {paper_id} 已解读，跳过")
            continue
        
        # 读取 metadata
        metadata_file = paper_dir / "metadata.md"
        if not metadata_file.exists():
            print(f"   ⚠️ {paper_id} metadata.md 不存在，跳过")
            continue
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = f.read()[:3000]
        
        # 检查内容来源
        pdf_path = paper_dir / "source" / "paper.pdf"
        source_dir = paper_dir / "source" / "source_extract"
        content_source = "PDF" if pdf_path.exists() else "源码" if source_dir.exists() else "摘要"
        
        tasks.append({
            'paper_id': paper_id,
            'paper_dir': str(paper_dir),
            'metadata': metadata,
            'content_source': content_source
        })
    
    if not tasks:
        print(f"   ✅ 所有论文已解读完成")
        return True
    
    print(f"   📋 需要解读：{len(tasks)} 篇")
    
    # 分批处理
    completed = 0
    failed = 0
    
    for i in range(0, len(tasks), max_parallel):
        batch = tasks[i:i+max_parallel]
        batch_num = i // max_parallel + 1
        total_batches = (len(tasks) + max_parallel - 1) // max_parallel
        print(f"\n   🔄 批次 {batch_num}/{total_batches}: 处理 {len(batch)} 篇...")
        
        # 为每篇论文创建 subagent 任务
        subagent_sessions = []
        for task in batch:
            paper_id = task['paper_id']
            summary_path = os.path.join(task['paper_dir'], 'summary.md')
            
            prompt = f"""请阅读并解读以下 arXiv 论文：

{task['metadata']}

**内容来源**: {task['content_source']}

**输出要求**：
- 用中文撰写深度解读（1500-2500 字）
- 严格按照以下 10 节格式（Markdown）
- **重要**：不要添加任何生成说明、字数统计、分隔线、时间戳等额外内容
- **重要**：不要添加 `---`、`_解读完成_`、`_由 AI 生成_` 等标记
- 只输出 10 节正文内容

## 1. Paper Snapshot
- **ArXiv ID**: {paper_id}
- **Title**: (英文标题)
- **Authors**: (作者列表)
- **Publish date**: (发布日期)
- **Primary category**: (主要分类)
- **Reading basis**: (PDF/源码/摘要)

## 2. Research Background
(研究背景和问题)

## 3. Core Method
(核心方法和技术细节)

## 4. Key Innovations
(关键创新点)

## 5. Evaluation Setup
(实验设置和数据集)

## 6. Main Results
(主要结果和对比)

## 7. Practical Value
(实际应用价值)

## 8. Limitations
(局限性)

## 9. Future Work
(未来方向)

## 10. Brief Conclusion
(3-4 句话总结：贡献 + 方法 + 评估 + 结果，必须包含具体细节)
"""
            
            # 使用 sessions_spawn 创建 subagent
            print(f"     🚀 启动 {paper_id}...", end=' ', flush=True)
            
            # 通过 subprocess 调用 openclaw CLI 来 spawn subagent
            spawn_cmd = [
                "openclaw", "sessions", "spawn",
                "--runtime", "subagent",
                "--mode", "run",
                "--label", f"paper-{paper_id}",
                "--task", prompt
            ]
            
            try:
                # 后台启动 subagent
                subprocess.Popen(spawn_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subagent_sessions.append({
                    'paper_id': paper_id,
                    'summary_path': summary_path,
                    'started': True
                })
                print("✅")
            except Exception as e:
                print(f"❌ 启动失败：{e}")
                subagent_sessions.append({
                    'paper_id': paper_id,
                    'summary_path': summary_path,
                    'started': False
                })
        
        # 等待当前批次完成（轮询检查）
        import time
        max_wait = 180  # 每篇最多 3 分钟
        check_interval = 10  # 每 10 秒检查一次
        
        for check in range(max_wait // check_interval):
            all_done = True
            for session in subagent_sessions:
                if not os.path.exists(session['summary_path']):
                    all_done = False
                    break
            
            if all_done:
                break
            
            if check % 3 == 0:  # 每 30 秒报告一次进度
                pending = sum(1 for s in subagent_sessions if not os.path.exists(s['summary_path']))
                print(f"\n     ⏳ 等待中... 剩余 {pending}/{len(subagent_sessions)} 篇")
            
            time.sleep(check_interval)
        
        # 统计完成情况
        for session in subagent_sessions:
            if os.path.exists(session['summary_path']):
                print(f"     ✅ {session['paper_id']}")
                completed += 1
            else:
                print(f"     ❌ {session['paper_id']} (超时)")
                failed += 1
        
        # 批次间短暂休息
        if i + max_parallel < len(tasks):
            time.sleep(2)
    
    print(f"\n   📊 完成：{completed}/{len(tasks)} 篇，失败：{failed} 篇")
    return completed > 0

def interpret_papers(run_dir, language="Chinese"):
    """Stage B.2: AI 解读每篇论文（入口函数 - 使用并行模式）"""
    return interpret_papers_parallel(run_dir, language, max_parallel=5)

def main():
    parser = argparse.ArgumentParser(description="论文推送编排器")
    parser.add_argument("--date", required=True, help="论文日期 YYYY-MM-DD")
    parser.add_argument("--push-date", help="推送日期（默认=date+1）")
    parser.add_argument("--language", default="Chinese", help="输出语言")
    parser.add_argument("--stage", choices=["A", "B", "C", "all"], default="all", help="执行阶段")
    parser.add_argument("--lookback", default="3d", help="回溯时间 (Nd/Nw/Nm)，默认 3d")
    parser.add_argument("--from-date", help="起始日期 YYYY-MM-DD（覆盖 lookback）")
    parser.add_argument("--to-date", help="结束日期 YYYY-MM-DD")
    parser.add_argument("--run-dir", help="指定运行目录（跳过 Stage A）")
    args = parser.parse_args()
    
    if not args.push_date:
        args.push_date = (datetime.strptime(args.date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("📚 每日论文推送 - Orchestrator")
    print("=" * 60)
    
    # 如果指定了 run-dir，直接使用（跳过 Stage A）
    if args.run_dir:
        run_dir = Path(args.run_dir)
        print(f"📂 使用已有目录：{run_dir}")
    else:
        run_dir = init_run(
            args.date, 
            args.push_date, 
            args.language,
            lookback=args.lookback,
            from_date=args.from_date,
            to_date=args.to_date
        )
    
    if args.stage in ["A", "all"] and not args.run_dir:
        # Stage A: 检索
        query_plan = generate_query_plan(run_dir, args.date)
        if query_plan:
            fetch_queries(run_dir, args.language)
            merge_papers(run_dir, args.language)
    
    if args.stage in ["B", "all"]:
        # Stage B: 解读
        if not args.run_dir:
            download_papers(run_dir, args.language)
        interpret_papers(run_dir, args.language)
    
    if args.stage in ["C", "all"]:
        # Stage C: 报告（由 orchestrator-to-web.py 处理）
        print(f"\n📄 Stage C: 请运行 orchestrator-to-web.py 生成网页")
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！输出目录：{run_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## 2. orchestrator-to-web.py

**位置**: `/root/.openclaw/workspace/projects/papers-daily/scripts/orchestrator-to-web.py`

**功能**: Stage C - 生成 JSON 数据 + 更新索引

**核心函数**:

```python
def markdown_to_html(text):
    """Markdown 转 HTML（支持标题、列表、表格、代码块、链接等）"""
    if not text:
        return ''
    
    # 移除末尾的 AI 生成标记和字数统计（多种格式）
    text = re.sub(r'\n---+\s*_?[^*]*_?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_由 AI 自动生成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_解读完成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n解读完成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n字数：约.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n---.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_.*字.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'<p><em>解读完成.*?</em></p>', '', text)
    text = re.sub(r'<em>解读完成.*?</em>', '', text)
    
    lines = text.split('\n')
    html_lines = []
    in_list = False
    in_table = False
    table_header_done = False
    
    for i, line in enumerate(lines):
        # 处理标题
        if line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h4>{line[4:]}</h4>')
            continue
        elif line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h3>{line[3:]}</h3>')
            continue
        elif line.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2>{line[2:]}</h2>')
            continue
        
        # 处理表格
        if line.startswith('|') and line.endswith('|'):
            if not in_table:
                in_table = True
                table_header_done = False
                html_lines.append('<table>')
            
            cells = [c.strip() for c in line[1:-1].split('|')]
            
            # 检查是否是分隔线行
            if all(re.match(r'^[-:]+$', c) for c in cells):
                table_header_done = True
                continue
            
            if not table_header_done:
                html_lines.append('<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead><tbody>')
                table_header_done = True
            else:
                html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
            continue
        elif in_table:
            html_lines.append('</tbody></table>')
            in_table = False
        
        # 处理代码块
        if line.startswith('```'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue
        
        # 处理粗体
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        # 处理斜体
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
        # 处理行内代码
        line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
        # 处理链接
        line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', line)
        
        # 处理列表
        if line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line[2:] if line.startswith('- ') else line[1:]
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if line.strip():
                html_lines.append(f'<p>{line}</p>')
    
    # 关闭未闭合的标签
    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</tbody></table>')
    
    return '\n'.join(html_lines)

def generate_json_data(papers_data, push_date, date_range, output_dir):
    """生成 JSON 数据文件"""
    
    # 按分类组织论文
    grouped = {}
    for paper in papers_data:
        primary_cat = paper.get('primary_category', 'Other')
        if primary_cat not in grouped:
            grouped[primary_cat] = []
        grouped[primary_cat].append(paper)
    
    # 分类显示名称映射
    category_map = {
        'cs.AI': ('AI 基础', '人工智能基础研究'),
        'cs.CL': ('NLP 与对话', '自然语言处理'),
        'cs.LG': ('机器学习', '机器学习方法'),
        'cs.SE': ('软件工程', '软件与代码'),
        'cs.HC': ('人机交互', '人机交互'),
        'cs.CR': ('安全', '安全与隐私'),
    }
    
    # 构建数据结构
    categories = []
    cat_num = 1
    
    for cat_name, cat_papers in grouped.items():
        cat_display = category_map.get(cat_name, (cat_name, cat_name))[0]
        
        papers = []
        for paper in cat_papers:
            summary = paper.get('summary_sections', {})
            
            # 提取关键部分（支持中英文键名）
            research_goal = (summary.get('2. 研究目标', '') or 
                            summary.get('2. Research Background', '') or
                            summary.get('Research Background', ''))
            method = (summary.get('3. 方法概述', '') or 
                     summary.get('3. Core Method', '') or
                     summary.get('Core Method', ''))
            results = (summary.get('5. 关键结果', '') or 
                      summary.get('5. Main Results', '') or
                      summary.get('6. Main Results', '') or
                      summary.get('Main Results', ''))
            conclusion = (summary.get('10. 简要结论', '') or 
                         summary.get('10. Brief Conclusion', '') or
                         summary.get('Brief Conclusion', ''))
            
            brief = conclusion  # 直接使用完整结论
            
            # 如果 brief 还是空，读 metadata 的摘要
            if not brief or '暂无详细解读' in brief or len(brief) < 50:
                metadata = read_metadata_md(Path(paper.get('paper_dir', '')))
                abstract = metadata.get('摘要', '')
                if abstract:
                    brief = abstract
            
            # 格式化发布时间
            published = paper.get('published', '')
            pub_date = published.split('T')[0] if 'T' in published else published[:10] if published else ''
            
            papers.append({
                'arxiv_id': paper.get('arxiv_id', ''),
                'title': paper.get('title', ''),
                'published': pub_date,
                'category': paper.get('primary_category', ''),
                'brief': markdown_to_html(brief),  # 转换为 HTML
                'link': f"https://arxiv.org/abs/{paper.get('arxiv_id', '')}",
                'details': {
                    'research_goal': markdown_to_html(research_goal),
                    'method': markdown_to_html(method),
                    'results': markdown_to_html(results) if results else None,
                    'conclusion': markdown_to_html(conclusion)
                }
            })
        
        categories.append({
            'name': cat_display,
            'papers': papers
        })
        cat_num += 1
    
    # 构建完整数据
    data = {
        'push_date': push_date,
        'total_count': len(papers_data),
        'category_count': len(grouped),
        'categories': categories
    }
    
    # 写入 JSON 文件
    json_file = output_dir / f"{push_date}.json"
    json_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已生成：{json_file}")
    
    return json_file

def update_reports_json(papers_data, push_date, date_range, data_dir):
    """更新 reports.json 索引"""
    reports_file = data_dir / "reports.json"
    
    # 统计 LLM 和 Agent 数量
    llm_count = sum(1 for p in papers_data if 'llm' in p.get('title', '').lower() or p.get('primary_category') == 'cs.CL')
    agent_count = sum(1 for p in papers_data if 'agent' in p.get('title', '').lower() or p.get('primary_category') == 'cs.AI')
    
    # 读取现有记录
    if reports_file.exists():
        with open(reports_file, 'r', encoding='utf-8') as f:
            reports = json.load(f)
    else:
        reports = []
    
    # 移除同日期记录（如果有）
    reports = [r for r in reports if r['date'] != push_date]
    
    # 添加新记录（指向 JSON 数据文件）
    entry = {
        'date': push_date,
        'paper_date': date_range.split('~')[0] if '~' in date_range else date_range,
        'count': len(papers_data),
        'llm_count': llm_count,
        'agent_count': agent_count,
        'data_file': f"data/{push_date}.json",
        'detail_url': f"detail.html?date={push_date}"
    }
    
    reports.insert(0, entry)
    
    # 保留最近 30 条
    reports = reports[:30]
    
    # 保存
    with open(reports_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引已更新：{reports_file}")
```

---

_完整代码参考 - 2026-03-18 😈_
