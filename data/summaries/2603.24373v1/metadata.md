## 基本信息

- **标题**: PP-OCRv5: A Specialized 5M-Parameter Model Rivaling Billion-Parameter Vision-Language Models on OCR Tasks
- **作者**: Cheng Cui, Yubo Zhang, Ting Sun, Xueqing Wang, Hongen Liu et al.
- **ArXiv ID**: 2603.24373v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: The advent of "OCR 2.0" and large-scale vision-language models (VLMs) has set new benchmarks in text recognition. However, these unified architectures often come with significant computational demands, challenges in precise text localization within complex layouts, and a propensity for textual hallucinations. Revisiting the prevailing notion that model scale is the sole path to high accuracy, this paper introduces PP-OCRv5, a meticulously optimized, lightweight OCR system with merely 5 million parameters. We demonstrate that PP-OCRv5 achieves performance competitive with many billion-parameter VLMs on standard OCR benchmarks, while offering superior localization precision and reduced hallucinations. The cornerstone of our success lies not in architectural expansion but in a data-centric investigation. We systematically dissect the role of training data by quantifying three critical dimensions: data difficulty, data accuracy, and data diversity. Our extensive experiments reveal that with a sufficient volume of high-quality, accurately labeled, and diverse data, the performance ceiling for traditional, efficient two-stage OCR pipelines is far higher than commonly assumed. This work provides compelling evidence for the viability of lightweight, specialized models in the large-model era and offers practical insights into data curation for OCR. The source code and models are publicly available at https://github.com/PaddlePaddle/PaddleOCR.
- **PDF 链接**: https://arxiv.org/pdf/2603.24373v1
