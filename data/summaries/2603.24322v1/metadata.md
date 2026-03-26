## 基本信息

- **标题**: Heuristic Self-Paced Learning for Domain Adaptive Semantic Segmentation under Adverse Conditions
- **作者**: Shiqin Wang, Haoyang Chen, Huaizhou Huang, Yinkan He, Dongfang Sun et al.
- **ArXiv ID**: 2603.24322v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: The learning order of semantic classes significantly impacts unsupervised domain adaptation for semantic segmentation, especially under adverse weather conditions. Most existing curricula rely on handcrafted heuristics (e.g., fixed uncertainty metrics) and follow a static schedule, which fails to adapt to a model's evolving, high-dimensional training dynamics, leading to category bias. Inspired by Reinforcement Learning, we cast curriculum learning as a sequential decision problem and propose an autonomous class scheduler. This scheduler consists of two components: (i) a high-dimensional state encoder that maps the model's training status into a latent space and distills key features indicative of progress, and (ii) a category-fair policy-gradient objective that ensures balanced improvement across classes. Coupled with mixed source-target supervision, the learned class rankings direct the network's focus to the most informative classes at each stage, enabling more adaptive and dynamic learning. It is worth noting that our method achieves state-of-the-art performance on three widely used benchmarks (e.g., ACDC, Dark Zurich, and Nighttime Driving) and shows generalization ability in synthetic-to-real semantic segmentation.
- **PDF 链接**: https://arxiv.org/pdf/2603.24322v1
