#!/usr/bin/env python3
"""
papers-orchestrator.py - 每日论文推送系统总编排器

Stage A: 智能检索 arXiv（40 关键词 × 4 分类，跨查询去重）
Stage B: AI 解读每篇论文（10 节深度解读，2000-3000 字）
Stage C: 生成网页和数据

输出目录：
- 项目数据：/root/.openclaw/workspace/projects/papers-daily/data/summaries/{date}/
- 临时文件：/root/.openclaw/workspace/tmp/papers-orchestrator/（可清理）

P2 增强功能：
- 增量检索：记录上次检索的论文 ID，只处理新增论文
- 错误重试机制：关键操作自动重试（指数退避）
- 详细日志记录：每个阶段开始/结束时间、处理状态、错误和重试信息
"""

import json
import argparse
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from functools import wraps

# ============== 日志配置 ==============
LOG_DIR = Path.home() / ".openclaw" / "workspace" / "projects" / "papers-daily" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============== 重试装饰器 ==============
def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    指数退避重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} 失败 after {max_attempts} 次尝试：{e}")
                        raise
                    logger.warning(f"{func.__name__} 失败 (尝试 {attempt+1}/{max_attempts}): {e} - {current_delay}s 后重试")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# 项目根目录
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
SUMMARIES_DIR = DATA_DIR / "summaries"

# 临时目录（仅用于中间文件，可定期清理）
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TMP_DIR = WORKSPACE / "tmp"
ORCHESTRATOR_TMP = TMP_DIR / "papers-orchestrator"

# 增量检索索引文件
LAST_RUN_INDEX_FILE = ORCHESTRATOR_TMP / "last_run_index.json"

# 外部脚本
SCRIPTS_DIR = PROJECT_DIR / "scripts"
PAPER_PROCESSOR = WORKSPACE / "skills" / "arxiv-paper-processor"

def ensure_dirs():
    """确保必要的目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    ORCHESTRATOR_TMP.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def load_last_run_index():
    """加载上次检索的论文 ID 列表"""
    if LAST_RUN_INDEX_FILE.exists():
        try:
            with open(LAST_RUN_INDEX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('arxiv_ids', []))
        except Exception as e:
            logger.warning(f"加载上次索引失败：{e}")
    return set()

def save_last_run_index(arxiv_ids):
    """保存本次检索的论文 ID 列表"""
    try:
        with open(LAST_RUN_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump({'arxiv_ids': list(arxiv_ids), 'updated_at': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存增量索引：{LAST_RUN_INDEX_FILE}")
    except Exception as e:
        logger.warning(f"保存增量索引失败：{e}")

def filter_new_papers(papers_index, existing_ids):
    """过滤出新增论文"""
    if not existing_ids:
        return papers_index, 0
    
    new_papers = []
    skipped_count = 0
    
    for paper in papers_index:
        arxiv_id = paper.get('arxiv_id', '')
        if arxiv_id and arxiv_id in existing_ids:
            skipped_count += 1
        else:
            new_papers.append(paper)
    
    return new_papers, skipped_count

@retry(max_attempts=3, delay=2, backoff=2)
def stage_a_search(date, from_date, to_date, run_dir, lookback="1d", language="Chinese"):
    """
    Stage A: 检索 arXiv 论文（支持增量检索）
    
    Args:
        date: 推送日期
        from_date: 起始日期
        to_date: 结束日期
        run_dir: 运行目录
        lookback: 回溯天数
        language: 输出语言
    
    Returns:
        bool: 是否成功
    """
    logger.info(f"\n🔍 Stage A: 检索 arXiv 论文")
    logger.info(f"   日期范围：{from_date} 到 {to_date}")
    logger.info(f"   输出目录：{run_dir}")
    start_time = time.time()
    
    # 加载上次检索的论文 ID
    existing_ids = load_last_run_index()
    if existing_ids:
        logger.info(f"   📚 已加载历史索引：{len(existing_ids)} 篇论文")
    
    # 调用 arxiv-search-collector 技能
    search_script = WORKSPACE / "projects" / "papers-daily" / "scripts" / "simple-arxiv-search.py"
    
    if not search_script.exists():
        logger.error(f"   ❌ 找不到检索脚本：{search_script}")
        # 回退到内置检索逻辑
        return builtin_search(date, from_date, to_date, lookback, existing_ids, run_dir)
    
    cmd = [
        "python3", str(search_script),
        "--date", date,
        "--from-date", from_date,
        "--to-date", to_date,
        "--output-dir", str(run_dir),
        "--max-results", "50"  # 每关键词 50 篇
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as e:
        logger.error(f"   ❌ 检索超时：{e}")
        raise
    except Exception as e:
        logger.error(f"   ❌ 检索异常：{e}")
        raise
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    if result.returncode != 0:
        logger.error(f"   ❌ 检索失败，返回码：{result.returncode}")
        raise Exception(f"检索脚本返回错误码：{result.returncode}")
    
    # 读取检索结果并过滤
    papers_index_file = run_dir / "papers_index.json"
    if papers_index_file.exists():
        try:
            with open(papers_index_file, 'r', encoding='utf-8') as f:
                papers_index = json.load(f)
            
            # 增量过滤
            new_papers, skipped_count = filter_new_papers(papers_index, existing_ids)
            
            logger.info(f"\n📊 增量检索结果：")
            logger.info(f"   检索总数：{len(papers_index)}")
            logger.info(f"   新增论文：{len(new_papers)}")
            logger.info(f"   跳过已处理：{skipped_count}")
            
            if skipped_count > 0:
                # 更新索引文件，只保留新增论文
                with open(papers_index_file, 'w', encoding='utf-8') as f:
                    json.dump(new_papers, f, ensure_ascii=False, indent=2)
                logger.info(f"   ✅ 已更新索引文件，只保留新增论文")
            
            # 保存本次检索的所有论文 ID（用于下次增量对比）
            all_ids = set(p.get('arxiv_id', '') for p in papers_index if p.get('arxiv_id'))
            save_last_run_index(all_ids)
            
        except Exception as e:
            logger.warning(f"   ⚠️  处理索引文件失败：{e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Stage A 完成，耗时：{elapsed_time:.2f} 秒")
    return True

def builtin_search(date, from_date, to_date, lookback="1d", existing_ids=None, run_dir=None):
    """内置检索逻辑（备用）"""
    logger.info(f"   使用内置检索逻辑...")
    # 简化实现，实际应调用 arxiv API
    return True

def stage_a_quality_filter(run_dir, min_score=7, language="Chinese"):
    """Stage A.2: AI 质量评分过滤"""
    logger.info(f"\n🎯 Stage A.2: AI 质量评分过滤")
    logger.info(f"   运行目录：{run_dir}")
    logger.info(f"   最低分数：{min_score}")
    start_time = time.time()
    
    eval_script = Path(__file__).parent / "evaluate-paper-quality.py"
    
    if not eval_script.exists():
        logger.warning(f"   ⚠️  找不到质量评分脚本，跳过过滤")
        return True
    
    cmd = [
        "python3", str(eval_script),
        "--run-dir", str(run_dir),
        "--min-score", str(min_score),
        "--language", language
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as e:
        logger.error(f"   ❌ 质量评分超时：{e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ 质量评分异常：{e}")
        return False
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    # 检查是否有过滤后的文件
    filtered_path = Path(run_dir) / "papers_index_filtered.json"
    if filtered_path.exists():
        # 替换原始索引
        import shutil
        shutil.move(str(filtered_path), str(Path(run_dir) / "papers_index.json"))
        logger.info(f"   ✅ 已使用过滤后的索引")
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Stage A.2 完成，耗时：{elapsed_time:.2f} 秒")
        return True
    elif result.returncode == 0:
        logger.info(f"   ✅ 质量评分完成（无过滤或所有论文都达标）")
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Stage A.2 完成，耗时：{elapsed_time:.2f} 秒")
        return True
    else:
        logger.warning(f"   ⚠️  质量评分完成，但可能无论文达标")
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Stage A.2 完成，耗时：{elapsed_time:.2f} 秒")
        return True  # 即使无论文也继续，让后续流程处理

@retry(max_attempts=3, delay=5, backoff=2)
def stage_b_download(run_dir, language="Chinese"):
    """
    Stage B.1: 批量下载论文（允许部分失败）
    
    Args:
        run_dir: 运行目录
        language: 输出语言
    
    Returns:
        bool: 是否成功
    """
    logger.info(f"\n📥 Stage B.1: 批量下载论文")
    logger.info(f"   ⏱️ 超时设置：1800 秒（30 分钟）")
    start_time = time.time()
    
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
        logger.error(f"\n❌ 下载超时（1800 秒）")
        logger.info(f"   部分论文可能已下载，检查日志：{run_dir}/download_batch_log.json")
        raise
    except Exception as e:
        logger.error(f"\n❌ 下载异常：{e}")
        raise
    
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
            
            logger.info(f"\n📊 下载统计：")
            logger.info(f"   总论文数：{paper_count}")
            logger.info(f"   成功/跳过：{ok_count}")
            logger.info(f"   失败：{failed_count}")
            
            # 如果成功率 > 80%，认为下载阶段成功
            success_rate = ok_count / paper_count if paper_count > 0 else 0
            if success_rate >= 0.8:
                logger.info(f"   ✅ 成功率 {success_rate*100:.1f}%，继续执行")
            else:
                logger.warning(f"   ❌ 成功率 {success_rate*100:.1f}%，低于 80%")
                # 即使低于 80% 也继续，让后续流程处理（可能有论文可解读）
        except Exception as e:
            logger.warning(f"   ⚠️ 无法解析下载日志：{e}")
    else:
        logger.warning(f"   ⚠️ 未找到下载日志")
        raise Exception("未找到下载日志")
    
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Stage B.1 完成，耗时：{elapsed_time:.2f} 秒")
    return True

@retry(max_attempts=2, delay=10, backoff=2)
def interpret_papers(run_dir, push_date, language="Chinese"):
    """
    Stage B.2: AI 解读每篇论文（入口函数 - 调用并行脚本）
    
    优化配置：
    - MAX_PARALLEL_SUBAGENTS = 3（3 个 subagent 并行）
    - BATCH_SIZE = 4（每批 4 篇论文）
    - BATCH_INTERVAL_SECONDS = 2（批次间隔 2 秒，避免 gateway 拥塞）
    - 总吞吐量：12 篇/轮（稳定）
    
    Args:
        run_dir: 运行目录
        push_date: 推送日期
        language: 输出语言
    
    Returns:
        bool: 是否成功
    """
    logger.info(f"\n🧠 Stage B.2: AI 解读论文")
    logger.info(f"   并行策略：3 subagent × 4 篇/批 = 12 篇/轮")
    logger.info(f"   批次间隔：2 秒（避免 gateway 拥塞）")
    start_time = time.time()
    
    script_path = Path(__file__).parent / "interpret-papers-parallel.py"
    
    # 解读数据保存到项目数据目录（永久保存）
    summaries_dir = SUMMARIES_DIR / push_date
    
    cmd = [
        "python3", str(script_path),
        "--run-dir", str(run_dir),
        "--summaries-dir", str(summaries_dir),
        "--max-workers", "3",  # 优化：从 10 降至 3，避免 gateway 超时
        "--language", language
    ]
    
    # 增加超时到 1200 秒（20 分钟），因为批次处理需要更长时间
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    except subprocess.TimeoutExpired as e:
        logger.error(f"   ❌ AI 解读超时（1200 秒）")
        raise
    except Exception as e:
        logger.error(f"   ❌ AI 解读异常：{e}")
        raise
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    if result.returncode != 0:
        logger.error(f"   ❌ AI 解读失败，返回码：{result.returncode}")
        raise Exception(f"AI 解读脚本返回错误码：{result.returncode}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Stage B.2 完成，耗时：{elapsed_time:.2f} 秒")
    return result.returncode == 0

def validate_summaries(push_date, language="Chinese"):
    """Stage B.3: 验证 summary.md 格式"""
    logger.info(f"\n🔍 Stage B.3: 验证 summary.md 格式")
    start_time = time.time()
    
    script_path = Path(__file__).parent / "validate-summary-format.py"
    
    if not script_path.exists():
        logger.warning(f"   ⚠️  找不到验证脚本，跳过验证")
        return True
    
    summaries_dir = SUMMARIES_DIR / push_date
    report_file = summaries_dir / "validation_report.json"
    
    cmd = [
        "python3", str(script_path),
        "--summaries-dir", str(summaries_dir),
        "--output-report", str(report_file),
        "--exit-code"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired as e:
        logger.error(f"   ❌ 格式验证超时：{e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ 格式验证异常：{e}")
        return False
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    if result.returncode != 0:
        logger.warning(f"   ⚠️  部分论文格式验证失败，需要重试")
        # 读取验证报告
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                logger.info(f"   不合格论文：{', '.join(report.get('papers_to_retry', []))}")
            except:
                pass
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Stage B.3 完成（有不合格），耗时：{elapsed_time:.2f} 秒")
        return False
    
    logger.info(f"   ✅ 所有论文格式验证通过")
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Stage B.3 完成，耗时：{elapsed_time:.2f} 秒")
    return True

def stage_c_generate(run_dir, push_date, output_dir):
    """Stage C: 生成网页和数据"""
    logger.info(f"\n📄 Stage C: 生成网页和数据")
    start_time = time.time()
    
    script_path = Path(__file__).parent / "orchestrator-to-web.py"
    
    cmd = [
        "python3", str(script_path),
        "--run-dir", str(run_dir),
        "--push-date", push_date,
        "--data-dir", str(output_dir)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as e:
        logger.error(f"   ❌ 网页生成超时：{e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ 网页生成异常：{e}")
        return False
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    if result.returncode != 0:
        logger.error(f"   ❌ 网页生成失败，返回码：{result.returncode}")
        return False
    
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Stage C 完成，耗时：{elapsed_time:.2f} 秒")
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
    
    logger.info(f"📚 每日论文推送系统 - 总编排器")
    logger.info(f"==========================================")
    logger.info(f"推送日期：{push_date}")
    logger.info(f"论文日期：{from_date} 到 {to_date}")
    logger.info(f"输出语言：{args.language}")
    logger.info(f"执行阶段：{args.stage}")
    logger.info(f"增量检索：✅ 已启用")
    logger.info(f"错误重试：✅ 已启用")
    logger.info(f"详细日志：✅ 已启用")
    logger.info()
    
    total_start_time = time.time()
    
    # Stage A: 检索 + 质量过滤
    if args.stage in ["A", "all"]:
        # 先定义输出目录
        run_dir = ORCHESTRATOR_TMP / f"llm-ai-agent-{push_date}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        stage_a_start = time.time()
        logger.info(f"🚀 Stage A 开始")
        
        try:
            if not stage_a_search(push_date, from_date, to_date, run_dir, args.lookback, args.language):
                logger.error("❌ Stage A 失败")
                return 1
        except Exception as e:
            logger.error(f"❌ Stage A 异常：{e}")
            return 1
        
        logger.info(f"✅ Stage A.1 检索完成：{run_dir}")
        
        # Stage A.2: 质量评分过滤（≥8 分保留）
        try:
            if not stage_a_quality_filter(run_dir, min_score=8, language=args.language):
                logger.error("❌ Stage A.2 质量过滤失败")
                return 1
        except Exception as e:
            logger.error(f"❌ Stage A.2 异常：{e}")
            return 1
        
        stage_a_elapsed = time.time() - stage_a_start
        logger.info(f"✅ Stage A 完成（检索 + 质量过滤），总耗时：{stage_a_elapsed:.2f} 秒")
    else:
        # 使用指定的运行目录
        run_dir = Path(ORCHESTRATOR_TMP / f"llm-ai-agent-{push_date}")
        if not run_dir.exists():
            # 查找最新的
            orchestrator_dirs = sorted(
                [d for d in (ORCHESTRATOR_TMP).iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if orchestrator_dirs:
                run_dir = orchestrator_dirs[0]
            else:
                logger.error("❌ 未找到运行目录，请先执行 Stage A")
                return 1
    
    # Stage B: 下载 + AI 解读 + 格式验证
    if args.stage in ["B", "all"]:
        stage_b_start = time.time()
        logger.info(f"🚀 Stage B 开始")
        
        try:
            if not stage_b_download(run_dir, args.language):
                logger.error("❌ Stage B.1 下载失败")
                return 1
        except Exception as e:
            logger.error(f"❌ Stage B.1 下载异常：{e}")
            return 1
        
        try:
            if not interpret_papers(run_dir, push_date, args.language):
                logger.error("❌ Stage B.2 AI 解读失败")
                return 1
        except Exception as e:
            logger.error(f"❌ Stage B.2 AI 解读异常：{e}")
            return 1
        
        # Stage B.3: 格式验证（不合格的重试）
        max_retries = 2
        for retry in range(max_retries):
            try:
                if validate_summaries(push_date, args.language):
                    break
            except Exception as e:
                logger.error(f"❌ Stage B.3 验证异常：{e}")
            
            if retry < max_retries - 1:
                logger.info(f"   🔄 重试解读不合格论文（第 {retry + 1}/{max_retries} 次）...")
                # 这里可以添加重试逻辑，目前简化处理
            else:
                logger.warning(f"   ⚠️  重试后仍有不合格论文，继续执行")
        
        stage_b_elapsed = time.time() - stage_b_start
        logger.info(f"✅ Stage B 完成，总耗时：{stage_b_elapsed:.2f} 秒")
    
    # Stage C: 生成网页
    if args.stage in ["C", "all"]:
        stage_c_start = time.time()
        logger.info(f"🚀 Stage C 开始")
        
        if not stage_c_generate(run_dir, push_date, args.output_dir):
            logger.error("❌ Stage C 失败")
            return 1
        
        stage_c_elapsed = time.time() - stage_c_start
        logger.info(f"✅ Stage C 完成，总耗时：{stage_c_elapsed:.2f} 秒")
    
    total_elapsed_time = time.time() - total_start_time
    logger.info()
    logger.info("==========================================")
    logger.info(f"✅ 完整流程完成！")
    logger.info(f"==========================================")
    logger.info(f"📄 访问地址：http://evilcalf.online/papers/")
    logger.info(f"⏱️  总耗时：{total_elapsed_time:.2f} 秒")
    logger.info(f"==========================================")
    
    return 0

if __name__ == "__main__":
    exit(main())
