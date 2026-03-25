## 基本信息

- **标题**: MSR-HuBERT: Self-supervised Pre-training for Adaptation to Multiple Sampling Rates
- **作者**: Zikang Huang, Meng Ge, Tianrui Wang, Xuanchen Li, Xiaobao Wang et al.
- **ArXiv ID**: 2603.23048v1
- **发布日期**: 2026-03-24
- **主分类**: cs.SD
- **分类**: cs.SD, cs.AI
- **摘要**: Self-supervised learning (SSL) has advanced speech processing. However, existing speech SSL methods typically assume a single sampling rate and struggle with mixed-rate data due to temporal resolution mismatch. To address this limitation, we propose MSRHuBERT, a multi-sampling-rate adaptive pre-training method. Building on HuBERT, we replace its single-rate downsampling CNN with a multi-sampling-rate adaptive downsampling CNN that maps raw waveforms from different sampling rates to a shared temporal resolution without resampling. This design enables unified mixed-rate pre-training and fine-tuning. In experiments spanning 16 to 48 kHz, MSRHuBERT outperforms HuBERT on speech recognition and full-band speech reconstruction, preserving high-frequency detail while modeling low-frequency semantic structure. Moreover, MSRHuBERT retains HuBERT's mask-prediction objective and Transformer encoder, so existing analyses and improvements that were developed for HuBERT can apply directly.
- **PDF 链接**: https://arxiv.org/pdf/2603.23048v1
