## 基本信息

- **标题**: Efficient Benchmarking of AI Agents
- **作者**: Franck Ndzomga
- **ArXiv ID**: 2603.23749v1
- **发布日期**: 2026-03-24
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Evaluating AI agents on comprehensive benchmarks is expensive because each evaluation requires interactive rollouts with tool use and multi-step reasoning. We study whether small task subsets can preserve agent rankings at substantially lower cost. Unlike static language model benchmarks, agent evaluation is subject to scaffold-driven distribution shift, since performance depends on the framework wrapping the underlying model. Across eight benchmarks, 33 agent scaffolds, and 70+ model configurations, we find that absolute score prediction degrades under this shift, while rank-order prediction remains stable. Exploiting this asymmetry, we propose a simple optimization-free protocol: evaluate new agents only on tasks with intermediate historical pass rates (30-70%). This mid-range difficulty filter, motivated by Item Response Theory, reduces the number of evaluation tasks by 44-70% while maintaining high rank fidelity under scaffold and temporal shifts. It provides more reliable rankings than random sampling, which exhibits high variance across seeds, and outperforms greedy task selection under distribution shift. These results suggest that reliable leaderboard ranking does not require full-benchmark evaluation.
- **PDF 链接**: https://arxiv.org/pdf/2603.23749v1
