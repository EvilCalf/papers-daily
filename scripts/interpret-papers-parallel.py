#!/usr/bin/env python3
"""
interpret-papers-parallel.py - 并行 AI 解读论文脚本

直接使用 API 调用（不通过 subagent），支持真正的 10 并发
每篇论文约 30 秒，40 篇约 5 分钟完成
"""

import json
import os
import sys
import requests
import concurrent.futures
from pathlib import Path
from datetime import datetime

# 配置
MAX_WORKERS = 10  # 最大并发数
TIMEOUT = 900  # 每篇论文超时时间（秒）- 15 分钟，因为要从 TeX 源码提取详细内容（8000-12000 字）
MODEL = "qwen3.5-plus"  # 使用支持长上下文的模型

# 从 OpenClaw 配置读取 API key
import json
from pathlib import Path

def load_dashscope_api_key():
    """从 OpenClaw 配置加载 Dashscope API key"""
    config_file = Path.home() / ".openclaw" / "openclaw.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        models = config.get('models', {})
        providers = models.get('providers', {})
        dashscope = providers.get('dashscope-aliyuncs-com', {})
        return dashscope.get('apiKey')
    return None

DASHSCOPE_API_KEY = load_dashscope_api_key()

def read_metadata_md(paper_dir):
    """读取 metadata.md"""
    metadata_file = Path(paper_dir) / "metadata.md"
    if not metadata_file.exists():
        return {}
    
    content = metadata_file.read_text(encoding='utf-8')
    metadata = {}
    
    for line in content.split('\n'):
        if line.startswith('- **') and '**:' in line:
            key = line.split('**')[1]
            value = line.split('**:')[1].strip()
            metadata[key] = value
    
    return metadata

def read_source_or_abstract(paper_dir):
    """读取论文内容（优先 TeX，其次 PDF 提取，最后摘要）"""
    source_dir = Path(paper_dir) / "source"
    
    # 尝试读取 TeX 源码（包括子目录）
    if source_dir.exists():
        tex_files = list(source_dir.rglob("*.tex"))
        if tex_files:
            # 读取所有 TeX 文件
            all_content = []
            for tex_file in tex_files[:10]:  # 最多读 10 个文件
                try:
                    content = tex_file.read_text(encoding='utf-8', errors='ignore')
                    all_content.append(content)
                except Exception as e:
                    pass
            
            full_text = "\n\n".join(all_content)
            
            # 提取摘要
            abstract = ""
            if '\\begin{abstract}' in full_text:
                abstract_raw = full_text.split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
                abstract = abstract_raw.replace('\\', '').replace('{', '').replace('}', '')[:1500]
            
            # 提取方法/实验章节
            sections_text = ""
            if '\\section{' in full_text:
                sections = full_text.split('\\section{')
                for sec in sections[1:8]:  # 前 7 个章节
                    sec_title = sec.split('}')[0].lower()
                    if any(kw in sec_title for kw in ['method', 'approach', 'model', 'experiment', 'result', 'evaluation', 'data']):
                        sections_text += f"\n\\section{{{sec.split('}')[0]}}}\n{sec[:1500]}\n"
            
            return f"""【摘要】{abstract}

【关键章节（TeX 源码）】{sections_text[:4000]}

【完整 TeX 内容】{full_text[:6000]}"""
    
    # 尝试读取 PDF 提取的文本
    pdf_txt = source_dir / "pdf_text.txt"
    if pdf_txt.exists():
        content = pdf_txt.read_text(encoding='utf-8', errors='ignore')
        return f"PDF 提取：{content[:3000]}"
    
    # 回退到摘要
    metadata = read_metadata_md(paper_dir)
    return metadata.get('摘要', '无可用内容')

def interpret_paper(paper_id, paper_dir, summaries_output_dir, language="Chinese"):
    """解读单篇论文"""
    try:
        # 检查是否已解读
        summary_file = Path(summaries_output_dir) / "summary.md"
        if summary_file.exists():
            print(f"  ✅ {paper_id} 已解读，跳过")
            return True
        
        # 读取元数据
        metadata = read_metadata_md(paper_dir)
        title = metadata.get('标题', metadata.get('Title', paper_id))
        authors = metadata.get('作者', metadata.get('Authors', 'Unknown'))
        abstract = metadata.get('摘要', metadata.get('Abstract', 'No abstract'))
        
        # 读取论文内容
        content = read_source_or_abstract(paper_dir)
        
        # 构建提示词 - 强调详细解读
        prompt = f"""请深度阅读并详细解读以下 arXiv 论文。

**论文信息**：
- ArXiv ID: {paper_id}
- 标题：{title}
- 作者：{authors}

**摘要/内容**：
{abstract}

**论文源码/全文内容**：
{content[:4000]}  # 增加到 4000 字

---

**输出要求**（非常重要）：

用中文撰写**深度学术解读**（2500-4000 字），严格按照以下 10 节格式。**每一节都要包含具体细节、数据、技术术语**，不要泛泛而谈。

## 1. Paper Snapshot（元数据）
- **标题**: {title}
- **作者**: {authors}（标注主要作者机构）
- **ArXiv 编号**: {paper_id}
- **发布时间**: {metadata.get('发布时间', 'Unknown')}
- **主分类**: {metadata.get('主分类', 'Unknown')}
- **核心贡献**: 用 1 句话概括最大创新
- **数据集**: 如论文提出或使用数据集，列出名称和规模
- **项目页面**: 如有项目主页/GitHub，列出链接

## 2. 研究目标（详细）
- **核心痛点**: 现有方法的 2-3 个具体问题（引用论文原文描述）
- **研究问题**: 论文明确要解决的技术挑战
- **研究目标**: 用 3-5 个 bullet points 列出具体目标
- **应用场景**: 该研究服务于哪些实际应用

## 3. 方法概述（技术细节）
- **核心思想**: 用 1-2 句话概括方法本质
- **架构设计**: 详细描述模型架构（如 Transformer 层数、注意力机制类型）
- **关键创新**: 分 3-5 个小节，每节详细说明一个技术创新
  - 包含**数学公式**（如损失函数、注意力计算）
  - 包含**具体参数**（如维度、层数、激活函数）
  - 包含**算法流程**（如训练步骤、推理流程）
- **与现有方法的区别**: 明确指出与 prior work 的关键差异

## 4. 数据和评估（完整信息）
- **数据集**: 
  - 名称、规模（样本数、时长、分辨率等）
  - 数据来源（如"从 YouTube 采集"、"使用 XXX 基准"）
  - 预处理方式（如裁剪、归一化）
- **评估设置**:
  - 对比方法（列出 3-5 个基线方法名称）
  - 评估指标（如 PSNR、FID、Accuracy，说明计算方式）
  - 实验配置（如分辨率、batch size、GPU 型号）
- **实现细节**:
  - 训练时长、迭代次数
  - 学习率、优化器类型
  - 框架（如 PyTorch、TensorFlow）

## 5. 关键结果（包含具体数字）
- **主实验结果**: 用**表格形式**呈现核心对比数据
  - 表格必须包含：方法名称、各项指标数值、最优值标注
  - 至少 3 行对比（本方法 vs 2 个以上基线）
- **关键发现**: 用 3-5 个 bullet points 总结
  - 每个发现必须包含**具体提升百分比**（如"提升 14%"）
  - 标注统计显著性（如 p<0.05）
- **消融实验**: 如论文有消融研究，总结关键配置的影响
- **定性结果**: 描述可视化/案例研究的主要观察

## 6. 优势（量化对比）
- **性能优势**: 相比 SOTA 方法，在哪些指标上提升多少（如"PSNR 提升 2.3dB"）
- **效率优势**: 推理速度、参数量、训练时间的对比
- **通用性优势**: 在哪些场景/数据集上表现更好
- **理论优势**: 方法设计上的根本性改进

## 7. 局限性和风险（诚实评估）
- **技术局限**: 方法本身的 2-3 个不足之处
- **实验局限**: 实验设置的限制（如"仅在室内场景测试"）
- **应用风险**: 实际部署可能遇到的问题
- **未来改进方向**: 论文明确提到的或你推测的改进空间

## 8. 可重复性说明
- **代码可用性**: 是否开源、GitHub 链接、许可证
- **数据可用性**: 数据集是否公开、获取方式
- **预训练模型**: 是否提供、下载链接
- **复现难度**: 根据你的理解评估复现门槛（高/中/低）

## 9. 实践启示
- **对研究者的价值**: 哪些技术可以借鉴到其他问题
- **对工程师的价值**: 实际落地需要考虑的因素
- **对行业的价值**: 可能影响哪些应用领域
- **跟进建议**: 推荐阅读的相关论文或后续工作

## 10. 简要结论（精华总结）
用 3-4 句话总结，必须包含：
- **核心贡献**: 方法名称 + 核心创新
- **关键结果**: 1-2 个最重要的量化结果
- **实际意义**: 对领域的影响或应用价值

---

**写作规范**（必须遵守）：
1. **使用 Markdown 格式**：表格、列表、粗体、代码块
2. **包含具体数字**：不要说"显著提升"，要说"提升 14.2%"
3. **使用专业术语**：如"自注意力"、"残差连接"、"梯度下降"
4. **避免空洞描述**：每句话都要有信息量
5. **严格 10 节格式**：必须包含以下 10 个章节，不能多不能少：
   - ## 1. Paper Snapshot（元数据）
   - ## 2. 研究目标（详细）
   - ## 3. 方法概述（技术细节）
   - ## 4. 数据和评估（完整信息）
   - ## 5. 关键结果（包含具体数字）
   - ## 6. 优势（量化对比）
   - ## 7. 局限性和风险（诚实评估）
   - ## 8. 可重复性说明
   - ## 9. 实践启示
   - ## 10. 简要结论（精华总结）
6. **禁止添加的内容**：
   - ❌ 不要写"---"分隔线
   - ❌ 不要写"解读完成"、"生成时间"、"字数统计"等说明
   - ❌ 不要添加时间戳、签名、AI 标记
   - ❌ 不要使用 markdown 以外的标记（如 HTML 标签）
   - ❌ 不要有前言、后记、解释说明
7. **直接输出 10 节正文**：从"## 1."开始，到第 10 节结束
"""
        
        # 调用 API
        start_time = datetime.now()
        print(f"  📖 {paper_id}: 发送请求（超时{TIMEOUT//60}分钟）...", flush=True)
        
        # 使用 OpenAI 兼容 API 调用（Dashscope coding 接口）
        import requests
        
        base_url = "https://coding.dashscope.aliyuncs.com/v1"
        
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096  # 支持长输出（2000-3000 字解读）
        }
        
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                interpretation = result['choices'][0]['message']['content']
                
                # 清理输出（移除可能的额外标记）
                interpretation = interpretation.strip()
                if interpretation.startswith('```markdown'):
                    interpretation = interpretation[11:]
                if interpretation.endswith('```'):
                    interpretation = interpretation[:-3]
                interpretation = interpretation.strip()
                
                # 写入文件
                summary_file.write_text(interpretation, encoding='utf-8')
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"  ✅ {paper_id}: 解读完成 ({len(interpretation)} 字，{elapsed:.1f}秒)")
                return True
            else:
                print(f"  ❌ {paper_id}: API 错误 - {response.status_code}: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"  ❌ {paper_id}: 异常 - {str(e)}")
            return False
            
    except Exception as e:
        print(f"  ❌ {paper_id}: 异常 - {str(e)}")
        return False

def interpret_papers_parallel(run_dir, language="Chinese", max_workers=MAX_WORKERS, summaries_dir=None):
    """并行解读所有论文"""
    run_dir = Path(run_dir)
    
    # 如果指定了 summaries_dir，使用项目数据目录；否则使用 run_dir 内目录
    if summaries_dir:
        summaries_path = Path(summaries_dir)
        summaries_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 解读数据目录：{summaries_path}")
    else:
        summaries_path = run_dir
    
    # 读取论文索引
    papers_index = run_dir / "papers_index.json"
    if not papers_index.exists():
        print(f"❌ papers_index.json 不存在：{papers_index}")
        return False
    
    with open(papers_index, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    print(f"🤖 并行 AI 解读（{max_workers} 并发）")
    print(f"   运行目录：{run_dir}")
    print(f"   解读输出：{summaries_path}")
    print(f"   待解读：{len(papers)} 篇")
    
    # 过滤已解读的
    tasks = []
    for paper in papers:
        paper_id = paper.get('arxiv_id', '')
        paper_dir = run_dir / paper_id
        
        if not paper_dir.exists():
            print(f"   ⚠️ {paper_id} 目录不存在，跳过")
            continue
        
        # summary.md 保存在 summaries_path 下
        summary_file = summaries_path / paper_id / "summary.md"
        if summary_file.exists():
            print(f"   ✅ {paper_id} 已解读，跳过")
            continue
        
        # 确保输出目录存在
        (summaries_path / paper_id).mkdir(parents=True, exist_ok=True)
        
        tasks.append((paper_id, str(paper_dir), str(summaries_path / paper_id)))
    
    if not tasks:
        print(f"   ✅ 所有论文已解读")
        return True
    
    print(f"   📋 需要解读：{len(tasks)} 篇")
    print()
    
    # 并行执行
    success_count = 0
    failed_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(interpret_paper, paper_id, paper_dir, output_dir, language): paper_id
            for paper_id, paper_dir, output_dir in tasks
        }
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            paper_id = futures[future]
            try:
                if future.result():
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"  ❌ {paper_id}: 异常 - {str(e)}")
                failed_count += 1
            
            # 进度显示
            if i % 5 == 0 or i == len(tasks):
                print(f"   进度：{i}/{len(tasks)} (成功:{success_count}, 失败:{failed_count})")
    
    print()
    print(f"✅ 解读完成：成功 {success_count}/{len(tasks)} 篇")
    
    return failed_count == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="并行 AI 解读论文")
    parser.add_argument("--run-dir", required=True, help="编排器运行目录")
    parser.add_argument("--summaries-dir", help="解读输出目录（默认在 run-dir 内）")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS, help="最大并发数")
    parser.add_argument("--language", default="Chinese", help="输出语言")
    
    args = parser.parse_args()
    
    success = interpret_papers_parallel(
        args.run_dir,
        args.language,
        args.max_workers,
        args.summaries_dir
    )
    
    sys.exit(0 if success else 1)
