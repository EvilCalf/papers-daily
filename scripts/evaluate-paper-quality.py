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
import time
from pathlib import Path
import subprocess
import sys
from datetime import datetime
import urllib.request
import urllib.error
import requests
import json_repair

# 项目路径
WORKSPACE = Path.home() / ".openclaw" / "workspace"
PAPER_PROCESSOR = WORKSPACE / "skills" / "arxiv-paper-processor"

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

**评分标准**（1-10 分，**极其严格**评分）：
- **10 分**：里程碑式突破，理论 + 实验双重大创新，多个数据集验证，性能大幅提升（>10%），被广泛引用的潜力
- **9 分**：重大创新，方法新颖，实验充分（≥4 个数据集/任务），明确超越 SOTA 且有量化指标
- **7-8 分**：扎实工作，有清晰方法创新，实验合理（≥3 个对比基线），性能提升明确
- **5-6 分**：增量改进，方法创新有限，或实验不够充分（<3 个基线/数据集）
- **1-4 分**：低质量，纯应用无创新，或重复已有研究，或缺少实验验证

**关键评分维度**（必须同时满足才能得 9 分以上）：
1. **创新性**（50%）：是否提出全新方法/框架/理论？纯应用/综述/改进型最高 7 分
2. **实验充分性**（30%）：是否有对比实验？基线数量≥4？数据集数量≥3？无实验最高 3 分
3. **性能提升**（20%）：是否明确超越 SOTA 且有具体数字？无量化指标最高 4 分

**严格扣分项**（必须执行）：
- 摘要模糊，无法识别核心贡献：-3 分
- 自称"SOTA"但无具体数据支持：-3 分
- 纯工程应用，无方法创新：最高 5 分
- 缺少量化指标（只有"显著提升"等模糊描述）：-3 分
- 综述/Survey 类型：最高 6 分
- 纯理论无实验：最高 5 分
- 只在 1 个数据集上验证：最高 6 分

**输出格式**（严格遵守，只返回 JSON，不要其他内容）：
{{
  "analysis": "100字以内的简短分析，说明论文核心特点",
  "score": 1-10的整数分数
}}

请评估："""
    else:
        prompt = f"""You are a senior AI researcher. Please evaluate this arXiv paper quality.

**Title**: {title}

**Abstract**:
{summary}

**Scoring Criteria** (1-10, **EXTREMELY STRICT** evaluation):
- **10**: Milestone breakthrough, theoretical + experimental innovation, multiple datasets (>3), significant improvement (>10%), high citation potential
- **9**: Major innovation, novel method, extensive experiments (≥4 datasets/tasks), clear SOTA with quantitative metrics
- **7-8**: Solid work, clear method innovation, reasonable experiments (≥3 baselines), explicit performance gain
- **5-6**: Incremental improvement, limited innovation, or insufficient experiments (<3 baselines/datasets)
- **1-4**: Low quality, pure application without innovation, repetition, or no experimental validation

**Key Dimensions** (ALL required for 9+ score):
1. **Novelty** (50%): New method/framework/theory? Pure application/survey/improvement max 7
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

Please evaluate:"""
    
    # 调用 ARK API（字节跳动豆包）带重试机制
    max_retries = 3
    retry_delay = 10  # 10秒重试间隔
    
    for attempt in range(max_retries):
        try:
            url = "https://ark.cn-beijing.volces.com/api/coding/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {ARK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": MODEL.split('/')[-1],  # 提取模型 ID（去掉前缀 arkcode/）
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200
            }
            
            print(f"  📡 调用 API (第 {attempt+1}/{max_retries} 次)...", file=sys.stderr)
            
            # 使用 urllib 调用 API
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=180) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            print(f"  📡 API 响应：200", file=sys.stderr)
            
            llm_response = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            # 使用 json_repair 解析，自动修复格式错误
            try:
                response_data = json_repair.loads(llm_response)
                score = int(response_data.get('score', 0))
                reason = response_data.get('analysis', '')
                
                # 验证分数范围
                if 1 <= score <= 10:
                    return score, reason
                else:
                    print(f"  ⚠️  分数超出范围：{score}，重试...", file=sys.stderr)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
            except Exception as e:
                print(f"  ⚠️  JSON 解析失败：{str(e)}，输出：{llm_response[:50]}...，重试...", file=sys.stderr)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                    
        except urllib.error.HTTPError as e:
            print(f"  ⚠️  API 错误：{e.code}", file=sys.stderr)
        except urllib.error.URLError as e:
            print(f"  ⚠️  API 超时或网络错误：{e.reason}", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️  评估失败：{e}", file=sys.stderr)
        
        # 重试等待
        if attempt < max_retries - 1:
            print(f"  ⏳ 等待 {retry_delay} 秒后重试...", file=sys.stderr)
            time.sleep(retry_delay)
    
    # 所有重试失败，回退到规则评分
    print(f"  ❌ 所有重试失败，使用规则评分", file=sys.stderr)
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
    
    # 不限制数量，所有评分≥min_score的论文都保留
    
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


def evaluate_all_papers_batched(run_dir, min_score=7, language="Chinese", batch_size=10, max_workers=4):
    """
    分批处理版本，每批处理后保存结果并释放内存
    避免 99 篇论文累积导致 OOM
    """
    import gc
    import json
    import shutil
    
    print(f"\n🎯 AI 质量评分（分批处理，每批{batch_size}篇）")
    print(f"   运行目录：{run_dir}")
    print(f"   最低分数：{min_score}")
    print(f"   输出语言：{language}")
    print()
    
    # 备份原始索引
    index_path = Path(run_dir) / "papers_index.json"
    backup_path = Path(run_dir) / "papers_index.json.backup"
    if index_path.exists():
        shutil.copy2(index_path, backup_path)
        print(f"📋 已备份原始索引：{backup_path}")
    
    # 加载论文
    papers = load_papers_index(run_dir)
    total = len(papers)
    print(f"📚 待评估：{total} 篇")
    print()
    
    if total == 0:
        print("⚠️  警告：没有论文可评估！")
        return []
    
    score_distribution = {i: 0 for i in range(1, 11)}
    completed = 0
    
    # 分批处理
    for batch_idx in range(0, total, batch_size):
        batch_end = min(batch_idx + batch_size, total)
        batch = papers[batch_idx:batch_end]
        print(f"📝 处理批次 {batch_idx//batch_size + 1}/{(total + batch_size - 1)//batch_size} (论文 {batch_idx+1}-{batch_end})")
        
        # 处理当前批次
        for i, paper in enumerate(batch):
            score, reason = evaluate_single_paper(paper, language)
            paper['quality_score'] = score
            paper['quality_reason'] = reason
            score_distribution[score] += 1
            completed += 1
            
            # 每 5 篇打印进度
            if completed % 5 == 0:
                print(f"  进度：{completed}/{total} 篇...")
        
        # 每批处理后保存中间结果并释放内存
        save_papers_index(papers, run_dir)
        gc.collect()
        print(f"  批次完成，已保存中间结果（已评 {completed}/{total} 篇）\n")
    
    # 打印分数分布
    print(f"\n📊 分数分布:")
    for score in range(10, 0, -1):
        count = score_distribution[score]
        if count > 0:
            bar = "█" * count
            print(f"  {score}分：{bar} ({count}篇)")
    
    # 过滤
    filtered = [p for p in papers if p.get('quality_score', 0) >= min_score]
    
    # 按分数排序
    filtered.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # 限制最多 40 篇
    MAX_PAPERS = 40
    if len(filtered) > MAX_PAPERS:
        print(f"✂️  限制最多 {MAX_PAPERS} 篇（当前 {len(filtered)} 篇，取前 {MAX_PAPERS} 篇高分）")
        filtered = filtered[:MAX_PAPERS]
    
    print(f"\n📈 过滤结果:")
    print(f"  原始：{total} 篇")
    print(f"  ≥{min_score}分：{len(filtered)} 篇")
    print(f"  过滤掉：{total - len(filtered)} 篇")
    
    # 保存过滤后的索引（不覆盖原始索引）
    if len(filtered) < total:
        filtered_path = Path(run_dir) / "papers_index_filtered.json"
        with open(filtered_path, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存过滤后索引：{filtered_path}")
    
    # 删除备份
    if backup_path.exists():
        backup_path.unlink()
        print(f"🗑️  已删除备份文件")
    
    return filtered


def main():
    parser = argparse.ArgumentParser(description="AI 论文质量评分")
    parser.add_argument("--run-dir", required=True, help="运行目录")
    parser.add_argument("--min-score", type=int, default=7, help="最低保留分数（默认 7）")
    parser.add_argument("--max-workers", type=int, default=4, help="并行进程数（默认 4）")
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
    
    # 执行评估（使用分批处理版本避免 OOM）
    # 使用更小的 batch_size 防止超时
    filtered = evaluate_all_papers_batched(run_dir, args.min_score, args.language, batch_size=5, max_workers=args.max_workers)
    
    # 输出结果
    print(f"\n✅ 质量评分完成！")
    print(f"   高质量论文：{len(filtered)} 篇（≥{args.min_score}分）")
    
    if len(filtered) == 0:
        print(f"\n⚠️  警告：没有论文达到{args.min_score}分！")
        print(f"   建议降低 --min-score 参数或检查检索质量")
        sys.exit(1)


if __name__ == "__main__":
    main()
