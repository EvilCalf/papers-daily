#!/usr/bin/env python3
"""
将 AI 生成的 rating.json 同步到 papers.db 数据库
"""

import argparse
import json
import sqlite3
import os
from datetime import datetime

def sync_ratings(db_path, ratings_file=None, papers_index_file=None):
    """同步评分数据到数据库"""
    
    # 优先级：1. papers_index.json > 2. rating.json
    if papers_index_file is None:
        papers_index_file = '/root/.openclaw/workspace/tmp/papers-orchestrator/llm-ai-agent-2026-03-24/papers_index.json'
    
    if ratings_file is None:
        ratings_file = '/root/.openclaw/workspace/projects/papers-daily/data/rating.json'
    
    # 优先从 papers_index.json 读取（包含 quality_score）
    ratings_data = {}
    if os.path.exists(papers_index_file):
        print(f"✅ 从 papers_index.json 读取评分数据")
        with open(papers_index_file, 'r', encoding='utf-8') as f:
            papers_index = json.load(f)
        
        for paper in papers_index:
            arxiv_id = paper.get('arxiv_id')
            quality_score = paper.get('quality_score')
            quality_reason = paper.get('quality_reason', '')
            
            if arxiv_id and quality_score:
                ratings_data[arxiv_id] = {
                    'overall': quality_score,
                    'quality': quality_score,
                    'reason': quality_reason,
                    'tags': ['AI 筛选']
                }
    elif os.path.exists(ratings_file):
        print(f"✅ 从 rating.json 读取评分数据")
        with open(ratings_file, 'r', encoding='utf-8') as f:
            ratings_data = json.load(f)
    else:
        print(f"⚠️  评分文件不存在")
        return
    
    # 连接数据库（禁用外键约束，避免依赖 users 表）
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    # 确保 papers 表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            categories TEXT,
            paper_date TEXT,
            push_date TEXT,
            pdf_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 确保 paper_ratings 表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_ratings (
            id TEXT PRIMARY KEY,
            arxiv_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            overall INTEGER CHECK(overall BETWEEN 1 AND 10),
            innovation INTEGER CHECK(innovation BETWEEN 1 AND 10),
            practicality INTEGER CHECK(practicality BETWEEN 1 AND 10),
            quality INTEGER CHECK(quality BETWEEN 1 AND 10),
            impact INTEGER CHECK(impact BETWEEN 1 AND 10),
            reason TEXT,
            tags TEXT,
            is_ai_generated BOOLEAN DEFAULT TRUE,
            is_admin_rating BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY(arxiv_id) REFERENCES papers(arxiv_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # 使用 AI 用户 ID（users.db 中的 admin 用户）
    ai_user_id = 'usr_admin'  # 使用预置的管理员账号
    
    synced_count = 0
    updated_count = 0
    
    for arxiv_id, rating in ratings_data.items():
        # 检查是否已存在评分
        cursor.execute(
            "SELECT id FROM paper_ratings WHERE arxiv_id = ? AND is_ai_generated = 1",
            (arxiv_id,)
        )
        existing = cursor.fetchone()
        
        rating_id = existing[0] if existing else f'rating_ai_{arxiv_id}'
        
        # 准备评分数据
        overall = rating.get('overall', 5)
        innovation = rating.get('innovation', overall)
        practicality = rating.get('practicality', overall)
        quality = rating.get('quality', overall)
        impact = rating.get('impact', overall)
        reason = rating.get('reason', '')
        tags = json.dumps(rating.get('tags', []))
        
        if existing:
            # 更新现有评分
            cursor.execute("""
                UPDATE paper_ratings 
                SET overall = ?, innovation = ?, practicality = ?, quality = ?, 
                    impact = ?, reason = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (overall, innovation, practicality, quality, impact, reason, tags, rating_id))
            updated_count += 1
        else:
            # 插入新评分（user_id 设为 AI 标识符）
            cursor.execute("""
                INSERT INTO paper_ratings 
                (id, arxiv_id, user_id, overall, innovation, practicality, quality, impact, reason, tags, is_ai_generated, is_admin_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """, (rating_id, arxiv_id, 'ai_generated', overall, innovation, practicality, quality, impact, reason, tags))
            synced_count += 1
        
        # 确保论文存在于 papers 表
        if 'title' in rating:
            cursor.execute("""
                INSERT OR IGNORE INTO papers (arxiv_id, title, abstract, categories, paper_date, push_date, pdf_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                arxiv_id,
                rating.get('title', ''),
                rating.get('abstract', ''),
                json.dumps(rating.get('categories', [])),
                rating.get('paper_date'),
                rating.get('push_date'),
                rating.get('pdf_url', f'https://arxiv.org/abs/{arxiv_id}')
            ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 同步完成：新增 {synced_count} 条评分，更新 {updated_count} 条评分")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='同步 AI 评分到数据库')
    parser.add_argument('--db', required=True, help='数据库路径')
    parser.add_argument('--ratings', help='评分 JSON 文件路径（可选）')
    args = parser.parse_args()
    
    sync_ratings(args.db, args.ratings)
