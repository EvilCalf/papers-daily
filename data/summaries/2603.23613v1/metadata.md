## 基本信息

- **标题**: LLMLOOP: Improving LLM-Generated Code and Tests through Automated Iterative Feedback Loops
- **作者**: Ravin Ravi, Dylan Bradshaw, Stefano Ruberto, Gunel Jahangirova, Valerio Terragni
- **ArXiv ID**: 2603.23613v1
- **发布日期**: 2026-03-24
- **主分类**: cs.SE
- **分类**: cs.SE, cs.AI
- **摘要**: Large Language Models (LLMs) are showing remarkable performance in generating source code, yet the generated code often has issues like compilation errors or incorrect code. Researchers and developers often face wasted effort in implementing checks and refining LLM-generated code, frequently duplicating their efforts. This paper presents LLMLOOP, a framework that automates the refinement of both source code and test cases produced by LLMs. LLMLOOP employs five iterative loops: resolving compilation errors, addressing static analysis issues, fixing test case failures, and improving test quality through mutation analysis. These loops ensure the generation of high-quality test cases that serve as both a validation mechanism and a regression test suite for the generated code. We evaluated LLMLOOP on HUMANEVAL-X, a recent benchmark of programming tasks. Results demonstrate the tool's effectiveness in refining LLM-generated outputs.
- **PDF 链接**: https://arxiv.org/pdf/2603.23613v1
