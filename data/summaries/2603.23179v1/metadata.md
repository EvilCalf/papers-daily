## 基本信息

- **标题**: Gimbal360: Differentiable Auto-Leveling for Canonicalized $360^\circ$ Panoramic Image Completion
- **作者**: Yuqin Lu, Haofeng Liu, Yang Zhou, Jun Liang, Shengfeng He et al.
- **ArXiv ID**: 2603.23179v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Diffusion models excel at 2D outpainting, but extending them to $360^\circ$ panoramic completion from unposed perspective images is challenging due to the geometric and topological mismatch between perspective projections and spherical panoramas. We present Gimbal360, a principled framework that explicitly bridges perspective observations and spherical panoramas. We introduce a Canonical Viewing Space that regularizes projective geometry and provides a consistent intermediate representation between the two domains. To anchor in-the-wild inputs to this space, we propose a Differentiable Auto-Leveling module that stabilizes feature orientation without requiring camera parameters at inference. Panoramic generation also introduces a topological challenge. Standard generative architectures assume a bounded Euclidean image plane, while Equirectangular Projection (ERP) panoramas exhibit intrinsic $S^1$ periodicity. Euclidean operations therefore break boundary continuity. We address this mismatch by enforcing topological equivariance in the latent space to preserve seamless periodic structure. To support this formulation, we introduce Horizon360, a curated large-scale dataset of gravity-aligned panoramic environments. Extensive experiments show that explicitly standardizing geometric and topological priors enables Gimbal360 to achieve state-of-the-art performance in structurally consistent $360^\circ$ scene completion.
- **PDF 链接**: https://arxiv.org/pdf/2603.23179v1
