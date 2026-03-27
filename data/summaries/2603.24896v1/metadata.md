## 基本信息

- **标题**: LogSigma at SemEval-2026 Task 3: Uncertainty-Weighted Multitask Learning for Dimensional Aspect-Based Sentiment Analysis
- **作者**: Baraa Hikal, Jonas Becker, Bela Gipp
- **ArXiv ID**: 2603.24896v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL, cs.AI
- **摘要**: This paper describes LogSigma, our system for SemEval-2026 Task 3: Dimensional Aspect-Based Sentiment Analysis (DimABSA). Unlike traditional Aspect-Based Sentiment Analysis (ABSA), which predicts discrete sentiment labels, DimABSA requires predicting continuous Valence and Arousal (VA) scores on a 1-9 scale. A central challenge is that Valence and Arousal differ in prediction difficulty across languages and domains. We address this using learned homoscedastic uncertainty, where the model learns task-specific log-variance parameters to automatically balance each regression objective during training. Combined with language-specific encoders and multi-seed ensembling, LogSigma achieves 1st place on five datasets across both tracks. The learned variance weights vary substantially across languages due to differing Valence-Arousal difficulty profiles-from 0.66x for German to 2.18x for English-demonstrating that optimal task balancing is language-dependent and cannot be determined a priori.
- **PDF 链接**: https://arxiv.org/pdf/2603.24896v1
