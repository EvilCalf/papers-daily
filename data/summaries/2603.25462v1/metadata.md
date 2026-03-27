## 基本信息

- **标题**: Temporally Decoupled Diffusion Planning for Autonomous Driving
- **作者**: Xiang Li, Bikun Wang, John Zhang, Jianjun Wang
- **ArXiv ID**: 2603.25462v1
- **发布日期**: 2026-03-26
- **主分类**: cs.RO
- **分类**: cs.RO, cs.AI
- **摘要**: Motion planning in dynamic urban environments requires balancing immediate safety with long-term goals. While diffusion models effectively capture multi-modal decision-making, existing approaches treat trajectories as monolithic entities, overlooking heterogeneous temporal dependencies where near-term plans are constrained by instantaneous dynamics and far-term plans by navigational goals. To address this, we propose Temporally Decoupled Diffusion Model (TDDM), which reformulates trajectory generation via a noise-as-mask paradigm. By partitioning trajectories into segments with independent noise levels, we implicitly treat high noise as information voids and weak noise as contextual cues. This compels the model to reconstruct corrupted near-term states by leveraging internal correlations with better-preserved temporal contexts. Architecturally, we introduce a Temporally Decoupled Adaptive Layer Normalization (TD-AdaLN) to inject segment-specific timesteps. During inference, our Asymmetric Temporal Classifier-Free Guidance utilizes weakly noised far-term priors to guide immediate path generation. Evaluations on the nuPlan benchmark show TDDM approaches or exceeds state-of-the-art baselines, particularly excelling in the challenging Test14-hard subset.
- **PDF 链接**: https://arxiv.org/pdf/2603.25462v1
