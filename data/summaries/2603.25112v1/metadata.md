## 基本信息

- **标题**: Do LLMs Know What They Know? Measuring Metacognitive Efficiency with Signal Detection Theory
- **作者**: Jon-Paul Cacioli
- **ArXiv ID**: 2603.25112v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL, cs.AI
- **摘要**: Standard evaluation of LLM confidence relies on calibration metrics (ECE, Brier score) that conflate two distinct capacities: how much a model knows (Type-1 sensitivity) and how well it knows what it knows (Type-2 metacognitive sensitivity). We introduce an evaluation framework based on Type-2 Signal Detection Theory that decomposes these capacities using meta-d' and the metacognitive efficiency ratio M-ratio. Applied to four LLMs (Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.3, Llama-3-8B-Base, Gemma-2-9B-Instruct) across 224,000 factual QA trials, we find: (1) metacognitive efficiency varies substantially across models even when Type-1 sensitivity is similar -- Mistral achieves the highest d' but the lowest M-ratio; (2) metacognitive efficiency is domain-specific, with different models showing different weakest domains, invisible to aggregate metrics; (3) temperature manipulation shifts Type-2 criterion while meta-d' remains stable for two of four models, dissociating confidence policy from metacognitive capacity; (4) AUROC_2 and M-ratio produce fully inverted model rankings, demonstrating these metrics answer fundamentally different evaluation questions. The meta-d' framework reveals which models "know what they don't know" versus which merely appear well-calibrated due to criterion placement -- a distinction with direct implications for model selection, deployment, and human-AI collaboration. Pre-registered analysis; code and data publicly available.
- **PDF 链接**: https://arxiv.org/pdf/2603.25112v1
