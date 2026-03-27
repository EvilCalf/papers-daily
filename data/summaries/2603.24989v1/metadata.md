## 基本信息

- **标题**: Learning Rollout from Sampling:An R1-Style Tokenized Traffic Simulation Model
- **作者**: Ziyan Wang, Peng Chen, Ding Li, Chiwei Li, Qichao Zhang et al.
- **ArXiv ID**: 2603.24989v1
- **发布日期**: 2026-03-26
- **主分类**: cs.RO
- **分类**: cs.RO, cs.AI
- **摘要**: Learning diverse and high-fidelity traffic simulations from human driving demonstrations is crucial for autonomous driving evaluation. The recent next-token prediction (NTP) paradigm, widely adopted in large language models (LLMs), has been applied to traffic simulation and achieves iterative improvements via supervised fine-tuning (SFT). However, such methods limit active exploration of potentially valuable motion tokens, particularly in suboptimal regions. Entropy patterns provide a promising perspective for enabling exploration driven by motion token uncertainty. Motivated by this insight, we propose a novel tokenized traffic simulation policy, R1Sim, which represents an initial attempt to explore reinforcement learning based on motion token entropy patterns, and systematically analyzes the impact of different motion tokens on simulation outcomes. Specifically, we introduce an entropy-guided adaptive sampling mechanism that focuses on previously overlooked motion tokens with high uncertainty yet high potential. We further optimize motion behaviors using Group Relative Policy Optimization (GRPO), guided by a safety-aware reward design. Overall, these components enable a balanced exploration-exploitation trade-off through diverse high-uncertainty sampling and group-wise comparative estimation, resulting in realistic, safe, and diverse multi-agent behaviors. Extensive experiments on the Waymo Sim Agent benchmark demonstrate that R1Sim achieves competitive performance compared to state-of-the-art methods.
- **PDF 链接**: https://arxiv.org/pdf/2603.24989v1
