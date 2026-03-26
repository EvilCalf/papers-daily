## 基本信息

- **标题**: Forecasting with Guidance: Representation-Level Supervision for Time Series Forecasting
- **作者**: Jiacheng Wang, Liang Fan, Baihua Li, Luyan Zhang
- **ArXiv ID**: 2603.24262v1
- **发布日期**: 2026-03-25
- **主分类**: cs.LG
- **分类**: cs.LG
- **摘要**: Nowadays, time series forecasting is predominantly approached through the end-to-end training of deep learning architectures using error-based objectives. While this is effective at minimizing average loss, it encourages the encoder to discard informative yet extreme patterns. This results in smooth predictions and temporal representations that poorly capture salient dynamics. To address this issue, we propose ReGuider, a plug-in method that can be seamlessly integrated into any forecasting architecture. ReGuider leverages pretrained time series foundation models as semantic teachers. During training, the input sequence is processed together by the target forecasting model and the pretrained model. Rather than using the pretrained model's outputs directly, we extract its intermediate embeddings, which are rich in temporal and semantic information, and align them with the target model's encoder embeddings through representation-level supervision. This alignment process enables the encoder to learn more expressive temporal representations, thereby improving the accuracy of downstream forecasting. Extensive experimentation across diverse datasets and architectures demonstrates that our ReGuider consistently improves forecasting performance, confirming its effectiveness and versatility.
- **PDF 链接**: https://arxiv.org/pdf/2603.24262v1
