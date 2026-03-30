#!/usr/bin/env python3
"""
将 arxiv-summarizer-orchestrator 的输出转换为网页格式
读取每篇论文的 summary.md（10 节深度解读）并生成 JSON 数据 + HTML

v2.1 - 数据/展示分离架构：
- 生成 JSON 数据文件（/etc/nginx/html/papers/data/{date}.json）
- 通用 detail.html 模板通过 JS 动态读取数据
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime
import re
import shutil
import markdown

def read_summary_md(paper_dir):
    """读取论文的 summary.md 并解析"""
    summary_file = paper_dir / "summary.md"
    if not summary_file.exists():
        return None
    
    content = summary_file.read_text(encoding='utf-8')
    
    # 解析各节
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # 检查是否有实际内容（支持多种键名格式 - 包含括号内的详细说明）
    def find_section(prefix, keywords):
        """查找匹配的 section，支持模糊匹配"""
        for key in sections.keys():
            if key.startswith(prefix) and any(kw in key for kw in keywords):
                return sections[key]
        return ''
    
    conclusion = (sections.get('10. 简要结论', '') or 
                  find_section('10.', ['结论', 'Conclusion']) or
                  sections.get('Brief Conclusion', '') or 
                  sections.get('10. Brief Conclusion', ''))
    
    research_goal = (find_section('2.', ['研究目标', '研究问题', '背景', 'Background']) or
                     sections.get('2. 研究目标', '') or 
                     sections.get('2. 研究问题与动机', '') or 
                     sections.get('Research Background', '') or
                     sections.get('2. Research Background', ''))
    
    method = (find_section('3.', ['方法', '核心贡献', 'Method']) or
              sections.get('3. 方法概述', '') or 
              sections.get('3. 核心贡献', '') or 
              sections.get('Core Method', '') or
              sections.get('3. Core Method', ''))
    
    results = (find_section('5.', ['关键结果', '结果', 'Results']) or
               sections.get('5. 关键结果', '') or 
               sections.get('5. Main Results', '') or 
               sections.get('6. Main Results', '') or
               sections.get('Main Results', ''))
    
    # 只在 summary.md 确实为空时才回退到英文摘要
    if not conclusion or len(conclusion) < 30:
        metadata = read_metadata_md(paper_dir)
        abstract = metadata.get('摘要', '')
        if abstract:
            has_any_conclusion = (sections.get('10. 简要结论', '') or 
                                  sections.get('Brief Conclusion', '') or 
                                  sections.get('10. Brief Conclusion', ''))
            if not has_any_conclusion:
                sections['10. 简要结论'] = abstract[:800]
    
    return sections

def read_metadata_md(paper_dir):
    """读取 metadata.md 获取基本信息"""
    metadata_file = paper_dir / "metadata.md"
    if not metadata_file.exists():
        return {}
    
    content = metadata_file.read_text(encoding='utf-8')
    metadata = {}
    
    current_section = None
    section_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                metadata[current_section] = '\n'.join(section_content).strip()
            current_section = line[3:].strip()
            section_content = []
        elif line.startswith('- **') and '**:' in line:
            key = line.split('**')[1]
            value = line.split('**:')[1].strip()
            metadata[key] = value
            if key == 'Published':
                metadata['发布时间'] = value
            elif key == 'Primary Category':
                metadata['主分类'] = value
            elif key == 'Abstract':
                metadata['摘要'] = value
            elif key == 'arXiv ID':
                metadata['arXiv ID'] = value
        elif current_section and line.strip():
            section_content.append(line.strip())
        elif current_section and not line.strip() and section_content:
            break
    
    if current_section:
        metadata[current_section] = '\n'.join(section_content).strip()
    
    return metadata

def convert_markdown_table(table_text, inline_math=None, display_math=None):
    """单独转换 markdown 表格为 HTML（保护公式占位符）"""
    lines = table_text.strip().split('\n')
    if len(lines) < 2:
        return table_text
    
    html = '<table>\n<thead>\n<tr>'
    
    # 表头
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    for h in headers:
        # 单元格内可能有粗体等 markdown，但不处理公式（已经保护）
        cell_html = markdown.markdown(h, extensions=['extra'], output_format='html5')
        cell_html = re.sub(r'^<p>|</p>$', '', cell_html)
        html += f'<th style="text-align: left;">{cell_html}</th>'
    html += '</tr>\n</thead>\n<tbody>'
    
    # 表体（跳过分隔行）
    for line in lines[2:]:
        if line.strip().startswith('|') and ':' in line and '-' in line:
            continue  # 跳过分隔行
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if cells:
            html += '<tr>'
            for cell in cells:
                # 保留单元格内的 markdown 格式（公式占位符保持不变）
                cell_html = markdown.markdown(cell, extensions=['extra'], output_format='html5')
                cell_html = re.sub(r'^<p>|</p>$', '', cell_html)
                html += f'<td style="text-align: left;">{cell_html}</td>'
            html += '</tr>'
    
    html += '</tbody>\n</table>'
    return html

def markdown_to_html(text):
    """Markdown 转 HTML（使用 Python markdown 库，支持嵌套列表、公式等）"""
    if not text:
        return ''
    
    # 移除末尾的 AI 生成标记和字数统计
    text = re.sub(r'\n---+\s*_?[^*]*_?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_由 AI 自动生成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_解读完成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n解读完成.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n字数：约.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n---.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n_.*字.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'<p><em>解读完成.*?</em></p>', '', text)
    text = re.sub(r'<em>解读完成.*?</em>', '', text)
    
    # 保护 LaTeX 公式（避免被 markdown 转义）
    # 1. 保护行间公式 $$...$$（先保护，避免被行内公式匹配）
    display_math = []
    def save_display(m):
        idx = len(display_math)
        display_math.append(m.group(1))
        return f'@@MATHDISPLAY{idx}@@'
    text = re.sub(r'\$\$([\s\S]+?)\$\$', save_display, text)
    
    # 2. 保护行内公式 $...$
    inline_math = []
    def save_inline(m):
        idx = len(inline_math)
        inline_math.append(m.group(1))
        return f'@@MATHINLINE{idx}@@'
    text = re.sub(r'\$([^$\n]+?)\$', save_inline, text)
    
    # 3. 保护 \[...\] 和 \(...\) 格式
    def save_bracket(m):
        idx = len(display_math)
        display_math.append(m.group(1))
        return f'@@MATHBRACKET{idx}@@'
    def save_paren(m):
        idx = len(display_math)
        display_math.append(m.group(1))
        return f'@@MATHPAREN{idx}@@'
    text = re.sub(r'\\\[(.*?)\\\]', save_bracket, text)
    text = re.sub(r'\\\((.*?)\\\)', save_paren, text)
    
    # 使用 Python markdown 库转换
    html = markdown.markdown(
        text,
        extensions=[
            'extra',
            'codehilite',
            'tables',
            'fenced_code',
        ],
        output_format='html5'
    )
    
    # 【关键修复】在 markdown 转换后，处理未被转换的 markdown 表格
    def convert_remaining_tables(html):
        # 匹配未被转换的 markdown 表格（允许前导空格）
        table_pattern = r'(\s*\|.*\|\n\s*\|[-:| ]+\|.*\n(?:\s*\|.*\|\n?)*)'
        
        def replace_table(match):
            table_md = match.group(1).strip()
            # 跳过已经包含 HTML 标签的内容
            if '<table' in table_md:
                return table_md
            return convert_markdown_table(table_md, inline_math, display_math)
        
        return re.sub(table_pattern, replace_table, html, flags=re.MULTILINE)
    
    html = convert_remaining_tables(html)
    
    # 恢复 LaTeX 公式
    for i, math in enumerate(inline_math):
        html = html.replace(f'@@MATHINLINE{i}@@', f'${math}$')
    
    for i, math in enumerate(display_math):
        html = html.replace(f'@@MATHDISPLAY{i}@@', f'$${math}$$')
        html = html.replace(f'@@MATHBRACKET{i}@@', f'$${math}$$')
        html = html.replace(f'@@MATHPAREN{i}@@', f'$${math}$$')
    
    return html

def generate_json_data(papers_data, push_date, date_range, output_dir):
    """生成完整的 JSON 数据文件（包含所有论文的 AI 解读）"""
    
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
    
    for cat_name, cat_papers in grouped.items():
        cat_display = category_map.get(cat_name, (cat_name, cat_name))[0]
        
        # 定义模糊匹配函数
        def find_section(sections, prefix, keywords):
            for key in sections.keys():
                if key.startswith(prefix) and any(kw in key for kw in keywords):
                    return sections[key]
            return ''
        
        papers = []
        for paper in cat_papers:
            summary = paper.get('summary_sections', {})
            
            # 提取关键部分（支持模糊匹配）
            research_goal = (find_section(summary, '2.', ['研究目标', '研究问题', '背景', 'Background']) or
                            summary.get('2. 研究目标', '') or 
                            summary.get('2. Research Background', '') or
                            summary.get('Research Background', ''))
            method = (find_section(summary, '3.', ['方法', '核心贡献', 'Method']) or
                     summary.get('3. 方法概述', '') or 
                     summary.get('3. 核心贡献', '') or
                     summary.get('Core Method', ''))
            results = (find_section(summary, '5.', ['关键结果', '结果', 'Results']) or
                      summary.get('5. 关键结果', '') or 
                      summary.get('5. Main Results', '') or
                      summary.get('6. Main Results', '') or
                      summary.get('Main Results', ''))
            conclusion = (find_section(summary, '10.', ['结论', 'Conclusion']) or
                         summary.get('10. 简要结论', '') or 
                         summary.get('10. Brief Conclusion', '') or
                         summary.get('Brief Conclusion', ''))
            
            # 优先使用 AI 解读的结论作为简要摘要
            brief = conclusion if conclusion else ''
            
            # 如果 conclusion 为空，回退到 metadata 的英文摘要
            if not brief or len(brief) < 50:
                metadata = read_metadata_md(Path(paper.get('paper_dir', '')))
                abstract = metadata.get('摘要', '')
                if abstract:
                    brief = abstract
            
            # 格式化发布时间
            published = paper.get('published', '')
            pub_date = published.split('T')[0] if 'T' in published else published[:10] if published else ''
            
            # 构建论文数据（包含完整解读）
            papers.append({
                'arxiv_id': paper.get('arxiv_id', ''),
                'title': paper.get('title', ''),
                'chinese_title': paper.get('chinese_title', ''),
                'published': pub_date,
                'category': paper.get('primary_category', ''),
                'brief': markdown_to_html(brief),
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
    
    # 构建完整数据
    data = {
        'push_date': push_date,
        'date_range': date_range,
        'total_count': len(papers_data),
        'category_count': len(grouped),
        'categories': categories
    }
    
    # 写入 JSON 文件到 nginx 目录（不是 data 子目录）
    json_file = output_dir / f"{push_date}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已生成：{json_file} ({os.path.getsize(json_file) / 1024:.1f}KB)")
    
    return json_file

def update_reports_json(papers_data, push_date, date_range, data_dir):
    """更新 reports.json 索引"""
    reports_file = data_dir / "reports.json"
    
    # 统计 LLM 和 Agent 数量（基于实际过滤后的论文列表）
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
    
    # 计算 paper_date（论文日期：周二到周五 = 推送日期 - 1 天，周一 = 推送日期 - 3 天 = 上周五）
    from datetime import datetime, timedelta
    push_date_obj = datetime.strptime(push_date, "%Y-%m-%d")
    day_of_week = push_date_obj.weekday()  # 0=周一，4=周五，5=周六，6=周日
    
    if day_of_week == 0:  # 周一，论文日期是周五
        paper_date = (push_date_obj - timedelta(days=3)).strftime("%Y-%m-%d")
        date_range_str = f"{paper_date}~{push_date}"
    else:  # 其他工作日，论文日期是前一天
        paper_date = (push_date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
        date_range_str = paper_date
    
    # 添加新记录（指向 JSON 数据文件）
    entry = {
        'date': push_date,
        'paper_date': paper_date,
        'date_range': date_range_str,
        'count': len(papers_data),
        'llm_count': llm_count,
        'agent_count': agent_count,
        'data_file': f"data/{push_date}.json",
        'detail_url': f"detail.html?date={push_date}"
    }
    
    reports.insert(0, entry)
    
    # 保留最近 30 条
    reports = reports[:30]
    
    # 保存（紧凑格式）
    with open(reports_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"✅ 索引已更新：{reports_file}")

def generate_static_html(papers_data, push_date, date_range, output_html, run_dir):
    """生成静态 HTML 网页（向后兼容，可选）"""
    
    # 按分类组织论文
    categories = {}
    for paper in papers_data:
        cat = paper.get('category', 'Other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(paper)
    
    category_map = {
        'cs.AI': ('AI 基础', '人工智能基础研究'),
        'cs.CL': ('NLP 与对话', '自然语言处理'),
        'cs.LG': ('机器学习', '机器学习方法'),
        'cs.SE': ('软件工程', '软件与代码'),
        'cs.HC': ('人机交互', '人机交互'),
        'cs.CR': ('安全', '安全与隐私'),
    }
    
    html_categories = ''
    cat_num = 1
    
    grouped = {}
    for paper in papers_data:
        primary_cat = paper.get('primary_category', 'Other')
        if primary_cat not in grouped:
            grouped[primary_cat] = []
        grouped[primary_cat].append(paper)
    
    for cat_name, cat_papers in grouped.items():
        cat_display = category_map.get(cat_name, (cat_name, cat_name))[0]
        
        html_categories += f'''
            <div class="section">
                <h2 class="section-title">{cat_num}、{cat_display}</h2>
        '''
        
        for paper in cat_papers:
            summary = paper.get('summary_sections', {})
            paper_id = paper.get('arxiv_id', '')
            paper_dir = run_dir / paper_id
            
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
            
            brief = conclusion[:500] + '...' if len(conclusion) > 500 else conclusion
            
            if not brief or '暂无详细解读' in brief or len(brief) < 50:
                metadata = read_metadata_md(paper_dir)
                abstract = metadata.get('摘要', '')
                if abstract:
                    brief = abstract[:500] + '...' if len(abstract) > 500 else abstract
            
            published = paper.get('published', '')
            pub_date = published.split('T')[0] if 'T' in published else published[:10] if published else ''
            
            html_categories += f'''
                <div class="paper-card">
                    <div class="paper-title">{paper.get('title', '')}</div>
                    <div class="paper-meta">
                        <span class="paper-date">📅 {pub_date}</span>
                        <span class="paper-category">{paper.get('primary_category', '')}</span>
                    </div>
                    <div class="paper-brief">{brief}</div>
                    <a href="https://arxiv.org/abs/{paper.get('arxiv_id', '')}" class="paper-link" target="_blank">📄 查看论文</a>
                    
                    <details class="paper-details">
                        <summary class="details-summary">🔍 展开深度解读</summary>
                        <div class="details-content">
                            <div class="summary-block">
                                <h4>🎯 研究目标</h4>
                                {markdown_to_html(research_goal)}
                            </div>
                            <div class="summary-block">
                                <h4>💡 方法概述</h4>
                                {markdown_to_html(method)}
                            </div>
                            {'<div class="summary-block"><h4>📊 关键结果</h4>' + markdown_to_html(results) + '</div>' if results else ''}
                            <div class="summary-block">
                                <h4>📝 完整结论</h4>
                                {markdown_to_html(conclusion)}
                            </div>
                        </div>
                    </details>
                </div>
            '''
        
        html_categories += '</div>'
        cat_num += 1
    
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
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 50px;
            padding: 30px;
            background: var(--card-bg);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}
        
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #fff, var(--glow), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1em;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: rgba(168, 85, 247, 0.15);
            padding: 15px 25px;
            border-radius: 10px;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: var(--glow);
        }}
        
        .stat-label {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9em;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: var(--glow);
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary);
        }}
        
        .paper-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(168, 85, 247, 0.2);
            transition: all 0.3s ease;
        }}
        
        .paper-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
            border-color: var(--primary);
        }}
        
        .paper-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #fff;
            margin-bottom: 10px;
        }}
        
        .paper-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 0.9em;
        }}
        
        .paper-date {{
            color: var(--glow);
        }}
        
        .paper-category {{
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .paper-brief {{
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.7;
            margin-bottom: 15px;
        }}
        
        .paper-link {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #fff;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .paper-link:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
        }}
        
        .paper-details {{
            margin-top: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
        }}
        
        .details-summary {{
            cursor: pointer;
            color: var(--glow);
            font-weight: 600;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .details-summary::-webkit-details-marker {{
            display: none;
        }}
        
        .details-summary:hover {{
            color: var(--accent);
        }}
        
        .details-content {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(168, 85, 247, 0.2);
        }}
        
        .summary-block {{
            margin-bottom: 20px;
        }}
        
        .summary-block h4 {{
            color: var(--accent);
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .summary-block p, .summary-block ul {{
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.7;
            font-size: 0.95em;
        }}
        
        .summary-block ul {{
            padding-left: 20px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9em;
        }}
        
        footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        footer a:hover {{
            color: var(--glow);
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 20px 10px; }}
            h1 {{ font-size: 1.8em; }}
            .stats {{ flex-direction: column; align-items: center; }}
            .paper-title {{ font-size: 1.1em; }}
        }}
    </style>
</head>
<body>
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
        <header>
            <h1>📚 每日论文推送</h1>
            <p class="subtitle">{push_date} · LLM and AI Agent applications</p>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{len(papers_data)}</div>
                    <div class="stat-label">论文总数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(grouped)}</div>
                    <div class="stat-label">研究方向</div>
                </div>
            </div>
        </header>
        
        <main>
            {html_categories}
        </main>
        
        <footer>
            <p>Powered by <a href="/">EvilBot 😈</a> | arxiv-summarizer-orchestrator | Data from arXiv</p>
        </footer>
    </div>
</body>
</html>'''
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    import sys
    from datetime import datetime, timedelta
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True, help='编排器运行目录')
    parser.add_argument('--push-date', help='推送日期（默认今天）')
    parser.add_argument('--output-html', help='输出 HTML 路径（可选，向后兼容）')
    parser.add_argument('--data-dir', default='/etc/nginx/html/papers', help='数据目录（默认 nginx）')
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"❌ 目录不存在：{run_dir}")
        return
    
    # 读取 task_meta.json 获取时间范围
    task_meta = run_dir / "task_meta.json"
    date_range = ""
    if task_meta.exists():
        with open(task_meta, 'r') as f:
            meta = json.load(f)
        params = meta.get('params', {})
        from_date = params.get('from_date', '')
        to_date = params.get('to_date', '')
        if from_date and to_date:
            date_range = f"{from_date}~{to_date}"
        else:
            lookback = params.get('lookback', '3d')
            date_range = f"过去 {lookback}"
    
    # 读取 papers_index.json
    papers_index = run_dir / "papers_index.json"
    if not papers_index.exists():
        print(f"❌ 错误：papers_index.json 文件不存在于目录 {run_dir}")
        print("💡 可能是编排器运行失败或未完成论文爬取，请先检查 upstream 任务状态")
        sys.exit(1)
    
    with open(papers_index, 'r') as f:
        papers_list = json.load(f)
    
    # 检查是否有 summaries_dir（项目数据目录）
    # 从 run_dir 名称提取日期 (llm-ai-agent-YYYY-MM-DD)
    if "llm-ai-agent" in run_dir.name:
        date_part = "-".join(run_dir.name.split("-")[-3:])  # 提取 YYYY-MM-DD
        summaries_dir = Path.home() / ".openclaw" / "workspace" / "projects" / "papers-daily" / "data" / "summaries" / date_part
    else:
        summaries_dir = None
    
    if summaries_dir and summaries_dir.exists():
        print(f"📁 使用项目数据目录：{summaries_dir}")
    else:
        # 回退到 run_dir 内查找
        summaries_dir = run_dir
        print(f"⚠️  未找到项目数据目录，使用 run_dir: {summaries_dir}")
    
    print(f"📚 处理 {len(papers_list)} 篇论文...")
    
    papers_data = []
    for paper in papers_list:
        arxiv_id = paper.get('arxiv_id', '')
        paper_dir_str = paper.get('paper_dir', '')
        if paper_dir_str:
            paper_dir = Path(paper_dir_str)
        else:
            paper_dir = run_dir / arxiv_id
        
        # 优先从 summaries_dir 读取 summary.md
        summary_path = summaries_dir / arxiv_id / "summary.md"
        if not summary_path.exists():
            summary_path = paper_dir / "summary.md"
        
        metadata = read_metadata_md(paper_dir)
        summary = read_summary_md(summary_path.parent)
        
        if not summary:
            print(f"  ⚠️ {arxiv_id} 无 summary.md")
            continue
        
        # 从 summary.md 读取标题和核心贡献
        snapshot = summary.get('1. Paper Snapshot（元数据）', '') or summary.get('1. Paper Snapshot', '')
        en_title = ''
        core_contribution = ''  # 用作中文副标题
        
        # 先从 summary.md 里找标题（1. 论文快照 部分）
        if summary:
            for section_name, section_content in summary.items():
                if '论文快照' in section_name or 'Paper Snapshot' in section_name:
                    for line in section_content.split('\n'):
                        if '- **标题**:' in line or '- **Title**:' in line:
                            en_title = line.split(':', 1)[1].strip()
                        elif '- **核心贡献**:' in line:
                            core_contribution = line.split(':', 1)[1].strip()
        
        # 如果没找到，从 papers_index.json 里补
        if not en_title and paper:
            en_title = paper.get('title', '')
        
        # chinese_title 使用核心贡献（中文总结，截取前 100 字）
        chinese_title = core_contribution[:100] + '...' if len(core_contribution) > 100 else core_contribution
        
        paper_data = {
            'arxiv_id': arxiv_id,
            'title': en_title,  # 英文标题
            'chinese_title': chinese_title,  # 中文副标题（核心贡献）
            'authors': metadata.get('作者', ''),
            'primary_category': paper.get('primary_category', '') or metadata.get('主分类', ''),
            'category': paper.get('primary_category', '') or metadata.get('主分类', 'Other'),
            'published': paper.get('published', '') or metadata.get('发布时间', ''),
            'link': metadata.get('摘要页链接', f'https://arxiv.org/abs/{arxiv_id}'),
            'summary_sections': summary,
            'paper_dir': str(paper_dir)
        }
        
        papers_data.append(paper_data)
        print(f"  ✅ {arxiv_id}: {paper_data['title'][:50]}...")
    
    push_date = args.push_date or datetime.now().strftime('%Y-%m-%d')
    data_dir = Path(args.data_dir)
    
    # 生成 JSON 数据文件（新架构）
    json_file = generate_json_data(papers_data, push_date, date_range, data_dir)
    
    # 更新 reports.json 索引
    update_reports_json(papers_data, push_date, date_range, data_dir)
    
    # 可选：生成静态 HTML（向后兼容）
    if args.output_html:
        generate_static_html(papers_data, push_date, date_range, args.output_html, run_dir)
        print(f"\n✅ 静态 HTML 已生成：{args.output_html}")
    
    print(f"\n✅ 数据处理完成！")
    print(f"📄 访问：http://evilcalf.online/papers/detail.html?date={push_date}")

if __name__ == "__main__":
    main()
