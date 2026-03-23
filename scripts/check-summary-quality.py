#!/usr/bin/env python3
"""
检查论文解读质量 - 验证 summary.md 格式和内容

用法：python3 check-summary-quality.py --run-dir /path/to/run_dir
"""

import json
import argparse
from pathlib import Path
import re

def check_summary_format(paper_dir):
    """检查单篇论文的 summary.md 格式"""
    summary_file = paper_dir / "summary.md"
    
    if not summary_file.exists():
        return {'status': 'missing', 'issues': ['summary.md 不存在']}
    
    content = summary_file.read_text(encoding='utf-8')
    issues = []
    
    # 检查文件大小
    if len(content) < 1000:
        issues.append(f'文件太小 ({len(content)} 字符，期望 >1000)')
    
    # 检查是否被 gateway 错误污染
    if 'Gateway agent failed' in content:
        issues.append('被 gateway 错误污染')
    
    if 'FailoverError' in content:
        issues.append('被 FailoverError 污染')
    
    # 检查是否有 10 节格式
    required_sections = [
        '1. Paper Snapshot',
        '2. Research Background',
        '3. Core Method',
        '4. Key Innovations',
        '5. Evaluation Setup',
        '6. Main Results',
        '7. Practical Value',
        '8. Limitations',
        '9. Future Work',
        '10. Brief Conclusion'
    ]
    
    missing_sections = []
    for section in required_sections:
        # 支持中英文
        if section not in content:
            # 尝试中文
            cn_map = {
                '1. Paper Snapshot': ['1. Paper Snapshot'],
                '2. Research Background': ['2. Research Background', '2. 研究背景', '2. 研究目标'],
                '3. Core Method': ['3. Core Method', '3. 方法概述', '3. 核心方法'],
                '4. Key Innovations': ['4. Key Innovations', '4. 关键创新'],
                '5. Evaluation Setup': ['5. Evaluation Setup', '5. 实验设置', '5. 评估设置'],
                '6. Main Results': ['6. Main Results', '6. 主要结果', '6. 关键结果'],
                '7. Practical Value': ['7. Practical Value', '7. 实际价值', '7. 应用价值'],
                '8. Limitations': ['8. Limitations', '8. 局限性'],
                '9. Future Work': ['9. Future Work', '9. 未来方向', '9. 未来工作'],
                '10. Brief Conclusion': ['10. Brief Conclusion', '10. 简要结论', '10. 总结']
            }
            
            found = False
            for variant in cn_map.get(section, [section]):
                if variant in content:
                    found = True
                    break
            
            if not found:
                missing_sections.append(section)
    
    if missing_sections:
        issues.append(f'缺少章节：{", ".join(missing_sections)}')
    
    # 检查是否有不应该出现的标记
    bad_patterns = [
        (r'_解读完成', '包含"解读完成"标记'),
        (r'_由 AI 自动生成', '包含"AI 自动生成"标记'),
        (r'字数：约', '包含字数统计'),
        (r'---\s*_', '包含分隔线 + 斜体标记'),
    ]
    
    for pattern, desc in bad_patterns:
        if re.search(pattern, content):
            issues.append(desc)
    
    # 返回结果
    if not issues:
        return {'status': 'ok', 'issues': [], 'size': len(content)}
    else:
        return {'status': 'issues', 'issues': issues, 'size': len(content)}

def main():
    parser = argparse.ArgumentParser(description='检查论文解读质量')
    parser.add_argument('--run-dir', required=True, help='编排器运行目录')
    parser.add_argument('--fix', action='store_true', help='自动修复（标记需要重生的论文）')
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"❌ 目录不存在：{run_dir}")
        return
    
    # 读取 papers_index.json
    papers_index = run_dir / "papers_index.json"
    if not papers_index.exists():
        print(f"❌ papers_index.json 不存在")
        return
    
    with open(papers_index, 'r') as f:
        papers = json.load(f)
    
    print(f"📊 检查 {len(papers)} 篇论文的 summary.md 质量...\n")
    
    # 检查结果统计
    stats = {'ok': 0, 'issues': 0, 'missing': 0}
    need_regen = []
    
    for paper in papers:
        paper_id = paper.get('arxiv_id', '')
        paper_dir = run_dir / paper_id
        
        result = check_summary_format(paper_dir)
        
        if result['status'] == 'ok':
            print(f"✅ {paper_id} ({result['size']} 字符)")
            stats['ok'] += 1
        elif result['status'] == 'missing':
            print(f"❌ {paper_id} - summary.md 不存在")
            stats['missing'] += 1
            need_regen.append(paper_id)
        else:
            print(f"⚠️ {paper_id} - 问题:")
            for issue in result['issues']:
                print(f"     - {issue}")
            stats['issues'] += 1
            need_regen.append(paper_id)
    
    # 汇总
    print(f"\n📈 统计:")
    print(f"   ✅ 正常：{stats['ok']} 篇")
    print(f"   ⚠️  有问题：{stats['issues']} 篇")
    print(f"   ❌ 缺失：{stats['missing']} 篇")
    print(f"   📝 总计：{len(papers)} 篇")
    
    if need_regen:
        print(f"\n🔄 需要重新生成的论文 ({len(need_regen)} 篇):")
        for paper_id in need_regen:
            print(f"   - {paper_id}")
        
        if args.fix:
            # 保存需要重生的列表
            regen_file = run_dir / "papers-need-regen.json"
            with open(regen_file, 'w') as f:
                json.dump(need_regen, f, indent=2)
            print(f"\n✅ 已保存到：{regen_file}")

if __name__ == "__main__":
    main()
