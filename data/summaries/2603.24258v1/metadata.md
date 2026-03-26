## 基本信息

- **标题**: Semantic Alignment across Ancient Egyptian Language Stages via Normalization-Aware Multitask Learning
- **作者**: He Huang
- **ArXiv ID**: 2603.24258v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: We study word-level semantic alignment across four historical stages of Ancient Egyptian. These stages differ in script and orthography, and parallel data are scarce. We jointly train a compact encoder-decoder model with a shared byte-level tokenizer on all four stages, combining masked language modeling (MLM), translation language modeling (TLM), sequence-to-sequence translation, and part-of-speech tagging under a task-aware loss with fixed weights and uncertainty-based scaling. To reduce surface divergence we add Latin transliteration and IPA reconstruction as auxiliary views. We integrate these views through KL-based consistency and through embedding-level fusion. We evaluate alignment quality using pairwise metrics, specifically ROC-AUC and triplet accuracy, on curated Egyptian-English and intra-Egyptian cognate datasets. Translation yields the strongest gains. IPA with KL consistency improves cross-branch alignment, while early fusion demonstrates limited efficacy. Although the overall alignment remains limited, the findings provide a reproducible baseline and practical guidance for modeling historical languages under real constraints. They also show how normalization and task design shape what counts as alignment in typologically distant settings.
- **PDF 链接**: https://arxiv.org/pdf/2603.24258v1
