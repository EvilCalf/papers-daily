## 基本信息

- **标题**: System Design for Maintaining Internal State Consistency in Long-Horizon Robotic Tabletop Games
- **作者**: Guangyu Zhao, Ceyao Zhang, Chengdong Ma, Tao Wu, Yiyang Song et al.
- **ArXiv ID**: 2603.25405v1
- **发布日期**: 2026-03-26
- **主分类**: cs.RO
- **分类**: cs.RO, cs.AI
- **摘要**: Long-horizon tabletop games pose a distinct systems challenge for robotics: small perceptual or execution errors can invalidate accumulated task state, propagate across decision-making modules, and ultimately derail interaction. This paper studies how to maintain internal state consistency in turn-based, multi-human robotic tabletop games through deliberate system design rather than isolated component improvement. Using Mahjong as a representative long-horizon setting, we present an integrated architecture that explicitly maintains perceptual, execution, and interaction state, partitions high-level semantic reasoning from time-critical perception and control, and incorporates verified action primitives with tactile-triggered recovery to prevent premature state corruption. We further introduce interaction-level monitoring mechanisms to detect turn violations and hidden-information breaches that threaten execution assumptions. Beyond demonstrating complete-game operation, we provide an empirical characterization of failure modes, recovery effectiveness, cross-module error propagation, and hardware-algorithm trade-offs observed during deployment. Our results show that explicit partitioning, monitored state transitions, and recovery mechanisms are critical for sustaining executable consistency over extended play, whereas monolithic or unverified pipelines lead to measurable degradation in end-to-end reliability. The proposed system serves as an empirical platform for studying system-level design principles in long-horizon, turn-based interaction.
- **PDF 链接**: https://arxiv.org/pdf/2603.25405v1
