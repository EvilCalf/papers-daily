#!/usr/bin/env python3
"""
evaluate-paper-quality-simple.py - AI 论文质量评分（简化版）
逐个处理论文，每篇处理后保存结果
"""

import json
import argparse
from pathlib import Path
import sys
from datetime import datetime
import requests
import gc

# 项目路径
WORKSPACE = Path.home() / ".openclaw" / "workspace"

# LLM 配置
MODEL = "arkcode/doubao-seed-2.0-pro"  # 使用 ARK 字节跳动豆包模型

def load_ark_api_key():
    """从 OpenClaw 配置加载 ARK API key"""
    config_file = Path.home() / ".openclaw" / "openclaw.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        models = config.get('models', {})
        providers = models.get('providers', {})
        arkcode = providers.get('arkcode', {})
        return arkcode.get('apiKey')
    return None

ARK_API_KEY = load_ark_api_key()

def load_papers_index(run_dir):
    """加载论文索引"""
    index_path = Path(run_dir) / "papers_index.json"
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_papers_index(papers, run_dir):
    """保存论文索引"""
    index_path = Path(run_dir) / "papers_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

def load_paper_metadata(paper_info):
    """从 metadata.md 加载完整论文信息"""
    metadata_path = Path(paper_info.get('paper_dir', '')) / 'metadata.md'
    
    if not metadata_path.exists():
        return {
            'title': paper_info.get('title', ''),
            'summary': paper_info.get('summary', ''),
            'authors': paper_info.get('authors', [])
        }
    
    content = metadata_path.read_text(encoding='utf-8')
    result = {}
    for line in content.split('\n'):
        if line.startswith('- **标题**'):
            result['title'] = line.split('**:')[1].strip()
        elif line.startswith('- **作者**'):
            authors_str = line.split('**:')[1].strip()
            authors_str = authors_str.replace(' et al.', '')
            result['authors'] = [a.strip() for a in authors_str.split(',')]
        elif line.startswith('- **摘要**'):
            result['summary'] = line.split('**:')[1].strip()
    
    return result

def evaluate_single_paper_llm(paper, language="Chinese"):
    """使用 LLM 评估单篇论文"""
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    
    prompt = f"""You are an expert AI paper reviewer. Evaluate this paper's abstract and give a quality score (1-10).

**Paper Title**: {title}

**Abstract**: {summary}

**Evaluation Criteria**:
1. **Novelty** (30%): Clear innovation? New method/insight?
2. **Experiments** (30%): Comparative experiments? ≥4 baselines? ≥3 datasets? No experiments max 3
3. **Performance** (20%): Clear SOTA with concrete numbers? No quantitative metrics max 4

**Strict Penalties** (MUST apply):
- Vague abstract, unclear contribution: -3
- Claims "SOTA" without concrete data: -3
- Pure engineering, no method innovation: max 5
- No quantitative metrics (only "significant improvement"): -3
- Survey/Review paper: max 6
- Theory only, no experiments: max 5
- Validated on only 1 dataset: max 6

Please evaluate and respond in {language}. Format:
分数：X
理由：..."""
    
    try:
        url = "https://ark.cn-beijing.volces.com/api/coding/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL.split('/')[-1],  # 提取模型 ID（去掉前缀 arkcode/）
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        print(f"  📡 调用 API...", file=sys.stderr)
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        print(f"  📡 API 响应：{response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            return 6, "API 错误，使用默认分数"
        
        result = response.json()
        llm_response = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        # 解析分数
        import re
        match = re.search(r'分数 [:：]\s*(\d+)', llm_response, re.IGNORECASE)
        if not match:
            match = re.search(r'\b([1-9]|10)\b', llm_response)
        
        if match:
            score = int(match.group(1))
            score = max(1, min(10, score))
            return score, llm_response
        
        return 6, llm_response
        
    except Exception as e:
        print(f"  ⚠️  评估失败：{e}", file=sys.stderr)
        return 6, f"评估失败：{e}"

def main():
    parser = argparse.ArgumentParser(description="AI 论文质量评分（简化版）")
    parser.add_argument("--run-dir", required=True, help="运行目录")
    parser.add_argument("--min-score", type=int, default=7, help="最低保留分数")
    parser.add_argument("--language", default="Chinese", help="输出语言")
    parser.add_argument("--start-index", type=int, default=0, help="从第几篇开始（0-based）")
    
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"❌ 目录不存在：{run_dir}")
        sys.exit(1)
    
    papers = load_papers_index(run_dir)
    total = len(papers)
    start_idx = args.start_index
    
    print(f"\n🎯 AI 质量评分（简化版 - 逐个处理）")
    print(f"   运行目录：{run_dir}")
    print(f"   总论文数：{total}")
    print(f"   起始索引：{start_idx}")
    print(f"   最低分数：{args.min_score}")
    print()
    
    score_distribution = {i: 0 for i in range(1, 11)}
    completed = start_idx
    
    # 检查已经评分的论文
    for i, paper in enumerate(papers):
        if 'quality_score' in paper and i < start_idx:
            score_distribution[paper['quality_score']] += 1
            completed = max(completed, i + 1)
    
    print(f"📚 待评估：从第 {start_idx + 1} 篇开始")
    print()
    
    # 逐个处理
    for i in range(start_idx, total):
        paper = papers[i]
        
        # 跳过已评分的
        if 'quality_score' in paper:
            print(f"⏭️  跳过已评分：{paper['arxiv_id']} ({paper['quality_score']}分)")
            continue
        
        print(f"📝 处理 [{i+1}/{total}] {paper['arxiv_id']}...")
        
        # 评估
        score, reason = evaluate_single_paper_llm(load_paper_metadata(paper), args.language)
        paper['quality_score'] = score
        paper['quality_reason'] = reason
        score_distribution[score] += 1
        completed += 1
        
        print(f"  ✅ 评分：{score}分")
        
        # 每篇处理后保存
        save_papers_index(papers, run_dir)
        gc.collect()
        
        # 每 5 篇打印进度和分布
        if completed % 5 == 0:
            print(f"\n📊 当前分数分布:")
            for s in range(10, 0, -1):
                if score_distribution[s] > 0:
                    print(f"  {s}分：{score_distribution[s]}篇")
            print()
    
    # 最终统计
    print(f"\n📊 最终分数分布:")
    for score in range(10, 0, -1):
        count = score_distribution[score]
        if count > 0:
            bar = "█" * count
            print(f"  {score}分：{bar} ({count}篇)")
    
    # 过滤
    filtered = [p for p in papers if p.get('quality_score', 0) >= args.min_score]
    filtered.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    MAX_PAPERS = 40
    if len(filtered) > MAX_PAPERS:
        print(f"\n✂️  限制最多 {MAX_PAPERS} 篇（当前 {len(filtered)} 篇）")
        filtered = filtered[:MAX_PAPERS]
    
    print(f"\n📈 过滤结果:")
    print(f"  原始：{total} 篇")
    print(f"  ≥{args.min_score}分：{len(filtered)} 篇")
    
    # 保存过滤后的索引
    filtered_path = Path(run_dir) / "papers_index_filtered.json"
    with open(filtered_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存过滤后索引：{filtered_path}")
    
    print(f"\n✅ 质量评分完成！")

if __name__ == "__main__":
    main()
