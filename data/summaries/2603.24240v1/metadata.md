## 基本信息

- **标题**: InstanceRSR: Real-World Super-Resolution via Instance-Aware Representation Alignment
- **作者**: Zixin Guo, Kai Zhao, Luyan Zhang
- **ArXiv ID**: 2603.24240v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Existing real-world super-resolution (RSR) methods based on generative priors have achieved remarkable progress in producing high-quality and globally consistent reconstructions. However, they often struggle to recover fine-grained details of diverse object instances in complex real-world scenes. This limitation primarily arises because commonly adopted denoising losses (e.g., MSE) inherently favor global consistency while neglecting instance-level perception and restoration. To address this issue, we propose InstanceRSR, a novel RSR framework that jointly models semantic information and introduces instance-level feature alignment. Specifically, we employ low-resolution (LR) images as global consistency guidance while jointly modeling image data and semantic segmentation maps to enforce semantic relevance during sampling. Moreover, we design an instance representation learning module to align the diffusion latent space with the instance latent space, enabling instance-aware feature alignment, and further incorporate a scale alignment mechanism to enhance fine-grained perception and detail recovery. Benefiting from these designs, our approach not only generates photorealistic details but also preserves semantic consistency at the instance level. Extensive experiments on multiple real-world benchmarks demonstrate that InstanceRSR significantly outperforms existing methods in both quantitative metrics and visual quality, achieving new state-of-the-art (SOTA) performance.
- **PDF 链接**: https://arxiv.org/pdf/2603.24240v1
