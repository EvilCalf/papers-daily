## 基本信息

- **标题**: LogitScope: A Framework for Analyzing LLM Uncertainty Through Information Metrics
- **作者**: Farhan Ahmed, Yuya Jeremy Ong, Chad DeLuca
- **ArXiv ID**: 2603.24929v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI, cs.CL, cs.IT
- **摘要**: Understanding and quantifying uncertainty in large language model (LLM) outputs is critical for reliable deployment. However, traditional evaluation approaches provide limited insight into model confidence at individual token positions during generation. To address this issue, we introduce LogitScope, a lightweight framework for analyzing LLM uncertainty through token-level information metrics computed from probability distributions. By measuring metrics such as entropy and varentropy at each generation step, LogitScope reveals patterns in model confidence, identifies potential hallucinations, and exposes decision points where models exhibit high uncertainty, all without requiring labeled data or semantic interpretation. We demonstrate LogitScope's utility across diverse applications including uncertainty quantification, model behavior analysis, and production monitoring. The framework is model-agnostic, computationally efficient through lazy evaluation, and compatible with any HuggingFace model, enabling both researchers and practitioners to inspect LLM behavior during inference.
- **PDF 链接**: https://arxiv.org/pdf/2603.24929v1
