## 基本信息

- **标题**: Optimizing Multilingual LLMs via Federated Learning: A Study of Client Language Composition
- **作者**: Aleix Sant, Jordi Luque, Carlos Escolano
- **ArXiv ID**: 2603.24242v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: Federated Learning (FL) of Large Language Models (LLMs) in multilingual environments presents significant challenges stemming from heterogeneous language distributions across clients and disparities in language resource availability. To address these challenges, we extended the FederatedScope-LLM framework to support multilingual instruction-tuning experiments with LLMs. We also introduced a novel client-specific early stopping mechanism, Local Dynamic Early Stopping (LDES-FL), which allows clients to pause and resume local training based on client-side validation performance, enhancing training efficiency and sustainability. Through a series of experiments, we studied how client language composition - from fully monolingual to increasingly multilingual clients - affects multilingual quality, fairness and training cost. Monolingual local fine-tuning remains the most effective for single-language specialization, whereas federated training is better suited to learning a single balanced multilingual model. In FL, increasing within-client multilinguality leads to stronger and fairer global models, narrows the gap to centralized multilingual fine-tuning, and yields the largest gains for lower-resource languages, albeit at the cost of more optimization steps. Overall, our results identify client language composition as a key design variable in multilingual FL, shaping performance, fairness and efficiency
- **PDF 链接**: https://arxiv.org/pdf/2603.24242v1
