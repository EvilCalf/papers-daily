## 基本信息

- **标题**: Bi-CRCL: Bidirectional Conservative-Radical Complementary Learning with Pre-trained Foundation Models for Class-incremental Medical Image Analysis
- **作者**: Xinyao Wu, Zhe Xu, Cheng Chen, Jiawei Ma, Yefeng Zheng et al.
- **ArXiv ID**: 2603.23729v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Class-incremental learning (CIL) in medical image-guided diagnosis requires retaining prior diagnostic knowledge while adapting to newly emerging disease categories, which is critical for scalable clinical deployment. This problem is particularly challenging due to heterogeneous data and privacy constraints that prevent memory replay. Although pretrained foundation models (PFMs) have advanced general-domain CIL, their potential in medical imaging remains underexplored, where domain-specific adaptation is essential yet difficult due to anatomical complexity and inter-institutional heterogeneity. To address this gap, we conduct a systematic benchmark of recent PFM-based CIL methods and propose Bidirectional Conservative-Radical Complementary Learning (Bi-CRCL), a dual-learner framework inspired by complementary learning systems. Bi-CRCL integrates a conservative learner that preserves prior knowledge through stability-oriented updates and a radical learner that rapidly adapts to new categories via plasticity-oriented learning. A bidirectional interaction mechanism enables forward transfer and backward consolidation, allowing continual integration of new knowledge while mitigating catastrophic forgetting. During inference, outputs from both learners are adaptively fused for robust predictions. Experiments on five medical imaging datasets demonstrate consistent improvements over state-of-the-art methods under diverse settings, including cross-dataset shifts and varying task configurations.
- **PDF 链接**: https://arxiv.org/pdf/2603.23729v1
