## 基本信息

- **标题**: Le MuMo JEPA: Multi-Modal Self-Supervised Representation Learning with Learnable Fusion Tokens
- **作者**: Ciem Cornelissen, Sam Leroux, Pieter Simoens
- **ArXiv ID**: 2603.24327v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Self-supervised learning has emerged as a powerful paradigm for learning visual representations without manual annotations, yet most methods still operate on a single modality and therefore miss the complementary structure available from heterogeneous sensors. We present Le MuMo JEPA, a self-supervised framework that learns unified representations from RGB images and aligned companion modalities. In our driving experiments, the second modality is camera-aligned LiDAR depth; we also evaluate RGB-thermal training and transfer on the Teledyne FLIR ADAS benchmark. Our approach extends LeJEPA to the multi-modal setting by learning fusion tokens that act as a latent bottleneck between modality-specific patch stems inside a shared transformer. Our default model employs a pruned fusion strategy: after an initial cross-modal attention layer, modality-specific tokens are dropped, forcing cross-modal information into the shared fusion-token grid as an efficient latent bottleneck before Sketched Isotropic Gaussian Regularization (SIGReg) is applied to the joint multimodal CLS embedding. On Waymo, Le MuMo JEPA gives the strongest performance-efficiency trade-off on downstream patch probes among the from-scratch multimodal baselines, improving CenterNet detection and dense depth while remaining competitive on segmentation. Under from-scratch training on nuScenes, Le MuMo JEPA remains the strongest model, and it also gives the best FLIR results, especially after Waymo-initialized fine-tuning. It also retains the best overall accuracy-efficiency balance in our study at substantially lower compute, memory, and estimated training time.
- **PDF 链接**: https://arxiv.org/pdf/2603.24327v1
