## 基本信息

- **标题**: Mechanistically Interpreting Compression in Vision-Language Models
- **作者**: Veeraraju Elluru, Arth Singh, Roberto Aguero, Ajay Agarwal, Debojyoti Das et al.
- **ArXiv ID**: 2603.25035v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Compressed vision-language models (VLMs) are widely used to reduce memory and compute costs, making them a suitable choice for real-world deployment. However, compressing these models raises concerns about whether internal computations and safety behaviors are preserved. In this work, we use causal circuit analysis and crosscoder-based feature comparisons to examine how pruning and quantization fundamentally change the internals across representative VLMs. We observe that pruning generally keeps circuit structure intact but rotates and attenuates internal features, while quantization modifies the circuits at a higher level yet leaves the surviving features better aligned. Leveraging this insight, we also introduce VLMSafe-420, a novel benchmark that pairs harmful inputs with matched benign counterfactuals across various safety categories. Our findings show that pruning causes a sharp drop in genuine refusal behavior, suggesting that the choice of compression has safety implications.
- **PDF 链接**: https://arxiv.org/pdf/2603.25035v1
