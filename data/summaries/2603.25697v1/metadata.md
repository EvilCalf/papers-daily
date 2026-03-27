## 基本信息

- **标题**: The Kitchen Loop: User-Spec-Driven Development for a Self-Evolving Codebase
- **作者**: Yannick Roy
- **ArXiv ID**: 2603.25697v1
- **发布日期**: 2026-03-26
- **主分类**: cs.SE
- **分类**: cs.SE, cs.AI
- **摘要**: Code production is now a commodity; the bottleneck is knowing what to build and proving it works. We present the Kitchen Loop, a framework for autonomous, self-evolving software built on a unified trust model: (1) a specification surface enumerating what the product claims to support; (2) 'As a User x 1000', where an LLM agent exercises that surface as a synthetic power user at 1,000x human cadence; (3) Unbeatable Tests, ground-truth verification the code author cannot fake; and (4) Drift Control, continuous quality measurement with automated pause gates. We validate across two production systems over 285+ iterations, producing 1,094+ merged pull requests with zero regressions detected by the regression oracle (methodology in Section 6.1). We observe emergent properties at scale: multi-iteration self-correction chains, autonomous infrastructure healing, and monotonically improving quality gates. The primitives are not new; our contribution is their composition into a production-tested system with the operational discipline that makes long-running autonomous evolution safe.
- **PDF 链接**: https://arxiv.org/pdf/2603.25697v1
