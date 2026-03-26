## 基本信息

- **标题**: RVLM: Recursive Vision-Language Models with Adaptive Depth
- **作者**: Nicanor Mayumu, Zeenath Khan, Melodena Stephens, Patrick Mukala, Farhad Oroumchian
- **ArXiv ID**: 2603.24224v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Medical AI systems face two fundamental limitations. First, conventional vision-language models (VLMs) perform single-pass inference, yielding black-box predictions that cannot be audited or explained in clinical terms. Second, iterative reasoning systems that expose intermediate steps rely on fixed iteration budgets wasting compute on simple cases while providing insufficient depth for complex ones. We address both limitations with a unified framework. RVLM replaces single-pass inference with an iterative generate-execute loop: at each step, the model writes Python code, invokes vision sub-agents, manipulates images, and accumulates evidence. Every diagnostic claim is grounded in executable code, satisfying auditability requirements of clinical AI governance frameworks. RRouter makes iteration depth adaptive: a lightweight controller predicts the optimal budget from task-complexity features, then monitors progress and terminates early when reasoning stalls. We evaluate on BraTS 2023 Meningioma (brain MRI) and MIMIC-CXR (chest X-ray) using Gemini 2.5 Flash without fine-tuning. Across repeated runs, RVLM shows high consistency on salient findings (e.g., mass presence and enhancement) and can detect cross-modal discrepancies between Fluid-Attenuated Inversion Recovery (FLAIR) signal characteristics and segmentation boundaries. On MIMIC-CXR, it generates structured reports and correctly recognises view-specific artefacts. Code: https://github.com/nican2018/rvlm.
- **PDF 链接**: https://arxiv.org/pdf/2603.24224v1
