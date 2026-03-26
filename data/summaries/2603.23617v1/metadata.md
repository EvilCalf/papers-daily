## 基本信息

- **标题**: M3T: Discrete Multi-Modal Motion Tokens for Sign Language Production
- **作者**: Alexandre Symeonidis-Herzig, Jianhe Low, Ozge Mercanoglu Sincan, Richard Bowden
- **ArXiv ID**: 2603.23617v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Sign language production requires more than hand motion generation. Non-manual features, including mouthings, eyebrow raises, gaze, and head movements, are grammatically obligatory and cannot be recovered from manual articulators alone. Existing 3D production systems face two barriers to integrating them: the standard body model provides a facial space too low-dimensional to encode these articulations, and when richer representations are adopted, standard discrete tokenization suffers from codebook collapse, leaving most of the expression space unreachable. We propose SMPL-FX, which couples FLAME's rich expression space with the SMPL-X body, and tokenize the resulting representation with modality-specific Finite Scalar Quantization VAEs for body, hands, and face. M3T is an autoregressive transformer trained on this multi-modal motion vocabulary, with an auxiliary translation objective that encourages semantically grounded embeddings. Across three standard benchmarks (How2Sign, CSL-Daily, Phoenix14T) M3T achieves state-of-the-art sign language production quality, and on NMFs-CSL, where signs are distinguishable only by non-manual features, reaches 58.3% accuracy against 49.0% for the strongest comparable pose baseline.
- **PDF 链接**: https://arxiv.org/pdf/2603.23617v1
