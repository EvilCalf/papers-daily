#!/usr/bin/env python3
"""
验证 summary.md 格式是否符合 10 节规范
"""

import json
import os
import argparse
from pathlib import Path
import re

# 期望的章节（支持模糊匹配）
EXPECTED_SECTIONS = [
    'Paper Snapshot',
    '研究目标',
    '方法概述',
    '数据和评估',
    '关键结果',
    '优势',
    '局限性和风险',
    '可重复性说明',
    '实践启示',
    '简要结论'
]

# 章节关键词匹配（支持中英文变体）
SECTION_KEYWORDS = {
    'Paper Snapshot': ['snapshot', '元数据', 'paper snapshot', '基本信息'],
    '研究目标': ['研究目标', '目标', 'purpose', 'objective'],
    '方法概述': ['方法概述', '方法', 'method', 'approach'],
    '数据和评估': ['数据和评估', '实验', '评估', 'data', 'experiment', 'evaluation'],
    '关键结果': ['关键结果', '结果', 'result', 'finding'],
    '优势': ['优势', '优点', 'advantage', 'contribution'],
    '局限性和风险': ['局限性', '不足', 'limitation', 'risk'],
    '可重复性说明': ['可重复性', '代码', '数据可用性', 'reproducibility', 'code'],
    '实践启示': ['实践启示', '启示', '意义', 'implication', 'value'],
    '简要结论': ['简要结论', '结论', 'conclusion', 'summary']
}

def parse_summary_md(summary_path):
    """解析 summary.md，返回章节字典"""
    if not summary_path.exists():
        return None
    
    content = summary_path.read_text(encoding='utf-8')
    
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
    
    return sections

def validate_sections(sections):
    """验证章节是否完整"""
    missing = []
    found = []
    
    for expected_section, keywords in SECTION_KEYWORDS.items():
        matched = False
        for actual_section in sections.keys():
            actual_section_lower = actual_section.lower()
            if any(kw.lower() in actual_section_lower for kw in keywords):
                matched = True
                found.append(expected_section)
                break
        
        if not matched:
            missing.append(expected_section)
    
    return missing, found

def validate_content_length(sections):
    """验证内容长度是否足够"""
    short_sections = []
    
    for section_name, content in sections.items():
        # 内容过短（少于 50 字）
        if len(content.strip()) < 50:
            short_sections.append(section_name)
    
    return short_sections

def main():
    parser = argparse.ArgumentParser(description='验证 summary.md 格式')
    parser.add_argument('--summaries-dir', required=True, help='解读文件目录')
    parser.add_argument('--output-report', required=True, help='验证报告输出路径')
    
    args = parser.parse_args()
    
    summaries_dir = Path(args.summaries_dir)
    if not summaries_dir.exists():
        print(f"❌ 目录不存在：{summaries_dir}")
        return
    
    # 查找所有 summary.md
    summary_files = list(summaries_dir.rglob('summary.md'))
    total = len(summary_files)
    valid = 0
    invalid = 0
    papers_to_retry = []
    
    print(f"🔍 共找到 {total} 篇论文解读")
    
    for summary_file in summary_files:
        arxiv_id = summary_file.parent.name
        print(f"\n📄 检查：{arxiv_id}")
        
        # 解析文件
        sections = parse_summary_md(summary_file)
        if not sections:
            print(f"   ❌ 无法解析 summary.md")
            invalid += 1
            papers_to_retry.append({
                'arxiv_id': arxiv_id,
                'reason': '无法解析文件'
            })
            continue
        
        # 验证章节
        missing, found = validate_sections(sections)
        if missing:
            print(f"   ⚠️  缺失章节：{', '.join(missing)}")
            invalid += 1
            papers_to_retry.append({
                'arxiv_id': arxiv_id,
                'reason': f"缺失章节：{', '.join(missing)}"
            })
            continue
        
        # 验证内容长度
        short_sections = validate_content_length(sections)
        if short_sections:
            print(f"   ⚠️  内容过短：{', '.join(short_sections)}")
            invalid += 1
            papers_to_retry.append({
                'arxiv_id': arxiv_id,
                'reason': f"内容过短：{', '.join(short_sections)}"
            })
            continue
        
        # 验证通过
        print(f"   ✅ 格式正确")
        valid += 1
    
    # 生成报告
    pass_rate = valid / total if total > 0 else 0
    report = {
        'total_count': total,
        'valid_count': valid,
        'invalid_count': invalid,
        'pass_rate': pass_rate,
        'papers_to_retry': papers_to_retry,
        'generated_at': os.path.getmtime(__file__)
    }
    
    # 保存报告
    with open(args.output_report, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 验证结果：")
    print(f"   总数：{total}")
    print(f"   合格：{valid}")
    print(f"   不合格：{invalid}")
    print(f"   合格率：{pass_rate*100:.1f}%")
    print(f"   报告已保存：{args.output_report}")

if __name__ == "__main__":
    main()
