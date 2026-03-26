## 基本信息

- **标题**: LLMORPH: Automated Metamorphic Testing of Large Language Models
- **作者**: Steven Cho, Stefano Ruberto, Valerio Terragni
- **ArXiv ID**: 2603.23611v1
- **发布日期**: 2026-03-24
- **主分类**: cs.SE
- **分类**: cs.SE, cs.AI, cs.CL, cs.LG
- **摘要**: Automated testing is essential for evaluating and improving the reliability of Large Language Models (LLMs), yet the lack of automated oracles for verifying output correctness remains a key challenge. We present LLMORPH, an automated testing tool specifically designed for LLMs performing NLP tasks, which leverages Metamorphic Testing (MT) to uncover faulty behaviors without relying on human-labeled data. MT uses Metamorphic Relations (MRs) to generate follow-up inputs from source test input, enabling detection of inconsistencies in model outputs without the need of expensive labelled data. LLMORPH is aimed at researchers and developers who want to evaluate the robustness of LLM-based NLP systems. In this paper, we detail the design, implementation, and practical usage of LLMORPH, demonstrating how it can be easily extended to any LLM, NLP task, and set of MRs. In our evaluation, we applied 36 MRs across four NLP benchmarks, testing three state-of-the-art LLMs: GPT-4, LLAMA3, and HERMES 2. This produced over 561,000 test executions. Results demonstrate LLMORPH's effectiveness in automatically exposing inconsistencies.
- **PDF 链接**: https://arxiv.org/pdf/2603.23611v1
