## 基本信息

- **标题**: Dual Contrastive Network for Few-Shot Remote Sensing Image Scene Classification
- **作者**: Zhong Ji, Liyuan Hou, Xuan Wang, Gang Wang, Yanwei Pang
- **ArXiv ID**: 2603.23161v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Few-shot remote sensing image scene classification (FS-RSISC) aims at classifying remote sensing images with only a few labeled samples. The main challenges lie in small inter-class variances and large intra-class variances, which are the inherent property of remote sensing images. To address these challenges, we propose a transfer-based Dual Contrastive Network (DCN), which incorporates two auxiliary supervised contrastive learning branches during the training process. Specifically, one is a Context-guided Contrastive Learning (CCL) branch and the other is a Detail-guided Contrastive Learning (DCL) branch, which focus on inter-class discriminability and intra-class invariance, respectively. In the CCL branch, we first devise a Condenser Network to capture context features, and then leverage a supervised contrastive learning on top of the obtained context features to facilitate the model to learn more discriminative features. In the DCL branch, a Smelter Network is designed to highlight the significant local detail information. And then we construct a supervised contrastive learning based on the detail feature maps to fully exploit the spatial information in each map, enabling the model to concentrate on invariant detail features. Extensive experiments on four public benchmark remote sensing datasets demonstrate the competitive performance of our proposed DCN.
- **PDF 链接**: https://arxiv.org/pdf/2603.23161v1
