## 基本信息

- **标题**: BXRL: Behavior-Explainable Reinforcement Learning
- **作者**: Ram Rachum, Yotam Amitai, Yonatan Nakar, Reuth Mirsky, Cameron Allen
- **ArXiv ID**: 2603.23738v1
- **发布日期**: 2026-03-24
- **主分类**: cs.LG
- **分类**: cs.LG
- **摘要**: A major challenge of Reinforcement Learning is that agents often learn undesired behaviors that seem to defy the reward structure they were given. Explainable Reinforcement Learning (XRL) methods can answer queries such as "explain this specific action", "explain this specific trajectory", and "explain the entire policy". However, XRL lacks a formal definition for behavior as a pattern of actions across many episodes. We provide such a definition, and use it to enable a new query: "Explain this behavior".   We present Behavior-Explainable Reinforcement Learning (BXRL), a new problem formulation that treats behaviors as first-class objects. BXRL defines a behavior measure as any function $m : Π\to \mathbb{R}$, allowing users to precisely express the pattern of actions that they find interesting and measure how strongly the policy exhibits it. We define contrastive behaviors that reduce the question "why does the agent prefer $a$ to $a'$?" to "why is $m(π)$ high?" which can be explored with differentiation. We do not implement an explainability method; we instead analyze three existing methods and propose how they could be adapted to explain behavior. We present a port of the HighwayEnv driving environment to JAX, which provides an interface for defining, measuring, and differentiating behaviors with respect to the model parameters.
- **PDF 链接**: https://arxiv.org/pdf/2603.23738v1
