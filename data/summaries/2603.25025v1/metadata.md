## 基本信息

- **标题**: System-Anchored Knee Estimation for Low-Cost Context Window Selection in PDE Forecasting
- **作者**: Wenshuo Wang, Fan Zhang
- **ArXiv ID**: 2603.25025v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Autoregressive neural PDE simulators predict the evolution of physical fields one step at a time from a finite history, but low-cost context-window selection for such simulators remains an unformalized problem. Existing approaches to context-window selection in time-series forecasting include exhaustive validation, direct low-cost search, and system-theoretic memory estimation, but they are either expensive, brittle, or not directly aligned with downstream rollout performance. We formalize explicit context-window selection for fixed-window autoregressive neural PDE simulators as an independent low-cost algorithmic problem, and propose \textbf{System-Anchored Knee Estimation (SAKE)}, a two-stage method that first identifies a small structured candidate set from physically interpretable system anchors and then performs knee-aware downstream selection within it. Across all eight PDEBench families evaluated under the shared \(L\in\{1,\dots,16\}\) protocol, SAKE is the strongest overall matched-budget low-cost selector among the evaluated methods, achieving 67.8\% Exact, 91.7\% Within-1, 6.1\% mean regret@knee, and a cost ratio of 0.051 (94.9\% normalized search-cost savings).
- **PDF 链接**: https://arxiv.org/pdf/2603.25025v1
