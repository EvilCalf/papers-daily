## 基本信息

- **标题**: Describe-Then-Act: Proactive Agent Steering via Distilled Language-Action World Models
- **作者**: Massimiliano Pappa, Luca Romani, Valentino Sacco, Alessio Palma, Stéphane Lathuilière et al.
- **ArXiv ID**: 2603.23149v1
- **发布日期**: 2026-03-24
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Deploying safety-critical agents requires anticipating the consequences of actions before they are executed. While world models offer a paradigm for this proactive foresight, current approaches relying on visual simulation incur prohibitive latencies, often exceeding several seconds per step. In this work, we challenge the assumption that visual processing is necessary for failure prevention. We show that a trained policy's latent state, combined with its planned actions, already encodes sufficient information to anticipate action outcomes, making visual simulation redundant for failure prevention. To this end, we introduce DILLO (DIstiLLed Language-ActiOn World Model), a fast steering layer that shifts the paradigm from "simulate-then-act" to "describe-then-act." DILLO is trained via cross-modal distillation, where a privileged Vision Language Model teacher annotates offline trajectories and a latent-conditioned Large Language Model student learns to predict semantic outcomes. This creates a text-only inference path, bypassing heavy visual generation entirely, achieving a 14x speedup over baselines. Experiments on MetaWorld and LIBERO demonstrate that DILLO produces high-fidelity descriptions of the next state and is able to steer the policy, improving episode success rate by up to 15 pp and 9.3 pp on average across tasks.
- **PDF 链接**: https://arxiv.org/pdf/2603.23149v1
