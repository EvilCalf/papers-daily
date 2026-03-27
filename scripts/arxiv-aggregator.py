#!/usr/bin/env python3
"""
arxiv-aggregator.py - 汇总论文解读并生成网页（带目录导航）
用法：python3 arxiv-aggregator.py --date 2026-03-12 --push-date 2026-03-13 --input-dir ./summaries --output-json out.json --output-html out.html
"""

import json
import argparse
import os
from datetime import datetime
from pathlib import Path

def markdown_to_html(text):
    """简单的 markdown 转 HTML 转换"""
    if not text:
        return ''
    
    import re
    
    # 处理粗体 **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # 处理斜体 *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # 处理换行：单个换行转为空格，保持段落紧凑
    text = text.replace('\n', ' ')
    # 压缩多个空格为单个
    text = re.sub(r'\s+', ' ', text)
    
    return text

def generate_empty_html(push_date, paper_date, is_weekend=False):
    """生成无新论文的 HTML 网页（深色渐变 + 粒子动画风格）"""
    if is_weekend:
        title = "🌙 周末无更新"
        message = "arXiv 周末不发布新论文（周六、周日无更新），周二再来查看吧～"
        icon = "🌙"
    else:
        title = "😅 今天没有新论文"
        message = "arXiv 今天没有新的 LLM/Agent 相关论文发布，明天再来看看吧～"
        icon = "😅"
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日论文推送 {push_date} - EvilCalf</title>
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
        
        .particles {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        }}
        
        .particle {{
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(168, 85, 247, 0.6);
            border-radius: 50%;
            animation: float 15s infinite ease-in-out;
            box-shadow: 0 0 10px var(--glow), 0 0 20px var(--primary);
        }}
        
        .particle:nth-child(2) {{ left: 20%; animation-delay: -2s; animation-duration: 12s; }}
        .particle:nth-child(3) {{ left: 40%; animation-delay: -4s; animation-duration: 18s; }}
        .particle:nth-child(4) {{ left: 60%; animation-delay: -6s; animation-duration: 14s; }}
        .particle:nth-child(5) {{ left: 80%; animation-delay: -8s; animation-duration: 16s; }}
        .particle:nth-child(6) {{ left: 10%; animation-delay: -3s; animation-duration: 20s; background: rgba(236, 72, 153, 0.5); }}
        .particle:nth-child(7) {{ left: 30%; animation-delay: -5s; animation-duration: 13s; background: rgba(99, 102, 241, 0.5); }}
        .particle:nth-child(8) {{ left: 50%; animation-delay: -7s; animation-duration: 17s; }}
        .particle:nth-child(9) {{ left: 70%; animation-delay: -1s; animation-duration: 11s; background: rgba(236, 72, 153, 0.5); }}
        .particle:nth-child(10) {{ left: 90%; animation-delay: -9s; animation-duration: 19s; background: rgba(99, 102, 241, 0.5); }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(100vh) scale(0);
                opacity: 0;
            }}
            10% {{ opacity: 1; transform: translateY(90vh) scale(1); }}
            90% {{ opacity: 1; transform: translateY(10vh) scale(1); }}
            100% {{
                transform: translateY(-10vh) scale(0);
                opacity: 0;
            }}
        }}
        
        .container {{
            position: relative;
            z-index: 1;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 40px;
            background: var(--card-bg);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}
        
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #fff, var(--glow), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 1em;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--primary);
            text-decoration: none;
            font-size: 1em;
            padding: 10px 20px;
            background: rgba(168, 85, 247, 0.15);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{
            background: rgba(168, 85, 247, 0.3);
            color: var(--glow);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4);
        }}
        
        .content {{
            background: var(--card-bg);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 40px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
        }}
        
        .empty-icon {{
            font-size: 5em;
            margin-bottom: 20px;
            filter: drop-shadow(0 0 20px var(--glow));
        }}
        
        .empty-title {{
            font-size: 1.8em;
            background: linear-gradient(135deg, #fff, var(--glow));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}
        
        .empty-message {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1em;
            line-height: 1.6;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9em;
        }}
        
        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .footer a:hover {{
            color: var(--glow);
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 20px 10px; }}
            .header h1 {{ font-size: 1.5em; }}
            .header {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>
    <!-- 粒子背景 -->
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📚 每日论文推送</h1>
            <p>📅 推送日期：{push_date} | 📄 论文日期：{paper_date}</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; margin-bottom: 30px;">
                <a href="/papers/" class="back-link">← 返回报告列表</a>
            </div>
            
            <div class="empty-state">
                <div class="empty-icon">{icon}</div>
                <div class="empty-title">{title}</div>
                <div class="empty-message">{message}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by <a href="/">EvilBot 😈</a> | Data from arXiv</p>
        </div>
    </div>
</body>
</html>'''
    return html

def generate_html(papers, push_date, paper_date):
    """生成 HTML 网页（带目录导航 - 深色渐变 + 粒子动画风格）"""
    llm_count = sum(1 for p in papers if p['topic'] == 'LLM')
    agent_count = sum(1 for p in papers if p['topic'] == 'Agent')
    
    # 生成目录项
    toc_items = ''
    for i, p in enumerate(papers, 1):
        tag_color = '#a855f7' if p['topic'] == 'LLM' else '#6366f1'
        toc_items += f'''
                <div class="toc-item">
                    <a href="#paper-{i}">
                        <span class="num">#{i}</span>
                        <span class="title">{p['title_en'][:50]}{'...' if len(p['title_en']) > 50 else ''}</span>
                        <span class="tag" style="background: {tag_color}">{p['topic']}</span>
                    </a>
                </div>'''
    
    # 生成论文卡片
    paper_cards = ''
    for i, p in enumerate(papers, 1):
        tag_color = '#a855f7' if p['topic'] == 'LLM' else '#6366f1'
        ai_summary = p.get('ai_summary', '')
        
        # 处理摘要中的 emoji 图标
        summary_html = ''
        if ai_summary:
            paragraphs = ai_summary.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    if para.startswith('🔬'):
                        summary_html += f'<div class="summary-section"><strong>🔬 研究背景</strong><p>{para[2:].strip()}</p></div>'
                    elif para.startswith('💡'):
                        summary_html += f'<div class="summary-section"><strong>💡 核心方法</strong><p>{para[2:].strip()}</p></div>'
                    elif para.startswith('📊'):
                        summary_html += f'<div class="summary-section"><strong>📊 主要发现</strong><p>{para[2:].strip()}</p></div>'
                    elif para.startswith('🎯'):
                        summary_html += f'<div class="summary-section"><strong>🎯 实际价值</strong><p>{para[2:].strip()}</p></div>'
                    elif para.startswith('⚠️'):
                        summary_html += f'<div class="summary-section"><strong>⚠️ 局限与未来</strong><p>{para[2:].strip()}</p></div>'
                    else:
                        summary_html += f'<p>{para}</p>'
        
        paper_cards += f'''
        <div class="paper-card" id="paper-{i}">
            <div class="paper-tag" style="background: {tag_color}">{p['topic']}</div>
            <h3 class="paper-title-en">{p['title_en']}</h3>
            <h4 class="paper-title-zh">{p.get('title_zh', '')}</h4>
            <div class="paper-meta">
                <span>👥 {p['authors']}</span>
                <span>🔗 <a href="{p['link']}" target="_blank" rel="noopener">arXiv 原文</a></span>
            </div>
            <div class="ai-summary">
                <div class="summary-title">🤖 AI 深度解读</div>
                {summary_html}
            </div>
        </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日论文推送 {push_date} - EvilCalf</title>
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
        
        .particles {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        }}
        
        .particle {{
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(168, 85, 247, 0.6);
            border-radius: 50%;
            animation: float 15s infinite ease-in-out;
            box-shadow: 0 0 10px var(--glow), 0 0 20px var(--primary);
        }}
        
        .particle:nth-child(2) {{ left: 20%; animation-delay: -2s; animation-duration: 12s; }}
        .particle:nth-child(3) {{ left: 40%; animation-delay: -4s; animation-duration: 18s; }}
        .particle:nth-child(4) {{ left: 60%; animation-delay: -6s; animation-duration: 14s; }}
        .particle:nth-child(5) {{ left: 80%; animation-delay: -8s; animation-duration: 16s; }}
        .particle:nth-child(6) {{ left: 10%; animation-delay: -3s; animation-duration: 20s; background: rgba(236, 72, 153, 0.5); }}
        .particle:nth-child(7) {{ left: 30%; animation-delay: -5s; animation-duration: 13s; background: rgba(99, 102, 241, 0.5); }}
        .particle:nth-child(8) {{ left: 50%; animation-delay: -7s; animation-duration: 17s; }}
        .particle:nth-child(9) {{ left: 70%; animation-delay: -1s; animation-duration: 11s; background: rgba(236, 72, 153, 0.5); }}
        .particle:nth-child(10) {{ left: 90%; animation-delay: -9s; animation-duration: 19s; background: rgba(99, 102, 241, 0.5); }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(100vh) scale(0);
                opacity: 0;
            }}
            10% {{ opacity: 1; transform: translateY(90vh) scale(1); }}
            90% {{ opacity: 1; transform: translateY(10vh) scale(1); }}
            100% {{
                transform: translateY(-10vh) scale(0);
                opacity: 0;
            }}
        }}
        
        .container {{
            position: relative;
            z-index: 1;
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 40px;
            background: var(--card-bg);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}
        
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #fff, var(--glow), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 1em;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--primary);
            text-decoration: none;
            font-size: 1em;
            padding: 10px 20px;
            background: rgba(168, 85, 247, 0.15);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{
            background: rgba(168, 85, 247, 0.3);
            color: var(--glow);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4);
        }}
        
        .content {{
            background: var(--card-bg);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 40px;
        }}
        
        .toc {{
            background: rgba(168, 85, 247, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(168, 85, 247, 0.2);
        }}
        
        .toc-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--glow);
            margin-bottom: 15px;
        }}
        
        .toc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}
        
        .toc-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 0.9em;
            transition: all 0.3s ease;
            border: 1px solid rgba(168, 85, 247, 0.2);
        }}
        
        .toc-item:hover {{
            background: rgba(168, 85, 247, 0.25);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
            border-color: var(--primary);
        }}
        
        .toc-item:hover a {{
            color: var(--glow);
        }}
        
        .toc-item a {{
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            display: block;
        }}
        
        .toc-item .num {{
            color: var(--accent);
            font-weight: 700;
            margin-right: 8px;
        }}
        
        .toc-item .title {{
            display: inline-block;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .toc-item .tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            color: white;
            margin-left: 8px;
        }}
        
        .paper-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            scroll-margin-top: 20px;
            border: 1px solid rgba(168, 85, 247, 0.2);
        }}
        
        .paper-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
            border-color: var(--primary);
        }}
        
        .paper-tag {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
            margin-bottom: 15px;
        }}
        
        .paper-title-en {{
            font-size: 1.3em;
            font-weight: 600;
            color: #fff;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .paper-title-zh {{
            font-size: 1.1em;
            color: var(--glow);
            margin-bottom: 15px;
            line-height: 1.4;
        }}
        
        .paper-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .paper-meta a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .paper-meta a:hover {{
            color: var(--glow);
            text-decoration: underline;
        }}
        
        .ai-summary {{
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid var(--primary);
            padding: 20px;
            border-radius: 0 8px 8px 0;
            margin-top: 20px;
        }}
        
        .summary-title {{
            font-size: 1em;
            font-weight: 600;
            color: var(--glow);
            margin-bottom: 15px;
        }}
        
        .summary-section {{
            margin-bottom: 15px;
        }}
        
        .summary-section:last-child {{
            margin-bottom: 0;
        }}
        
        .summary-section strong {{
            display: block;
            color: var(--accent);
            margin-bottom: 8px;
            font-size: 0.95em;
        }}
        
        .summary-section p {{
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.7;
            font-size: 0.95em;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9em;
        }}
        
        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .footer a:hover {{
            color: var(--glow);
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.5em; }}
            .toc-grid {{ grid-template-columns: 1fr; }}
            .paper-title-en {{ font-size: 1.1em; }}
            .paper-meta {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <!-- 粒子背景 -->
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📚 每日论文推送</h1>
            <p>📅 推送日期：{push_date} | 📄 论文日期：{paper_date} | 共{len(papers)}篇 (LLM: {llm_count}, Agent: {agent_count})</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; margin-bottom: 30px;">
                <a href="/papers/" class="back-link">← 返回报告列表</a>
            </div>
            
            <!-- 目录导航 -->
            <nav class="toc">
                <div class="toc-title">📑 目录导航 (点击跳转)</div>
                <div class="toc-grid">
                    {toc_items}
                </div>
            </nav>
            
            <!-- 论文列表 -->
            <div class="papers">
                {paper_cards}
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by <a href="/">EvilBot 😈</a> | Data from arXiv</p>
        </div>
    </div>
</body>
</html>'''
    return html

def update_reports_index(push_date, paper_date, count, llm_count, agent_count, is_weekend=False):
    """更新 reports.json 索引"""
    index_file = "/etc/nginx/html/papers/reports.json"
    
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            reports = json.load(f)
    else:
        reports = []
    
    reports = [r for r in reports if r['date'] != push_date]
    
    entry = {
        'date': push_date,
        'paper_date': paper_date,
        'count': count,
        'llm_count': llm_count,
        'agent_count': agent_count,
        'file': f"{push_date}.html"
    }
    
    if is_weekend:
        entry['weekend_no_update'] = True
    
    reports.insert(0, entry)
    reports.sort(key=lambda x: x['date'], reverse=True)
    reports = reports[:30]
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', required=True, help='论文日期')
    parser.add_argument('--push-date', help='推送日期（默认等于论文日期）')
    parser.add_argument('--input-dir', help='解读文件目录（无论文时可不传）')
    parser.add_argument('--output-json', required=True, help='输出 JSON 路径')
    parser.add_argument('--output-html', required=True, help='输出 HTML 路径')
    parser.add_argument('--weekend', action='store_true', help='是否是周末无更新')
    args = parser.parse_args()
    
    # 如果没有指定推送日期，默认等于论文日期
    if not args.push_date:
        args.push_date = args.date
    
    print(f"📊 汇总 {args.date} 的论文...")
    
    # 读取所有解读文件
    papers = []
    if args.input_dir:
        input_dir = Path(args.input_dir)
        if input_dir.exists():
            for f in sorted(input_dir.glob('paper-*.json')):
                with open(f, 'r', encoding='utf-8') as file:
                    papers.append(json.load(file))
    
    llm_count = sum(1 for p in papers if p.get('topic') == 'LLM')
    agent_count = sum(1 for p in papers if p.get('topic') == 'Agent')
    
    print(f"  总计：{len(papers)} 篇 (LLM: {llm_count}, Agent: {agent_count})")
    
    # 从实际论文数据中推断正确的 paper_date（避免检索参数±2 天误差导致日期不一致）
    actual_paper_date = args.date
    if papers:
        # 统计论文日期，选择最多的那个作为 paper_date
        date_counts = {}
        for p in papers:
            d = p.get('date', args.date)
            date_counts[d] = date_counts.get(d, 0) + 1
        actual_paper_date = max(date_counts.keys(), key=lambda d: date_counts[d])
        print(f"  实际论文日期：{actual_paper_date} (检索参数：{args.date})")
    
    # 生成完整数据
    data = {
        'push_date': args.push_date,
        'paper_date': actual_paper_date,
        'generated_at': datetime.now().isoformat(),
        'total_count': len(papers),
        'llm_count': llm_count,
        'agent_count': agent_count,
        'papers': papers
    }
    
    if args.weekend:
        data['weekend_no_update'] = True
    
    # 保存 JSON
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {args.output_json}")
    
    # 生成 HTML
    if papers:
        html = generate_html(papers, args.push_date, actual_paper_date)
    else:
        html = generate_empty_html(args.push_date, actual_paper_date, is_weekend=args.weekend)
    
    os.makedirs(os.path.dirname(args.output_html), exist_ok=True)
    with open(args.output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML: {args.output_html}")
    
    # 更新索引
    update_reports_index(args.push_date, actual_paper_date, len(papers), llm_count, agent_count)
    print(f"✅ 索引已更新")
    
    print(f"📄 访问：http://evilcalf.online/papers/{args.push_date}.html")

if __name__ == "__main__":
    main()
