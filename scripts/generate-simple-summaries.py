#!/usr/bin/env python3
"""
为论文生成简单的 summary.md 文件（基于 metadata，不使用 AI）
用于在 AI 解读失败时提供基本数据
"""

import json
import argparse
from pathlib import Path
import re

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

def extract_abstract_from_source(paper_dir):
    """从源码中提取 abstract"""
    source_dir = paper_dir / "source" / "source_extract"
    if not source_dir.exists():
        return None
    
    # 查找 main.tex 或类似的 tex 文件
    tex_files = list(source_dir.glob("*.tex")) + list(source_dir.glob("main*.tex"))
    
    for tex_file in tex_files:
        content = tex_file.read_text(encoding='utf-8', errors='ignore')
        # 查找 abstract 环境
        match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            # 清理 LaTeX 命令
            abstract = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', abstract)
            abstract = re.sub(r'\\[a-zA-Z]+', '', abstract)
            abstract = re.sub(r'[{}]', '', abstract)
            abstract = re.sub(r'\s+', ' ', abstract).strip()
            if len(abstract) > 50:
                return abstract
    
    return None

def generate_simple_summary(paper_dir, metadata):
    """生成简单的 summary.md"""
    arxiv_id = metadata.get('arXiv ID', '')
    title = metadata.get('标题', metadata.get('Title', ''))
    authors = metadata.get('作者', metadata.get('Authors', ''))
    abstract = metadata.get('摘要', metadata.get('Abstract', ''))
    primary_cat = metadata.get('主分类', metadata.get('Primary Category', ''))
    published = metadata.get('发布时间', metadata.get('Published', ''))
    
    # 尝试从源码提取 abstract
    if not abstract or len(abstract) < 100:
        source_abstract = extract_abstract_from_source(paper_dir)
        if source_abstract:
            abstract = source_abstract
    
    # 生成简单的 summary
    summary = f"""## 1. Paper Snapshot
- **ArXiv ID**: {arxiv_id}
- **Title**: {title}
- **Authors**: {authors}
- **Published**: {published}
- **Category**: {primary_cat}

## 2. Research Background
{abstract[:500] if abstract else 'N/A'}

## 3. Core Method
基于论文标题和摘要，本研究探讨了相关领域的技术问题。详细方法需要阅读完整论文源码。

## 4. Key Innovations
- 本研究提出了新的方法/技术
- 具体创新点需要进一步分析论文内容

## 5. Evaluation Setup
实验设置详情需要参考论文原文。

## 6. Main Results
主要结果需要参考论文原文。

## 7. Practical Value
本研究的实际应用价值需要进一步分析。

## 8. Limitations
论文局限性需要进一步分析。

## 9. Future Work
未来研究方向需要进一步分析。

## 10. Brief Conclusion
本研究为相关领域提供了新的见解。详细结论需要阅读完整论文。
"""
    
    return summary

def main():
    parser = argparse.ArgumentParser(description='为论文生成简单 summary.md')
    parser.add_argument('--run-dir', required=True, help='论文运行目录')
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
    
    if not isinstance(papers, list):
        papers = papers.get('papers', [])
    
    print(f"📄 待处理：{len(papers)} 篇论文")
    
    generated = 0
    for paper in papers:
        arxiv_id = paper.get('arxiv_id', '')
        paper_dir = run_dir / arxiv_id
        
        if not paper_dir.exists():
            print(f"  ⚠️ {arxiv_id} 目录不存在")
            continue
        
        summary_file = paper_dir / "summary.md"
        if summary_file.exists():
            print(f"  ✅ {arxiv_id} 已存在 summary.md")
            generated += 1
            continue
        
        metadata = read_metadata_md(paper_dir)
        if not metadata:
            print(f"  ⚠️ {arxiv_id} 无 metadata.md")
            continue
        
        summary = generate_simple_summary(paper_dir, metadata)
        summary_file.write_text(summary, encoding='utf-8')
        print(f"  ✅ {arxiv_id} 已生成 summary.md")
        generated += 1
    
    print(f"\n✅ 完成！生成 {generated}/{len(papers)} 篇 summary.md")

if __name__ == "__main__":
    main()
