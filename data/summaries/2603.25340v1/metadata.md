## 基本信息

- **标题**: Large Language Model as Token Compressor and Decompressor
- **作者**: Wenbing Li, Zikai Song, Jielei Zhang, Tianhao Zhao, Junkai Lin et al.
- **ArXiv ID**: 2603.25340v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: In this paper, we establish the novel insight that an off-the-shelf LLM can function as an excellent token compressor and decompressor. To demonstrate, we design a self-expressive autoencoding learning framework fine-tunes a pretrained LLM to translate long texts into a compact internal language of discrete, variable-length latent codes, termed Z-tokens, and to reconstruct the original text exactly from them. The resulting representation is content-adaptive: semantically dense segments receive more Z-tokens, while redundant or predictable regions are aggressively compressed, via lightweight LoRA-based adapter heads. Empirically, our method achieves up to 18 times token reduction on Wikipedia, CNN/DailyMail, HotpotQA, and Qulac-style long-query datasets, while preserving reconstruction fidelity and downstream performance. This simple yet effective design supports applications including prompt compression and autoregressive generation directly in the Z-token space, offering a potential pathway toward token-efficient long-context reasoning.
- **PDF 链接**: https://arxiv.org/pdf/2603.25340v1
