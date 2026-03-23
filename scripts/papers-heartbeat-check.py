#!/usr/bin/env python3
"""
papers-heartbeat-check.py - HEARTBEAT 论文推送检查脚本（备份机制）

检查逻辑：
1. 如果推送已完成 → 跳过
2. 如果无新论文标记 → 生成空页面
3. 如果有编排器输出但未生成网页 → 调用 generate-daily.sh
4. 如果都没有 → 等待 cron 执行
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_DIR = "/root/.openclaw/workspace/projects/papers-daily"
WORKSPACE = "/root/.openclaw/workspace"

# 路径配置
SCRIPTS_DIR = f"{PROJECT_DIR}/scripts"
TMP_DIR = f"{WORKSPACE}/tmp"
NGINX_PAPERS = "/etc/nginx/html/papers"

def get_push_date():
    """获取推送日期（今天）"""
    return datetime.now().strftime("%Y-%m-%d")

def log(message):
    """日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def check_push_done(push_date):
    """检查推送是否已完成"""
    done_file = f"{TMP_DIR}/papers-done/{push_date}.json"
    if os.path.exists(done_file):
        log(f"✅ 推送已完成：{done_file}")
        return True
    return False

def check_no_new_papers(push_date):
    """检查是否标记为无新论文"""
    no_new_file = f"{TMP_DIR}/papers-no-new-{push_date}.json"
    if os.path.exists(no_new_file):
        log(f"✅ 发现无新论文标记：{no_new_file}")
        with open(no_new_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def find_orchestrator_dir_for_date(push_date):
    """查找指定推送日期的编排器输出目录"""
    orchestrator_dir = f"{TMP_DIR}/papers-orchestrator"
    if not os.path.exists(orchestrator_dir):
        return None
    
    # 查找包含推送日期的目录
    dirs = [d for d in Path(orchestrator_dir).iterdir() if d.is_dir()]
    
    for d in dirs:
        # 检查目录名是否包含推送日期
        if push_date in d.name:
            if (d / "papers_index.json").exists():
                return str(d)
    
    return None

def generate_empty_webpage(push_date, paper_date):
    """生成无新论文的空页面"""
    log("📄 生成无新论文空页面...")
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日论文推送 {push_date} - 无新论文</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --primary: #a855f7;
            --secondary: #6366f1;
            --accent: #ec4899;
            --glow: #c084fc;
            --bg-dark: #0f0c29;
            --card-bg: rgba(30, 30, 50, 0.8);
        }}
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #fff;
            padding: 40px 20px;
        }}
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
            padding: 60px 20px;
        }}
        .emoji {{
            font-size: 5em;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #fff, var(--glow), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        p {{
            font-size: 1.2em;
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.8;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 40px;
            margin-top: 40px;
            border: 1px solid rgba(168, 85, 247, 0.3);
            backdrop-filter: blur(10px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">😅</div>
        <h1>今天没有新论文</h1>
        <div class="card">
            <p>arXiv 今天没有新的 <strong>LLM / AI Agent / Transformer / Attention</strong> 相关论文发布。</p>
            <p style="margin-top: 20px;">明天再来看看吧～</p>
        </div>
    </div>
</body>
</html>
'''
    
    # 写入文件
    html_file = f"{NGINX_PAPERS}/{push_date}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 更新 reports.json
    reports_file = Path(NGINX_PAPERS) / "reports.json"
    if reports_file.exists():
        with open(reports_file, 'r', encoding='utf-8') as f:
            reports = json.load(f)
    else:
        reports = []
    
    # 移除同日期记录
    reports = [r for r in reports if r['date'] != push_date]
    
    # 添加无论文记录
    reports.insert(0, {
        'date': push_date,
        'paper_date': paper_date,
        'count': 0,
        'llm_count': 0,
        'agent_count': 0,
        'data_file': 'data/empty.json',
        'detail_url': f'detail.html?date={push_date}',
        'is_empty': True
    })
    
    # 保留最近 30 条
    reports = reports[:30]
    
    with open(reports_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    # 创建空数据文件
    data_dir = Path(NGINX_PAPERS) / "data"
    data_dir.mkdir(exist_ok=True)
    empty_data = {
        'push_date': push_date,
        'total_count': 0,
        'category_count': 0,
        'categories': []
    }
    with open(data_dir / f"{push_date}.json", 'w', encoding='utf-8') as f:
        json.dump(empty_data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 空页面已生成：{html_file}")
    
    # 创建完成标记
    mark_push_done(push_date, paper_date=paper_date, count=0)
    
    # 清理无新论文标记
    os.remove(f"{TMP_DIR}/papers-no-new-{push_date}.json")
    log(f"✅ 已清理无新论文标记")

def mark_push_done(push_date, paper_date=None, count=0):
    """标记推送已完成"""
    done_dir = f"{TMP_DIR}/papers-done"
    os.makedirs(done_dir, exist_ok=True)
    done_file = f"{done_dir}/{push_date}.json"
    
    data = {
        'date': push_date,
        'status': 'success',
        'completed_at': datetime.now().isoformat(),
        'count': count,
        'triggered_by': 'heartbeat'
    }
    
    if paper_date:
        data['paper_date'] = paper_date
    
    with open(done_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 已标记推送完成：{done_file}")

def execute_generate_script(push_date, run_dir):
    """调用 generate-daily.sh 生成网页"""
    log(f"🚀 调用 generate-daily.sh 生成网页...")
    
    cmd = [
        'bash',
        f'{SCRIPTS_DIR}/generate-daily.sh',
        push_date,
        run_dir
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        log(f"✅ 网页生成成功")
        
        # 更新完成标记为 heartbeat 触发
        with open(f"{TMP_DIR}/papers-done/{push_date}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['triggered_by'] = 'heartbeat'
        with open(f"{TMP_DIR}/papers-done/{push_date}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    else:
        log(f"❌ 网页生成失败")
        return False

def main():
    push_date = get_push_date()
    
    log(f"📅 推送日期：{push_date}")
    log(f"📅 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否周末（周六=5，周日=6）
    day_of_week = datetime.now().weekday()
    if day_of_week >= 5:
        log(f"🎉 周末时间，跳过推送（arXiv 周末不更新论文）")
        log(f"💤 下周一再见～")
        return
    
    print()
    
    # 检查 1: 推送是否已完成
    if check_push_done(push_date):
        log(f"\n✅ 今日推送已完成，跳过")
        return
    
    # 检查 2: 是否标记为无新论文
    no_new_data = check_no_new_papers(push_date)
    if no_new_data:
        log(f"\n📋 场景：无新论文，生成空页面...")
        paper_date = no_new_data.get('paper_date', push_date)
        generate_empty_webpage(push_date, paper_date)
        return
    
    # 检查 3: 查找编排器输出（必须日期匹配）
    run_dir = find_orchestrator_dir_for_date(push_date)
    if run_dir:
        log(f"\n📋 场景：发现编排器输出，生成网页...")
        log(f"运行目录：{run_dir}")
        
        # 检查是否已有网页
        data_file = f"{NGINX_PAPERS}/data/{push_date}.json"
        if os.path.exists(data_file):
            log(f"⚠️  网页已存在：{data_file}")
            log(f"💡 可能是 cron 已执行但完成标记丢失")
            # 创建完成标记
            with open(f"{run_dir}/papers_index.json", 'r', encoding='utf-8') as f:
                papers = json.load(f)
            mark_push_done(push_date, count=len(papers))
            return
        
        # 执行生成脚本
        success = execute_generate_script(push_date, run_dir)
        if success:
            log(f"\n✅ 网页生成完成")
        else:
            log(f"\n⚠️  网页生成失败，等待下次重试")
        return
    
    # 检查 3b: 如果有其他日期的编排器输出，可能是日期不匹配
    orchestrator_dir = f"{TMP_DIR}/papers-orchestrator"
    if os.path.exists(orchestrator_dir):
        dirs = [d for d in Path(orchestrator_dir).iterdir() if d.is_dir() and (d / "papers_index.json").exists()]
        if dirs:
            log(f"\n⚠️  发现其他日期的编排器输出，但不匹配今日推送日期 {push_date}")
            for d in dirs:
                log(f"  - {d.name}")
            log(f"💡 等待 cron 在 23:00 执行检索 {push_date} 的论文")
            return
    
    # 检查 4: 都没有
    log(f"\n📋 场景：编排器输出不存在")
    log(f"💡 可能 cron 还未执行（23:00）或执行失败")
    log(f"💡 等待下次 heartbeat 检查或手动触发")

def send_notification(push_date, count, status):
    """发送通知消息（可选）"""
    # 这个函数可以通过 message 工具发送通知
    # 但目前脚本模式不直接调用，由 heartbeat 主逻辑处理
    pass

if __name__ == "__main__":
    main()
