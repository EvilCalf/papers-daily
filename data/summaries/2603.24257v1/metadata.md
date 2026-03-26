## 基本信息

- **标题**: Memory-Augmented Vision-Language Agents for Persistent and Semantically Consistent Object Captioning
- **作者**: Tommaso Galliena, Stefano Rosa, Tommaso Apicella, Pietro Morerio, Alessio Del Bue et al.
- **ArXiv ID**: 2603.24257v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Vision-Language Models (VLMs) often yield inconsistent descriptions of the same object across viewpoints, hindering the ability of embodied agents to construct consistent semantic representations over time. Previous methods resolved inconsistencies using offline multi-view aggregation or multi-stage pipelines that decouple exploration, data association, and caption learning, with limited capacity to reason over previously observed objects. In this paper, we introduce a unified, memory-augmented Vision-Language agent that simultaneously handles data association, object captioning, and exploration policy within a single autoregressive framework. The model processes the current RGB observation, a top-down explored map, and an object-level episodic memory serialized into object-level tokens, ensuring persistent object identity and semantic consistency across extended sequences. To train the model in a self-supervised manner, we collect a dataset in photorealistic 3D environments using a disagreement-based policy and a pseudo-captioning model that enforces consistency across multi-view caption histories. Extensive evaluation on a manually annotated object-level test set, demonstrate improvements of up to +11.86% in standard captioning scores and +7.39% in caption self-similarity over baseline models, while enabling scalable performance through a compact scene representation. Code, model weights, and data are available at https://github.com/hsp-iit/epos-vlm
- **PDF 链接**: https://arxiv.org/pdf/2603.24257v1
