## 基本信息

- **标题**: Synchronous Signal Temporal Logic for Decidable Verification of Cyber-Physical Systems
- **作者**: Partha Roop, Sobhan Chatterjee, Avinash Malik, Nathan Allen, Logan Kenwright
- **ArXiv ID**: 2603.25531v1
- **发布日期**: 2026-03-26
- **主分类**: cs.FL
- **分类**: cs.FL, cs.CL
- **摘要**: Many Cyber Physical System (CPS) work in a safety-critical environment, where correct execution, reliability and trustworthiness are essential. Signal Temporal Logic (STL) provides a formal framework for checking safety-critical CPS. However, static verification of STL is undecidable in general, except when we want to verify using run-time-based methods, which have limitations. We propose Synchronous Signal Temporal Logic (SSTL), a decidable fragment of STL, which admits static safety and liveness property verification. In SSTL, we assume that a signal is sampled at fixed discrete steps, called ticks, and then propose a hypothesis, called the Signal Invariance Hypothesis (SIH), which is inspired by a similar hypothesis for synchronous programs. We define the syntax and semantics of SSTL and show that SIH is a necessary and sufficient condition for equivalence between an STL formula and its SSTL counterpart. By translating SSTL to LTL_P (LTL defined over predicates), we enable decidable model checking using the SPIN model checker. We demonstrate the approach on a 33-node human heart model and other case studies.
- **PDF 链接**: https://arxiv.org/pdf/2603.25531v1
