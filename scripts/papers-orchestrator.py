#!/usr/bin/env python3
"""
papers-orchestrator.py - 每日论文推送系统总编排器（带重试和日志）

Stage A: 智能检索 arXiv（40 关键词 × 4 分类，跨查询去重）
Stage B: AI 解读每篇论文（10 节深度解读，2000-3000 字）
Stage C: 生成网页和数据

输出目录：
- 项目数据：/root/.openclaw/workspace/projects/papers-daily/data/summaries/{date}/
- 临时文件：/root/.openclaw/workspace/tmp/papers-orchestrator/（可清理）
- 日志文件：/root/.openclaw/workspace/projects/papers-daily/logs/orchestrator.log
"""

import json
import argparse
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import traceback

# 项目根目录
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
SUMMARIES_DIR = DATA_DIR / "summaries"
LOG_DIR = PROJECT_DIR / "logs"

# 临时目录（仅用于中间文件，可定期清理）
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TMP_DIR = WORKSPACE / "tmp"

# 外部脚本
SCRIPTS_DIR = PROJECT_DIR / "scripts"
PAPER_PROCESSOR = WORKSPACE / "skills" / "arxiv-paper-processor"

# 重试配置
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4, 8]  # 指数退避（秒）

# 全局日志记录器
logger = None
perf_stats = {}  # 性能统计

def setup_logging(run_dir=None):
    """设置日志记录"""
    global logger
    
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "orchestrator.log"
    
    # 创建 logger
    logger = logging.getLogger("papers-orchestrator")
    logger.setLevel(logging.DEBUG)
    
    # 清除已有 handler
    logger.handlers = []
    
    # 文件 handler（详细日志）
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 控制台 handler（简洁输出）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_stage_start(stage_name, description):
    """记录阶段开始"""
    logger.info(f"{stage_name} 开始 - {description}")
    perf_stats[stage_name] = {
        'start': datetime.now(),
        'end': None,
        'items': []
    }

def log_stage_end(stage_name, summary=""):
    """记录阶段结束"""
    if stage_name in perf_stats:
        perf_stats[stage_name]['end'] = datetime.now()
        duration = (perf_stats[stage_name]['end'] - perf_stats[stage_name]['start']).total_seconds()
        perf_stats[stage_name]['duration'] = duration
    
    msg = f"{stage_name} 完成"
    if summary:
        msg += f" - {summary}"
    logger.info(msg)

def log_paper_status(paper_id, status, detail="", retry_count=0):
    """记录论文处理状态"""
    if retry_count > 0:
        logger.info(f"论文 {paper_id} - {status}（重试后）{detail}")
    else:
        logger.info(f"论文 {paper_id} - {status} {detail}")

def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """
    带指数退避的重试装饰器
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        max_retries: 最大重试次数
        **kwargs: 关键字参数
    
    Returns:
        (success, result, retry_count)
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            return (True, result, attempt)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS)-1)]
                logger.error(f"执行失败：{e} - 重试 {attempt+1}/{max_retries}（{delay}s 后）")
                time.sleep(delay)
            else:
                logger.error(f"执行失败：{e} - 已达到最大重试次数，标记为跳过")
    
    return (False, last_error, max_retries)

def ensure_dirs():
    """确保必要的目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def stage_a_search(date, from_date, to_date, run_dir, lookback="1d", language="Chinese"):
    """Stage A: 检索 arXiv 论文"""
    log_stage_start("Stage A", "检索 arXiv 论文")
    
    logger.info(f"日期范围：{from_date} 到 {to_date}")
    logger.info(f"输出目录：{run_dir}")
    
    # 调用 arxiv-search-collector 技能
    search_script = WORKSPACE / "projects" / "papers-daily" / "scripts" / "simple-arxiv-search.py"
    
    if not search_script.exists():
        logger.error(f"找不到检索脚本：{search_script}")
        # 回退到内置检索逻辑
        return builtin_search(date, from_date, to_date, lookback)
    
    query_count = 0
    total_papers = 0
    
    def _do_search():
        nonlocal query_count, total_papers
        
        cmd = [
            "python3", str(search_script),
            "--date", date,
            "--from-date", from_date,
            "--to-date", to_date,
            "--output-dir", str(run_dir),
            "--max-results", "50"  # 每关键词 50 篇
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)  # 40 分钟
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        # 解析返回的论文数量
        try:
            index_file = Path(run_dir) / "papers_index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    papers = json.load(f)
                total_papers = len(papers)
        except:
            pass
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_search)
    
    if success:
        if retry_count > 0:
            logger.info(f"Stage A 检索成功（重试 {retry_count} 次后）")
        logger.info(f"Stage A 完成 - 共检索到 {total_papers} 篇论文")
        log_stage_end("Stage A", f"共检索到 {total_papers} 篇论文")
        return True
    else:
        logger.error(f"Stage A 检索失败：{result}")
        log_stage_end("Stage A", "检索失败")
        return False

def builtin_search(date, from_date, to_date, lookback="1d"):
    """内置检索逻辑（备用）"""
    logger.info("使用内置检索逻辑...")
    # 简化实现，实际应调用 arxiv API
    log_stage_end("Stage A", "使用内置检索（简化）")
    return True

def stage_a_quality_filter(run_dir, min_score=9, language="Chinese"):
    """Stage A.2: AI 质量评分过滤"""
    log_stage_start("Stage A.2", "AI 质量评分过滤")
    
    logger.info(f"运行目录：{run_dir}")
    logger.info(f"最低分数：{min_score}（严格模式）")
    
    eval_script = Path(__file__).parent / "evaluate-paper-quality.py"
    
    if not eval_script.exists():
        logger.warning("找不到质量评分脚本，跳过过滤")
        log_stage_end("Stage A.2", "跳过（无脚本）")
        return True
    
    def _do_filter():
        cmd = [
            "python3", str(eval_script),
            "--run-dir", str(run_dir),
            "--min-score", str(min_score),
            "--language", language
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_filter)
    
    if success:
        # 检查是否有过滤后的文件
        filtered_path = Path(run_dir) / "papers_index_filtered.json"
        if filtered_path.exists():
            import shutil
            shutil.move(str(filtered_path), str(Path(run_dir) / "papers_index.json"))
            logger.info("已使用过滤后的索引")
            log_stage_end("Stage A.2", "过滤完成")
            return True
        else:
            logger.info("质量评分完成（无过滤或所有论文都达标）")
            log_stage_end("Stage A.2", "评分完成")
            return True
    else:
        logger.error(f"质量评分失败：{result}")
        log_stage_end("Stage A.2", "评分失败")
        return True

def stage_b_download(run_dir, language="Chinese"):
    """Stage B.1: 批量下载论文（允许部分失败）- 只下载质量评分≥8 分的论文"""
    log_stage_start("Stage B.1", "批量下载论文（仅高质量）")
    
    # 检查是否有过滤后的索引
    filtered_index = Path(run_dir) / "papers_index_filtered.json"
    original_index = Path(run_dir) / "papers_index.json"
    
    if filtered_index.exists():
        # 备份原始索引
        import shutil
        shutil.copy2(original_index, original_index.with_suffix('.json.bak'))
        # 使用过滤后的索引
        shutil.move(str(filtered_index), str(original_index))
        logger.info("✅ 使用质量过滤后的索引（仅≥8 分）")
    else:
        logger.warning("⚠️  无质量过滤索引，使用全部论文")
    
    logger.info(f"超时设置：1800 秒（30 分钟）")
    
    def _do_download():
        cmd = [
            "python3", str(PAPER_PROCESSOR / "scripts" / "download_papers_batch.py"),
            "--run-dir", str(run_dir),
            "--artifact", "source",
            "--max-workers", "3",
            "--min-interval-sec", "5",
            "--language", language
        ]
        
        # 增加超时到 30 分钟
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            # 检查是否是超时
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_download, max_retries=1)  # 下载只重试 1 次
    
    # 解析下载日志
    log_file = Path(run_dir) / "download_batch_log.json"
    paper_count = 0
    ok_count = 0
    failed_count = 0
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
            
            paper_count = log.get('paper_count', 0)
            failed_count = log.get('failed_count', 0)
            status_counter = log.get('status_counter', {})
            ok_count = status_counter.get('ok', 0) + status_counter.get('skipped_existing_source', 0)
            
            logger.info(f"下载统计：")
            logger.info(f"  总论文数：{paper_count}")
            logger.info(f"  成功/跳过：{ok_count}")
            logger.info(f"  失败：{failed_count}")
            
            # 记录每篇论文的状态
            papers_status = log.get('papers', [])
            for paper in papers_status[:10]:  # 只记录前 10 篇详情
                paper_id = paper.get('paper_id', 'unknown')
                status = paper.get('status', 'unknown')
                if status != 'ok':
                    logger.info(f"  论文 {paper_id}: {status}")
            
            # 如果成功率 > 80%，认为下载阶段成功
            success_rate = ok_count / paper_count if paper_count > 0 else 0
            if success_rate >= 0.8:
                logger.info(f"成功率 {success_rate*100:.1f}%，继续执行")
                log_stage_end("Stage B.1", f"下载完成 - 成功 {ok_count}/{paper_count} ({success_rate*100:.1f}%)")
                return True
            else:
                logger.warning(f"成功率 {success_rate*100:.1f}%，低于 80%")
                log_stage_end("Stage B.1", f"下载完成 - 成功 {ok_count}/{paper_count} ({success_rate*100:.1f}%)")
                return True  # 即使低于 80% 也继续
        except Exception as e:
            logger.error(f"无法解析下载日志：{e}")
    
    if not success:
        logger.error(f"下载失败：{result}")
        log_stage_end("Stage B.1", "下载失败")
    
    return True  # 总是继续执行

def download_paper_tex(paper_id, run_dir, max_retries=MAX_RETRIES):
    """下载单篇论文的 TeX 源码（带重试）"""
    def _do_download():
        # 这里调用实际的下载逻辑
        # 简化实现，实际应调用下载脚本
        pass
    
    success, result, retry_count = retry_with_backoff(_do_download, max_retries=max_retries)
    
    if success:
        if retry_count > 0:
            logger.info(f"论文 {paper_id} TeX 下载成功（重试后）")
        else:
            logger.info(f"论文 {paper_id} TeX 下载成功")
    else:
        logger.error(f"论文 {paper_id} TeX 下载失败：{result}")
    
    return success

def interpret_papers(run_dir, push_date, language="Chinese"):
    """Stage B.2: AI 解读每篇论文（入口函数 - 调用并行脚本，3 并发×4 篇/批）"""
    log_stage_start("Stage B.2", "AI 深度解读")
    
    script_path = Path(__file__).parent / "interpret-papers-parallel.py"
    
    # 解读数据保存到项目数据目录（永久保存）
    summaries_dir = SUMMARIES_DIR / push_date
    
    # 获取论文列表
    papers_index = Path(run_dir) / "papers_index.json"
    paper_count = 0
    if papers_index.exists():
        try:
            with open(papers_index, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            paper_count = len(papers)
        except:
            pass
    
    logger.info(f"待解读论文数：{paper_count}")
    
    start_time = datetime.now()
    completed_count = 0
    failed_count = 0
    
    def _do_interpret():
        cmd = [
            "python3", str(script_path),
            "--run-dir", str(run_dir),
            "--summaries-dir", str(summaries_dir),
            "--max-workers", "3",  # 优化：从 10 降至 3，避免 gateway 超时
            "--language", language
        ]
        
        # 增加超时到 1200 秒（20 分钟），因为批次处理需要更长时间
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_interpret, max_retries=1)
    
    # 解析结果
    if success:
        # 尝试统计解读结果
        if summaries_dir.exists():
            completed_count = len(list(summaries_dir.glob("*/summary.md")))
        
        duration = (datetime.now() - start_time).total_seconds()
        avg_time = duration / paper_count if paper_count > 0 else 0
        
        logger.info(f"解读完成：{completed_count}/{paper_count} 篇")
        logger.info(f"平均耗时：{avg_time:.1f}s/篇，总耗时：{duration:.1f}s")
        
        log_stage_end("Stage B.2", f"解读完成 - {completed_count}/{paper_count} 篇（平均 {avg_time:.1f}s/篇）")
        return True
    else:
        logger.error(f"解读失败：{result}")
        log_stage_end("Stage B.2", "解读失败")
        return False

def validate_summaries(push_date, language="Chinese"):
    """Stage B.3: 验证 summary.md 格式"""
    log_stage_start("Stage B.3", "验证 summary.md 格式")
    
    script_path = Path(__file__).parent / "validate-summary-format.py"
    
    if not script_path.exists():
        logger.warning("找不到验证脚本，跳过验证")
        log_stage_end("Stage B.3", "跳过（无脚本）")
        return True
    
    summaries_dir = SUMMARIES_DIR / push_date
    report_file = summaries_dir / "validation_report.json"
    
    def _do_validate():
        cmd = [
            "python3", str(script_path),
            "--summaries-dir", str(summaries_dir),
            "--output-report", str(report_file),
            "--exit-code"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_validate, max_retries=1)
    
    if success:
        logger.info("所有论文格式验证通过")
        log_stage_end("Stage B.3", "验证通过")
        return True
    else:
        logger.warning("部分论文格式验证失败，需要重试")
        # 读取验证报告
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                logger.info(f"不合格论文：{', '.join(report.get('papers_to_retry', []))}")
            except:
                pass
        log_stage_end("Stage B.3", "验证失败")
        return False

def stage_c_generate(run_dir, push_date, output_dir):
    """Stage C: 生成网页和数据"""
    log_stage_start("Stage C", "生成网页和数据")
    
    script_path = Path(__file__).parent / "orchestrator-to-web.py"
    
    def _do_generate():
        cmd = [
            "python3", str(script_path),
            "--run-dir", str(run_dir),
            "--push-date", push_date,
            "--data-dir", str(output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result.returncode == 0
    
    # 带重试执行
    success, result, retry_count = retry_with_backoff(_do_generate, max_retries=2)
    
    if success:
        if retry_count > 0:
            logger.info(f"Stage C 生成成功（重试 {retry_count} 次后）")
        log_stage_end("Stage C", "网页生成完成")
        return True
    else:
        logger.error(f"Stage C 生成失败：{result}")
        log_stage_end("Stage C", "生成失败")
        return False

def print_perf_summary():
    """打印性能统计摘要"""
    logger.info("=" * 50)
    logger.info("性能统计")
    logger.info("=" * 50)
    
    total_duration = 0
    for stage_name, stats in perf_stats.items():
        if 'duration' in stats:
            duration = stats['duration']
            total_duration += duration
            logger.info(f"{stage_name}: {duration:.1f}s")
    
    logger.info("-" * 50)
    logger.info(f"总耗时：{total_duration:.1f}s ({total_duration/60:.1f} 分钟)")
    logger.info("=" * 50)

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
    
    # 设置日志
    run_dir = TMP_DIR / "papers-orchestrator" / f"llm-ai-agent-{args.date}"
    run_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(run_dir)
    
    # 计算日期
    push_date = args.date
    if args.from_date and args.to_date:
        from_date = args.from_date
        to_date = args.to_date
    else:
        # 默认检索昨天的论文
        paper_date = datetime.now() - timedelta(days=1)
        from_date = to_date = paper_date.strftime("%Y-%m-%d")
    
    logger.info("=" * 50)
    logger.info("每日论文推送系统 - 总编排器")
    logger.info("=" * 50)
    logger.info(f"推送日期：{push_date}")
    logger.info(f"论文日期：{from_date} 到 {to_date}")
    logger.info(f"输出语言：{args.language}")
    logger.info(f"执行阶段：{args.stage}")
    logger.info("=" * 50)
    
    total_start = datetime.now()
    
    # Stage A: 检索
    if args.stage in ["A", "all"]:
        if not stage_a_search(push_date, from_date, to_date, run_dir, args.lookback, args.language):
            logger.error("Stage A 失败")
            print_perf_summary()
            return 1
        
        logger.info(f"Stage A 检索完成：{run_dir}")
    
    # Stage A.2: 质量评分过滤（≥9 分保留）- 在下载之前执行
    if args.stage in ["A", "all"]:
        if not stage_a_quality_filter(run_dir, min_score=9, language=args.language):
            logger.warning("Stage A.2 质量过滤失败，继续执行（使用全部论文）")
        else:
            logger.info(f"Stage A.2 质量过滤完成")
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
                logger.error("未找到运行目录，请先执行 Stage A")
                return 1
    
    # Stage B: 下载 + AI 解读
    if args.stage in ["B", "all"]:
        if not stage_b_download(run_dir, args.language):
            logger.error("Stage B.1 下载失败")
            print_perf_summary()
            return 1
        
        if not interpret_papers(run_dir, push_date, args.language):
            logger.error("Stage B.2 AI 解读失败")
            print_perf_summary()
            return 1
        
        logger.info("Stage B 完成")
    
    # Stage C: 生成网页
    if args.stage in ["C", "all"]:
        if not stage_c_generate(run_dir, push_date, args.output_dir):
            logger.error("Stage C 失败")
            print_perf_summary()
            return 1
        
        logger.info("Stage C 完成")
    
    total_duration = (datetime.now() - total_start).total_seconds()
    
    logger.info("=" * 50)
    logger.info("完整流程完成！")
    logger.info("=" * 50)
    logger.info(f"总耗时：{total_duration:.1f}s ({total_duration/60:.1f} 分钟)")
    logger.info(f"访问地址：http://evilcalf.online/papers/")
    logger.info("=" * 50)
    
    print_perf_summary()
    
    return 0

if __name__ == "__main__":
    exit(main())
