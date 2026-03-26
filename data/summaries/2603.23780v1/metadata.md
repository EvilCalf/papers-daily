## 基本信息

- **标题**: Lightweight Fairness for LLM-Based Recommendations via Kernelized Projection and Gated Adapters
- **作者**: Nan Cui, Wendy Hui Wang, Yue Ning
- **ArXiv ID**: 2603.23780v1
- **发布日期**: 2026-03-24
- **主分类**: cs.LG
- **分类**: cs.LG
- **摘要**: Large Language Models (LLMs) have introduced new capabilities to recommender systems, enabling dynamic, context-aware, and conversational recommendations. However, LLM-based recommender systems inherit and may amplify social biases embedded in their pre-training data, especially when demographic cues are present. Existing fairness solutions either require extra parameters fine-tuning, or suffer from optimization instability. We propose a lightweight and scalable bias mitigation method that combines a kernelized Iterative Null-space Projection (INLP) with a gated Mixture-of-Experts (MoE) adapter. Our approach estimates a closed-form projection that removes single or multiple sensitive attributes from LLM representations with no additional trainable parameters. To preserve task utility, we introduce a two-level MoE adapter that selectively restores useful signals without reintroducing bias. Experiments on two public datasets show that our method reduces attribute leakage across multiple protected variables while maintaining competitive recommendation accuracy.
- **PDF 链接**: https://arxiv.org/pdf/2603.23780v1
