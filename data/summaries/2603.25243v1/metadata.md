## 基本信息

- **标题**: FluxEDA: A Unified Execution Infrastructure for Stateful Agentic EDA
- **作者**: Zhengrui Chen, Zixuan Song, Yu Li, Qi Sun, Cheng Zhuo
- **ArXiv ID**: 2603.25243v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AR
- **分类**: cs.AR, cs.AI
- **摘要**: Large language models and autonomous agents are increasingly explored for EDA automation, but many existing integrations still rely on script-level or request-level interactions, which makes it difficult to preserve tool state and support iterative optimization in real production-oriented environments. In this work, we present FluxEDA, a unified and stateful infrastructure substrate for agentic EDA. FluxEDA introduces a managed gateway-based execution interface with structured request and response handling. It also maintains persistent backend instances. Together, these features allow upper-layer agents and programmable clients to interact with heterogeneous EDA tools through preserved runtime state, rather than through isolated shell invocations. We evaluate the framework using two representative commercial backend case studies: automated post-route timing ECO and standard-cell sub-library optimization. The results show that FluxEDA can support multi-step analysis and optimization over real tool contexts, including state reuse, rollback, and coordinated iterative execution. These findings suggest that a stateful and governed infrastructure layer is a practical foundation for agent-assisted EDA automation.
- **PDF 链接**: https://arxiv.org/pdf/2603.25243v1
