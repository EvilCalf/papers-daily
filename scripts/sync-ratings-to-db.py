#!/usr/bin/env python3
"""
将 AI 生成的 rating.json 同步到 papers.db 数据库
"""

import argparse
import json
import sqlite3
import os
from datetime import datetime

def sync_ratings(db_path, ratings_file=None):
    """同步评分数据到数据库"""
    
    # 默认 rating.json 路径
    if ratings_file is None:
        ratings_file = '/root/.openclaw/workspace/projects/papers-daily/data/rating.json'
    
    if not os.path.exists(ratings_file):
        print(f"⚠️  评分文件不存在：{ratings_file}")
        return
    
    # 读取评分数据
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings_data = json.load(f)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
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
    
    # 获取或创建 AI 用户 ID（用于 AI 生成的评分）
    ai_user_id = 'ai_system'
    cursor.execute("SELECT id FROM users WHERE id = ?", (ai_user_id,))
    if not cursor.fetchone():
        # 如果 users.db 中不存在，尝试在 papers.db 中创建（或跳过）
        print(f"ℹ️  AI 用户不存在，使用虚拟 ID: {ai_user_id}")
    
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
            # 插入新评分
            cursor.execute("""
                INSERT INTO paper_ratings 
                (id, arxiv_id, user_id, overall, innovation, practicality, quality, impact, reason, tags, is_ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (rating_id, arxiv_id, ai_user_id, overall, innovation, practicality, quality, impact, reason, tags))
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
