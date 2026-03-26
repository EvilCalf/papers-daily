## 基本信息

- **标题**: Foundation Model Embeddings Meet Blended Emotions: A Multimodal Fusion Approach for the BLEMORE Challenge
- **作者**: Masoumeh Chapariniya, Aref Farhadipour, Sarah Ebling, Volker Dellwo, Teodora Vukovic
- **ArXiv ID**: 2603.23650v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: We present our system for the BLEMORE Challenge at FG 2026 on blended emotion recognition with relative salience prediction. Our approach combines six encoder families through late probability fusion: an S4D-ViTMoE face encoder adapted with soft-label KL training, frozen layer-selective Wav2Vec2 audio features, finetuned body-language encoders (TimeSformer, VideoMAE), and -- for the first time in emotion recognition -- Gemini Embedding 2.0, a large multimodal model whose video embeddings produce competitive presence accuracy (ACCP = 0.320) from only 2 seconds of input. Three key findings emerge from our experiments: selecting prosody-encoding layers (6--12) from frozen Wav2Vec2 outperforms end-to-end finetuning (Score 0.207 vs. 0.161), as the non-verbal nature of BLEMORE audio makes phonetic layers irrelevant; the post-processing salience threshold $β$ varies from 0.05 to 0.43 across folds, revealing that personalized expression styles are the primary bottleneck; and task-adapted encoders collectively receive 62\% of ensemble weight over general-purpose baselines. Our 12-encoder system achieves Score = 0.279 (ACCP = 0.391, ACCS = 0.168) on the test set, placing 6th.
- **PDF 链接**: https://arxiv.org/pdf/2603.23650v1
