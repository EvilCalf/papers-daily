## 基本信息

- **标题**: MCLMR: A Model-Agnostic Causal Learning Framework for Multi-Behavior Recommendation
- **作者**: Ranxu Zhang, Junjie Meng, Ying Sun, Ziqi Xu, Bing Yin et al.
- **ArXiv ID**: 2603.25126v1
- **发布日期**: 2026-03-26
- **主分类**: cs.IR
- **分类**: cs.IR, cs.AI
- **摘要**: Multi-Behavior Recommendation (MBR) leverages multiple user interaction types (e.g., views, clicks, purchases) to enrich preference modeling and alleviate data sparsity issues in traditional single-behavior approaches. However, existing MBR methods face fundamental challenges: they lack principled frameworks to model complex confounding effects from user behavioral habits and item multi-behavior distributions, struggle with effective aggregation of heterogeneous auxiliary behaviors, and fail to align behavioral representations across semantic gaps while accounting for bias distortions. To address these limitations, we propose MCLMR, a novel model-agnostic causal learning framework that can be seamlessly integrated into various MBR architectures. MCLMR first constructs a causal graph to model confounding effects and performs interventions for unbiased preference estimation. Under this causal framework, it employs an Adaptive Aggregation module based on Mixture-of-Experts to dynamically fuse auxiliary behavior information and a Bias-aware Contrastive Learning module to align cross-behavior representations in a bias-aware manner. Extensive experiments on three real-world datasets demonstrate that MCLMR achieves significant performance improvements across various baseline models, validating its effectiveness and generality. All data and code will be made publicly available. For anonymous review, our code is available at the following the link: https://github.com/gitrxh/MCLMR.
- **PDF 链接**: https://arxiv.org/pdf/2603.25126v1
