## 基本信息

- **标题**: 4OPS: Structural Difficulty Modeling in Integer Arithmetic Puzzles
- **作者**: Yunus E. Zeytuncu
- **ArXiv ID**: 2603.25356v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Arithmetic puzzle games provide a controlled setting for studying difficulty in mathematical reasoning tasks, a core challenge in adaptive learning systems. We investigate the structural determinants of difficulty in a class of integer arithmetic puzzles inspired by number games. We formalize the problem and develop an exact dynamic-programming solver that enumerates reachable targets, extracts minimal-operation witnesses, and enables large-scale labeling.   Using this solver, we construct a dataset of over 3.4 million instances and define difficulty via the minimum number of operations required to reach a target. We analyze the relationship between difficulty and solver-derived features. While baseline machine learning models based on bag- and target-level statistics can partially predict solvability, they fail to reliably distinguish easy instances. In contrast, we show that difficulty is fully determined by a small set of interpretable structural attributes derived from exact witnesses. In particular, the number of input values used in a minimal construction serves as a minimal sufficient statistic for difficulty under this labeling.   These results provide a transparent, computationally grounded account of puzzle difficulty that bridges symbolic reasoning and data-driven modeling. The framework supports explainable difficulty estimation and principled task sequencing, with direct implications for adaptive arithmetic learning and intelligent practice systems.
- **PDF 链接**: https://arxiv.org/pdf/2603.25356v1
