## 基本信息

- **标题**: Revealing the influence of participant failures on model quality in cross-silo Federated Learning
- **作者**: Fabian Stricker, David Bermbach, Christian Zirpins
- **ArXiv ID**: 2603.25289v1
- **发布日期**: 2026-03-26
- **主分类**: cs.DC
- **分类**: cs.DC, cs.AI
- **摘要**: Federated Learning (FL) is a paradigm for training machine learning (ML) models in collaborative settings while preserving participants' privacy by keeping raw data local. A key requirement for the use of FL in production is reliability, as insufficient reliability can compromise the validity, stability, and reproducibility of learning outcomes. FL inherently operates as a distributed system and is therefore susceptible to crash failures, network partitioning, and other fault scenarios. Despite this, the impact of such failures on FL outcomes has not yet been studied systematically.   In this paper, we address this gap by investigating the impact of missing participants in FL. To this end, we conduct extensive experiments on image, tabular, and time-series data and analyze how the absence of participants affects model performance, taking into account influencing factors such as data skewness, different availability patterns, and model architectures. Furthermore, we examine scenario-specific aspects, including the utility of the global model for missing participants. Our experiments provide detailed insights into the effects of various influencing factors. In particular, we show that data skewness has a strong impact, often leading to overly optimistic model evaluations and, in some cases, even altering the effects of other influencing factors.
- **PDF 链接**: https://arxiv.org/pdf/2603.25289v1
