## 基本信息

- **标题**: Improving Lean4 Autoformalization via Cycle Consistency Fine-tuning
- **作者**: Arsen Shebzukhov
- **ArXiv ID**: 2603.24372v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: Autoformalization - automatically translating natural language mathematical texts into formal proof language such as Lean4 - can help accelerate AI-assisted mathematical research, be it via proof verification or proof search. I fine-tune Qwen3.5-2B with LoRA for natural language to Lean4 formalization on FineLeanCorpus and consider three training regimes: supervised fine-tuning (SFT) with curriculum learning (difficulty 1 to 10), SFT without curriculum ordering, and reinforcement learning using group relative policy optimization (GRPO) with a cycle consistency reward. Cycle consistency measures how well the meaning of a statement is preserved through a NL to Lean4 to NL' loop, computed as cosine similarity of off-the-shelf sentence embeddings. On an unseen subset of FineLeanCorpus (FLC) and on PutnamBench, RL substantially outperforms both SFT variants (mean cycle consistency 0.669 vs. 0.513 on FLC; 0.561 vs. 0.422 on PutnamBench), while increasing cross-entropy loss by only 0.011 nats, with minimal impact on formalization quality. Curriculum ordering provides no measurable benefit over shuffled training.
- **PDF 链接**: https://arxiv.org/pdf/2603.24372v1
