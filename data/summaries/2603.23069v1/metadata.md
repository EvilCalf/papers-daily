## 基本信息

- **标题**: AuthorMix: Modular Authorship Style Transfer via Layer-wise Adapter Mixing
- **作者**: Sarubi Thillainathan, Ji-Ung Lee, Michael Sullivan, Alexander Koller
- **ArXiv ID**: 2603.23069v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CL
- **分类**: cs.CL, cs.AI
- **摘要**: The task of authorship style transfer involves rewriting text in the style of a target author while preserving the meaning of the original text. Existing style transfer methods train a single model on large corpora to model all target styles at once: this high-cost approach offers limited flexibility for target-specific adaptation, and often sacrifices meaning preservation for style transfer. In this paper, we propose AuthorMix: a lightweight, modular, and interpretable style transfer framework. We train individual, style-specific LoRA adapters on a small set of high-resource authors, allowing the rapid training of specialized adaptation models for each new target via learned, layer-wise adapter mixing, using only a handful of target style training examples. AuthorMix outperforms existing, SoTA style-transfer baselines -- as well as GPT-5.1 -- for low-resource targets, achieving the highest overall score and substantially improving meaning preservation.
- **PDF 链接**: https://arxiv.org/pdf/2603.23069v1
