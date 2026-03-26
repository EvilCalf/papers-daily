#!/usr/bin/env python3
"""
simple-arxiv-search.py - 简化的 arXiv 检索脚本

直接调用 arXiv API，获取指定日期范围内的论文
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
import time

# 检索关键词（40 个）
KEYWORDS = {
    "LLM": [
        "large language model", "LLM", "language model", "foundation model",
        "generative AI", "transformer model", "pre-trained language model",
        "instruction tuning", "prompt engineering", "few-shot learning"
    ],
    "Agent": [
        "AI agent", "autonomous agent", "intelligent agent", "software agent",
        "multi-agent system", "agent planning", "agent reasoning",
        "task automation", "cognitive agent", "agentic workflow"
    ],
    "Transformer": [
        "transformer architecture", "attention mechanism", "self-attention",
        "vision transformer", "ViT", "BERT", "GPT", "decoder-only",
        "encoder-decoder", "transformer model"
    ],
    "Attention": [
        "attention mechanism", "cross-attention", "multi-head attention",
        "sparse attention", "efficient attention", "attention pooling",
        "attention weight", "attention map", "attention layer", "scaled dot-product"
    ]
}

# arXiv 分类
# 只保留 cs.AI（人工智能）和 cs.CL（计算与语言/NLP）
CATEGORIES = ["cs.AI", "cs.CL"]
EXCLUDE_CATEGORIES = ["cs.CV", "cs.LG", "cs.NE"]  # 排除 CV、机器学习系统、神经进化计算

def search_arxiv(query, max_results=50, date_from=None, date_to=None):
    """搜索 arXiv（单个关键词）"""
    base_url = "http://export.arxiv.org/api/query"
    
    # 构建查询
    search_query = f"all:{query}"
    
    # 添加日期过滤
    if date_from and date_to:
        search_query += f" AND submittedDate:[{date_from} TO {date_to}]"
    
    # 添加分类过滤
    category_query = " OR ".join([f"cat:{cat}" for cat in CATEGORIES])
    search_query = f"({search_query}) AND ({category_query})"
    
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ 搜索失败：{e}")
        return None

def search_arxiv_combined(combined_query, max_results=250, date_from=None, date_to=None):
    """搜索 arXiv（组合查询，多个关键词用 OR 连接）"""
    base_url = "http://export.arxiv.org/api/query"
    
    # combined_query 已经是 all:keyword1 OR all:keyword2 格式
    search_query = combined_query
    
    # 添加日期过滤
    if date_from and date_to:
        search_query += f" AND submittedDate:[{date_from} TO {date_to}]"
    
    # 添加分类过滤
    category_query = " OR ".join([f"cat:{cat}" for cat in CATEGORIES])
    search_query = f"({search_query}) AND ({category_query})"
    
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ 搜索失败：{e}")
        return None

def parse_arxiv_response(xml_content):
    """解析 arXiv XML 响应"""
    import xml.etree.ElementTree as ET
    
    try:
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            paper = {
                'arxiv_id': None,
                'title': None,
                'summary': None,
                'published': None,
                'categories': [],
                'authors': [],
                'pdf_link': None
            }
            
            # 提取 arxiv_id
            id_elem = entry.find('atom:id', ns)
            if id_elem is not None:
                paper_id = id_elem.text.split('/')[-1]
                paper['arxiv_id'] = paper_id
            
            # 提取标题
            title_elem = entry.find('atom:title', ns)
            if title_elem is not None:
                paper['title'] = title_elem.text.strip().replace('\n', ' ')
            
            # 提取摘要
            summary_elem = entry.find('atom:summary', ns)
            if summary_elem is not None:
                paper['summary'] = summary_elem.text.strip().replace('\n', ' ')
            
            # 提取发布日期
            published_elem = entry.find('atom:published', ns)
            if published_elem is not None:
                paper['published'] = published_elem.text[:10]  # YYYY-MM-DD
            
            # 提取分类
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term')
                if term:
                    paper['categories'].append(term)
            
            # 提取作者
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    paper['authors'].append(name_elem.text)
            
            # 提取 PDF 链接
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    paper['pdf_link'] = link.get('href')
                    break
            
            if paper['arxiv_id'] and paper['title']:
                papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"❌ 解析失败：{e}")
        return []

def deduplicate_papers(papers):
    """去重"""
    seen = set()
    unique = []
    for paper in papers:
        if paper['arxiv_id'] not in seen:
            seen.add(paper['arxiv_id'])
            unique.append(paper)
    return unique

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="简化的 arXiv 检索")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="推送日期")
    parser.add_argument("--from-date", help="检索起始日期")
    parser.add_argument("--to-date", help="检索结束日期")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--max-results", type=int, default=50, help="每关键词最大结果数（默认 50 篇）")
    
    args = parser.parse_args()
    
    # 计算日期
    if args.from_date and args.to_date:
        date_from = args.from_date.replace('-', '') + '0000'
        date_to = args.to_date.replace('-', '') + '2359'
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date_from = yesterday.strftime("%Y%m%d") + '0000'
        date_to = yesterday.strftime("%Y%m%d") + '2359'
    
    print(f"🔍 arXiv 检索")
    print(f"   日期范围：{args.from_date or 'yesterday'} 到 {args.to_date or 'yesterday'}")
    print(f"   输出目录：{args.output_dir}")
    print()
    
    # 创建输出目录
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    all_papers = []
    
    # 检索每个类别（每个类别的关键词用 OR 连接，一次请求）
    for category, keywords in KEYWORDS.items():
        print(f"📌 类别：{category}")
        
        # 将关键词用 OR 连接，一次请求多个关键词
        combined_query = " OR ".join([f"all:{kw}" for kw in keywords[:5]])  # 每个类别前 5 个关键词
        print(f"   🔎 组合查询：{combined_query[:60]}...", end=' ... ', flush=True)
        
        xml_result = search_arxiv_combined(
            combined_query,
            max_results=args.max_results * 5,  # 每个类别最多 250 篇
            date_from=date_from,
            date_to=date_to
        )
        
        if xml_result:
            papers = parse_arxiv_response(xml_result)
            print(f"找到 {len(papers)} 篇")
            all_papers.extend(papers)
        else:
            print("❌ 失败")
        
        time.sleep(0.5)  # 避免请求太快
        print()
    
    # 去重
    print(f"🧹 去重...")
    unique_papers = deduplicate_papers(all_papers)
    print(f"   检索总数：{len(all_papers)}")
    print(f"   去重后：{len(unique_papers)}")
    print()
    
    # 过滤掉 CV/LG/NE 领域的论文（检查所有分类，不只是 primary_category）
    if EXCLUDE_CATEGORIES:
        print(f"🚫 排除领域：{', '.join(EXCLUDE_CATEGORIES)}")
        filtered_papers = []
        excluded_count = 0
        for paper in unique_papers:
            # 检查论文的所有分类
            all_cats = paper.get('categories', [])
            # 如果任何分类在排除列表中，就排除这篇论文
            has_excluded_cat = any(cat in EXCLUDE_CATEGORIES for cat in all_cats)
            if not has_excluded_cat:
                filtered_papers.append(paper)
            else:
                excluded_count += 1
        print(f"   过滤前：{len(unique_papers)} 篇")
        print(f"   过滤后：{len(filtered_papers)} 篇")
        print(f"   排除：{excluded_count} 篇（包含 CV/LG/NE 分类）")
        unique_papers = filtered_papers
        print()
    
    # 按发布日期过滤（arXiv API 的 submittedDate 不可靠，需要后过滤）
    if args.from_date and args.to_date:
        print(f"📅 按发布日期过滤：{args.from_date} 到 {args.to_date}")
        filtered_papers = []
        excluded_by_date = 0
        for paper in unique_papers:
            paper_date = paper['published']
            if args.from_date <= paper_date <= args.to_date:
                filtered_papers.append(paper)
            else:
                excluded_by_date += 1
        print(f"   过滤前：{len(unique_papers)} 篇")
        print(f"   过滤后：{len(filtered_papers)} 篇")
        print(f"   排除：{excluded_by_date} 篇（不在目标日期范围）")
        unique_papers = filtered_papers
        print()
    
    # 保存 papers_index.json
    # 不限制数量，让 Stage A.2 质量评分过滤（≥8 分保留）
    papers_index = []
    for paper in unique_papers:  # 全部保留（通常 100-200 篇）
        paper_dir = output_path / paper['arxiv_id']
        paper_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存 metadata.md
        metadata_content = f"""## 基本信息

- **标题**: {paper['title']}
- **作者**: {', '.join(paper['authors'][:5])}{' et al.' if len(paper['authors']) > 5 else ''}
- **ArXiv ID**: {paper['arxiv_id']}
- **发布日期**: {paper['published']}
- **主分类**: {paper['categories'][0] if paper['categories'] else 'Unknown'}
- **分类**: {', '.join(paper['categories'])}
- **摘要**: {paper['summary']}
- **PDF 链接**: {paper['pdf_link']}
"""
        (paper_dir / "metadata.md").write_text(metadata_content, encoding='utf-8')
        
        papers_index.append({
            'arxiv_id': paper['arxiv_id'],
            'title': paper['title'],
            'primary_category': paper['categories'][0] if paper['categories'] else 'Unknown',
            'published': paper['published'] + 'T00:00:00Z',
            'paper_dir': str(paper_dir),
            'metadata_md': str(paper_dir / "metadata.md")
        })
    
    # 保存索引
    with open(output_path / "papers_index.json", 'w', encoding='utf-8') as f:
        json.dump(papers_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 检索完成")
    print(f"   保存论文：{len(papers_index)} 篇")
    print(f"   索引文件：{output_path / 'papers_index.json'}")
    print()
    
    # 下载论文源码（使用 arxiv-paper-processor 技能）
    print(f"📥 下载论文源码...")
    download_script = Path.home() / ".openclaw" / "workspace" / "skills" / "arxiv-paper-processor" / "scripts" / "download_papers_batch.py"
    
    if download_script.exists():
        import subprocess
        
        cmd = [
            "python3", str(download_script),
            "--run-dir", str(output_path),
            "--artifact", "source",
            "--max-workers", "3",
            "--min-interval-sec", "5"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)  # 40 分钟，足够下载 40 篇论文
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # 检查下载结果
        source_count = 0
        for paper_dir in output_path.iterdir():
            if paper_dir.is_dir() and paper_dir.name.startswith("2603."):
                source_dir = paper_dir / "source" / "source_extract"
                if source_dir.exists() and list(source_dir.glob("*.tex")):
                    source_count += 1
        
        print(f"✅ 源码下载完成：{source_count}/{len(papers_index)} 篇")
    else:
        print(f"⚠️  找不到下载脚本：{download_script}")
        print(f"   跳过源码下载，只使用摘要")

if __name__ == "__main__":
    main()
