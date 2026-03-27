#!/usr/bin/env python3
"""
evaluate-paper-quality.py - AI 论文质量评分

使用 LLM 评估每篇论文的摘要，进行 1-10 分的质量评估

评分标准：
- 9-10: 突破性工作，实验充分，写作清晰，有明确 SOTA
- 7-8:  扎实工作，有明确贡献，实验合理
- 5-6:  一般工作，贡献有限，或实验不足
- 1-4:  低质量，重复工作，摘要不完整，或纯观点无实验

用法：
    python3 evaluate-paper-quality.py --run-dir /path/to/run-dir --min-score 6
"""

import json
import argparse
from pathlib import Path
import subprocess
import sys
from datetime import datetime
import requests

# 项目路径
WORKSPACE = Path.home() / ".openclaw" / "workspace"
PAPER_PROCESSOR = WORKSPACE / "skills" / "arxiv-paper-processor"

# LLM 配置
MODEL = "qwen3.5-plus"  # 使用支持长上下文的模型

def load_dashscope_api_key():
    """从 OpenClaw 配置加载 Dashscope API key"""
    config_file = Path.home() / ".openclaw" / "openclaw.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        models = config.get('models', {})
        providers = models.get('providers', {})
        dashscope = providers.get('dashscope-aliyuncs-com', {})
        return dashscope.get('apiKey')
    return None

DASHSCOPE_API_KEY = load_dashscope_api_key()

def load_paper_metadata(paper_info):
    """
    从 metadata.md 加载完整论文信息
    
    Args:
        paper_info: dict with 'arxiv_id', 'paper_dir'
    
    Returns:
        dict with 'title', 'summary', 'authors'
    """
    metadata_path = Path(paper_info.get('paper_dir', '')) / 'metadata.md'
    
    if not metadata_path.exists():
        # 回退：使用 paper_info 中的信息
        return {
            'title': paper_info.get('title', ''),
            'summary': paper_info.get('summary', ''),
            'authors': paper_info.get('authors', [])
        }
    
    content = metadata_path.read_text(encoding='utf-8')
    
    # 解析 metadata.md
    result = {}
    for line in content.split('\n'):
        if line.startswith('- **标题**'):
            result['title'] = line.split('**:')[1].strip()
        elif line.startswith('- **作者**'):
            authors_str = line.split('**:')[1].strip()
            # 解析作者列表
            authors_str = authors_str.replace(' et al.', '')
            result['authors'] = [a.strip() for a in authors_str.split(',')]
        elif line.startswith('- **摘要**'):
            result['summary'] = line.split('**:')[1].strip()
    
    return result


def evaluate_single_paper_rule_based(paper_info):
    """
    基于规则快速评估论文质量（仅用于 LLM 评分失败时的回退）
    
    Args:
        paper_info: dict with 'title', 'summary', 'authors', 'arxiv_id'
    
    Returns:
        (score, reason): (int, str) 分数和理由
    """
    # 从 metadata.md 加载完整信息
    paper = load_paper_metadata(paper_info)
    
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    
    # 简单规则：只检查明显低质量情况
    score = 5  # 默认中等分数
    reasons = []
    
    # 1. 摘要过短（可能不完整）
    if len(summary) < 100:
        score = 3
        reasons.append("摘要过短")
    
    # 2. 摘要包含明显低质量信号
    summary_lower = summary.lower()
    if 'preliminary' in summary_lower or 'work in progress' in summary_lower:
        score = min(score, 4)
        reasons.append("初步工作")
    
    if 'position paper' in summary_lower or 'opinion' in summary_lower:
        score = min(score, 5)
        reasons.append("观点论文")
    
    # 3. 无实验信号
    experiment_keywords = ['experiment', 'evaluation', 'result', 'benchmark', 'performance']
    has_experiment = any(kw in summary_lower for kw in experiment_keywords)
    if not has_experiment:
        score = min(score, 5)
        reasons.append("无实验")
    
    # 限制在 1-10 范围内
    score = max(1, min(10, score))
    
    reason = "; ".join(reasons) if reasons else "规则评分（回退）"
    
    return score, reason


def evaluate_single_paper_llm(paper_info, language="Chinese"):
    """
    使用 LLM 评估单篇论文质量（只评估摘要）
    
    Args:
        paper_info: dict with 'title', 'summary', 'authors', 'arxiv_id'
        language: 输出语言
    
    Returns:
        (score, reason): (int, str) 分数和理由
    """
    title = paper_info.get('title', '')
    summary = paper_info.get('summary', '')
    authors = paper_info.get('authors', [])
    
    # 构建评估 prompt（只评估摘要）
    if language == "Chinese":
        prompt = f"""你是一个资深 AI 研究员，请评估以下 arXiv 论文的质量。

**论文标题**：{title}

**摘要**：
{summary}

**评分标准**（1-10 分，严格评分）：
- 9-10 分：突破性工作，有理论证明 + 充分实验（≥3 个数据集/任务），明确超越 SOTA
- 7-8 分：扎实工作，有清晰方法创新，实验设计合理（≥2 个对比基线），性能提升明确
- 5-6 分：增量改进，方法创新有限，或实验不够充分（<2 个基线/数据集）
- 1-4 分：低质量，纯应用无创新，或重复已有研究，或缺少实验验证

**关键评分维度**（必须同时满足才能得高分）：
1. 创新性（40%）：是否提出新方法/新框架/新理论？纯应用/综述最高 6 分
2. 实验充分性（40%）：是否有对比实验？基线数量？数据集数量？无实验最高 4 分
3. 性能提升（20%）：是否明确超越 SOTA？无量化指标最高 5 分

**扣分项**：
- 摘要模糊，无法识别核心贡献：-2 分
- 自称"SOTA"但无具体数据支持：-2 分
- 纯工程应用，无方法创新：最高 6 分
- 缺少量化指标（只有"显著提升"等模糊描述）：-2 分

**输出格式**（严格遵守，只返回一行）：
分数：[1-10 的数字] 理由：[1 句话说明评分理由]

请评估："""
    else:
        prompt = f"""You are a senior AI researcher. Please evaluate this arXiv paper quality.

**Title**: {title}

**Abstract**:
{summary}

**Scoring Criteria** (1-10, strict evaluation):
- 9-10: Breakthrough work, theoretical proof + extensive experiments (≥3 datasets/tasks), clear SOTA improvement
- 7-8: Solid work, clear method innovation, reasonable experiments (≥2 baselines), explicit performance gain
- 5-6: Incremental improvement, limited innovation, or insufficient experiments (<2 baselines/datasets)
- 1-4: Low quality, pure application without innovation, or repetition, or no experimental validation

**Key Dimensions** (all required for high score):
1. Novelty (40%): New method/framework/theory? Pure application/survey max 6
2. Experiments (40%): Comparative experiments? Number of baselines? datasets? No experiments max 4
3. Performance (20%): Clear SOTA improvement? No quantitative metrics max 5

**Penalties**:
- Vague abstract, unclear contribution: -2
- Claims "SOTA" without concrete data: -2
- Pure engineering, no method innovation: max 6
- No quantitative metrics (only "significant improvement"): -2

Please evaluate:"""
    
    # 调用 Dashscope API（使用 OpenAI 兼容格式）
    try:
        url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        
        if response.status_code != 200:
            print(f"  ⚠️  API 错误：{response.status_code}", file=sys.stderr)
            # 回退到规则评分
            return evaluate_single_paper_rule_based(paper_info)
        
        result = response.json()
        llm_response = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        # 解析响应
        score = parse_score_from_response(llm_response)
        reason = parse_reason_from_response(llm_response)
        
        return score, reason
        
    except requests.exceptions.Timeout:
        print(f"  ⚠️  API 超时", file=sys.stderr)
        return evaluate_single_paper_rule_based(paper_info)
    except Exception as e:
        print(f"  ⚠️  评估失败：{e}", file=sys.stderr)
        return evaluate_single_paper_rule_based(paper_info)


def evaluate_single_paper(paper_info, language="Chinese"):
    """
    评估单篇论文质量（主入口）
    
    Args:
        paper_info: dict with 'title', 'summary', 'authors', 'arxiv_id'
        language: 输出语言
    
    Returns:
        (score, reason): (int, str) 分数和理由
    """
    # 从 metadata.md 加载完整信息
    paper = load_paper_metadata(paper_info)
    
    # 使用 LLM 评估
    return evaluate_single_paper_llm(paper, language)


def parse_score_from_response(response):
    """从响应中解析分数"""
    import re
    
    # 尝试匹配"分数：X"或"Score: X"
    match = re.search(r'分数 [:：]\s*(\d+)', response, re.IGNORECASE)
    if not match:
        match = re.search(r'Score [:：]\s*(\d+)', response, re.IGNORECASE)
    if not match:
        # 尝试匹配单独的数字（1-10）
        match = re.search(r'\b([1-9]|10)\b', response)
    
    if match:
        score = int(match.group(1))
        return max(1, min(10, score))  # 限制在 1-10 范围内
    
    return 6  # 默认分数


def parse_reason_from_response(response):
    """从响应中解析理由"""
    import re
    
    # 尝试匹配"理由：XXX"或"Reason: XXX"
    match = re.search(r'理由 [:：]\s*(.+?)(?:\n|$)', response, re.IGNORECASE | re.DOTALL)
    if not match:
        match = re.search(r'Reason [:：]\s*(.+?)(?:\n|$)', response, re.IGNORECASE | re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # 返回整个响应作为理由
    return response[:200]


def load_papers_index(run_dir):
    """加载论文索引"""
    index_path = Path(run_dir) / "papers_index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"找不到论文索引：{index_path}")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_papers_index(papers, run_dir):
    """保存论文索引"""
    index_path = Path(run_dir) / "papers_index.json"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存索引：{index_path}")


def evaluate_all_papers_parallel(run_dir, min_score=7, language="Chinese", max_workers=10):
    """
    并行评估所有论文质量并过滤
    
    使用 LLM 评估每篇论文的完整摘要（从 metadata.md 读取，无需 tex 源码）
    """
    """
    并行评估所有论文质量并过滤
    
    Args:
        run_dir: 运行目录
        min_score: 最低保留分数
        language: 输出语言
        max_workers: 最大并发数
    
    Returns:
        filtered_papers: 通过过滤的论文列表
    """
    print(f"\n🎯 AI 质量评分（{max_workers}并发）")
    print(f"   运行目录：{run_dir}")
    print(f"   最低分数：{min_score}")
    print(f"   输出语言：{language}")
    print()
    
    # 加载论文
    papers = load_papers_index(run_dir)
    print(f"📚 待评估：{len(papers)} 篇")
    print(f"   预计时间：约 {len(papers) // max_workers * 15} 秒")
    print()
    
    import concurrent.futures
    
    # 并行评估
    scored_papers = []
    score_distribution = {i: 0 for i in range(1, 11)}
    
    # 进度计数器（使用列表以便在嵌套函数中修改）
    progress_counter = [0]
    import threading
    progress_lock = threading.Lock()
    
    def evaluate_with_progress(paper):
        score, reason = evaluate_single_paper(paper, language)
        paper['quality_score'] = score
        paper['quality_reason'] = reason
        with progress_lock:
            progress_counter[0] += 1
            current = progress_counter[0]
            # 每 10 篇打印一次进度，避免输出缓冲导致看起来卡住
            if current % 10 == 0 or current == len(papers):
                print(f"  进度：{current}/{len(papers)} 篇...")
        return paper
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(evaluate_with_progress, papers))
        scored_papers = results
        for paper in scored_papers:
            score_distribution[paper['quality_score']] += 1
    
    # 打印分数分布
    print(f"\n📊 分数分布:")
    for score in range(10, 0, -1):
        count = score_distribution[score]
        if count > 0:
            bar = "█" * count
            print(f"  {score}分：{bar} ({count}篇)")
    
    # 过滤
    filtered = [p for p in scored_papers if p['quality_score'] >= min_score]
    
    # 按分数排序
    filtered.sort(key=lambda x: x['quality_score'], reverse=True)
    
    # 限制最多 40 篇（防止解读时间过长）
    MAX_PAPERS = 40
    if len(filtered) > MAX_PAPERS:
        print(f"✂️  限制最多 {MAX_PAPERS} 篇（当前 {len(filtered)} 篇，取前 {MAX_PAPERS} 篇高分）")
        filtered = filtered[:MAX_PAPERS]
    
    print(f"\n📈 过滤结果:")
    print(f"  原始：{len(papers)} 篇")
    print(f"  ≥{min_score}分：{len(filtered)} 篇")
    print(f"  过滤掉：{len(papers) - len(filtered)} 篇")
    print(f"  耗时：约 {len(papers) // max_workers * 15} 秒")
    
    # 保存结果
    save_papers_index(scored_papers, run_dir)
    
    # 保存过滤后的索引
    if len(filtered) < len(papers):
        filtered_path = Path(run_dir) / "papers_index_filtered.json"
        with open(filtered_path, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存过滤后索引：{filtered_path}")
    
    return filtered


# 别名：保持向后兼容
evaluate_all_papers = evaluate_all_papers_parallel


def evaluate_all_papers_serial(run_dir, min_score=7, language="Chinese"):
    """串行版本，用于内存受限环境"""
    return evaluate_all_papers_parallel(run_dir, min_score, language, max_workers=2)


def main():
    parser = argparse.ArgumentParser(description="AI 论文质量评分")
    parser.add_argument("--run-dir", required=True, help="运行目录")
    parser.add_argument("--min-score", type=int, default=7, help="最低保留分数（默认 7）")
    parser.add_argument("--language", default="Chinese", help="输出语言")
    
    args = parser.parse_args()
    
    # 验证目录
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"❌ 目录不存在：{run_dir}")
        sys.exit(1)
    
    if not (run_dir / "papers_index.json").exists():
        print(f"❌ 找不到 papers_index.json")
        sys.exit(1)
    
    # 执行评估（使用串行版本避免 OOM）
    filtered = evaluate_all_papers_serial(run_dir, args.min_score, args.language)
    
    # 输出结果
    print(f"\n✅ 质量评分完成！")
    print(f"   高质量论文：{len(filtered)} 篇（≥{args.min_score}分）")
    
    if len(filtered) == 0:
        print(f"\n⚠️  警告：没有论文达到{args.min_score}分！")
        print(f"   建议降低 --min-score 参数或检查检索质量")
        sys.exit(1)


if __name__ == "__main__":
    main()
