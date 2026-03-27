#!/usr/bin/env python3
"""生成论文推送统计报告"""
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path("/root/.openclaw/workspace/projects/papers-daily/data/summaries")

def collect_statistics():
    """统计所有推送数据"""
    stats = {
        "total_days": 0,
        "total_papers": 0,
        "by_category": Counter(),
        "by_field": Counter(),
    }
    
    for date_dir in sorted(DATA_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        stats["total_days"] += 1
        
        for paper_dir in date_dir.iterdir():
            if not paper_dir.is_dir():
                continue
            stats["total_papers"] += 1
            
            # 读取 metadata.md
            metadata_file = paper_dir / "metadata.md"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 简单解析分类
                if "cs.AI" in content:
                    stats["by_category"]["cs.AI"] += 1
                if "cs.LG" in content:
                    stats["by_category"]["cs.LG"] += 1
    
    return stats

def print_report(stats):
    """打印统计报告"""
    print("=" * 50)
    print("📊 论文推送统计报告")
    print("=" * 50)
    print(f"累计推送天数：{stats['total_days']}")
    print(f"累计推送论文数：{stats['total_papers']}")
    print(f"平均每天论文数：{stats['total_papers'] / max(stats['total_days'], 1):.1f}")
    print("\n按 arXiv 分类分布:")
    for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print("=" * 50)

if __name__ == "__main__":
    stats = collect_statistics()
    print_report(stats)
    
    # 保存 JSON
    output_file = Path("/root/.openclaw/workspace/projects/papers-daily/data/statistics.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n统计报告已保存到：{output_file}")
