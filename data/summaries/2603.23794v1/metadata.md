## 基本信息

- **标题**: Sparse Autoencoders for Interpretable Medical Image Representation Learning
- **作者**: Philipp Wesp, Robbie Holland, Vasiliki Sideri-Lampretsa, Sergios Gatidis
- **ArXiv ID**: 2603.23794v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV, cs.LG
- **摘要**: Vision foundation models (FMs) achieve state-of-the-art performance in medical imaging. However, they encode information in abstract latent representations that clinicians cannot interrogate or verify. The goal of this study is to investigate Sparse Autoencoders (SAEs) for replacing opaque FM image representations with human-interpretable, sparse features. We train SAEs on embeddings from BiomedParse (biomedical) and DINOv3 (general-purpose) using 909,873 CT and MRI 2D image slices from the TotalSegmentator dataset. We find that learned sparse features: (a) reconstruct original embeddings with high fidelity (R2 up to 0.941) and recover up to 87.8% of downstream performance using only 10 features (99.4% dimensionality reduction), (b) preserve semantic fidelity in image retrieval tasks, (c) correspond to specific concepts that can be expressed in language using large language model (LLM)-based auto-interpretation. (d) bridge clinical language and abstract latent representations in zero-shot language-driven image retrieval. Our work indicates SAEs are a promising pathway towards interpretable, concept-driven medical vision systems. Code repository: https://github.com/pwesp/sail.
- **PDF 链接**: https://arxiv.org/pdf/2603.23794v1
