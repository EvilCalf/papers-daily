## 基本信息

- **标题**: Sparse Visual Thought Circuits in Vision-Language Models
- **作者**: Yunpeng Zhou
- **ArXiv ID**: 2603.25075v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Sparse autoencoders (SAEs) improve interpretability in multimodal models, but it remains unclear whether SAE features form modular, composable units for reasoning-an assumption underlying many intervention-based steering methods. We test this modularity hypothesis and find it often fails: intervening on a task-selective feature set can modestly improve reasoning accuracy, while intervening on the union of two such sets reliably induces output drift (large unintended changes in predictions) and degrades accuracy, even under norm-matched perturbations. This non modular circuit interference is consistent with shared internal pathways where feature unions amplify activation shifts. We develop a reproducible causal pipeline to localize and test these sparse visual thought circuits in Qwen3-VL-8B. On a controlled synthetic benchmark with seven task types and three difficulty levels, linear probes identify a mid decoder locus for task type information. We train SAEs at this layer, construct task-selective sets via an explicit rule, and perform inference time scaling and ablation while quantifying accuracy and drift. Our findings-validated with bootstrapped subsamples and permutation controls, and replicated across multiple VLM families and five diverse datasets clarify the boundaries of SAE feature composability and provide a rigorous diagnostic framework for more reliable VLM control.
- **PDF 链接**: https://arxiv.org/pdf/2603.25075v1
