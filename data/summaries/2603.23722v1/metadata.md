## 基本信息

- **标题**: Dual-Gated Epistemic Time-Dilation: Autonomous Compute Modulation in Asynchronous MARL
- **作者**: Igor Jankowski
- **ArXiv ID**: 2603.23722v1
- **发布日期**: 2026-03-24
- **主分类**: cs.MA
- **分类**: cs.MA, cs.LG
- **摘要**: While Multi-Agent Reinforcement Learning (MARL) algorithms achieve unprecedented successes across complex continuous domains, their standard deployment strictly adheres to a synchronous operational paradigm. Under this paradigm, agents are universally forced to execute deep neural network inferences at every micro-frame, regardless of immediate necessity. This dense throughput acts as a fundamental barrier to physical deployment on edge-devices where thermal and metabolic budgets are highly constrained. We propose Epistemic Time-Dilation MAPPO (ETD-MAPPO), augmented with a Dual-Gated Epistemic Trigger. Instead of depending on rigid frame-skipping (macro-actions), agents autonomously modulate their execution frequency by interpreting aleatoric uncertainty (via Shannon entropy of their policy) and epistemic uncertainty (via state-value divergence in a Twin-Critic architecture). To format this, we structure the environment as a Semi-Markov Decision Process (SMDP) and build the SMDP-Aligned Asynchronous Gradient Masking Critic to ensure proper credit assignment. Empirical findings demonstrate massive improvements (> 60% relative baseline acquisition leaps) over current temporal models. By assessing LBF, MPE, and the 115-dimensional state space of Google Research Football (GRF), ETD correctly prevented premature policy collapse. Remarkably, this unconstrained approach leads to emergent Temporal Role Specialization, reducing computational overhead by a statistically dominant 73.6% entirely during off-ball execution without deteriorating centralized task dominance.
- **PDF 链接**: https://arxiv.org/pdf/2603.23722v1
