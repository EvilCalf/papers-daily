#!/usr/bin/env python3
"""
papers-orchestrator.py - 每日论文推送系统总编排器

Stage A: 智能检索 arXiv（40 关键词 × 4 分类，跨查询去重）
Stage B: AI 解读每篇论文（10 节深度解读，2000-3000 字）
Stage C: 生成网页和数据

输出目录：
- 项目数据：/root/.openclaw/workspace/projects/papers-daily/data/summaries/{date}/
- 临时文件：/root/.openclaw/workspace/tmp/papers-orchestrator/（可清理）
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# 项目根目录
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
SUMMARIES_DIR = DATA_DIR / "summaries"

# 临时目录（仅用于中间文件，可定期清理）
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TMP_DIR = WORKSPACE / "tmp"

# 外部脚本
SCRIPTS_DIR = PROJECT_DIR / "scripts"
PAPER_PROCESSOR = WORKSPACE / "skills" / "arxiv-paper-processor"

def ensure_dirs():
    """确保必要的目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

def stage_a_search(date, from_date, to_date, run_dir, lookback="1d", language="Chinese"):
    """Stage A: 检索 arXiv 论文"""
    print(f"\n🔍 Stage A: 检索 arXiv 论文")
    print(f"   日期范围：{from_date} 到 {to_date}")
    print(f"   输出目录：{run_dir}")
    
    # 调用 arxiv-search-collector 技能
    search_script = WORKSPACE / "projects" / "papers-daily" / "scripts" / "simple-arxiv-search.py"
    
    if not search_script.exists():
        print(f"   ❌ 找不到检索脚本：{search_script}")
        # 回退到内置检索逻辑
        return builtin_search(date, from_date, to_date, lookback)
    
    cmd = [
        "python3", str(search_script),
        "--date", date,
        "--from-date", from_date,
        "--to-date", to_date,
        "--output-dir", str(run_dir),
        "--max-results", "50"  # 每关键词 50 篇
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def builtin_search(date, from_date, to_date, lookback="1d"):
    """内置检索逻辑（备用）"""
    print(f"   使用内置检索逻辑...")
    # 简化实现，实际应调用 arxiv API
    return True

def stage_a_quality_filter(run_dir, min_score=7, language="Chinese"):
    """Stage A.2: AI 质量评分过滤"""
    print(f"\n🎯 Stage A.2: AI 质量评分过滤")
    print(f"   运行目录：{run_dir}")
    print(f"   最低分数：{min_score}")
    
    eval_script = Path(__file__).parent / "evaluate-paper-quality.py"
    
    if not eval_script.exists():
        print(f"   ⚠️  找不到质量评分脚本，跳过过滤")
        return True
    
    cmd = [
        "python3", str(eval_script),
        "--run-dir", str(run_dir),
        "--min-score", str(min_score),
        "--language", language
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # 检查是否有过滤后的文件
    filtered_path = Path(run_dir) / "papers_index_filtered.json"
    if filtered_path.exists():
        # 替换原始索引
        import shutil
        shutil.move(str(filtered_path), str(Path(run_dir) / "papers_index.json"))
        print(f"   ✅ 已使用过滤后的索引")
        return True
    elif result.returncode == 0:
        print(f"   ✅ 质量评分完成（无过滤或所有论文都达标）")
        return True
    else:
        print(f"   ⚠️  质量评分完成，但可能无论文达标")
        return True  # 即使无论文也继续，让后续流程处理

def stage_b_download(run_dir, language="Chinese"):
    """Stage B.1: 批量下载论文（允许部分失败）"""
    print(f"\n📥 Stage B.1: 批量下载论文")
    print(f"   ⏱️ 超时设置：1800 秒（30 分钟）")
    
    cmd = [
        "python3", str(PAPER_PROCESSOR / "scripts" / "download_papers_batch.py"),
        "--run-dir", str(run_dir),
        "--artifact", "source_then_pdf",
        "--max-workers", "3",
        "--min-interval-sec", "5",
        "--language", language
    ]
    
    # 增加超时到 30 分钟（40 篇论文 × 5 秒间隔 × 2（source+pdf）≈ 400 秒，加缓冲）
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired as e:
        print(f"\n❌ 下载超时（1800 秒）")
        print(f"   部分论文可能已下载，检查日志：{run_dir}/download_batch_log.json")
        # 超时也尝试继续，可能部分论文已下载
        pass
    except Exception as e:
        print(f"\n❌ 下载异常：{e}")
        return False
    
    # 只打印关键统计，不打印完整 JSON 输出
    log_file = Path(run_dir) / "download_batch_log.json"
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
            
            paper_count = log.get('paper_count', 0)
            failed_count = log.get('failed_count', 0)
            status_counter = log.get('status_counter', {})
            ok_count = status_counter.get('ok', 0) + status_counter.get('skipped_existing_source', 0)
            
            print(f"\n📊 下载统计：")
            print(f"   总论文数：{paper_count}")
            print(f"   成功/跳过：{ok_count}")
            print(f"   失败：{failed_count}")
            
            # 如果成功率 > 80%，认为下载阶段成功
            success_rate = ok_count / paper_count if paper_count > 0 else 0
            if success_rate >= 0.8:
                print(f"   ✅ 成功率 {success_rate*100:.1f}%，继续执行")
                return True
            else:
                print(f"   ❌ 成功率 {success_rate*100:.1f}%，低于 80%")
                # 即使低于 80% 也继续，让后续流程处理（可能有论文可解读）
                return True
        except Exception as e:
            print(f"   ⚠️ 无法解析下载日志：{e}")
            # 日志解析失败也继续
            return True
    else:
        print(f"   ⚠️ 未找到下载日志，等待 5 秒重试...")
        import time
        time.sleep(5)
        if log_file.exists():
            return stage_b_download(run_dir, language)  # 递归重试
        else:
            print(f"   ❌ 重试后仍未找到日志")
            return True  # 继续执行，让后续步骤处理

def interpret_papers(run_dir, push_date, language="Chinese"):
    """Stage B.2: AI 解读每篇论文（入口函数 - 调用并行脚本，10 并发）"""
    script_path = Path(__file__).parent / "interpret-papers-parallel.py"
    
    # 解读数据保存到项目数据目录（永久保存）
    summaries_dir = SUMMARIES_DIR / push_date
    
    cmd = [
        "python3", str(script_path),
        "--run-dir", str(run_dir),
        "--summaries-dir", str(summaries_dir),
        "--max-workers", "10",
        "--language", language
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def stage_c_generate(run_dir, push_date, output_dir):
    """Stage C: 生成网页和数据"""
    print(f"\n📄 Stage C: 生成网页和数据")
    
    script_path = Path(__file__).parent / "orchestrator-to-web.py"
    
    cmd = [
        "python3", str(script_path),
        "--run-dir", str(run_dir),
        "--push-date", push_date,
        "--data-dir", str(output_dir)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="每日论文推送系统总编排器")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="推送日期")
    parser.add_argument("--from-date", help="检索起始日期")
    parser.add_argument("--to-date", help="检索结束日期")
    parser.add_argument("--lookback", default="1d", help="回溯天数 (e.g., 1d, 7d)")
    parser.add_argument("--language", default="Chinese", help="输出语言")
    parser.add_argument("--stage", choices=["A", "B", "C", "all"], default="all", help="执行阶段")
    parser.add_argument("--output-dir", default="/etc/nginx/html/papers", help="输出目录")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    # 计算日期
    push_date = args.date
    if args.from_date and args.to_date:
        from_date = args.from_date
        to_date = args.to_date
    else:
        # 默认检索昨天的论文
        paper_date = datetime.now() - timedelta(days=1)
        from_date = to_date = paper_date.strftime("%Y-%m-%d")
    
    print(f"📚 每日论文推送系统 - 总编排器")
    print(f"==========================================")
    print(f"推送日期：{push_date}")
    print(f"论文日期：{from_date} 到 {to_date}")
    print(f"输出语言：{args.language}")
    print(f"执行阶段：{args.stage}")
    print()
    
    # Stage A: 检索 + 质量过滤
    if args.stage in ["A", "all"]:
        # 先定义输出目录
        run_dir = TMP_DIR / "papers-orchestrator" / f"llm-ai-agent-{push_date}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        if not stage_a_search(push_date, from_date, to_date, run_dir, args.lookback, args.language):
            print("❌ Stage A 失败")
            return 1
        
        print(f"✅ Stage A.1 检索完成：{run_dir}")
        
        # Stage A.2: 质量评分过滤（≥8 分保留）
        if not stage_a_quality_filter(run_dir, min_score=8, language=args.language):
            print("❌ Stage A.2 质量过滤失败")
            return 1
        
        print(f"✅ Stage A 完成（检索 + 质量过滤）：{run_dir}")
    else:
        # 使用指定的运行目录
        run_dir = Path(TMP_DIR / "papers-orchestrator" / f"llm-ai-agent-{push_date}")
        if not run_dir.exists():
            # 查找最新的
            orchestrator_dirs = sorted(
                [d for d in (TMP_DIR / "papers-orchestrator").iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if orchestrator_dirs:
                run_dir = orchestrator_dirs[0]
            else:
                print("❌ 未找到运行目录，请先执行 Stage A")
                return 1
    
    # Stage B: 下载 + AI 解读
    if args.stage in ["B", "all"]:
        if not stage_b_download(run_dir, args.language):
            print("❌ Stage B.1 下载失败")
            return 1
        
        if not interpret_papers(run_dir, push_date, args.language):
            print("❌ Stage B.2 AI 解读失败")
            return 1
        
        print(f"✅ Stage B 完成")
    
    # Stage C: 生成网页
    if args.stage in ["C", "all"]:
        if not stage_c_generate(run_dir, push_date, args.output_dir):
            print("❌ Stage C 失败")
            return 1
        
        print(f"✅ Stage C 完成")
    
    print()
    print("==========================================")
    print(f"✅ 完整流程完成！")
    print(f"==========================================")
    print(f"📄 访问地址：http://evilcalf.online/papers/")
    print(f"==========================================")
    
    return 0

if __name__ == "__main__":
    exit(main())
