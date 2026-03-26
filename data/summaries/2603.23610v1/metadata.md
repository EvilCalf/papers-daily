## 基本信息

- **标题**: Environment Maps: Structured Environmental Representations for Long-Horizon Agents
- **作者**: Yenchia Feng, Chirag Sharma, Karime Maamari
- **ArXiv ID**: 2603.23610v1
- **发布日期**: 2026-03-24
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Although large language models (LLMs) have advanced rapidly, robust automation of complex software workflows remains an open problem. In long-horizon settings, agents frequently suffer from cascading errors and environmental stochasticity; a single misstep in a dynamic interface can lead to task failure, resulting in hallucinations or trial-and-error. This paper introduces $\textit{Environment Maps}$: a persistent, agent-agnostic representation that mitigates these failures by consolidating heterogeneous evidence, such as screen recordings and execution traces, into a structured graph. The representation consists of four core components: (1) Contexts (abstracted locations), (2) Actions (parameterized affordances), (3) Workflows (observed trajectories), and (4) Tacit Knowledge (domain definitions and reusable procedures). We evaluate this framework on the WebArena benchmark across five domains. Agents equipped with environment maps achieve a 28.2% success rate, nearly doubling the performance of baselines limited to session-bound context (14.2%) and outperforming agents that have access to the raw trajectory data used to generate the environment maps (23.3%). By providing a structured interface between the model and the environment, Environment Maps establish a persistent foundation for long-horizon planning that is human-interpretable, editable, and incrementally refinable.
- **PDF 链接**: https://arxiv.org/pdf/2603.23610v1
