#!/usr/bin/env python3
"""
validate-summary-format.py - 验证 summary.md 格式

检查项：
- ✅ 是否包含 10 节标准格式（## 1. 到 ## 10.）
- ✅ 每节是否有内容（非空）
- ✅ 总字数是否达标（>1500 字）
- ✅ 是否包含 gateway 错误污染（"Gateway agent failed"）
- ✅ 是否包含 AI 生成标记（"--- _解读完成"）

输出：
- 验证报告（JSON 格式）
- 标记不合格的文件供重试
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# 标准 10 节格式
STANDARD_SECTIONS = [
    "## 1.",  # Paper Snapshot
    "## 2.",  # 研究目标
    "## 3.",  # 方法概述
    "## 4.",  # 数据和评估
    "## 5.",  # 关键结果
    "## 6.",  # 优势
    "## 7.",  # 局限性和风险
    "## 8.",  # 可重复性说明
    "## 9.",  # 实践启示
    "## 10.", # 简要结论
]

# 禁止内容（AI 生成标记、错误污染等）
FORBIDDEN_PATTERNS = [
    r"Gateway agent failed",
    r"--- _解读完成",
    r"---\s*_解读完成",
    r"生成时间[:：]",
    r"字数统计[:：]",
    r"```markdown\s*\n*## 1\.",  # 多余的代码块标记
]

def check_sections(content):
    """检查是否包含 10 节标准格式"""
    found_sections = []
    missing_sections = []
    
    for i, section_pattern in enumerate(STANDARD_SECTIONS, 1):
        # 使用正则匹配章节标题
        pattern = rf"{section_pattern}"
        if re.search(pattern, content):
            found_sections.append(i)
        else:
            missing_sections.append(i)
    
    return found_sections, missing_sections

def check_section_content(content, section_num):
    """检查指定章节是否有内容"""
    # 匹配章节内容（从当前章节到下一章节之间的内容）
    if section_num < 10:
        pattern = rf"## {section_num}\..*?(?=## {section_num + 1}\.)"
    else:
        pattern = rf"## {section_num}\..*$"
    
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if not match:
        return False, 0
    
    section_content = match.group(0)
    # 移除章节标题，计算实际内容
    content_lines = [line for line in section_content.split('\n')[1:] if line.strip() and not line.strip().startswith('##')]
    
    # 检查是否有实质性内容（至少 3 行或 50 字）
    content_text = '\n'.join(content_lines)
    char_count = len(content_text.strip())
    
    has_content = char_count >= 50 or len(content_lines) >= 3
    return has_content, char_count

def check_word_count(content):
    """检查总字数"""
    # 移除 markdown 标记，计算纯文本字数
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # 移除代码块
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # 移除标题标记
    text = re.sub(r'\*\*|\*|__|_', '', text)  # 移除粗体/斜体标记
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # 移除链接
    text = re.sub(r'^-\s*|^\d+\.\s*', '', text, flags=re.MULTILINE)  # 移除列表标记
    
    # 中文字数统计
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 英文单词统计
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    total_chars = len(text.strip())
    return total_chars, chinese_chars, english_words

def check_forbidden_patterns(content):
    """检查是否包含禁止内容"""
    found_patterns = []
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            found_patterns.append(pattern)
    
    return found_patterns

def validate_summary(summary_path):
    """验证单个 summary.md 文件"""
    result = {
        'file': str(summary_path),
        'paper_id': summary_path.parent.name,
        'valid': True,
        'errors': [],
        'warnings': [],
        'stats': {}
    }
    
    if not summary_path.exists():
        result['valid'] = False
        result['errors'].append('文件不存在')
        return result
    
    try:
        content = summary_path.read_text(encoding='utf-8')
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f'读取失败：{str(e)}')
        return result
    
    # 1. 检查 10 节标准格式
    found_sections, missing_sections = check_sections(content)
    result['stats']['found_sections'] = found_sections
    result['stats']['missing_sections'] = missing_sections
    
    if missing_sections:
        result['valid'] = False
        result['errors'].append(f'缺少章节：{", ".join([f"第{i}节" for i in missing_sections])}')
    
    # 2. 检查每节是否有内容
    empty_sections = []
    for i in range(1, 11):
        has_content, char_count = check_section_content(content, i)
        if not has_content and i not in missing_sections:
            empty_sections.append({'section': i, 'char_count': char_count})
    
    if empty_sections:
        result['valid'] = False
        section_list = [f"第{e['section']}节 ({e['char_count']}字)" for e in empty_sections]
        result['errors'].append(f'空章节：{", ".join(section_list)}')
    
    # 3. 检查总字数
    total_chars, chinese_chars, english_words = check_word_count(content)
    result['stats']['total_chars'] = total_chars
    result['stats']['chinese_chars'] = chinese_chars
    result['stats']['english_words'] = english_words
    
    if total_chars < 1500:
        result['valid'] = False
        result['errors'].append(f'字数不足：{total_chars}字（要求≥1500 字）')
    
    # 4. 检查禁止内容
    found_forbidden = check_forbidden_patterns(content)
    if found_forbidden:
        result['valid'] = False
        result['errors'].append(f'包含禁止内容：{", ".join(found_forbidden)}')
    
    # 5. 额外检查：是否有明显的 AI 生成痕迹
    if content.strip().startswith('```'):
        result['warnings'].append('文件以代码块标记开头，建议清理')
    
    if content.strip().endswith('```'):
        result['warnings'].append('文件以代码块标记结尾，建议清理')
    
    return result

def validate_directory(summaries_dir, output_report=None):
    """验证目录下所有 summary.md 文件"""
    summaries_dir = Path(summaries_dir)
    
    if not summaries_dir.exists():
        print(f"❌ 目录不存在：{summaries_dir}")
        return None
    
    # 查找所有 summary.md 文件
    summary_files = list(summaries_dir.rglob("summary.md"))
    
    if not summary_files:
        print(f"⚠️  未找到 summary.md 文件：{summaries_dir}")
        return None
    
    print(f"📋 验证 {len(summary_files)} 篇论文的 summary.md 格式")
    print(f"   目录：{summaries_dir}")
    print()
    
    results = []
    valid_count = 0
    invalid_count = 0
    
    for summary_file in summary_files:
        result = validate_summary(summary_file)
        results.append(result)
        
        if result['valid']:
            valid_count += 1
            status = "✅"
        else:
            invalid_count += 1
            status = "❌"
        
        paper_id = result['paper_id']
        errors_count = len(result['errors'])
        warnings_count = len(result['warnings'])
        total_chars = result['stats'].get('total_chars', 0)
        
        print(f"   {status} {paper_id}: {total_chars}字, {errors_count}错误, {warnings_count}警告")
        if result['errors']:
            for error in result['errors'][:2]:  # 只显示前 2 个错误
                print(f"      - {error}")
    
    print()
    print(f"📊 验证统计：")
    print(f"   总数：{len(summary_files)}")
    print(f"   合格：{valid_count}")
    print(f"   不合格：{invalid_count}")
    print(f"   合格率：{valid_count/len(summary_files)*100:.1f}%")
    
    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'summaries_dir': str(summaries_dir),
        'total_count': len(summary_files),
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'pass_rate': valid_count / len(summary_files) if summary_files else 0,
        'results': results,
        'retry_needed': invalid_count > 0,
        'papers_to_retry': [r['paper_id'] for r in results if not r['valid']]
    }
    
    # 输出报告
    if output_report:
        report_path = Path(output_report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 验证报告已保存：{report_path}")
    
    return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="验证 summary.md 格式")
    parser.add_argument("--summaries-dir", required=True, help="解读输出目录")
    parser.add_argument("--output-report", help="验证报告输出路径（JSON）")
    parser.add_argument("--exit-code", action="store_true", help="根据验证结果返回退出码（不合格=1）")
    
    args = parser.parse_args()
    
    report = validate_directory(args.summaries_dir, args.output_report)
    
    if not report:
        sys.exit(1)
    
    if args.exit_code and report['invalid_count'] > 0:
        print(f"\n⚠️  有 {report['invalid_count']} 篇论文需要重试")
        sys.exit(1)
    
    print(f"\n✅ 所有论文格式验证通过")
    sys.exit(0)

if __name__ == "__main__":
    main()
