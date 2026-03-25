## 基本信息

- **标题**: Policy-based Tuning of Autoregressive Image Models with Instance- and Distribution-Level Rewards
- **作者**: Orhun Buğra Baran, Melih Kandemir, Ramazan Gokberk Cinbis
- **ArXiv ID**: 2603.23086v1
- **发布日期**: 2026-03-24
- **主分类**: cs.LG
- **分类**: cs.LG, cs.CV
- **摘要**: Autoregressive (AR) models are highly effective for image generation, yet their standard maximum-likelihood estimation training lacks direct optimization for sample quality and diversity. While reinforcement learning (RL) has been used to align diffusion models, these methods typically suffer from output diversity collapse. Similarly, concurrent RL methods for AR models rely strictly on instance-level rewards, often trading off distributional coverage for quality. To address these limitations, we propose a lightweight RL framework that casts token-based AR synthesis as a Markov Decision Process, optimized via Group Relative Policy Optimization (GRPO). Our core contribution is the introduction of a novel distribution-level Leave-One-Out FID (LOO-FID) reward; by leveraging an exponential moving average of feature moments, it explicitly encourages sample diversity and prevents mode collapse during policy updates. We integrate this with composite instance-level rewards (CLIP and HPSv2) for strict semantic and perceptual fidelity, and stabilize the multi-objective learning with an adaptive entropy regularization term. Extensive experiments on LlamaGen and VQGAN architectures demonstrate clear improvements across standard quality and diversity metrics within only a few hundred tuning iterations. The results also show that the model can be updated to produce competitive samples even without Classifier-Free Guidance, and bypass its 2x inference cost.
- **PDF 链接**: https://arxiv.org/pdf/2603.23086v1
